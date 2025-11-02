"""
Batch processing functionality for multiple PDFs
"""
import os
import json
import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime

from summarizer import (
    extract_text_from_pdf, improved_extract_title, extract_authors,
    summarize, extract_keywords_with_bert, clean_text
)
from config import FILE_CONFIG

logger = logging.getLogger(__name__)

class BatchProcessor:
    """Handles batch processing of multiple PDF files"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.results = []
        self.errors = []
    
    def process_single_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Process a single PDF file"""
        try:
            logger.info(f"Processing: {pdf_path}")
            
            # Extract text
            text = extract_text_from_pdf(pdf_path)
            if not text.strip():
                raise ValueError("No text extracted from PDF")
            
            # Extract metadata
            title = improved_extract_title(text, pdf_path=pdf_path)
            authors = extract_authors(text, title=title, pdf_path=pdf_path)
            
            # Generate summary
            cleaned_text = clean_text(text)
            summary_text = cleaned_text[:FILE_CONFIG["text_chunk_size"]]
            summary = summarize(summary_text)
            
            # Extract keywords
            keywords = extract_keywords_with_bert(summary)
            
            # Calculate statistics
            stats = self._calculate_statistics(text, summary)
            
            result = {
                "file_path": pdf_path,
                "file_name": os.path.basename(pdf_path),
                "file_size": os.path.getsize(pdf_path),
                "title": title,
                "authors": authors,
                "summary": summary,
                "keywords": keywords,
                "statistics": stats,
                "processed_at": datetime.now().isoformat(),
                "status": "success"
            }
            
            logger.info(f"Successfully processed: {pdf_path}")
            return result
            
        except Exception as e:
            error_result = {
                "file_path": pdf_path,
                "file_name": os.path.basename(pdf_path),
                "error": str(e),
                "processed_at": datetime.now().isoformat(),
                "status": "error"
            }
            logger.error(f"Error processing {pdf_path}: {e}")
            return error_result
    
    def _calculate_statistics(self, text: str, summary: str) -> Dict[str, Any]:
        """Calculate document statistics"""
        words = text.split()
        sentences = text.split('.')
        
        return {
            "character_count": len(text),
            "word_count": len(words),
            "sentence_count": len(sentences),
            "average_word_length": sum(len(word) for word in words) / len(words) if words else 0,
            "average_sentence_length": len(words) / len(sentences) if sentences else 0,
            "summary_length": len(summary),
            "compression_ratio": len(summary) / len(text) if text else 0
        }
    
    def process_batch(self, pdf_paths: List[str], progress_callback=None) -> Dict[str, Any]:
        """Process multiple PDF files in parallel"""
        start_time = time.time()
        self.results = []
        self.errors = []
        
        logger.info(f"Starting batch processing of {len(pdf_paths)} files")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_path = {
                executor.submit(self.process_single_pdf, pdf_path): pdf_path 
                for pdf_path in pdf_paths
            }
            
            # Process completed tasks
            for i, future in enumerate(as_completed(future_to_path), 1):
                pdf_path = future_to_path[future]
                try:
                    result = future.result()
                    if result["status"] == "success":
                        self.results.append(result)
                    else:
                        self.errors.append(result)
                    
                    if progress_callback:
                        progress_callback(i, len(pdf_paths), result)
                        
                except Exception as e:
                    error_result = {
                        "file_path": pdf_path,
                        "file_name": os.path.basename(pdf_path),
                        "error": str(e),
                        "processed_at": datetime.now().isoformat(),
                        "status": "error"
                    }
                    self.errors.append(error_result)
                    logger.error(f"Unexpected error processing {pdf_path}: {e}")
        
        processing_time = time.time() - start_time
        
        batch_summary = {
            "total_files": len(pdf_paths),
            "successful": len(self.results),
            "failed": len(self.errors),
            "processing_time": processing_time,
            "average_time_per_file": processing_time / len(pdf_paths) if pdf_paths else 0,
            "results": self.results,
            "errors": self.errors,
            "processed_at": datetime.now().isoformat()
        }
        
        logger.info(f"Batch processing completed: {len(self.results)} successful, {len(self.errors)} failed")
        return batch_summary
    
    def export_results(self, output_dir: str, format: str = "json") -> str:
        """Export batch processing results"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == "json":
            output_path = os.path.join(output_dir, f"batch_results_{timestamp}.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "summary": {
                        "total_files": len(self.results) + len(self.errors),
                        "successful": len(self.results),
                        "failed": len(self.errors)
                    },
                    "results": self.results,
                    "errors": self.errors
                }, f, indent=2, ensure_ascii=False)
        
        elif format.lower() == "csv":
            if self.results:
                df = pd.DataFrame(self.results)
                output_path = os.path.join(output_dir, f"batch_results_{timestamp}.csv")
                df.to_csv(output_path, index=False)
            else:
                output_path = None
        
        elif format.lower() == "excel":
            if self.results:
                df = pd.DataFrame(self.results)
                output_path = os.path.join(output_dir, f"batch_results_{timestamp}.xlsx")
                df.to_excel(output_path, index=False)
            else:
                output_path = None
        
        return output_path

def find_pdf_files(directory: str) -> List[str]:
    """Find all PDF files in a directory"""
    pdf_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

