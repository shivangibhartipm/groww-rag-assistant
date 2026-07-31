"""
Phase 2.9: Indexer
Builds vector index using ChromaDB for similarity search.
Consumes output from Embedder (chunks with embeddings).
"""

import logging
from typing import List, Dict
from pathlib import Path
import uuid

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("chromadb not installed")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Indexer:
    """Builds and manages vector index."""
    
    def __init__(self, collection_name: str = "groww_corpus", persist_directory: str = None):
        """Initialize indexer."""
        if not CHROMADB_AVAILABLE:
            raise ImportError("chromadb not installed. Install with: pip install chromadb")
        
        self.collection_name = collection_name
        
        if persist_directory is None:
            from ..ingestion.config import VECTOR_INDEX_DIR
            persist_directory = VECTOR_INDEX_DIR
        
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Groww mutual fund corpus"}
        )
        
        logger.info(f"Indexer initialized at {self.persist_directory}")
    
    def index_all(self, chunks: List[Dict]) -> Dict:
        """
        Index all chunks with embeddings.
        
        Args:
            chunks: List of chunks with embeddings from Embedder
            
        Returns:
            Indexing summary
        """
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for chunk in chunks:
            chunk_id = str(uuid.uuid4())
            ids.append(chunk_id)
            
            embedding = chunk.get('embedding')
            if embedding is None:
                logger.warning(f"Chunk missing embedding, skipping")
                continue
            embeddings.append(embedding)
            
            documents.append(chunk.get('text', ''))
            
            metadata = chunk.get('metadata', {})
            flat_metadata = self._flatten_metadata(metadata)
            metadatas.append(flat_metadata)
        
        if not embeddings:
            logger.warning("No valid embeddings to index")
            return {'indexed_count': 0, 'total_chunks': len(chunks)}
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        logger.info(f"Indexed {len(ids)} chunks")
        return {
            'indexed_count': len(ids),
            'total_chunks': len(chunks),
            'collection_name': self.collection_name
        }
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Search for similar chunks."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        formatted = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                formatted.append({
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'score': results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted
    
    def get_by_metadata(self, where: Dict) -> List[Dict]:
        """Fetch chunks matching metadata filters."""
        results = self.collection.get(
            where=where,
            include=["documents", "metadatas"]
        )
        formatted = []
        ids = results.get('ids') or []
        documents = results.get('documents') or []
        metadatas = results.get('metadatas') or []
        for i, doc_id in enumerate(ids):
            formatted.append({
                'id': doc_id,
                'text': documents[i] if i < len(documents) else '',
                'metadata': metadatas[i] if i < len(metadatas) else {},
                'score': 1.0,  # explicit include; treat as highly relevant
            })
        return formatted
    
    def get_stats(self) -> Dict:
        """Get index statistics."""
        return {
            'collection_name': self.collection_name,
            'total_chunks': self.collection.count(),
            'persist_directory': str(self.persist_directory)
        }
    
    def clear(self):
        """Clear the index."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Groww mutual fund corpus"}
        )
        logger.info(f"Cleared collection: {self.collection_name}")
    
    def _flatten_metadata(self, metadata: Dict) -> Dict:
        """Flatten nested metadata for ChromaDB."""
        flat = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                flat[key] = value
            elif isinstance(value, list):
                flat[key] = str(value)
            elif isinstance(value, dict):
                for sub_key, sub_value in self._flatten_metadata(value).items():
                    flat[f"{key}_{sub_key}"] = sub_value
            else:
                flat[key] = str(value)
        return flat
