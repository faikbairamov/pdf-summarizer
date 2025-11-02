import fitz
from keybert import KeyBERT
from transformers import pipeline
import re
import logging
from functools import lru_cache
from config import MODEL_CONFIG, FILE_CONFIG, LOGGING_CONFIG

logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG["level"]),
    format=LOGGING_CONFIG["format"]
)
logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def get_models():
    """Cache model loading to avoid reloading on each function call"""
    logger.info("Loading models...")
    try:
        kw_model = KeyBERT(model=MODEL_CONFIG["keybert_model"])
        summarizer = pipeline("summarization", model=MODEL_CONFIG["summarizer_model"], device=-1)  # Use CPU to avoid device issues
        return kw_model, summarizer
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        # Fallback to CPU-only models
        kw_model = KeyBERT(model=MODEL_CONFIG["keybert_model"])
        summarizer = pipeline("summarization", model=MODEL_CONFIG["summarizer_model"], device=-1)
        return kw_model, summarizer


def extract_text_from_pdf(pdf_path, max_pages=None):
    """Extract text from PDF with font information for the first page"""
    if max_pages is None:
        max_pages = FILE_CONFIG["max_pages_extract"]
    
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc[:max_pages]:
            full_text += page.get_text()
        doc.close()
        return full_text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise


def extract_text_with_font_info(pdf_path):
    """Extract text with font size information from the first page"""
    try:
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            doc.close()
            return []

        page = doc[0]
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
                                if text:
                                    text_with_font.append((text, size))
        doc.close()
        return text_with_font
    except Exception as e:
        logger.error(f"Error extracting font info: {e}")
        return []


def extract_title_from_font_info(text_with_font):
    """Extract title based on font size and position"""
    if not text_with_font:
        return None

    first_elements = text_with_font[:10]
    font_sizes = [size for _, size in first_elements]

    if not font_sizes:
        return None

    max_font = max(font_sizes)
    title_threshold = max_font * 0.8
    title_elements = []

    for text, size in first_elements:
        if (len(text) <= 1 or len(text) < 4) and size < max_font:
            continue

        if re.search(r'^\[\d+\]$|^[a-zA-Z]$', text):
            continue

        if size >= title_threshold:
            if not re.search(r'\b(department|university|institute|email|@)\b', text.lower()):
                title_elements.append(text)
        else:
            if title_elements:
                break

    if title_elements:
        return " ".join(title_elements)

    return None


def extract_authors(text, title=None, pdf_path=None):
    """Extract author names from the text after the title"""
    if pdf_path:
        try:
            text_with_font = extract_text_with_font_info(pdf_path)

            if title:
                title_end_index = -1
                title_words = title.split()

                for i, (text_elem, _) in enumerate(text_with_font):
                    if any(title_word in text_elem for title_word in title_words[-2:]):
                        title_end_index = i
                        break

                if title_end_index >= 0 and title_end_index + 1 < len(text_with_font):
                    potential_authors = []
                    for i in range(title_end_index + 1, min(title_end_index + 10, len(text_with_font))):
                        text_elem, size = text_with_font[i]

                        if re.search(r'\b(abstract|introduction|keywords)\b', text_elem.lower()):
                            break

                        if (',' in text_elem or ' and ' in text_elem.lower() or
                                (len(text_elem.split()) <= 4 and len(text_elem) > 3)):
                            potential_authors.append(text_elem)

                        if re.search(r'\b(university|department|institute|school)\b', text_elem.lower()):
                            break

                    if potential_authors:
                        return " ".join(potential_authors)
        except Exception as e:
            logger.error(f"Font-based author extraction error: {e}")

    if title:
        lines = text.strip().split("\n")
        title_found = False
        author_candidates = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if not title_found:
                title_words = [w for w in title.split() if len(w) > 3]
                if any(word in line for word in title_words[:3]):
                    title_found = True
                continue

            if title_found:
                if re.search(r'\b(abstract|introduction|keywords)\b', line.lower()):
                    break

                if (',' in line or ' and ' in line.lower() or
                        (len(line.split()) <= 6 and len(line) > 3 and len(line) < 100)):
                    author_candidates.append(line)

                if (re.search(r'\b(university|department|institute|school)\b', line.lower()) or
                        len(line) > 100):
                    break

                if len(author_candidates) >= 3:
                    break

        if author_candidates:
            filtered_authors = []
            for candidate in author_candidates:
                if (re.search(r'\b(http|www|doi|©|journal|received|accepted|published)\b',
                              candidate.lower())):
                    continue
                filtered_authors.append(candidate)

            if filtered_authors:
                return " ".join(filtered_authors)

    lines = text.strip().split("\n")
    for i in range(min(10, len(lines))):
        line = lines[i].strip()
        if (',' in line and ' and ' in line.lower() and
                not re.search(r'\b(abstract|introduction|http|www)\b', line.lower()) and
                len(line) < 150):
            return line

    return "Authors not found"


def clean_title(title):
    """Clean title by removing arXiv metadata and other unwanted elements"""
    if not title:
        return title
    
    # Remove arXiv patterns
    title = re.sub(r'arXiv:\d+\.\d+v\d+\s*\[.*?\]\s*\d+\s+\w+\s+\d{4}\s*', '', title)
    
    # Remove common metadata patterns
    title = re.sub(r'^\s*\d{4}\s*$\s*', '', title)  # Years at start
    title = re.sub(r'^\s*\[.*?\]\s*', '', title)  # Brackets at start
    title = re.sub(r'^\s*\d+\s*$\s*', '', title)  # Numbers at start
    
    # Clean up extra whitespace
    title = re.sub(r'\s+', ' ', title).strip()
    
    return title

def improved_extract_title(text, pdf_path=None):
    """Extract title using multiple strategies for scientific papers.
    If pdf_path is provided, use font information for better accuracy."""
    if pdf_path:
        try:
            text_with_font = extract_text_with_font_info(pdf_path)
            font_based_title = extract_title_from_font_info(text_with_font)
            if font_based_title and len(font_based_title) > 10:
                cleaned_title = clean_title(font_based_title)
                if cleaned_title and len(cleaned_title) > 10:
                    return cleaned_title
        except Exception as e:
            logger.error(f"Font-based extraction error: {e}")

    lines = text.strip().split("\n")
    content_lines = []

    for line in lines:
        line = line.strip()
        if line and not re.search(r'(page|doi|©|http|www|\d+\s*$)', line.lower()):
            content_lines.append(line)

    title_lines = []

    end_markers = [
        r'\babstract\b',
        r'\bintroduction\b',
        r'\b(university|institute|college|school)\b',
        r'\b(department)\b',
        r'@',
        r'\bemail\b',
        r'^\d\s',
        r'\[\d+\]',
        r'\d{4}',
        r'\b(submitted|received|accepted|published)\b'
    ]

    for i in range(min(5, len(content_lines))):
        line = content_lines[i]

        if len(line) < 3 and i > 0:
            continue

        if any(re.search(pattern, line.lower()) for pattern in end_markers):
            break

        if i > 0 and (len(line) < 30 and (',' in line or len(line.split()) <= 3)):
            is_likely_author = True
            for prev_line in title_lines:
                if len(prev_line) < 50 and not prev_line.endswith('.'):
                    is_likely_author = False
                    break
            if is_likely_author:
                break

        if len(line) < 200:
            title_lines.append(line)

    if title_lines:
        raw_title = " ".join(title_lines)
        cleaned_title = clean_title(raw_title)
        if cleaned_title and len(cleaned_title) > 10:
            return cleaned_title
        return raw_title

    try:
        kw_model, _ = get_models()
        first_text = " ".join(content_lines[:15])
        keywords = kw_model.extract_keywords(
            first_text,
            keyphrase_ngram_range=(3, 8),
            stop_words='english',
            top_n=1,
            use_maxsum=True
        )
        if keywords:
            cleaned_keyword = clean_title(keywords[0][0])
            if cleaned_keyword and len(cleaned_keyword) > 10:
                return cleaned_keyword
            return keywords[0][0]
    except Exception as e:
        logger.error(f"KeyBERT fallback error: {e}")

    for line in content_lines[:3]:
        if len(line) > 15 and len(line) < 200:
            cleaned_line = clean_title(line)
            if cleaned_line and len(cleaned_line) > 10:
                return cleaned_line
            return line

    return "Unknown Title"


def clean_text(text):
    text = text.replace("-\n", "")
    text = text.replace("\n", " ")
    return text


def extract_keywords_with_bert(text, top_n=None):
    if top_n is None:
        top_n = MODEL_CONFIG['keywords_top_n']
    
    kw_model, _ = get_models()
    keywords = kw_model.extract_keywords(
        text, 
        keyphrase_ngram_range=MODEL_CONFIG['keywords_ngram_range'], 
        stop_words='english', 
        top_n=top_n
    )
    return [kw for kw, score in keywords]


def summarize(text):
    _, summarizer = get_models()
    max_input_length = MODEL_CONFIG["max_input_length"]
    if len(text.split()) > max_input_length:
        text = " ".join(text.split()[:max_input_length])

    try:
        # Calculate appropriate max_length based on input length
        input_length = len(text.split())
        max_length = min(MODEL_CONFIG["summary_max_length"], max(input_length // 2, 10))
        min_length = min(MODEL_CONFIG["summary_min_length"], max(input_length // 4, 5))
        
        # Ensure min_length is less than max_length
        if min_length >= max_length:
            min_length = max(1, max_length - 1)
        
        summary = summarizer(
            text, 
            max_length=max_length, 
            min_length=min_length, 
            do_sample=False
        )
        return summary[0]['summary_text']
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return "Summary generation failed"
