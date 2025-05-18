import fitz
import json
from keybert import KeyBERT
from transformers import pipeline

# Initialize models
kw_model = KeyBERT(model='all-MiniLM-L6-v2')
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def extract_text_from_pdf(pdf_path, max_pages=2):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc[:max_pages]:
        text += page.get_text()
    return text

def clean_text(text):
    text = text.replace("-\n", "")  # Fix hyphenation splits
    text = text.replace("\n", " ")  # Flatten line breaks
    return text

def extract_keywords_with_bert(text, top_n=15):
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 3), stop_words='english', top_n=top_n)
    return [kw for kw, score in keywords]

def summarize(text):
    summary = summarizer(text, max_length=100, min_length=30, do_sample=False)
    return summary[0]['summary_text']

def main():
    print("Loading PDF...")
    pdf_path = "sample2.pdf"
    text = extract_text_from_pdf(pdf_path)
    print("Extracted text from PDF")

    cleaned_text = clean_text(text)
    print("Cleaned text")

    abstract_raw = cleaned_text[:1000].strip()
    print("Generating summary...")
    abstract = summarize(abstract_raw)
    print("Summary generated")

    print("Extracting keywords...")
    keywords = extract_keywords_with_bert(abstract, top_n=30)
    print("Keywords extracted")

    result = {
        "title": "Towards a Deeper Understanding of Reasoning Capabilities in Large Language Models",
        "abstract": abstract,
        "keywords": keywords
    }

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("Done! Check output.json")

if __name__ == "__main__":
    main()
