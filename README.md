# Advanced PDF NLP Suite

A comprehensive PDF processing and analysis platform that extracts, analyzes, and visualizes scientific papers using advanced NLP techniques.

## 🚀 Features

### Core Processing

- **PDF Text Extraction**: Extract text from PDF files with font information
- **Title Detection**: Advanced title extraction using font size analysis and pattern recognition
- **Author Extraction**: Multi-strategy author identification from scientific papers
- **Text Summarization**: AI-powered summarization using BART model
- **Keyword Extraction**: KeyBERT-based keyword extraction

### Advanced Features

- **Batch Processing**: Process multiple PDFs simultaneously with parallel processing
- **Analytics Dashboard**: Comprehensive analytics and statistics with interactive visualizations
- **Document Comparison**: Find similar documents and analyze content relationships
- **Document Clustering**: Group documents by content similarity
- **Multiple Export Formats**: JSON, CSV, Excel, Word, and PDF export options
- **REST API**: Full REST API for programmatic access
- **Interactive Visualizations**: Charts, graphs, and keyword clouds
- **Performance Optimization**: Model caching and efficient processing

## Recent Improvements

### Code Quality

- ✅ Removed all inline comments for cleaner code
- ✅ Added comprehensive error handling and logging
- ✅ Implemented proper input validation
- ✅ Refactored code into smaller, maintainable functions

### Performance Optimizations

- ✅ Model caching with `@lru_cache` to avoid reloading
- ✅ Configurable parameters through `config.py`
- ✅ Optimized text processing and chunking
- ✅ Memory-efficient PDF processing

### UI/UX Enhancements

- ✅ Improved layout with two-column design
- ✅ File validation with size limits
- ✅ Progress indicators with spinners
- ✅ Debug information in collapsible sections
- ✅ Document statistics display
- ✅ Better error messages and user feedback

### Technical Improvements

- ✅ Type hints throughout the codebase
- ✅ Configuration management
- ✅ Proper resource cleanup (file handling)
- ✅ Updated dependencies with version pinning

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd pdf-nlp-project
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Download spaCy model (if needed):

```bash
python -m spacy download en_core_web_sm
```

## Usage

### Running the Application

**Main Streamlit Application:**

```bash
streamlit run app.py
```

**REST API Server:**

```bash
python api.py
```

The applications will open in your browser at:

- Streamlit: `http://localhost:8501`
- API: `http://localhost:5000`

### Using the Enhanced Features

**Batch Processing:**

```python
from batch_processor import BatchProcessor, find_pdf_files

# Process multiple PDFs
processor = BatchProcessor()
pdf_files = find_pdf_files("path/to/pdf/directory")
results = processor.process_batch(pdf_files)
```

**Analytics:**

```python
from analytics import DocumentAnalytics

# Analyze results
analytics = DocumentAnalytics(results)
report = analytics.generate_report()
```

**Export to Multiple Formats:**

```python
from export_manager import ExportManager

# Export results
export_manager = ExportManager()
export_manager.export_all_formats(results)
```

### Using the API

**Process Single PDF:**

```bash
curl -X POST -F "file=@document.pdf" http://localhost:5000/process
```

**Batch Processing:**

```bash
curl -X POST -F "files=@doc1.pdf" -F "files=@doc2.pdf" http://localhost:5000/batch
```

**Export Results:**

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"results": [...], "format": "json"}' \
  http://localhost:5000/export
```

## Configuration

The application uses a centralized configuration system in `config.py`:

- **Model Settings**: AI model configurations
- **File Processing**: File size limits and processing parameters
- **UI Settings**: Interface configuration
- **Logging**: Logging level and format settings

## 📁 Project Structure

```
pdf-nlp-project/
├── app.py                    # Main Streamlit application with all features
├── api.py                    # REST API endpoints
├── summarizer.py             # Core NLP processing functions
├── batch_processor.py        # Batch processing functionality
├── analytics.py              # Analytics and statistics
├── visualization.py          # Data visualization and charts
├── export_manager.py         # Export functionality for multiple formats
├── config.py                # Configuration settings
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── test_pdfs/               # Test PDF files
│   ├── sample.pdf
│   ├── sample1.pdf
│   └── sample2.pdf
├── exports/                 # Export output directory
└── venv/                    # Virtual environment
```

## Dependencies

- **Streamlit**: Web application framework
- **PyMuPDF**: PDF text extraction
- **Transformers**: BART summarization model
- **KeyBERT**: Keyword extraction
- **spaCy**: Natural language processing
- **NumPy**: Numerical computations

## Performance Notes

- Models are cached after first load for faster subsequent processing
- PDF processing is limited to first 2 pages by default (configurable)
- Text summarization is limited to 1024 tokens for optimal performance
- File size is limited to 50MB by default

## Error Handling

The application includes comprehensive error handling:

- PDF extraction errors
- Model loading failures
- Invalid file formats
- Memory limitations
- Network issues (for model downloads)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.
