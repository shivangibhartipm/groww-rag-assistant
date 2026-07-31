"""
Phase 2.2: Embedding Generation
Generates embeddings for text chunks using sentence-transformers.
"""

import logging
from typing import List, Dict, Optional
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("sentence-transformers not installed. Install with: pip install sentence-transformers")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates embeddings for text chunks."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", use_openai: bool = False):
        """
        Initialize embedding generator.
        
        Args:
            model_name: Model name for sentence-transformers
            use_openai: Whether to use OpenAI embeddings instead
        """
        self.model_name = model_name
        self.use_openai = use_openai
        self.model = None
        
        if use_openai:
            logger.info("Using OpenAI embeddings")
            self._init_openai()
        else:
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                logger.info(f"Loading sentence-transformers model: {model_name}")
                self.model = SentenceTransformer(model_name)
                logger.info(f"Model loaded. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
            else:
                raise ImportError("sentence-transformers not installed. Install with: pip install sentence-transformers")
    
    def _init_openai(self):
        """Initialize OpenAI client for embeddings."""
        try:
            import openai
            from dotenv import load_dotenv
            load_dotenv()
            
            self.openai_client = openai.OpenAI()
            self.openai_model = "text-embedding-3-small"
            logger.info("OpenAI client initialized")
        except ImportError:
            raise ImportError("openai not installed. Install with: pip install openai")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as numpy array
        """
        if self.use_openai:
            return self._generate_openai_embedding(text)
        else:
            return self._generate_sentence_transformer_embedding(text)
    
    def _generate_sentence_transformer_embedding(self, text: str) -> np.ndarray:
        """Generate embedding using sentence-transformers."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def _generate_openai_embedding(self, text: str) -> np.ndarray:
        """Generate embedding using OpenAI API."""
        response = self.openai_client.embeddings.create(
            input=text,
            model=self.openai_model
        )
        embedding = np.array(response.data[0].embedding)
        return embedding
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        logger.info(f"Generating embeddings for {len(texts)} texts with batch size {batch_size}")
        
        if self.use_openai:
            return self._generate_openai_embeddings_batch(texts, batch_size)
        else:
            return self._generate_sentence_transformer_embeddings_batch(texts, batch_size)
    
    def _generate_sentence_transformer_embeddings_batch(self, texts: List[str], batch_size: int) -> List[np.ndarray]:
        """Generate embeddings using sentence-transformers in batches."""
        embeddings = self.model.encode(texts, batch_size=batch_size, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.tolist() if isinstance(embeddings, np.ndarray) else embeddings
    
    def _generate_openai_embeddings_batch(self, texts: List[str], batch_size: int) -> List[np.ndarray]:
        """Generate embeddings using OpenAI API in batches."""
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
            
            response = self.openai_client.embeddings.create(
                input=batch,
                model=self.openai_model
            )
            
            batch_embeddings = [np.array(item.embedding) for item in response.data]
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            Embedding dimension
        """
        if self.use_openai:
            # text-embedding-3-small has 1536 dimensions
            return 1536
        else:
            return self.model.get_sentence_embedding_dimension()
    
    def generate_for_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Generate embeddings for chunks and attach them.
        
        Args:
            chunks: List of chunk dictionaries with 'text' field
            
        Returns:
            List of chunks with 'embedding' field added
        """
        texts = [chunk.get('text', '') for chunk in chunks]
        embeddings = self.generate_embeddings_batch(texts)
        
        for chunk, embedding in zip(chunks, embeddings):
            chunk['embedding'] = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
        
        logger.info(f"Generated embeddings for {len(chunks)} chunks")
        return chunks
