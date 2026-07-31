"""
Phase 2.1: Text Preprocessing - Metadata Enrichment
Attaches source URL, document type, scheme name, and category to chunks.
"""

import logging
from typing import Dict, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetadataEnricher:
    """Enriches chunks with metadata from source documents."""
    
    # Document type mapping based on URL patterns
    DOCUMENT_TYPE_PATTERNS = {
        'factsheet': ['factsheet', 'fact-sheet', 'factsheet'],
        'kim': ['kim', 'key-information', 'key information'],
        'sid': ['sid', 'scheme-information', 'scheme information'],
        'faq': ['faq', 'help', 'support'],
        'guidance': ['guidance', 'investor-education', 'education'],
        'scheme_page': ['mutual-funds', 'scheme']
    }
    
    def __init__(self):
        """Initialize metadata enricher."""
        pass
    
    def enrich_chunk(self, chunk: Dict, source_document: Dict) -> Dict:
        """
        Enrich a single chunk with metadata from source document.
        
        Args:
            chunk: Chunk dictionary with text and basic metadata
            source_document: Source document with full metadata
            
        Returns:
            Enriched chunk dictionary
        """
        # Copy existing chunk metadata
        enriched_metadata = chunk.get('metadata', {}).copy()
        
        # Add source-level metadata
        enriched_metadata['source_url'] = source_document.get('url')
        enriched_metadata['scheme_name'] = source_document.get('scheme_name')
        enriched_metadata['scheme_type'] = source_document.get('scheme_type')
        enriched_metadata['plan'] = source_document.get('plan')
        
        # Infer document type from URL or source_type
        source_type = source_document.get('source_type', '')
        if source_type:
            enriched_metadata['document_type'] = source_type
        else:
            enriched_metadata['document_type'] = self._infer_document_type(
                source_document.get('url', '')
            )
        
        # Add timestamp
        enriched_metadata['last_updated'] = source_document.get('timestamp') or datetime.utcnow().isoformat()
        
        # Add content statistics
        chunk_text = chunk.get('text', '')
        enriched_metadata['word_count'] = len(chunk_text.split())
        enriched_metadata['char_count'] = len(chunk_text)
        
        # Update chunk
        chunk['metadata'] = enriched_metadata
        
        return chunk
    
    def enrich_chunks_batch(self, chunks: List[Dict], source_document: Dict) -> List[Dict]:
        """
        Enrich multiple chunks from the same source document.
        
        Args:
            chunks: List of chunk dictionaries
            source_document: Source document with full metadata
            
        Returns:
            List of enriched chunk dictionaries
        """
        enriched_chunks = []
        
        for chunk in chunks:
            enriched_chunk = self.enrich_chunk(chunk, source_document)
            enriched_chunks.append(enriched_chunk)
        
        logger.info(f"Enriched {len(chunks)} chunks with metadata")
        return enriched_chunks
    
    def enrich_multiple_documents(self, documents_chunks: List[Dict]) -> List[Dict]:
        """
        Enrich chunks from multiple source documents.
        
        Args:
            documents_chunks: List of dictionaries with 'chunks' and 'source_document'
            
        Returns:
            List of all enriched chunks
        """
        all_enriched_chunks = []
        
        for doc_data in documents_chunks:
            chunks = doc_data.get('chunks', [])
            source_document = doc_data.get('source_document', {})
            
            enriched = self.enrich_chunks_batch(chunks, source_document)
            all_enriched_chunks.extend(enriched)
        
        logger.info(f"Enriched {len(all_enriched_chunks)} total chunks from multiple documents")
        return all_enriched_chunks
    
    def _infer_document_type(self, url: str) -> str:
        """
        Infer document type from URL.
        
        Args:
            url: Document URL
            
        Returns:
            Inferred document type
        """
        url_lower = url.lower()
        
        for doc_type, patterns in self.DOCUMENT_TYPE_PATTERNS.items():
            for pattern in patterns:
                if pattern in url_lower:
                    return doc_type
        
        # Default to 'unknown' if no pattern matches
        return 'unknown'
    
    def validate_metadata(self, chunk: Dict) -> bool:
        """
        Validate that a chunk has required metadata fields.
        
        Args:
            chunk: Chunk dictionary
            
        Returns:
            True if metadata is valid
        """
        metadata = chunk.get('metadata', {})
        
        required_fields = ['source_url', 'document_type', 'chunk_id']
        
        for field in required_fields:
            if field not in metadata or not metadata[field]:
                logger.warning(f"Chunk missing required metadata field: {field}")
                return False
        
        return True
    
    def get_metadata_summary(self, chunks: List[Dict]) -> Dict:
        """
        Generate a summary of metadata across all chunks.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Summary dictionary
        """
        if not chunks:
            return {'message': 'No chunks provided'}
        
        # Count by document type
        doc_type_counts = {}
        scheme_counts = {}
        total_words = 0
        
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            
            doc_type = metadata.get('document_type', 'unknown')
            doc_type_counts[doc_type] = doc_type_counts.get(doc_type, 0) + 1
            
            scheme_name = metadata.get('scheme_name', 'unknown')
            scheme_counts[scheme_name] = scheme_counts.get(scheme_name, 0) + 1
            
            total_words += metadata.get('word_count', 0)
        
        return {
            'total_chunks': len(chunks),
            'total_words': total_words,
            'document_types': doc_type_counts,
            'schemes': scheme_counts,
            'avg_words_per_chunk': total_words / len(chunks) if chunks else 0
        }
