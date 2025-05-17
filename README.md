# 🧠 PDF Summarizer

A Python-based Natural Language Processing (NLP) tool that extracts and summarizes text from PDF documents using powerful NLP models like BART and KeyBERT. Ideal for students, researchers, and professionals who want quick insights and keywords from PDF documents.

---

## 🚀 Features
- 📥 Extracts clean text from PDFs using PyMuPDF (fitz)
- 🧠 Generates concise summaries using BART-large-CNN model
- 🔑 Extracts relevant keywords using KeyBERT
- 🧹 Cleans and processes text from PDFs
- 📊 Exports results in structured JSON format

---

## 📦 Built With
- Python 3.x
- [`PyMuPDF (fitz)`](https://pymupdf.readthedocs.io/en/latest/) – PDF text extraction
- [`transformers`](https://huggingface.co/docs/transformers/index) – Summarization via BART-large-CNN model
- [`KeyBERT`](https://maartengr.github.io/KeyBERT/) – Keyword extraction using BERT embeddings
- [`all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) – Sentence transformer model for KeyBERT

---

## 🛠 Setup

### 1. Clone the repository
```bash
git clone https://github.com/faikbairamov/pdf-summarizer.git
cd pdf-summarizer
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate # For macOS/Linux
# or
venv\Scripts\activate # For Windows
```

### 3. Install dependencies
```bash
pip install pymupdf transformers keybert torch
```

💡 You may also need to install additional dependencies based on your environment.

## 🧪 Usage

### Running the Script
```bash
python summarizer.py
```

By default, the script processes "sample2.pdf" in the same directory and outputs results to "output.json".

### As a Module
```python
from summarizer import extract_text_from_pdf, clean_text, extract_keywords_with_bert, summarize

# Extract text from PDF
text = extract_text_from_pdf("my_document.pdf")

# Clean the extracted text
cleaned_text = clean_text(text)

# Generate summary
summary = summarize(cleaned_text[:1000])  # Summarize first 1000 chars

# Extract keywords
keywords = extract_keywords_with_bert(summary)

print(summary)
print(keywords)
```

## 📁 Project Structure
```
pdf-summarizer/
├── summarizer.py  # Main script with PDF processing and NLP functions
├── sample2.pdf    # Example PDF file to process
├── output.json    # Generated output with summary and keywords
├── README.md
└── requirements.txt  # Optional
```

## 🧠 Example Output

Input PDF: A research paper (sample2.pdf)

Output JSON:
```json
{
  "title": "Towards a Deeper Understanding of Reasoning Capabilities in Large Language Models",
  "abstract": "Generated summary of the paper's abstract...",
  "keywords": [
    "reasoning capabilities",
    "language models",
    "understanding",
    "deeper understanding",
    "...more keywords..."
  ]
}
```
