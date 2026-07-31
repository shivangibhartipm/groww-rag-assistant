"""
Phase 2.3: Knowledge Base Construction
Constructs and manages the vector index with proper structure and optimization.
"""

import logging
from typing import List, Dict, Optional
from pathlib import Path
import json

from .vector_database import VectorDatabase
from .embedding_generator import EmbeddingGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeBase:
    """Manages knowledge base construction and optimization."""
    
    def __init__(self, 
                 collection_name: str = "mutual_fund_chunks",
                 persist_directory: str = None,
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 use_openai: bool = False):
        """
        Initialize knowledge base.
        
        Args:
            collection_name: Name of the vector collection
            persist_directory: Directory to persist the database
            embedding_model: Embedding model name
            use_openai: Whether to use OpenAI embeddings
        """
        self.vector_db = VectorDatabase(collection_name, persist_directory)
        self.embedding_generator = EmbeddingGenerator(embedding_model, use_openai)
        
        # Search parameters
        self.default_top_k = 5
        self.similarity_threshold = 0.7
        
        logger.info("Knowledge base initialized")
    
    def build_from_chunks(self, chunks: List[Dict]) -> Dict:
        """
        Build knowledge base from chunks.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Build summary
        """
        logger.info(f"Building knowledge base from {len(chunks)} chunks")
        
        # Step 1: Generate embeddings for chunks
        logger.info("Step 1: Generating embeddings...")
        chunks_with_embeddings = self.embedding_generator.generate_for_chunks(chunks)
        
        # Step 2: Add to vector database
        logger.info("Step 2: Adding chunks to vector database...")
        added_count = self.vector_db.add_chunks(chunks_with_embeddings)
        
        # Step 3: Get statistics
        stats = self.vector_db.get_collection_stats()
        
        summary = {
            'total_chunks': len(chunks),
            'chunks_with_embeddings': len(chunks_with_embeddings),
            'chunks_added_to_db': added_count,
            'total_chunks_in_db': stats['total_chunks'],
            'embedding_dimension': self.embedding_generator.get_embedding_dimension()
        }
        
        logger.info(f"Knowledge base built: {summary}")
        return summary
    
    def rebuild(self, chunks: List[Dict]) -> Dict:
        """
        Rebuild knowledge base (clear existing and rebuild).
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Build summary
        """
        logger.info("Rebuilding knowledge base...")
        self.vector_db.clear_collection()
        return self.build_from_chunks(chunks)
    
    def search(self, query: str, top_k: int = None, filter_metadata: Dict = None) -> List[Dict]:
        """
        Search knowledge base for relevant chunks.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            List of search results
        """
        if top_k is None:
            top_k = self.default_top_k
        
        logger.info(f"Searching knowledge base with query: {query[:50]}...")
        
        results = self.vector_db.search_by_text(
            query_text=query,
            embedding_generator=self.embedding_generator,
            top_k=top_k,
            where=filter_metadata
        )
        
        # Filter by similarity threshold if scores are available
        filtered_results = []
        for result in results:
            score = result.get('score')
            if score is None or score >= self.similarity_threshold:
                filtered_results.append(result)
        
        logger.info(f"Search returned {len(filtered_results)} results (threshold: {self.similarity_threshold})")
        return filtered_results
    
    def search_by_scheme(self, query: str, scheme_name: str, top_k: int = None) -> List[Dict]:
        """
        Search knowledge base filtered by specific scheme.
        
        Args:
            query: Search query text
            scheme_name: Name of the mutual fund scheme
            top_k: Number of results to return
            
        Returns:
            List of search results
        """
        filter_metadata = {"scheme_name": scheme_name}
        return self.search(query, top_k, filter_metadata)
    
    def search_by_document_type(self, query: str, document_type: str, top_k: int = None) -> List[Dict]:
        """
        Search knowledge base filtered by document type.
        
        Args:
            query: Search query text
            document_type: Type of document (factsheet, FAQ, etc.)
            top_k: Number of results to return
            
        Returns:
            List of search results
        """
        filter_metadata = {"document_type": document_type}
        return self.search(query, top_k, filter_metadata)
    
    def get_statistics(self) -> Dict:
        """
        Get knowledge base statistics.
        
        Returns:
            Statistics dictionary
        """
        db_stats = self.vector_db.get_collection_stats()
        
        return {
            'collection_name': db_stats['collection_name'],
            'total_chunks': db_stats['total_chunks'],
            'persist_directory': db_stats['persist_directory'],
            'embedding_dimension': self.embedding_generator.get_embedding_dimension(),
            'default_top_k': self.default_top_k,
            'similarity_threshold': self.similarity_threshold
        }
    
    def export_index_info(self, output_path: str = None) -> str:
        """
        Export index information to JSON file.
        
        Args:
            output_path: Path to save the export
            
        Returns:
            Path to exported file
        """
        if output_path is None:
            from ..ingestion.config import VECTOR_INDEX_DIR
            output_path = Path(VECTOR_INDEX_DIR) / "index_info.json"
        
        stats = self.get_statistics()
        chunks = self.vector_db.get_all_chunks(limit=100)  # Sample first 100
        
        export_data = {
            'statistics': stats,
            'sample_chunks': chunks,
            'export_timestamp': stats.get('persist_directory', '')
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported index info to {output_path}")
        return str(output_path)
    
    def set_search_parameters(self, top_k: int = None, similarity_threshold: float = None):
        """
        Update search parameters.
        
        Args:
            top_k: Default number of results
            similarity_threshold: Minimum similarity score
        """
        if top_k is not None:
            self.default_top_k = top_k
        if similarity_threshold is not None:
            self.similarity_threshold = similarity_threshold
        
        logger.info(f"Search parameters updated: top_k={self.default_top_k}, "
                   f"threshold={self.similarity_threshold}")
    
    def delete_by_scheme(self, scheme_name: str) -> int:
        """
        Delete all chunks for a specific scheme.
        
        Args:
            scheme_name: Name of the scheme to delete
            
        Returns:
            Number of chunks deleted
        """
        filter_metadata = {"scheme_name": scheme_name}
        return self.vector_db.delete_by_metadata(filter_metadata)
    
    def get_unique_schemes(self) -> List[str]:
        """
        Get list of unique schemes in the knowledge base.
        
        Returns:
            List of scheme names
        """
        chunks = self.vector_db.get_all_chunks()
        schemes = set()
        
        for chunk in chunks:
            scheme = chunk.get('metadata', {}).get('scheme_name')
            if scheme:
                schemes.add(scheme)
        
        return sorted(list(schemes))
    
    def get_unique_document_types(self) -> List[str]:
        """
        Get list of unique document types in the knowledge base.
        
        Returns:
            List of document types
        """
        chunks = self.vector_db.get_all_chunks()
        doc_types = set()
        
        for chunk in chunks:
            doc_type = chunk.get('metadata', {}).get('document_type')
            if doc_type:
                doc_types.add(doc_type)
        
        return sorted(list(doc_types))
