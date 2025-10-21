import os
from typing import Dict, Any

# Model configurations
MODEL_CONFIG: Dict[str, Any] = {
    "keybert_model": "all-MiniLM-L6-v2",
    "summarizer_model": "facebook/bart-large-cnn",
    "max_input_length": 1024,
    "summary_max_length": 100,
    "summary_min_length": 30,
    "keywords_top_n": 15,
    "keywords_ngram_range": (1, 3)
}

# File processing configurations
FILE_CONFIG: Dict[str, Any] = {
    "max_file_size_mb": 50,
    "max_pages_extract": 2,
    "text_chunk_size": 3000
}

# UI configurations
UI_CONFIG: Dict[str, Any] = {
    "page_title": "Advanced PDF NLP Suite",
    "layout": "wide",
    "sidebar_state": "expanded"
}

# Batch processing configurations
BATCH_CONFIG: Dict[str, Any] = {
    "max_workers": 4,
    "chunk_size": 1000,
    "progress_update_interval": 1
}

# Analytics configurations
ANALYTICS_CONFIG: Dict[str, Any] = {
    "similarity_threshold": 0.3,
    "max_clusters": 10,
    "keyword_cloud_max_words": 50
}

# Export configurations
EXPORT_CONFIG: Dict[str, Any] = {
    "output_directory": "exports",
    "supported_formats": ["json", "csv", "excel", "word", "pdf"],
    "default_format": "json"
}

# API configurations
API_CONFIG: Dict[str, Any] = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": True,
    "max_content_length": 50 * 1024 * 1024  # 50MB
}

# Logging configuration
LOGGING_CONFIG: Dict[str, Any] = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}
