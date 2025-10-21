"""
Data visualization and chart generation
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DocumentVisualizer:
    """Create visualizations for document analysis"""
    
    def __init__(self, results: List[Dict[str, Any]]):
        self.results = results
        self.df = pd.DataFrame(results) if results else pd.DataFrame()
    
    def create_word_count_chart(self) -> go.Figure:
        """Create a bar chart of word counts"""
        if self.df.empty:
            return go.Figure()
        
        word_counts = self.df['statistics'].apply(lambda x: x['word_count']).tolist()
        file_names = self.df['file_name'].tolist()
        
        fig = go.Figure(data=[
            go.Bar(x=file_names, y=word_counts, name='Word Count')
        ])
        
        fig.update_layout(
            title='Word Count by Document',
            xaxis_title='Document',
            yaxis_title='Word Count',
            xaxis_tickangle=-45
        )
        
        return fig
    
    def create_keyword_cloud_data(self) -> Dict[str, int]:
        """Prepare data for keyword cloud visualization"""
        if self.df.empty:
            return {}
        
        all_keywords = []
        for keywords in self.df['keywords']:
            all_keywords.extend(keywords)
        
        from collections import Counter
        keyword_counts = Counter(all_keywords)
        return dict(keyword_counts.most_common(50))
    
    def create_compression_ratio_chart(self) -> go.Figure:
        """Create a scatter plot of compression ratios"""
        if self.df.empty:
            return go.Figure()
        
        compression_ratios = self.df['statistics'].apply(lambda x: x['compression_ratio']).tolist()
        file_names = self.df['file_name'].tolist()
        
        fig = go.Figure(data=[
            go.Scatter(
                x=file_names,
                y=compression_ratios,
                mode='markers',
                marker=dict(size=10, color=compression_ratios, colorscale='Viridis'),
                text=file_names,
                hovertemplate='<b>%{text}</b><br>Compression Ratio: %{y:.3f}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title='Summary Compression Ratios',
            xaxis_title='Document',
            yaxis_title='Compression Ratio',
            xaxis_tickangle=-45
        )
        
        return fig
    
    def create_author_network_chart(self) -> go.Figure:
        """Create a network chart of author collaborations"""
        if self.df.empty:
            return go.Figure()
        
        # Extract all authors and their connections
        author_connections = []
        all_authors = set()
        
        for doc in self.results:
            authors = doc.get('authors', '')
            if authors and authors != "Authors not found":
                # Simple author extraction
                author_list = [author.strip() for author in authors.split(',') if author.strip()]
                all_authors.update(author_list)
                
                # Create connections between authors in the same document
                for i, author1 in enumerate(author_list):
                    for author2 in author_list[i+1:]:
                        author_connections.append((author1, author2))
        
        if not author_connections:
            return go.Figure()
        
        # Create network data
        nodes = list(all_authors)
        edges = author_connections
        
        # Create the network visualization
        fig = go.Figure()
        
        # Add edges
        for edge in edges:
            fig.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1],  # Placeholder coordinates
                mode='lines',
                line=dict(width=1, color='gray'),
                showlegend=False,
                hoverinfo='none'
            ))
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=[0] * len(nodes),  # Placeholder coordinates
            y=[0] * len(nodes),
            mode='markers+text',
            marker=dict(size=20, color='lightblue'),
            text=nodes,
            textposition="middle center",
            name='Authors'
        ))
        
        fig.update_layout(
            title='Author Collaboration Network',
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        return fig
    
    def create_statistics_dashboard(self) -> Dict[str, go.Figure]:
        """Create a comprehensive statistics dashboard"""
        dashboard = {}
        
        if self.df.empty:
            return dashboard
        
        # Word count distribution
        dashboard['word_count'] = self.create_word_count_chart()
        
        # Compression ratios
        dashboard['compression'] = self.create_compression_ratio_chart()
        
        # Author network
        dashboard['author_network'] = self.create_author_network_chart()
        
        # Document size distribution
        file_sizes = self.df['file_size'].tolist()
        file_names = self.df['file_name'].tolist()
        
        fig_size = go.Figure(data=[
            go.Bar(x=file_names, y=file_sizes, name='File Size (bytes)')
        ])
        fig_size.update_layout(
            title='Document File Sizes',
            xaxis_title='Document',
            yaxis_title='File Size (bytes)',
            xaxis_tickangle=-45
        )
        dashboard['file_sizes'] = fig_size
        
        return dashboard
    
    def create_timeline_chart(self) -> go.Figure:
        """Create a timeline chart of processing"""
        if self.df.empty:
            return go.Figure()
        
        # Extract processing times (simplified)
        processing_times = []
        for i, doc in enumerate(self.results):
            # Simulate processing time based on file size
            processing_time = doc['file_size'] / (1024 * 1024) * 0.1  # Rough estimate
            processing_times.append(processing_time)
        
        cumulative_time = np.cumsum(processing_times)
        file_names = self.df['file_name'].tolist()
        
        fig = go.Figure(data=[
            go.Scatter(
                x=list(range(len(file_names))),
                y=cumulative_time,
                mode='lines+markers',
                name='Cumulative Processing Time',
                line=dict(color='blue', width=2),
                marker=dict(size=8)
            )
        ])
        
        fig.update_layout(
            title='Cumulative Processing Time',
            xaxis_title='Document Index',
            yaxis_title='Cumulative Time (seconds)'
        )
        
        return fig

def display_analytics_dashboard(results: List[Dict[str, Any]]):
    """Display a comprehensive analytics dashboard in Streamlit"""
    if not results:
        st.warning("No data available for visualization")
        return
    
    visualizer = DocumentVisualizer(results)
    
    st.header("📊 Document Analytics Dashboard")
    
    # Basic statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Documents", len(results))
    
    with col2:
        avg_words = np.mean([doc['statistics']['word_count'] for doc in results])
        st.metric("Avg Word Count", f"{avg_words:.0f}")
    
    with col3:
        avg_compression = np.mean([doc['statistics']['compression_ratio'] for doc in results])
        st.metric("Avg Compression", f"{avg_compression:.3f}")
    
    with col4:
        total_size = sum(doc['file_size'] for doc in results) / (1024 * 1024)
        st.metric("Total Size (MB)", f"{total_size:.1f}")
    
    # Charts
    st.subheader("📈 Document Statistics")
    
    # Word count chart
    word_count_fig = visualizer.create_word_count_chart()
    st.plotly_chart(word_count_fig, use_container_width=True)
    
    # Compression ratio chart
    compression_fig = visualizer.create_compression_ratio_chart()
    st.plotly_chart(compression_fig, use_container_width=True)
    
    # File sizes
    dashboard = visualizer.create_statistics_dashboard()
    if 'file_sizes' in dashboard:
        st.plotly_chart(dashboard['file_sizes'], use_container_width=True)
    
    # Keyword analysis
    st.subheader("🔑 Keyword Analysis")
    keyword_data = visualizer.create_keyword_cloud_data()
    
    if keyword_data:
        # Create a simple keyword frequency chart
        keywords = list(keyword_data.keys())[:20]  # Top 20
        counts = list(keyword_data.values())[:20]
        
        fig_keywords = go.Figure(data=[
            go.Bar(x=keywords, y=counts, name='Keyword Frequency')
        ])
        fig_keywords.update_layout(
            title='Top 20 Keywords',
            xaxis_title='Keywords',
            yaxis_title='Frequency',
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_keywords, use_container_width=True)
    
    # Timeline
    st.subheader("⏱️ Processing Timeline")
    timeline_fig = visualizer.create_timeline_chart()
    st.plotly_chart(timeline_fig, use_container_width=True)
