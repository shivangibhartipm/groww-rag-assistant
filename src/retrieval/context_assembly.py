"""
Phase 3.2: Context Assembly
Constructs and optimizes context window from retrieved chunks.
"""

import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContextAssembly:
    """Assembles and optimizes context from retrieved chunks."""
    
    def __init__(self, max_tokens: int = 2000, max_chunk_tokens: int = 700):
        """
        Initialize context assembly.
        
        Args:
            max_tokens: Maximum tokens for context window
            max_chunk_tokens: Per-chunk truncation limit so multiple chunks fit
        """
        self.max_tokens = max_tokens
        self.max_chunk_tokens = max_chunk_tokens
        logger.info("Context assembly initialized")
    
    def assemble_context(self, chunks: List[Dict], preserve_sources: bool = True) -> Dict:
        """
        Assemble context from retrieved chunks.
        
        Args:
            chunks: List of retrieved chunks with metadata
            preserve_sources: Whether to include source information
            
        Returns:
            Assembled context with metadata
        """
        if not chunks:
            return {
                'context': '',
                'chunks_used': 0,
                'total_tokens': 0,
                'sources': [],
                'chunks': []
            }
        
        # Keep retrieval relevance order; only remove near-duplicates.
        # Do NOT re-rank by dates scraped from body text (false positives).
        optimized_chunks = self._optimize_chunks(chunks)
        
        context_parts = []
        sources = []
        seen_sources = set()
        used_chunks = []
        total_tokens = 0
        chunks_used = 0
        
        for chunk in optimized_chunks:
            chunk_text = self._truncate_text(chunk.get('text', ''), self.max_chunk_tokens)
            chunk_tokens = self._estimate_tokens(chunk_text)
            
            if total_tokens + chunk_tokens > self.max_tokens:
                logger.info(f"Token limit reached after {chunks_used} chunks")
                break
            
            source_url = chunk.get('metadata', {}).get('source_url', 'Unknown')
            scheme_name = chunk.get('metadata', {}).get('scheme_name', 'Unknown')
            
            if preserve_sources:
                context_parts.append(f"[Scheme: {scheme_name} | Source: {source_url}]")
                if source_url not in seen_sources:
                    sources.append(source_url)
                    seen_sources.add(source_url)
            
            context_parts.append(chunk_text)
            used_chunks.append(chunk)
            total_tokens += chunk_tokens
            chunks_used += 1
        
        context = '\n\n'.join(context_parts)
        
        return {
            'context': context,
            'chunks_used': chunks_used,
            'total_tokens': total_tokens,
            'sources': sources,
            'chunks': used_chunks,
            'token_limit': self.max_tokens
        }
    
    def _optimize_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Optimize chunks by removing redundancy while preserving relevance order.
        
        Args:
            chunks: List of chunks to optimize
            
        Returns:
            Optimized list of chunks
        """
        if not chunks:
            return chunks
        
        # Sort by relevance score (higher similarity is better)
        sorted_chunks = sorted(chunks, key=lambda x: x.get('score', 0), reverse=True)
        return self._deduplicate_chunks(sorted_chunks)
    
    def _truncate_text(self, text: str, max_tokens: int) -> str:
        """Truncate long scraped pages so multiple chunks fit in context."""
        max_chars = max_tokens * 4
        if len(text) <= max_chars:
            return text
        return text[:max_chars].rsplit(' ', 1)[0] + '...'
    
    def _deduplicate_chunks(self, chunks: List[Dict], similarity_threshold: float = 0.9) -> List[Dict]:
        """
        Remove chunks with highly similar content.
        
        Args:
            chunks: List of chunks
            similarity_threshold: Threshold for considering chunks similar
            
        Returns:
            Deduplicated chunks
        """
        if len(chunks) <= 1:
            return chunks
        
        unique_chunks = [chunks[0]]
        
        for chunk in chunks[1:]:
            is_duplicate = False
            chunk_text = chunk.get('text', '').lower()
            
            for existing_chunk in unique_chunks:
                existing_text = existing_chunk.get('text', '').lower()
                
                # Simple similarity check using Jaccard similarity
                similarity = self._jaccard_similarity(chunk_text, existing_text)
                
                if similarity > similarity_threshold:
                    is_duplicate = True
                    logger.debug(f"Removed duplicate chunk (similarity: {similarity:.2f})")
                    break
            
            if not is_duplicate:
                unique_chunks.append(chunk)
        
        return unique_chunks
    
    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count from text (rough approximation).
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        # Rough approximation: 1 token ≈ 4 characters for English
        return len(text) // 4
