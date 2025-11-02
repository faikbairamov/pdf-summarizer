"""
Enhanced Streamlit application with advanced features
"""
import streamlit as st
import os
import tempfile
import json
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Import our modules
from summarizer import (
    extract_text_from_pdf, improved_extract_title, extract_authors,
    summarize, extract_keywords_with_bert, clean_text
)
from batch_processor import BatchProcessor, find_pdf_files
from analytics import DocumentAnalytics, DocumentComparator
from export_manager import ExportManager
from visualization import display_analytics_dashboard
from config import FILE_CONFIG, UI_CONFIG

# Page configuration
st.set_page_config(
    page_title="Advanced PDF NLP Suite",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function"""
    st.title("🚀 Advanced PDF NLP Suite")
    st.markdown("Comprehensive PDF analysis with batch processing, analytics, and visualization")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Single PDF Analysis", "Batch Processing", "Analytics Dashboard", "Document Comparison", "Export Tools", "API Documentation"]
    )
    
    if page == "Single PDF Analysis":
        single_pdf_analysis()
    elif page == "Batch Processing":
        batch_processing()
    elif page == "Analytics Dashboard":
        analytics_dashboard()
    elif page == "Document Comparison":
        document_comparison()
    elif page == "Export Tools":
        export_tools()
    elif page == "API Documentation":
        api_documentation()

def single_pdf_analysis():
    """Single PDF analysis page"""
    st.header("📄 Single PDF Analysis")
    
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf", help="Upload a scientific paper PDF file")
    
    if uploaded_file:
        if not validate_pdf_file(uploaded_file):
            st.stop()
        
        result = process_pdf(uploaded_file)
        
        if not result:
            st.stop()
        
        # Display results in tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Results", "📈 Statistics", "🔍 Debug Info", "💾 Export"])
        
        with tab1:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📌 Title")
                st.markdown(f"**{result['title']}**")
                
                st.subheader("👥 Authors")
                st.write(result['authors'])
                
                st.subheader("📝 Summary")
                st.write(result['summary'])
                
                st.subheader("🔑 Keywords")
                st.write(", ".join(result['keywords']))
            
            with col2:
                st.subheader("📊 Document Stats")
                st.metric("Text Length", f"{len(result['raw_text']):,} characters")
                st.metric("Word Count", f"{len(result['raw_text'].split()):,} words")
                st.metric("File Size", f"{result.get('file_size', 0) / (1024*1024):.2f} MB")
        
        with tab2:
            display_single_document_stats(result)
        
        with tab3:
            display_debug_info(uploaded_file, result)
        
        with tab4:
            export_single_document(result)

def batch_processing():
    """Batch processing page"""
    st.header("📚 Batch Processing")
    
    # Upload multiple files
    uploaded_files = st.file_uploader(
        "Upload multiple PDF files", 
        type="pdf", 
        accept_multiple_files=True,
        help="Upload multiple PDF files for batch processing"
    )
    
    # Or select from directory
    st.subheader("Or process files from directory")
    directory_path = st.text_input("Enter directory path containing PDF files")
    
    if st.button("Find PDFs in Directory") and directory_path:
        if os.path.exists(directory_path):
            pdf_files = find_pdf_files(directory_path)
            st.success(f"Found {len(pdf_files)} PDF files")
            
            if pdf_files:
                st.write("Files found:")
                for file in pdf_files[:10]:  # Show first 10
                    st.write(f"- {file}")
                if len(pdf_files) > 10:
                    st.write(f"... and {len(pdf_files) - 10} more files")
        else:
            st.error("Directory not found")
    
    # Process files
    if uploaded_files or (directory_path and os.path.exists(directory_path)):
        if st.button("Start Batch Processing"):
            with st.spinner("Processing files..."):
                processor = BatchProcessor()
                
                if uploaded_files:
                    # Process uploaded files
                    temp_paths = []
                    for file in uploaded_files:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                            tmp_file.write(file.read())
                            temp_paths.append(tmp_file.name)
                    
                    results = processor.process_batch(temp_paths)
                    
                    # Clean up temp files
                    for path in temp_paths:
                        if os.path.exists(path):
                            os.unlink(path)
                
                elif directory_path:
                    pdf_files = find_pdf_files(directory_path)
                    results = processor.process_batch(pdf_files)
                
                # Store results in session state
                st.session_state.batch_results = results
                st.success(f"Processed {results['successful']} files successfully, {results['failed']} failed")
                
                # Display results
                display_batch_results(results)

def analytics_dashboard():
    """Analytics dashboard page"""
    st.header("📊 Analytics Dashboard")
    
    if 'batch_results' not in st.session_state:
        st.warning("No batch processing results available. Please run batch processing first.")
        return
    
    results = st.session_state.batch_results['results']
    
    if not results:
        st.warning("No successful results to analyze")
        return
    
    # Display analytics dashboard
    display_analytics_dashboard(results)

def document_comparison():
    """Document comparison page"""
    st.header("🔍 Document Comparison")
    
    if 'batch_results' not in st.session_state:
        st.warning("No batch processing results available. Please run batch processing first.")
        return
    
    results = st.session_state.batch_results['results']
    
    if len(results) < 2:
        st.warning("Need at least 2 documents for comparison")
        return
    
    st.subheader("Similarity Analysis")
    threshold = st.slider("Similarity Threshold", 0.0, 1.0, 0.3, 0.1)
    
    if st.button("Find Similar Documents"):
        comparator = DocumentComparator(results)
        similar_docs = comparator.find_similar_documents(threshold)
        
        if similar_docs:
            st.subheader("Similar Document Pairs")
            for pair in similar_docs:
                with st.expander(f"{pair['doc1']} ↔ {pair['doc2']} (Similarity: {pair['similarity']:.3f})"):
                    st.write(f"**Similarity Score:** {pair['similarity']:.3f}")
                    st.write(f"**Common Keywords:** {', '.join(pair['common_keywords'])}")
        else:
            st.info("No similar documents found with the current threshold")
    
    st.subheader("Document Clustering")
    n_clusters = st.slider("Number of Clusters", 2, min(10, len(results)), 3)
    
    if st.button("Cluster Documents"):
        comparator = DocumentComparator(results)
        clusters = comparator.cluster_documents(n_clusters)
        
        st.subheader("Document Clusters")
        for cluster_name, documents in clusters.items():
            with st.expander(f"{cluster_name} ({len(documents)} documents)"):
                for doc in documents:
                    st.write(f"- {doc}")

def export_tools():
    """Export tools page"""
    st.header("💾 Export Tools")
    
    if 'batch_results' not in st.session_state:
        st.warning("No batch processing results available. Please run batch processing first.")
        return
    
    results = st.session_state.batch_results['results']
    
    if not results:
        st.warning("No results to export")
        return
    
    st.subheader("Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Single Format Export**")
        format_type = st.selectbox("Select format", ["json", "csv", "excel", "word", "pdf"])
        
        if st.button(f"Export as {format_type.upper()}"):
            export_manager = ExportManager()
            try:
                if format_type == "json":
                    filepath = export_manager.export_to_json(results)
                elif format_type == "csv":
                    filepath = export_manager.export_to_csv(results)
                elif format_type == "excel":
                    filepath = export_manager.export_to_excel(results)
                elif format_type == "word":
                    filepath = export_manager.export_to_word(results)
                elif format_type == "pdf":
                    filepath = export_manager.export_to_pdf(results)
                
                st.success(f"Exported successfully: {filepath}")
                
                # Provide download link
                with open(filepath, 'rb') as f:
                    st.download_button(
                        label=f"Download {format_type.upper()} file",
                        data=f.read(),
                        file_name=os.path.basename(filepath),
                        mime="application/octet-stream"
                    )
            except Exception as e:
                st.error(f"Export failed: {e}")
    
    with col2:
        st.write("**Export All Formats**")
        if st.button("Export All Formats"):
            export_manager = ExportManager()
            try:
                exported_files = export_manager.export_all_formats(results)
                st.success(f"Exported to {len(exported_files)} formats")
                
                for format_name, filepath in exported_files.items():
                    with open(filepath, 'rb') as f:
                        st.download_button(
                            label=f"Download {format_name.upper()}",
                            data=f.read(),
                            file_name=os.path.basename(filepath),
                            mime="application/octet-stream"
                        )
            except Exception as e:
                st.error(f"Export failed: {e}")

def api_documentation():
    """API documentation page"""
    st.header("🔌 API Documentation")
    
    st.subheader("REST API Endpoints")
    
    endpoints = [
        {
            "endpoint": "/health",
            "method": "GET",
            "description": "Health check endpoint"
        },
        {
            "endpoint": "/process",
            "method": "POST",
            "description": "Process a single PDF file"
        },
        {
            "endpoint": "/batch",
            "method": "POST",
            "description": "Process multiple PDF files"
        },
        {
            "endpoint": "/analyze",
            "method": "POST",
            "description": "Analyze processing results"
        },
        {
            "endpoint": "/export",
            "method": "POST",
            "description": "Export results to various formats"
        },
        {
            "endpoint": "/compare",
            "method": "POST",
            "description": "Compare documents for similarity"
        },
        {
            "endpoint": "/cluster",
            "method": "POST",
            "description": "Cluster documents based on content"
        }
    ]
    
    for endpoint in endpoints:
        with st.expander(f"{endpoint['method']} {endpoint['endpoint']}"):
            st.write(f"**Description:** {endpoint['description']}")
            st.code(f"curl -X {endpoint['method']} http://localhost:5000{endpoint['endpoint']}")
    
    st.subheader("Start API Server")
    if st.button("Start API Server"):
        st.info("To start the API server, run: python api.py")
        st.code("python api.py", language="bash")

# Helper functions
def validate_pdf_file(uploaded_file) -> bool:
    """Validate uploaded PDF file"""
    if uploaded_file is None:
        return False
    if uploaded_file.size == 0:
        st.error("The uploaded file is empty.")
        return False
    max_size = FILE_CONFIG["max_file_size_mb"] * 1024 * 1024
    if uploaded_file.size > max_size:
        st.error(f"File size too large. Please upload a file smaller than {FILE_CONFIG['max_file_size_mb']}MB.")
        return False
    return True

def process_pdf(uploaded_file) -> Dict[str, Any]:
    """Process a single PDF file"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name
    
    try:
        with st.spinner("Extracting text from PDF..."):
            raw_text = extract_text_from_pdf(tmp_path)
            if not raw_text.strip():
                st.error("No text could be extracted from the PDF.")
                return {}
        
        with st.spinner("Extracting title..."):
            title = improved_extract_title(raw_text, pdf_path=tmp_path)
        
        with st.spinner("Extracting authors..."):
            authors = extract_authors(raw_text, title=title, pdf_path=tmp_path)
        
        with st.spinner("Generating summary..."):
            cleaned_text = clean_text(raw_text)
            summary_text = cleaned_text[:FILE_CONFIG["text_chunk_size"]]
            summary = summarize(summary_text)
        
        with st.spinner("Extracting keywords..."):
            keywords = extract_keywords_with_bert(summary)
        
        return {
            "title": title,
            "authors": authors,
            "summary": summary,
            "keywords": keywords,
            "raw_text": raw_text,
            "file_size": uploaded_file.size
        }
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return {}
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def display_single_document_stats(result: Dict[str, Any]):
    """Display statistics for a single document"""
    stats = {
        "Character Count": len(result['raw_text']),
        "Word Count": len(result['raw_text'].split()),
        "Sentence Count": len(result['raw_text'].split('.')),
        "Keyword Count": len(result['keywords']),
        "Summary Length": len(result['summary']),
        "Compression Ratio": len(result['summary']) / len(result['raw_text']) if result['raw_text'] else 0
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        for metric, value in list(stats.items())[:3]:
            st.metric(metric, f"{value:,}")
    
    with col2:
        for metric, value in list(stats.items())[3:]:
            if metric == "Compression Ratio":
                st.metric(metric, f"{value:.3f}")
            else:
                st.metric(metric, f"{value:,}")

def display_debug_info(uploaded_file, result: Dict[str, Any]):
    """Display debug information"""
    st.subheader("Debug Information")
    
    with st.expander("File Information"):
        st.write(f"**File Name:** {uploaded_file.name}")
        st.write(f"**File Size:** {uploaded_file.size / (1024*1024):.2f} MB")
        st.write(f"**File Type:** {uploaded_file.type}")
    
    with st.expander("Processing Statistics"):
        st.json({
            "text_length": len(result['raw_text']),
            "title_length": len(result['title']),
            "summary_length": len(result['summary']),
            "keyword_count": len(result['keywords'])
        })

def export_single_document(result: Dict[str, Any]):
    """Export single document results"""
    st.subheader("Export Options")
    
    export_manager = ExportManager()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export as JSON"):
            filepath = export_manager.export_to_json([result])
            st.success(f"Exported to: {filepath}")
    
    with col2:
        if st.button("Export as CSV"):
            filepath = export_manager.export_to_csv([result])
            st.success(f"Exported to: {filepath}")

def display_batch_results(results: Dict[str, Any]):
    """Display batch processing results"""
    st.subheader("Batch Processing Results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Files", results['total_files'])
    
    with col2:
        st.metric("Successful", results['successful'])
    
    with col3:
        st.metric("Failed", results['failed'])
    
    with col4:
        st.metric("Processing Time", f"{results['processing_time']:.2f}s")
    
    # Display results table
    if results['results']:
        st.subheader("Successful Results")
        df = pd.DataFrame(results['results'])
        st.dataframe(df[['file_name', 'title', 'authors', 'statistics']], use_container_width=True)
    
    if results['errors']:
        st.subheader("Errors")
        for error in results['errors']:
            st.error(f"{error['file_name']}: {error['error']}")

def display_analytics_dashboard(results: List[Dict[str, Any]]):
    """Display analytics dashboard"""
    from visualization import display_analytics_dashboard
    display_analytics_dashboard(results)

if __name__ == "__main__":
    main()

