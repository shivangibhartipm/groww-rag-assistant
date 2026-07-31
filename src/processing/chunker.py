"""
Phase 2.1: Text Preprocessing - Chunking Strategy
Splits documents into semantically meaningful chunks with overlap.
"""

import re
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentChunker:
    """Chunks documents into semantically meaningful pieces."""
    
    def __init__(self, 
                 min_chunk_size: int = 200,
                 max_chunk_size: int = 500,
                 overlap_percent: float = 0.15):
        """
        Initialize document chunker.
        
        Args:
            min_chunk_size: Minimum tokens per chunk
            max_chunk_size: Maximum tokens per chunk
            overlap_percent: Overlap percentage (0.1-0.2 for 10-20%)
        """
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap_percent = overlap_percent
        self.overlap_size = int(max_chunk_size * overlap_percent)
        
        logger.info(f"Chunker initialized: min={min_chunk_size}, max={max_chunk_size}, "
                   f"overlap={overlap_percent*100:.0f}%")
    
    def chunk_document(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Chunk a document into semantically meaningful pieces.
        
        Args:
            text: Document text
            metadata: Document metadata to attach to chunks
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        if metadata is None:
            metadata = {}
        
        if not text or not text.strip():
            logger.warning("Empty text provided for chunking")
            return []
        
        # Step 1: Split into paragraphs
        paragraphs = self._split_into_paragraphs(text)
        
        # Step 2: Group paragraphs into chunks
        chunks = self._group_paragraphs_into_chunks(paragraphs)
        
        # Step 3: Add metadata to each chunk
        chunk_dicts = []
        for i, chunk_text in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'chunk_id': i,
                'total_chunks': len(chunks),
                'chunk_size': len(chunk_text.split())
            })
            
            chunk_dicts.append({
                'text': chunk_text,
                'metadata': chunk_metadata
            })
        
        logger.info(f"Chunked document into {len(chunks)} chunks")
        return chunk_dicts
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs while preserving structure.
        
        Args:
            text: Input text
            
        Returns:
            List of paragraphs
        """
        # Split by newlines and filter empty
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        # If no paragraphs, split by sentences
        if not paragraphs:
            paragraphs = self._split_into_sentences(text)
        
        return paragraphs
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting by punctuation
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def _group_paragraphs_into_chunks(self, paragraphs: List[str]) -> List[str]:
        """
        Group paragraphs into chunks respecting size limits and overlap.
        
        Args:
            paragraphs: List of paragraphs
            
        Returns:
            List of chunk texts
        """
        chunks = []
        current_chunk = []
        current_size = 0
        
        i = 0
        while i < len(paragraphs):
            paragraph = paragraphs[i]
            paragraph_size = len(paragraph.split())
            
            # If adding paragraph exceeds max size, finalize current chunk
            if current_size + paragraph_size > self.max_chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                
                # Start new chunk with overlap
                overlap_paragraphs = self._get_overlap_paragraphs(current_chunk)
                current_chunk = overlap_paragraphs
                current_size = sum(len(p.split()) for p in current_chunk)
                
                # If overlap alone exceeds max, reduce overlap
                if current_size > self.max_chunk_size:
                    current_chunk = []
                    current_size = 0
            else:
                current_chunk.append(paragraph)
                current_size += paragraph_size
                i += 1
        
        # Add final chunk if it meets minimum size
        if current_chunk and current_size >= self.min_chunk_size:
            chunks.append(' '.join(current_chunk))
        elif current_chunk and current_size < self.min_chunk_size and chunks:
            # Merge with previous chunk if too small
            chunks[-1] += ' ' + ' '.join(current_chunk)
        
        return chunks
    
    def _get_overlap_paragraphs(self, chunk_paragraphs: List[str]) -> List[str]:
        """
        Get overlap paragraphs from current chunk for next chunk.
        
        Args:
            chunk_paragraphs: Current chunk paragraphs
            
        Returns:
            List of overlap paragraphs
        """
        if not chunk_paragraphs:
            return []
        
        overlap_size = 0
        overlap_paragraphs = []
        
        # Take paragraphs from the end until we reach overlap size
        for paragraph in reversed(chunk_paragraphs):
            para_size = len(paragraph.split())
            if overlap_size + para_size <= self.overlap_size:
                overlap_paragraphs.insert(0, paragraph)
                overlap_size += para_size
            else:
                break
        
        return overlap_paragraphs
    
    def chunk_documents_batch(self, documents: List[Dict]) -> List[Dict]:
        """
        Chunk multiple documents.
        
        Args:
            documents: List of document dictionaries with 'text' and 'metadata'
            
        Returns:
            List of all chunks from all documents
        """
        all_chunks = []
        
        for doc in documents:
            text = doc.get('text', '')
            metadata = doc.get('metadata', {})
            
            chunks = self.chunk_document(text, metadata)
            all_chunks.extend(chunks)
        
        logger.info(f"Chunked {len(documents)} documents into {len(all_chunks)} total chunks")
        return all_chunks
    
    def estimate_token_count(self, text: str) -> int:
        """
        Estimate token count (rough approximation: 1 token ≈ 0.75 words).
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        word_count = len(text.split())
        return int(word_count / 0.75)
