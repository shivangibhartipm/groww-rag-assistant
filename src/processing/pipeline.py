"""
Phase 2.1: Document Processing Pipeline
Orchestrates text cleaning, chunking, and metadata enrichment.
"""

import logging
from typing import List, Dict
from pathlib import Path

from .text_cleaner import TextCleaner
from .chunker import DocumentChunker
from .metadata_enricher import MetadataEnricher
from ..ingestion.document_storage import DocumentStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProcessingPipeline:
    """Pipeline for processing documents into chunks with metadata."""
    
    def __init__(self, 
                 min_chunk_size: int = 200,
                 max_chunk_size: int = 500,
                 overlap_percent: float = 0.15):
        """
        Initialize processing pipeline.
        
        Args:
            min_chunk_size: Minimum tokens per chunk
            max_chunk_size: Maximum tokens per chunk
            overlap_percent: Overlap percentage for chunks
        """
        self.cleaner = TextCleaner()
        self.chunker = DocumentChunker(min_chunk_size, max_chunk_size, overlap_percent)
        self.enricher = MetadataEnricher()
        self.storage = DocumentStorage()
        
        logger.info("Processing pipeline initialized")
    
    def process_document(self, document: Dict) -> Dict:
        """
        Process a single document through the pipeline.
        
        Args:
            document: Document dictionary with main_text and metadata
            
        Returns:
            Processing result with chunks and summary
        """
        logger.info(f"Processing document: {document.get('url')}")
        
        # Step 1: Clean text
        raw_text = document.get('main_text', '')
        cleaned_text = self.cleaner.clean(raw_text)
        
        # Step 2: Chunk document
        metadata = {
            'url': document.get('url'),
            'scheme_name': document.get('scheme_name'),
            'scheme_type': document.get('scheme_type'),
            'plan': document.get('plan'),
            'source_type': document.get('source_type'),
            'timestamp': document.get('timestamp')
        }
        
        chunks = self.chunker.chunk_document(cleaned_text, metadata)
        
        # Step 3: Enrich chunks with metadata
        enriched_chunks = self.enricher.enrich_chunks_batch(chunks, document)
        
        # Step 4: Validate chunks
        valid_chunks = [c for c in enriched_chunks if self.enricher.validate_metadata(c)]
        
        result = {
            'source_url': document.get('url'),
            'total_chunks': len(chunks),
            'valid_chunks': len(valid_chunks),
            'chunks': valid_chunks,
            'summary': self.enricher.get_metadata_summary(valid_chunks)
        }
        
        logger.info(f"Processed document: {len(valid_chunks)} valid chunks created")
        
        return result
    
    def process_batch(self, documents: List[Dict]) -> Dict:
        """
        Process multiple documents through the pipeline.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            Batch processing summary with all chunks
        """
        logger.info(f"Starting batch processing for {len(documents)} documents")
        
        all_chunks = []
        processing_results = []
        
        for doc in documents:
            try:
                result = self.process_document(doc)
                processing_results.append(result)
                all_chunks.extend(result['chunks'])
            except Exception as e:
                logger.error(f"Error processing document {doc.get('url')}: {str(e)}")
                processing_results.append({
                    'source_url': doc.get('url'),
                    'error': str(e),
                    'chunks': []
                })
        
        # Generate batch summary
        batch_summary = {
            'total_documents': len(documents),
            'successfully_processed': len([r for r in processing_results if 'error' not in r]),
            'failed_processing': len([r for r in processing_results if 'error' in r]),
            'total_chunks': len(all_chunks),
            'chunks': all_chunks,
            'document_results': processing_results,
            'overall_summary': self.enricher.get_metadata_summary(all_chunks)
        }
        
        logger.info(f"Batch processing complete: {batch_summary['total_chunks']} chunks from "
                   f"{batch_summary['successfully_processed']}/{batch_summary['total_documents']} documents")
        
        return batch_summary
    
    def process_from_storage(self, storage_dir: str = None) -> Dict:
        """
        Process all documents from storage.
        
        Args:
            storage_dir: Directory containing raw documents (uses default if not provided)
            
        Returns:
            Batch processing summary
        """
        if storage_dir:
            self.storage = DocumentStorage(storage_dir)
        
        # Load all documents from storage
        documents = self.storage.load_all_documents()
        
        if not documents:
            logger.warning("No documents found in storage")
            return {'message': 'No documents to process'}
        
        logger.info(f"Loaded {len(documents)} documents from storage")
        
        # Process batch
        return self.process_batch(documents)
    
    def save_processed_chunks(self, chunks: List[Dict], output_dir: str = None) -> List[str]:
        """
        Save processed chunks to disk.
        
        Args:
            chunks: List of chunk dictionaries
            output_dir: Output directory (uses processed data dir if not provided)
            
        Returns:
            List of saved file paths
        """
        if output_dir is None:
            from ..ingestion.config import PROCESSED_DATA_DIR
            output_dir = PROCESSED_DATA_DIR
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        saved_paths = []
        
        for chunk in chunks:
            # Generate filename
            chunk_id = chunk.get('metadata', {}).get('chunk_id', 0)
            source_url = chunk.get('metadata', {}).get('source_url', 'unknown')
            filename = self._chunk_to_filename(source_url, chunk_id)
            filepath = output_path / filename
            
            # Save chunk as JSON
            import json
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(chunk, f, indent=2, ensure_ascii=False)
            
            saved_paths.append(str(filepath))
        
        logger.info(f"Saved {len(saved_paths)} chunks to {output_dir}")
        return saved_paths
    
    def _chunk_to_filename(self, url: str, chunk_id: int) -> str:
        """
        Generate filename from URL and chunk ID.
        
        Args:
            url: Source URL
            chunk_id: Chunk ID
            
        Returns:
            Filename string
        """
        # Simplify URL
        url = url.replace('https://', '').replace('http://', '')
        url = url.replace('/', '_')[:50]  # Limit length
        
        return f"{url}_chunk_{chunk_id}.json"


def main():
    """Main entry point for running the processing pipeline."""
    pipeline = ProcessingPipeline()
    
    # Process documents from storage
    result = pipeline.process_from_storage()
    
    if 'message' in result:
        print(result['message'])
        return
    
    # Save processed chunks
    saved_paths = pipeline.save_processed_chunks(result['chunks'])
    
    print("\n" + "="*50)
    print("PROCESSING PIPELINE SUMMARY")
    print("="*50)
    print(f"Total Documents: {result['total_documents']}")
    print(f"Successfully Processed: {result['successfully_processed']}")
    print(f"Failed: {result['failed_processing']}")
    print(f"Total Chunks: {result['total_chunks']}")
    print(f"Chunks Saved: {len(saved_paths)}")
    
    summary = result.get('overall_summary', {})
    if summary:
        print(f"\nChunk Statistics:")
        print(f"  Total Words: {summary.get('total_words', 0)}")
        print(f"  Avg Words/Chunk: {summary.get('avg_words_per_chunk', 0):.1f}")
        print(f"  Document Types: {summary.get('document_types', {})}")
    
    print("="*50)


if __name__ == "__main__":
    main()
