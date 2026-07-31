"""
Phase 3.1: Similarity Search
Performs vector similarity search in the vector database.
"""

import logging
from typing import List, Dict

from ..corpus_pipeline.indexer import Indexer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimilaritySearch:
    """Performs similarity search on vector database."""
    
    def __init__(self, collection_name: str = "groww_corpus", persist_directory: str = None):
        """
        Initialize similarity search.
        
        Args:
            collection_name: Name of the vector collection
            persist_directory: Directory for vector database
        """
        self.indexer = Indexer(collection_name, persist_directory)
        self.default_top_k = 5
        # Chroma returns L2 distances; we convert to similarity = 1/(1+distance).
        # Typical relevant hits land around 0.30–0.45 for this corpus.
        self.relevance_threshold = 0.30
        logger.info("Similarity search initialized")
    
    def search(self, query_embedding: List[float], top_k: int = None, threshold: float = None) -> Dict:
        """
        Perform similarity search with query embedding.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            threshold: Minimum similarity score (higher is better)
            
        Returns:
            Search results with ranked chunks
        """
        if top_k is None:
            top_k = self.default_top_k
        if threshold is None:
            threshold = self.relevance_threshold
        
        # Perform search (Indexer returns Chroma L2 distances as 'score')
        results = self.indexer.search(query_embedding, top_k)
        
        # Convert L2 distance -> similarity and filter/rank
        filtered_results = []
        for result in results:
            distance = result.get('score')
            if distance is None:
                similarity = 0.0
            else:
                similarity = 1.0 / (1.0 + float(distance))
                result['distance'] = float(distance)
            result['score'] = similarity
            
            if similarity >= threshold:
                filtered_results.append(result)
        
        # Higher similarity is better
        filtered_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        sources = self._extract_sources(filtered_results)
        
        return {
            'results': filtered_results,
            'count': len(filtered_results),
            'sources': sources,
            'threshold': threshold,
            'top_k': top_k
        }
    
    def _extract_sources(self, results: List[Dict]) -> List[str]:
        """Extract unique source URLs from results, preserving relevance order."""
        sources = []
        seen = set()
        for result in results:
            source_url = result.get('metadata', {}).get('source_url')
            if source_url and source_url not in seen:
                sources.append(source_url)
                seen.add(source_url)
        return sources
    
    def set_search_parameters(self, top_k: int = None, threshold: float = None):
        """Update search parameters."""
        if top_k is not None:
            self.default_top_k = top_k
        if threshold is not None:
            self.relevance_threshold = threshold
        logger.info(f"Search parameters updated: top_k={self.default_top_k}, threshold={self.relevance_threshold}")
