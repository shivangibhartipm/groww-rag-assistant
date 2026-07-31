"""
Phase 3.1: Query Processing
Processes user queries and generates embeddings using the same model as corpus.
"""

import logging
from typing import Dict
import numpy as np

from ..corpus_pipeline.embedder import Embedder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryProcessor:
    """Processes user queries and generates embeddings."""
    
    def __init__(self):
        """Initialize query processor. Raises EmbedderUnavailable if the model is missing."""
        self.embedder = Embedder()
        logger.info("Query processor initialized")
    
    def process_query(self, query: str) -> Dict:
        """
        Process a user query and generate embedding.
        
        Args:
            query: User query text
            
        Returns:
            Processed query with embedding
        """
        if not query or not query.strip():
            return {
                'query': query,
                'embedding': None,
                'error': 'Empty query'
            }
        
        # Clean query
        cleaned_query = self._clean_query(query)
        
        # Generate embedding
        embedding = self.embedder.encode([cleaned_query])[0]
        
        return {
            'query': query,
            'cleaned_query': cleaned_query,
            'embedding': embedding.tolist(),
            'embedding_dimension': self.embedder.get_embedding_dimension(),
            'error': None
        }
    
    def _clean_query(self, query: str) -> str:
        """Clean and normalize query text."""
        # Remove extra whitespace
        query = ' '.join(query.split())
        # Remove special characters but keep basic punctuation
        import re
        query = re.sub(r'[^\w\s.,?!]', '', query)
        return query.strip()
