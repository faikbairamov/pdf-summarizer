"""
REST API endpoints for PDF processing
"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import json
from typing import Dict, Any
import logging
from werkzeug.utils import secure_filename

from summarizer import (
    extract_text_from_pdf, improved_extract_title, extract_authors,
    summarize, extract_keywords_with_bert, clean_text
)
from batch_processor import BatchProcessor
from analytics import DocumentAnalytics
from export_manager import ExportManager

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "PDF NLP API",
        "version": "1.0.0"
    })

@app.route('/process', methods=['POST'])
def process_single_pdf():
    """Process a single PDF file"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Only PDF files are allowed"}), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            file.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        try:
            # Process the PDF
            text = extract_text_from_pdf(tmp_path)
            if not text.strip():
                return jsonify({"error": "No text could be extracted from the PDF"}), 400
            
            title = improved_extract_title(text, pdf_path=tmp_path)
            authors = extract_authors(text, title=title, pdf_path=tmp_path)
            
            # Generate summary
            cleaned_text = clean_text(text)
            summary = summarize(cleaned_text[:3000])
            
            # Extract keywords
            keywords = extract_keywords_with_bert(summary)
            
            # Calculate statistics
            stats = {
                "character_count": len(text),
                "word_count": len(text.split()),
                "sentence_count": len(text.split('.')),
                "compression_ratio": len(summary) / len(text) if text else 0
            }
            
            result = {
                "file_name": filename,
                "title": title,
                "authors": authors,
                "summary": summary,
                "keywords": keywords,
                "statistics": stats,
                "status": "success"
            }
            
            return jsonify(result)
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/batch', methods=['POST'])
def process_batch():
    """Process multiple PDF files"""
    try:
        if 'files' not in request.files:
            return jsonify({"error": "No files provided"}), 400
        
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            return jsonify({"error": "No files selected"}), 400
        
        # Validate all files
        for file in files:
            if not allowed_file(file.filename):
                return jsonify({"error": f"Invalid file type: {file.filename}. Only PDF files are allowed"}), 400
        
        # Save files temporarily
        temp_paths = []
        try:
            for file in files:
                filename = secure_filename(file.filename)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    file.save(tmp_file.name)
                    temp_paths.append(tmp_file.name)
            
            # Process batch
            processor = BatchProcessor()
            batch_results = processor.process_batch(temp_paths)
            
            return jsonify(batch_results)
            
        finally:
            # Clean up temporary files
            for tmp_path in temp_paths:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    except Exception as e:
        logger.error(f"Error processing batch: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_results():
    """Analyze processing results"""
    try:
        data = request.get_json()
        if not data or 'results' not in data:
            return jsonify({"error": "No results data provided"}), 400
        
        results = data['results']
        analytics = DocumentAnalytics(results)
        report = analytics.generate_report()
        
        return jsonify(report)
    
    except Exception as e:
        logger.error(f"Error analyzing results: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/export', methods=['POST'])
def export_results():
    """Export results to various formats"""
    try:
        data = request.get_json()
        if not data or 'results' not in data:
            return jsonify({"error": "No results data provided"}), 400
        
        results = data['results']
        format_type = data.get('format', 'json')
        
        export_manager = ExportManager()
        
        if format_type == 'json':
            filepath = export_manager.export_to_json(results)
        elif format_type == 'csv':
            filepath = export_manager.export_to_csv(results)
        elif format_type == 'excel':
            filepath = export_manager.export_to_excel(results)
        elif format_type == 'word':
            filepath = export_manager.export_to_word(results)
        elif format_type == 'pdf':
            filepath = export_manager.export_to_pdf(results)
        else:
            return jsonify({"error": "Unsupported format"}), 400
        
        return send_file(filepath, as_attachment=True)
    
    except Exception as e:
        logger.error(f"Error exporting results: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/compare', methods=['POST'])
def compare_documents():
    """Compare documents for similarity"""
    try:
        data = request.get_json()
        if not data or 'results' not in data:
            return jsonify({"error": "No results data provided"}), 400
        
        results = data['results']
        threshold = data.get('threshold', 0.3)
        
        from analytics import DocumentComparator
        comparator = DocumentComparator(results)
        similar_docs = comparator.find_similar_documents(threshold)
        
        return jsonify({
            "similar_documents": similar_docs,
            "threshold": threshold,
            "total_comparisons": len(similar_docs)
        })
    
    except Exception as e:
        logger.error(f"Error comparing documents: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/cluster', methods=['POST'])
def cluster_documents():
    """Cluster documents based on content similarity"""
    try:
        data = request.get_json()
        if not data or 'results' not in data:
            return jsonify({"error": "No results data provided"}), 400
        
        results = data['results']
        n_clusters = data.get('n_clusters', 3)
        
        from analytics import DocumentComparator
        comparator = DocumentComparator(results)
        clusters = comparator.cluster_documents(n_clusters)
        
        return jsonify({
            "clusters": clusters,
            "n_clusters": n_clusters,
            "total_documents": len(results)
        })
    
    except Exception as e:
        logger.error(f"Error clustering documents: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large. Maximum size is 50MB"}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True, host='0.0.0.0', port=5000)
