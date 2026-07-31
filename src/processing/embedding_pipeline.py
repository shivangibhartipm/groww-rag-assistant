"""
Phase 2.2: Embedding Pipeline
Orchestrates embedding generation and knowledge base construction.
"""

import logging
from typing import List, Dict
from pathlib import Path
import json

from .embedding_generator import EmbeddingGenerator
from .vector_database import VectorDatabase
from .knowledge_base import KnowledgeBase
from .pipeline import ProcessingPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingPipeline:
    """Pipeline for generating embeddings and building knowledge base."""
    
    def __init__(self,
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 use_openai: bool = False,
                 collection_name: str = "mutual_fund_chunks"):
        """
        Initialize embedding pipeline.
        
        Args:
            embedding_model: Embedding model name
            use_openai: Whether to use OpenAI embeddings
            collection_name: Name of the vector collection
        """
        self.processing_pipeline = ProcessingPipeline()
        self.knowledge_base = KnowledgeBase(
            collection_name=collection_name,
            embedding_model=embedding_model,
            use_openai=use_openai
        )
        
        logger.info("Embedding pipeline initialized")
    
    def run_full_pipeline(self, rebuild: bool = False) -> Dict:
        """
        Run the complete pipeline: process documents → generate embeddings → build KB.
        
        Args:
            rebuild: Whether to rebuild the knowledge base from scratch
            
        Returns:
            Complete pipeline summary
        """
        logger.info("Starting full embedding pipeline")
        
        # Step 1: Process documents (clean, chunk, enrich)
        logger.info("Step 1: Processing documents...")
        processing_result = self.processing_pipeline.process_from_storage()
        
        if 'message' in processing_result:
            logger.error(processing_result['message'])
            return processing_result
        
        chunks = processing_result['chunks']
        logger.info(f"Processed {len(chunks)} chunks")
        
        # Step 2: Build knowledge base
        logger.info("Step 2: Building knowledge base...")
        if rebuild:
            kb_result = self.knowledge_base.rebuild(chunks)
        else:
            kb_result = self.knowledge_base.build_from_chunks(chunks)
        
        # Step 3: Generate summary
        summary = {
            'processing': {
                'total_documents': processing_result['total_documents'],
                'successfully_processed': processing_result['successfully_processed'],
                'total_chunks': processing_result['total_chunks']
            },
            'embedding': {
                'chunks_with_embeddings': kb_result['chunks_with_embeddings'],
                'chunks_added_to_db': kb_result['chunks_added_to_db'],
                'total_chunks_in_db': kb_result['total_chunks_in_db'],
                'embedding_dimension': kb_result['embedding_dimension']
            },
            'knowledge_base': self.knowledge_base.get_statistics()
        }
        
        logger.info(f"Full pipeline completed: {summary}")
        return summary
    
    def build_from_processed_chunks(self, chunks: List[Dict], rebuild: bool = False) -> Dict:
        """
        Build knowledge base from already processed chunks.
        
        Args:
            chunks: List of processed chunk dictionaries
            rebuild: Whether to rebuild the knowledge base
            
        Returns:
            Build summary
        """
        logger.info(f"Building knowledge base from {len(chunks)} processed chunks")
        
        if rebuild:
            return self.knowledge_base.rebuild(chunks)
        else:
            return self.knowledge_base.build_from_chunks(chunks)
    
    def load_chunks_from_directory(self, chunks_dir: str = None) -> List[Dict]:
        """
        Load processed chunks from directory.
        
        Args:
            chunks_dir: Directory containing chunk JSON files
            
        Returns:
            List of chunk dictionaries
        """
        if chunks_dir is None:
            from ..ingestion.config import PROCESSED_DATA_DIR
            chunks_dir = PROCESSED_DATA_DIR
        
        chunks_path = Path(chunks_dir)
        if not chunks_path.exists():
            logger.error(f"Chunks directory not found: {chunks_dir}")
            return []
        
        chunks = []
        for chunk_file in chunks_path.glob('*.json'):
            try:
                with open(chunk_file, 'r', encoding='utf-8') as f:
                    chunk = json.load(f)
                    chunks.append(chunk)
            except Exception as e:
                logger.error(f"Error loading {chunk_file}: {str(e)}")
        
        logger.info(f"Loaded {len(chunks)} chunks from {chunks_dir}")
        return chunks
    
    def test_search(self, query: str) -> Dict:
        """
        Test the knowledge base with a search query.
        
        Args:
            query: Search query text
            
        Returns:
            Search results
        """
        logger.info(f"Testing search with query: {query}")
        
        results = self.knowledge_base.search(query, top_k=3)
        
        return {
            'query': query,
            'results_count': len(results),
            'results': results
        }
    
    def export_knowledge_base_info(self, output_path: str = None) -> str:
        """
        Export knowledge base information.
        
        Args:
            output_path: Path to save export
            
        Returns:
            Path to exported file
        """
        return self.knowledge_base.export_index_info(output_path)


def main():
    """Main entry point for running the embedding pipeline."""
    pipeline = EmbeddingPipeline()
    
    # Run full pipeline
    summary = pipeline.run_full_pipeline(rebuild=True)
    
    print("\n" + "="*50)
    print("EMBEDDING PIPELINE SUMMARY")
    print("="*50)
    
    if 'message' in summary:
        print(summary['message'])
        return
    
    print("\nProcessing Results:")
    print(f"  Documents Processed: {summary['processing']['successfully_processed']}/{summary['processing']['total_documents']}")
    print(f"  Chunks Created: {summary['processing']['total_chunks']}")
    
    print("\nEmbedding Results:")
    print(f"  Chunks with Embeddings: {summary['embedding']['chunks_with_embeddings']}")
    print(f"  Chunks Added to DB: {summary['embedding']['chunks_added_to_db']}")
    print(f"  Total Chunks in DB: {summary['embedding']['total_chunks_in_db']}")
    print(f"  Embedding Dimension: {summary['embedding']['embedding_dimension']}")
    
    print("\nKnowledge Base Stats:")
    kb_stats = summary['knowledge_base']
    print(f"  Collection: {kb_stats['collection_name']}")
    print(f"  Total Chunks: {kb_stats['total_chunks']}")
    print(f"  Persist Directory: {kb_stats['persist_directory']}")
    
    # Test search
    print("\n" + "-"*50)
    test_query = "expense ratio"
    print(f"Testing search with query: '{test_query}'")
    test_results = pipeline.test_search(test_query)
    print(f"Results found: {test_results['results_count']}")
    
    if test_results['results']:
        print("\nTop result:")
        top_result = test_results['results'][0]
        print(f"  Score: {top_result.get('score', 'N/A')}")
        print(f"  Source: {top_result.get('metadata', {}).get('source_url', 'N/A')}")
        print(f"  Text: {top_result.get('text', '')[:100]}...")
    
    print("="*50)


if __name__ == "__main__":
    main()
