"""
Corpus Pipeline: URLs → Fetcher → Extractor → Cleaner → Chunker → Embedder → Indexer
Orchestrates the complete corpus building pipeline.
"""

import logging
from typing import Dict, List
import json
from pathlib import Path

from .fetcher import Fetcher
from .extractor import Extractor
from .cleaner import Cleaner
from .chunker import Chunker
from .fact_extractor import FactExtractor

try:
    from .embedder import Embedder
    from .indexer import Indexer
    EMBEDDING_AVAILABLE = True
except Exception as e:
    EMBEDDING_AVAILABLE = False
    logging.warning(f"Embedding/indexing not available: {str(e)}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CorpusPipeline:
    """Orchestrates the complete corpus building pipeline."""
    
    def __init__(self, 
                 min_chunk_size: int = 200,
                 max_chunk_size: int = 500,
                 overlap_percent: float = 0.15,
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 collection_name: str = "groww_corpus",
                 skip_embeddings: bool = False):
        """Initialize corpus pipeline."""
        self.fetcher = Fetcher()
        self.extractor = Extractor()
        self.cleaner = Cleaner()
        self.chunker = Chunker(min_chunk_size, max_chunk_size, overlap_percent)
        self.fact_extractor = FactExtractor()
        self.skip_embeddings = skip_embeddings
        
        if not skip_embeddings and EMBEDDING_AVAILABLE:
            try:
                self.embedder = Embedder(embedding_model)
                self.indexer = Indexer(collection_name)
                logger.info("Embedding and indexing enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize embedder/indexer: {str(e)}. Running without embeddings.")
                self.skip_embeddings = True
        else:
            self.skip_embeddings = True
            logger.info("Running without embeddings (fetch → extract → clean → chunk only)")
        
        logger.info("Corpus pipeline initialized")
    
    def run(self, rebuild_index: bool = True) -> Dict:
        """
        Run the complete pipeline: URLs → Fetch → Extract → Clean → Fact cards → (Embed → Index)
        
        Args:
            rebuild_index: Whether to clear and rebuild the index
            
        Returns:
            Complete pipeline summary
        """
        logger.info("="*60)
        logger.info("STARTING CORPUS PIPELINE")
        logger.info("="*60)
        
        # Phase 2.4: Fetcher
        logger.info("\n[2.4] Fetching URLs...")
        fetch_results = self.fetcher.fetch_all()
        self.fetcher.close()
        
        successful_fetches = [r for r in fetch_results if r.get('success')]
        logger.info(f"✓ Fetched {len(successful_fetches)}/{len(fetch_results)} URLs")
        
        # Phase 2.5: Extractor
        logger.info("\n[2.5] Extracting content...")
        extraction_results = self.extractor.extract_all(fetch_results)
        logger.info(f"✓ Extracted content from {len(extraction_results)} documents")
        
        # Phase 2.6: Cleaner
        logger.info("\n[2.6] Cleaning text...")
        cleaning_results = self.cleaner.clean_all(extraction_results)
        logger.info(f"✓ Cleaned {len(cleaning_results)} documents")
        
        # Phase 2.7: Structured fact cards + static knowledge chunks
        logger.info("\n[2.7] Building fact cards and knowledge chunks...")
        fact_chunks = self.fact_extractor.build_chunks(cleaning_results)
        static_results = [
            r for r in cleaning_results
            if (r.get('metadata') or {}).get('source_type') == 'static_knowledge'
        ]
        static_chunks = []
        for result in static_results:
            text = (result.get('cleaned_text') or '').strip()
            if not text:
                continue
            metadata = dict(result.get('metadata') or {})
            metadata.update({
                'chunk_id': 0,
                'total_chunks': 1,
                'chunk_size': len(text.split()),
                'source_url': result.get('url') or metadata.get('url'),
                'content_type': 'static_knowledge',
            })
            static_chunks.append({'text': text, 'metadata': metadata})
        chunks = fact_chunks + static_chunks
        logger.info(
            f"✓ Created {len(fact_chunks)} fact cards + {len(static_chunks)} static chunks "
            f"= {len(chunks)} total"
        )
        
        # Save chunks to disk
        chunks_saved = self._save_chunks(chunks)
        logger.info(f"✓ Saved {chunks_saved} chunks to disk")
        
        # Phase 2.8 & 2.9: Embedder & Indexer (if available)
        embedding_dim = None
        index_result = None
        stats = None
        
        if not self.skip_embeddings:
            try:
                # Phase 2.8: Embedder
                logger.info("\n[2.8] Generating embeddings...")
                chunks_with_embeddings = self.embedder.embed_all(chunks)
                embedding_dim = self.embedder.get_embedding_dimension()
                logger.info(f"✓ Generated embeddings (dimension: {embedding_dim})")
                
                # Phase 2.9: Indexer
                logger.info("\n[2.9] Building vector index...")
                if rebuild_index:
                    self.indexer.clear()
                
                index_result = self.indexer.index_all(chunks_with_embeddings)
                logger.info(f"✓ Indexed {index_result['indexed_count']} chunks")
                
                # Get final stats
                stats = self.indexer.get_stats()
            except Exception as e:
                logger.error(f"Embedding/indexing failed: {str(e)}")
                logger.info("Continuing without embeddings...")
        else:
            logger.info("\n[2.8-2.9] Skipping embeddings and indexing")
        
        # Summary
        summary = {
            'pipeline': 'corpus_pipeline',
            'with_embeddings': not self.skip_embeddings,
            'phases': {
                '2.4_fetcher': {'total': len(fetch_results), 'successful': len(successful_fetches)},
                '2.5_extractor': {'processed': len(extraction_results)},
                '2.6_cleaner': {'processed': len(cleaning_results)},
                '2.7_chunker': {
                    'total_chunks': len(chunks),
                    'fact_cards': len(fact_chunks),
                    'static_chunks': len(static_chunks),
                    'saved_to_disk': chunks_saved,
                },
            },
            'final_stats': stats
        }
        
        if not self.skip_embeddings and embedding_dim:
            summary['phases']['2.8_embedder'] = {'embedded': len(chunks), 'dimension': embedding_dim}
            summary['phases']['2.9_indexer'] = {'indexed': index_result['indexed_count']}
        
        logger.info("\n" + "="*60)
        logger.info("CORPUS PIPELINE COMPLETED")
        logger.info("="*60)
        
        return summary
    
    def _save_chunks(self, chunks: List[Dict]) -> int:
        """Save chunks to data/processed directory."""
        from ..ingestion.config import PROCESSED_DATA_DIR
        output_dir = Path(PROCESSED_DATA_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        saved_count = 0
        for chunk in chunks:
            chunk_id = chunk.get('metadata', {}).get('chunk_id', 0)
            source_url = chunk.get('metadata', {}).get('source_url', 'unknown')
            filename = self._chunk_to_filename(source_url, chunk_id)
            filepath = output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(chunk, f, indent=2, ensure_ascii=False)
            saved_count += 1
        
        return saved_count
    
    def _chunk_to_filename(self, url: str, chunk_id: int) -> str:
        """Generate filename from URL and chunk ID."""
        url = url.replace('https://', '').replace('http://', '')
        url = url.replace('/', '_')[:50]
        return f"{url}_chunk_{chunk_id}.json"
    
    def test_query(self, query: str) -> Dict:
        """
        Test the built corpus with a query.
        
        Args:
            query: Search query
            
        Returns:
            Search results
        """
        if self.skip_embeddings:
            return {'error': 'Embeddings not available, cannot test query'}
        
        logger.info(f"\nTesting query: '{query}'")
        
        # Generate embedding for query
        query_embedding = self.embedder.encode([query])[0]
        
        # Search
        results = self.indexer.search(query_embedding.tolist(), top_k=3)
        
        return {
            'query': query,
            'results_count': len(results),
            'results': results
        }


def main():
    """Main entry point."""
    pipeline = CorpusPipeline(skip_embeddings=False)  # Enable embeddings
    
    # Run pipeline
    summary = pipeline.run(rebuild_index=True)
    
    # Print summary
    print("\n" + "="*60)
    print("CORPUS PIPELINE SUMMARY")
    print("="*60)
    
    phases = summary['phases']
    print(f"\n[2.4] Fetcher:     {phases['2.4_fetcher']['successful']}/{phases['2.4_fetcher']['total']} URLs")
    print(f"[2.5] Extractor:   {phases['2.5_extractor']['processed']} documents")
    print(f"[2.6] Cleaner:     {phases['2.6_cleaner']['processed']} documents")
    print(f"[2.7] Chunker:     {phases['2.7_chunker']['total_chunks']} chunks")
    print(f"                  Saved to disk: {phases['2.7_chunker']['saved_to_disk']} chunks")
    
    if not summary['with_embeddings']:
        print(f"\n[2.8-2.9] Embedding/Indexing: SKIPPED (SSL issues)")
        print(f"          Chunks saved to data/processed/ for later use")
    else:
        print(f"[2.8] Embedder:    {phases['2.8_embedder']['embedded']} chunks (dim: {phases['2.8_embedder']['dimension']})")
        print(f"[2.9] Indexer:     {phases['2.9_indexer']['indexed']} chunks indexed")
        
        stats = summary['final_stats']
        print(f"\nFinal Index Stats:")
        print(f"  Collection: {stats['collection_name']}")
        print(f"  Total Chunks: {stats['total_chunks']}")
        print(f"  Location: {stats['persist_directory']}")
    
    print("="*60)


if __name__ == "__main__":
    main()
