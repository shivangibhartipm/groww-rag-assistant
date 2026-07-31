"""
Phase 2.2: Vector Database
Manages vector storage using ChromaDB for similarity search.
"""

import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import uuid

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("chromadb not installed. Install with: pip install chromadb")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorDatabase:
    """Manages vector storage and retrieval using ChromaDB."""
    
    def __init__(self, collection_name: str = "mutual_fund_chunks", persist_directory: str = None):
        """
        Initialize vector database.
        
        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist the database
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("chromadb not installed. Install with: pip install chromadb")
        
        self.collection_name = collection_name
        
        if persist_directory is None:
            from ..ingestion.config import VECTOR_INDEX_DIR
            persist_directory = VECTOR_INDEX_DIR
        
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Mutual fund FAQ chunks"}
        )
        
        logger.info(f"Vector database initialized at {self.persist_directory}")
        logger.info(f"Collection: {collection_name}, Count: {self.collection.count()}")
    
    def add_chunks(self, chunks: List[Dict]) -> int:
        """
        Add chunks to the vector database.
        
        Args:
            chunks: List of chunk dictionaries with 'embedding', 'text', and 'metadata'
            
        Returns:
            Number of chunks added
        """
        if not chunks:
            logger.warning("No chunks to add")
            return 0
        
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for chunk in chunks:
            # Generate unique ID
            chunk_id = str(uuid.uuid4())
            ids.append(chunk_id)
            
            # Extract embedding
            embedding = chunk.get('embedding')
            if embedding is None:
                logger.warning(f"Chunk missing embedding, skipping")
                continue
            embeddings.append(embedding)
            
            # Extract text
            documents.append(chunk.get('text', ''))
            
            # Extract and flatten metadata
            metadata = chunk.get('metadata', {})
            flat_metadata = self._flatten_metadata(metadata)
            metadatas.append(flat_metadata)
        
        if not embeddings:
            logger.warning("No valid embeddings to add")
            return 0
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        logger.info(f"Added {len(ids)} chunks to vector database")
        return len(ids)
    
    def search(self, query_embedding: List[float], top_k: int = 5, where: Dict = None) -> List[Dict]:
        """
        Search for similar chunks.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            where: Metadata filter conditions
            
        Returns:
            List of search results with scores and metadata
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where
        )
        
        # Format results
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'score': results['distances'][0][i] if 'distances' in results else None
                })
        
        logger.info(f"Search returned {len(formatted_results)} results")
        return formatted_results
    
    def search_by_text(self, query_text: str, embedding_generator, top_k: int = 5, where: Dict = None) -> List[Dict]:
        """
        Search by text query (generates embedding first).
        
        Args:
            query_text: Query text
            embedding_generator: EmbeddingGenerator instance
            top_k: Number of results to return
            where: Metadata filter conditions
            
        Returns:
            List of search results
        """
        query_embedding = embedding_generator.generate_embedding(query_text)
        return self.search(query_embedding.tolist(), top_k, where)
    
    def delete_by_metadata(self, metadata_filter: Dict) -> int:
        """
        Delete chunks matching metadata filter.
        
        Args:
            metadata_filter: Metadata conditions to match
            
        Returns:
            Number of chunks deleted
        """
        # Get matching IDs first
        results = self.collection.get(where=metadata_filter)
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
            logger.info(f"Deleted {len(results['ids'])} chunks matching filter")
            return len(results['ids'])
        
        return 0
    
    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        count = self.collection.count()
        
        return {
            'collection_name': self.collection_name,
            'total_chunks': count,
            'persist_directory': str(self.persist_directory)
        }
    
    def clear_collection(self):
        """Clear all chunks from the collection."""
        # Delete and recreate collection
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Mutual fund FAQ chunks"}
        )
        logger.info(f"Cleared collection: {self.collection_name}")
    
    def _flatten_metadata(self, metadata: Dict) -> Dict:
        """
        Flatten nested metadata for ChromaDB.
        
        Args:
            metadata: Nested metadata dictionary
            
        Returns:
            Flattened metadata dictionary
        """
        flat = {}
        
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                flat[key] = value
            elif isinstance(value, list):
                # Convert lists to strings
                flat[key] = str(value)
            elif isinstance(value, dict):
                # Recursively flatten nested dicts
                for sub_key, sub_value in self._flatten_metadata(value).items():
                    flat[f"{key}_{sub_key}"] = sub_value
            else:
                flat[key] = str(value)
        
        return flat
    
    def get_all_chunks(self, limit: int = None) -> List[Dict]:
        """
        Retrieve all chunks from the collection.
        
        Args:
            limit: Maximum number of chunks to retrieve
            
        Returns:
            List of chunk dictionaries
        """
        results = self.collection.get(limit=limit)
        
        chunks = []
        if results['ids']:
            for i in range(len(results['ids'])):
                chunks.append({
                    'id': results['ids'][i],
                    'text': results['documents'][i],
                    'metadata': results['metadatas'][i],
                    'embedding': results.get('embeddings', [[]])[i] if 'embeddings' in results else None
                })
        
        return chunks
