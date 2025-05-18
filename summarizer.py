import fitz
from keybert import KeyBERT
from transformers import pipeline
import re

# Initialize the models
kw_model = KeyBERT(model='all-MiniLM-L6-v2')
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def extract_text_from_pdf(pdf_path, max_pages=2):
    """Extract text from PDF with font information for the first page"""
    doc = fitz.open(pdf_path)

    # For regular text extraction (used for summary, etc.)
    full_text = ""
    for page in doc[:max_pages]:
        full_text += page.get_text()

    return full_text


def extract_text_with_font_info(pdf_path):
    """Extract text with font size information from the first page"""
    doc = fitz.open(pdf_path)
    if len(doc) == 0:
        return []

    page = doc[0]  # Get just the first page where title usually is

    # Extract text blocks with their font sizes
    text_with_font = []
    blocks = page.get_text("dict")["blocks"]

    for block in blocks:
        if "lines" in block:
            for line in block["lines"]:
                if "spans" in line:
                    for span in line["spans"]:
                        if "text" in span and "size" in span:
                            text = span["text"].strip()
                            size = span["size"]
                            if text:  # Only add non-empty text
                                text_with_font.append((text, size))

    return text_with_font


def extract_title_from_font_info(text_with_font):
    """Extract title based on font size and position"""
    if not text_with_font:
        return None

    # Find the largest font size in the first few items (likely to be the title)
    # Only consider the first 10 text elements to avoid picking up section headers
    first_elements = text_with_font[:10]
    font_sizes = [size for _, size in first_elements]

    if not font_sizes:
        return None

    # Find elements with the largest or near-largest font
    # (sometimes title might be slightly smaller than a header number)
    max_font = max(font_sizes)
    title_threshold = max_font * 0.8  # Allow some variation in font size

    # Get consecutive text elements with large font that are likely the title
    title_elements = []

    for text, size in first_elements:
        # Skip single characters or very short elements unless they have the max font size
        if (len(text) <= 1 or len(text) < 4) and size < max_font:
            continue

        # Skip items that are clearly not part of title (references, single letters)
        if re.search(r'^\[\d+\]$|^[a-zA-Z]$', text):
            continue

        # Include text elements with font size at or above our threshold
        if size >= title_threshold:
            # Check if it looks like author information
            if not re.search(r'\b(department|university|institute|email|@)\b', text.lower()):
                title_elements.append(text)
        else:
            # Once we hit smaller text, we've likely moved past the title
            # (Assuming title is at the top with consistent font size)
            if title_elements:  # Only break if we already found some title elements
                break

    if title_elements:
        return " ".join(title_elements)

    return None


def extract_authors(text, title=None, pdf_path=None):
    """Extract author names from the text after the title"""

    # Strategy 1: Use font information to identify authors
    if pdf_path:
        try:
            text_with_font = extract_text_with_font_info(pdf_path)

            # If we have a title, find where the title ends
            if title:
                title_end_index = -1
                title_words = title.split()

                # Find the last word of the title in the text_with_font
                for i, (text_elem, _) in enumerate(text_with_font):
                    if any(title_word in text_elem for title_word in title_words[-2:]):
                        title_end_index = i
                        break

                # Look for authors after the title
                if title_end_index >= 0 and title_end_index + 1 < len(text_with_font):
                    # Check the next few elements for author patterns
                    potential_authors = []
                    for i in range(title_end_index + 1, min(title_end_index + 10, len(text_with_font))):
                        text_elem, size = text_with_font[i]

                        # Skip if it's likely part of an abstract, header, or email
                        if re.search(r'\b(abstract|introduction|keywords)\b', text_elem.lower()):
                            break

                        # Authors often have commas, 'and', or are short names
                        if (',' in text_elem or ' and ' in text_elem.lower() or
                                (len(text_elem.split()) <= 4 and len(text_elem) > 3)):
                            potential_authors.append(text_elem)

                        # Stop if we hit institution information
                        if re.search(r'\b(university|department|institute|school)\b', text_elem.lower()):
                            break

                    if potential_authors:
                        return " ".join(potential_authors)
        except Exception as e:
            print(f"Font-based author extraction error: {e}")

    # Strategy 2: Position-based extraction from plain text
    if title:
        lines = text.strip().split("\n")
        title_found = False
        author_candidates = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip until we find the title
            if not title_found:
                # Check if this line contains a significant part of the title
                title_words = [w for w in title.split() if len(w) > 3]
                if any(word in line for word in title_words[:3]):
                    title_found = True
                continue

            # Once we find the title, check the next few non-empty lines for author patterns
            if title_found:
                # Skip if it's likely part of an abstract, header, or email
                if re.search(r'\b(abstract|introduction|keywords)\b', line.lower()):
                    break

                # Authors often have commas, 'and', or are short names with no special formatting
                if (',' in line or ' and ' in line.lower() or
                        (len(line.split()) <= 6 and len(line) > 3 and len(line) < 100)):
                    author_candidates.append(line)

                # Stop if we hit institution information or likely paragraph text
                if (re.search(r'\b(university|department|institute|school)\b', line.lower()) or
                        len(line) > 100):
                    break

                # Stop after collecting a few lines that are likely authors
                if len(author_candidates) >= 3:
                    break

        if author_candidates:
            # Filter out lines that are clearly not author names
            filtered_authors = []
            for candidate in author_candidates:
                # Skip lines with obvious non-author indicators
                if (re.search(r'\b(http|www|doi|©|journal|received|accepted|published)\b',
                              candidate.lower())):
                    continue
                filtered_authors.append(candidate)

            if filtered_authors:
                return " ".join(filtered_authors)

    # Strategy 3: Pattern-based extraction without title context
    lines = text.strip().split("\n")
    for i in range(min(10, len(lines))):
        line = lines[i].strip()
        # Look for typical author patterns in the first few lines
        if (',' in line and ' and ' in line.lower() and
                not re.search(r'\b(abstract|introduction|http|www)\b', line.lower()) and
                len(line) < 150):
            return line

    return "Authors not found"


def improved_extract_title(text, pdf_path=None):
    """Extract title using multiple strategies for scientific papers.
    If pdf_path is provided, use font information for better accuracy."""

    # Strategy 1: Extract based on font size if PDF path is available
    if pdf_path:
        try:
            text_with_font = extract_text_with_font_info(pdf_path)
            font_based_title = extract_title_from_font_info(text_with_font)
            if font_based_title and len(font_based_title) > 10:
                return font_based_title
        except Exception as e:
            print(f"Font-based extraction error: {e}")

    # Strategy 2: Position and pattern-based extraction
    lines = text.strip().split("\n")
    content_lines = []

    # Get non-empty lines without headers/footers
    for line in lines:
        line = line.strip()
        if line and not re.search(r'(page|doi|©|http|www|\d+\s*$)', line.lower()):
            content_lines.append(line)

    # Look at the first few non-empty lines as title candidates
    title_lines = []

    # List of patterns that typically appear after the title
    end_markers = [
        r'\babstract\b',
        r'\bintroduction\b',
        r'\b(university|institute|college|school)\b',
        r'\b(department)\b',
        r'@',
        r'\bemail\b',
        r'^\d\s',  # Numbers that start author affiliations
        r'\[\d+\]',  # Citation-style references
        r'\d{4}',  # Years
        r'\b(submitted|received|accepted|published)\b'
    ]

    # Collect potential title lines from the beginning
    for i in range(min(5, len(content_lines))):
        line = content_lines[i]

        # Skip very short lines unless it's the only line we have
        if len(line) < 3 and i > 0:
            continue

        # Stop if we hit title end markers
        if any(re.search(pattern, line.lower()) for pattern in end_markers):
            break

        # Check if this looks like author names (typically shorter and with commas)
        if i > 0 and (len(line) < 30 and (',' in line or len(line.split()) <= 3)):
            is_likely_author = True
            # But make sure we don't mistake short title fragments for author names
            for prev_line in title_lines:
                # If it looks like it completes the previous line, include it
                if len(prev_line) < 50 and not prev_line.endswith('.'):
                    is_likely_author = False
                    break
            if is_likely_author:
                break

        # Include the line if it passes our checks
        if len(line) < 200:  # Avoid extremely long lines
            title_lines.append(line)

    # Combine title lines
    if title_lines:
        return " ".join(title_lines)

    # Strategy 3: Fallback to KeyBERT
    try:
        first_text = " ".join(content_lines[:15])
        keywords = kw_model.extract_keywords(
            first_text,
            keyphrase_ngram_range=(3, 8),
            stop_words='english',
            top_n=1,
            use_maxsum=True
        )
        if keywords:
            return keywords[0][0]
    except Exception as e:
        print(f"KeyBERT fallback error: {e}")

    # Final fallback - take the first substantial line
    for line in content_lines[:3]:
        if len(line) > 15 and len(line) < 200:
            return line

    return "Unknown Title"


def clean_text(text):
    text = text.replace("-\n", "")
    text = text.replace("\n", " ")
    return text


def extract_keywords_with_bert(text, top_n=15):
    keywords = kw_model.extract_keywords(
        text, keyphrase_ngram_range=(1, 3), stop_words='english', top_n=top_n
    )
    return [kw for kw, score in keywords]


def summarize(text):
    # Make sure we're within the model's token limits
    max_input_length = 1024  # BART has input limitations
    if len(text.split()) > max_input_length:
        text = " ".join(text.split()[:max_input_length])

    summary = summarizer(text, max_length=100, min_length=30, do_sample=False)
    return summary[0]['summary_text']