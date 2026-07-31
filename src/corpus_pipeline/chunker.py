"""
Phase 2.7: Chunker
Splits documents into semantically meaningful chunks with overlap.
Consumes output from Cleaner (cleaned_text).
"""

import re
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Chunker:
    """Chunks documents into semantically meaningful pieces."""
    
    def __init__(self, min_chunk_size: int = 50, max_chunk_size: int = 200, overlap_percent: float = 0.15):
        """Initialize chunker."""
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap_percent = overlap_percent
        self.overlap_size = int(max_chunk_size * overlap_percent)
    
    def chunk_all(self, cleaning_results: List[Dict]) -> List[Dict]:
        """
        Chunk all cleaning results.
        
        Args:
            cleaning_results: List of cleaning results from Cleaner
            
        Returns:
            List of chunking results with chunks
        """
        all_chunks = []
        
        for cleaning_result in cleaning_results:
            if not cleaning_result.get('success'):
                logger.warning(f"Skipping failed cleaning: {cleaning_result.get('url')}")
                continue
            
            chunks = self.chunk_single(cleaning_result)
            all_chunks.extend(chunks)
        
        logger.info(f"Created {len(all_chunks)} total chunks")
        return all_chunks
    
    def chunk_single(self, cleaning_result: Dict) -> List[Dict]:
        """
        Chunk a single cleaning result.
        
        Args:
            cleaning_result: Cleaning result with cleaned_text
            
        Returns:
            List of chunk dictionaries
        """
        cleaned_text = cleaning_result.get('cleaned_text', '')
        url = cleaning_result.get('url')
        metadata = cleaning_result.get('metadata', {})
        
        if not cleaned_text:
            logger.warning(f"No text to chunk for {url}")
            return []
        
        # Split into paragraphs
        paragraphs = self._split_into_paragraphs(cleaned_text)
        
        # Group into chunks
        chunk_texts = self._group_into_chunks(paragraphs)
        
        # Create chunk dictionaries
        chunks = []
        for i, chunk_text in enumerate(chunk_texts):
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'chunk_id': i,
                'total_chunks': len(chunk_texts),
                'chunk_size': len(chunk_text.split()),
                'source_url': url
            })
            
            chunks.append({
                'text': chunk_text,
                'metadata': chunk_metadata
            })
        
        logger.info(f"Chunked {url} into {len(chunks)} chunks")
        return chunks
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs."""
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        if not paragraphs:
            paragraphs = re.split(r'[.!?]+', text)
            paragraphs = [s.strip() for s in paragraphs if s.strip()]
        return paragraphs
    
    def _group_into_chunks(self, paragraphs: List[str]) -> List[str]:
        """Group paragraphs into chunks with overlap."""
        chunks = []
        current_chunk = []
        current_size = 0
        
        i = 0
        while i < len(paragraphs):
            paragraph = paragraphs[i]
            para_size = len(paragraph.split())
            
            if current_size + para_size > self.max_chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                
                # Get overlap
                overlap = self._get_overlap(current_chunk)
                current_chunk = overlap
                current_size = sum(len(p.split()) for p in current_chunk)
                
                if current_size > self.max_chunk_size:
                    current_chunk = []
                    current_size = 0
            else:
                current_chunk.append(paragraph)
                current_size += para_size
                i += 1
        
        if current_chunk and current_size >= self.min_chunk_size:
            chunks.append(' '.join(current_chunk))
        elif current_chunk and current_size < self.min_chunk_size and chunks:
            chunks[-1] += ' ' + ' '.join(current_chunk)
        
        return chunks
    
    def _get_overlap(self, chunk_paragraphs: List[str]) -> List[str]:
        """Get overlap paragraphs from chunk."""
        overlap_size = 0
        overlap_paragraphs = []
        
        for paragraph in reversed(chunk_paragraphs):
            para_size = len(paragraph.split())
            if overlap_size + para_size <= self.overlap_size:
                overlap_paragraphs.insert(0, paragraph)
                overlap_size += para_size
            else:
                break
        
        return overlap_paragraphs
