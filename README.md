# PDF summarizer for scientific papers

A tool for automatically extracting and summarizing information from scientific papers in PDF format.

## features

- **Title Extraction**: Automatically identifies the title of the paper using font information and positional analysis
- **Author Detection**: Extracts author names from the document
- **Keyword Extraction**: Uses KeyBERT to identify the most important keywords and phrases
- **Automatic Summarization**: Generates concise summaries using BART large CNN model
- **JSON Export**: Download results in structured JSON format

## live demo

The project is deployed using Streamlit Cloud and available at:
[https://faikbairamov-pdf-summarizer-app-hqdh2v.streamlit.app/](https://faikbairamov-pdf-summarizer-app-hqdh2v.streamlit.app/)

You can test the app with the `sample_file.pdf` from the repository.

> **Note**: The application is currently in beta. Some bugs and issues have been identified and will be fixed in upcoming updates.

## requirements

- Python 3.8+
- PyMuPDF (fitz)
- KeyBERT
- Transformers
- Streamlit
- BART model for summarization

## installation

1. Clone this repository
```bash
  git clone https://github.com/yourusername/pdf-summarizer.git
  cd pdf-summarizer
```

2. Install the required packages
```bash
  pip install -r requirements.txt
```

3. Run the application locally
```bash
  streamlit run app.py
```

## project structure

- `app.py`: Main Streamlit application
- `summarizer.py`: Core functions for text extraction and summarization
- `requirements.txt`: Project dependencies

## how it works

1. **PDF Text Extraction**: Uses PyMuPDF to extract raw text with font information
2. **Title Identification**: Analyzes font sizes and positions to identify the title
3. **Author Detection**: Uses patterns and positioning to identify author information
4. **Text Cleaning**: Removes unnecessary line breaks and normalizes text
5. **Summarization**: Leverages BART model to generate concise summaries
6. **Keyword Extraction**: Uses KeyBERT to identify key topics in the document

## known issues

- Title extraction may not work correctly on PDFs with unusual formatting
- Author extraction has limited accuracy on complex author lists
- Longer documents may be truncated due to model token limitations
- Some PDFs with complex layouts may not extract text properly

These issues are being actively addressed and will be fixed in upcoming releases.

## contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## acknowledgements

- [KeyBERT](https://github.com/MaartenGr/KeyBERT) for keyword extraction
- [Hugging Face Transformers](https://huggingface.co/facebook/bart-large-cnn) for the BART summarization model
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) for PDF processing
- [Streamlit](https://streamlit.io/) for the web application framework
