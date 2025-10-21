"""
Advanced analytics and statistics for PDF processing
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
import re
from collections import Counter
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DocumentAnalytics:
    """Advanced analytics for document processing"""
    
    def __init__(self, results: List[Dict[str, Any]]):
        self.results = results
        self.df = pd.DataFrame(results) if results else pd.DataFrame()
    
    def get_basic_statistics(self) -> Dict[str, Any]:
        """Get basic statistics about the processed documents"""
        if self.df.empty:
            return {}
        
        stats = {
            "total_documents": len(self.df),
            "average_character_count": self.df['statistics'].apply(lambda x: x['character_count']).mean(),
            "average_word_count": self.df['statistics'].apply(lambda x: x['word_count']).mean(),
            "average_sentence_count": self.df['statistics'].apply(lambda x: x['sentence_count']).mean(),
            "average_compression_ratio": self.df['statistics'].apply(lambda x: x['compression_ratio']).mean(),
            "total_processing_time": self.df['file_size'].sum() / (1024 * 1024),  # MB
        }
        
        return stats
    
    def analyze_keywords(self) -> Dict[str, Any]:
        """Analyze keywords across all documents"""
        if self.df.empty:
            return {}
        
        all_keywords = []
        for keywords in self.df['keywords']:
            all_keywords.extend(keywords)
        
        keyword_counts = Counter(all_keywords)
        
        return {
            "total_unique_keywords": len(keyword_counts),
            "most_common_keywords": keyword_counts.most_common(20),
            "keyword_frequency_distribution": dict(keyword_counts),
            "average_keywords_per_document": len(all_keywords) / len(self.df)
        }
    
    def analyze_authors(self) -> Dict[str, Any]:
        """Analyze author patterns"""
        if self.df.empty:
            return {}
        
        all_authors = []
        author_counts = []
        
        for authors in self.df['authors']:
            if authors and authors != "Authors not found":
                # Split authors by common delimiters
                author_list = re.split(r'[,;]|\sand\s', authors)
                author_list = [author.strip() for author in author_list if author.strip()]
                all_authors.extend(author_list)
                author_counts.append(len(author_list))
        
        return {
            "total_authors": len(all_authors),
            "unique_authors": len(set(all_authors)),
            "average_authors_per_document": np.mean(author_counts) if author_counts else 0,
            "most_common_authors": Counter(all_authors).most_common(10),
            "collaboration_network": self._build_collaboration_network(all_authors)
        }
    
    def _build_collaboration_network(self, authors: List[str]) -> Dict[str, List[str]]:
        """Build a simple collaboration network"""
        network = {}
        for author in set(authors):
            collaborators = [a for a in set(authors) if a != author]
            network[author] = collaborators
        return network
    
    def analyze_content_themes(self) -> Dict[str, Any]:
        """Analyze content themes and topics"""
        if self.df.empty:
            return {}
        
        # Extract common themes from titles and keywords
        all_titles = self.df['title'].tolist()
        all_keywords = []
        for keywords in self.df['keywords']:
            all_keywords.extend(keywords)
        
        # Simple theme extraction based on common words
        title_words = []
        for title in all_titles:
            words = re.findall(r'\b\w+\b', title.lower())
            title_words.extend(words)
        
        keyword_words = []
        for keyword in all_keywords:
            words = re.findall(r'\b\w+\b', keyword.lower())
            keyword_words.extend(words)
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        
        title_words = [w for w in title_words if w not in stop_words and len(w) > 2]
        keyword_words = [w for w in keyword_words if w not in stop_words and len(w) > 2]
        
        return {
            "common_title_words": Counter(title_words).most_common(20),
            "common_keyword_words": Counter(keyword_words).most_common(20),
            "themes": self._extract_themes(all_titles, all_keywords)
        }
    
    def _extract_themes(self, titles: List[str], keywords: List[str]) -> List[str]:
        """Extract common themes from titles and keywords"""
        # Simple theme extraction - can be enhanced with NLP
        themes = []
        
        # Look for common academic themes
        academic_themes = [
            'machine learning', 'artificial intelligence', 'deep learning',
            'neural networks', 'natural language processing', 'computer vision',
            'data science', 'statistics', 'mathematics', 'algorithms',
            'optimization', 'research', 'analysis', 'modeling', 'prediction'
        ]
        
        all_text = ' '.join(titles + keywords).lower()
        for theme in academic_themes:
            if theme in all_text:
                themes.append(theme)
        
        return themes
    
    def analyze_processing_performance(self) -> Dict[str, Any]:
        """Analyze processing performance metrics"""
        if self.df.empty:
            return {}
        
        file_sizes = self.df['file_size'].tolist()
        character_counts = self.df['statistics'].apply(lambda x: x['character_count']).tolist()
        
        return {
            "file_size_stats": {
                "min": min(file_sizes),
                "max": max(file_sizes),
                "mean": np.mean(file_sizes),
                "median": np.median(file_sizes),
                "std": np.std(file_sizes)
            },
            "character_count_stats": {
                "min": min(character_counts),
                "max": max(character_counts),
                "mean": np.mean(character_counts),
                "median": np.median(character_counts),
                "std": np.std(character_counts)
            },
            "processing_efficiency": {
                "average_chars_per_mb": np.mean(character_counts) / (np.mean(file_sizes) / (1024 * 1024)),
                "compression_ratios": self.df['statistics'].apply(lambda x: x['compression_ratio']).tolist()
            }
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive analytics report"""
        return {
            "basic_statistics": self.get_basic_statistics(),
            "keyword_analysis": self.analyze_keywords(),
            "author_analysis": self.analyze_authors(),
            "content_themes": self.analyze_content_themes(),
            "performance_metrics": self.analyze_processing_performance(),
            "generated_at": datetime.now().isoformat()
        }

class DocumentComparator:
    """Compare and analyze similarities between documents"""
    
    def __init__(self, results: List[Dict[str, Any]]):
        self.results = results
    
    def calculate_similarity(self, doc1: Dict[str, Any], doc2: Dict[str, Any]) -> float:
        """Calculate similarity between two documents"""
        # Simple similarity based on keywords overlap
        keywords1 = set(doc1.get('keywords', []))
        keywords2 = set(doc2.get('keywords', []))
        
        if not keywords1 or not keywords2:
            return 0.0
        
        intersection = keywords1.intersection(keywords2)
        union = keywords1.union(keywords2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def find_similar_documents(self, threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Find documents with similarity above threshold"""
        similar_pairs = []
        
        for i, doc1 in enumerate(self.results):
            for j, doc2 in enumerate(self.results[i+1:], i+1):
                similarity = self.calculate_similarity(doc1, doc2)
                if similarity >= threshold:
                    similar_pairs.append({
                        "doc1": doc1['file_name'],
                        "doc2": doc2['file_name'],
                        "similarity": similarity,
                        "common_keywords": list(set(doc1.get('keywords', [])).intersection(set(doc2.get('keywords', []))))
                    })
        
        return sorted(similar_pairs, key=lambda x: x['similarity'], reverse=True)
    
    def cluster_documents(self, n_clusters: int = 3) -> Dict[str, List[str]]:
        """Simple document clustering based on keywords"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.cluster import KMeans
        
        if len(self.results) < n_clusters:
            return {"cluster_0": [doc['file_name'] for doc in self.results]}
        
        # Prepare text data for clustering
        texts = []
        for doc in self.results:
            text = f"{doc.get('title', '')} {' '.join(doc.get('keywords', []))}"
            texts.append(text)
        
        # Vectorize texts
        vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(tfidf_matrix)
        
        # Group documents by cluster
        clusters_dict = {}
        for i, cluster_id in enumerate(clusters):
            cluster_key = f"cluster_{cluster_id}"
            if cluster_key not in clusters_dict:
                clusters_dict[cluster_key] = []
            clusters_dict[cluster_key].append(self.results[i]['file_name'])
        
        return clusters_dict
