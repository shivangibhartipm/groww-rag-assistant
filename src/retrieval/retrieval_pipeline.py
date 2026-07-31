"""
Phase 3.1: Retrieval Pipeline
Orchestrates query processing and similarity search for RAG retrieval.
"""

import logging
from typing import Dict

from .query_processor import QueryProcessor
from .similarity_search import SimilaritySearch
from .context_assembly import ContextAssembly

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RetrievalPipeline:
    """Orchestrates the retrieval component of RAG pipeline."""
    
    def __init__(self, 
                 collection_name: str = "groww_corpus",
                 persist_directory: str = None,
                 top_k: int = 5,
                 threshold: float = 0.30,
                 max_context_tokens: int = 2000):
        """
        Initialize retrieval pipeline.
        
        Args:
            collection_name: Name of the vector collection
            persist_directory: Directory for vector database
            top_k: Number of results to retrieve
            threshold: Relevance threshold
            max_context_tokens: Maximum tokens for context window
        """
        self.query_processor = QueryProcessor()
        self.similarity_search = SimilaritySearch(collection_name, persist_directory)
        self.context_assembly = ContextAssembly(max_tokens=max_context_tokens)
        
        # Set search parameters
        self.similarity_search.set_search_parameters(top_k, threshold)
        
        logger.info("Retrieval pipeline initialized")
    
    def retrieve(self, query: str, top_k: int = None, threshold: float = None) -> Dict:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: User query text
            top_k: Number of results to return (overrides default)
            threshold: Relevance threshold (overrides default)
            
        Returns:
            Retrieval results with ranked chunks and sources
        """
        logger.info(f"Processing query: {query[:50]}...")
        
        # Step 1: Process query and generate embedding
        query_result = self.query_processor.process_query(query)
        
        if query_result.get('error'):
            return {
                'query': query,
                'error': query_result['error'],
                'results': [],
                'count': 0
            }
        
        # Step 2: Perform similarity search
        search_results = self.similarity_search.search(
            query_result['embedding'],
            top_k=top_k,
            threshold=threshold
        )
        
        # Step 3: Format results
        retrieval_result = {
            'query': query,
            'cleaned_query': query_result['cleaned_query'],
            'results': search_results['results'],
            'count': search_results['count'],
            'sources': search_results['sources'],
            'embedding_dimension': query_result['embedding_dimension'],
            'threshold': search_results['threshold'],
            'top_k': search_results['top_k']
        }
        
        logger.info(f"Retrieved {retrieval_result['count']} relevant chunks")
        return retrieval_result
    
    def get_context(self, query: str, top_k: int = 3, preserve_sources: bool = True) -> Dict:
        """
        Get assembled context from retrieved chunks using context assembly.
        
        Args:
            query: User query text
            top_k: Number of chunks to include in context
            preserve_sources: Whether to include source information
            
        Returns:
            Assembled context with metadata
        """
        retrieval_result = self.retrieve(query, top_k=top_k)
        
        if retrieval_result['count'] == 0:
            return {
                'context': '',
                'chunks_used': 0,
                'total_tokens': 0,
                'sources': [],
                'error': 'No relevant chunks found'
            }
        
        # Use context assembly to build optimized context
        context_result = self.context_assembly.assemble_context(
            retrieval_result['results'],
            preserve_sources=preserve_sources
        )
        
        return context_result


def main():
    """Main entry point for testing retrieval pipeline."""
    pipeline = RetrievalPipeline()
    
    # Test queries
    test_queries = [
        "What is the expense ratio?",
        "What is the minimum investment amount?",
        "What is the fund category?"
    ]
    
    print("="*60)
    print("RETRIEVAL PIPELINE TEST")
    print("="*60)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        
        # Test retrieval
        result = pipeline.retrieve(query, top_k=3)
        
        print(f"Results found: {result['count']}")
        print(f"Sources: {result['sources']}")
        
        if result['results']:
            print("\nTop result:")
            top = result['results'][0]
            print(f"  Score: {top.get('score', 'N/A')}")
            print(f"  Source: {top.get('metadata', {}).get('source_url', 'N/A')}")
            print(f"  Text: {top.get('text', '')[:200]}...")
        
        # Test context assembly
        print("\nContext Assembly:")
        context_result = pipeline.get_context(query, top_k=3)
        print(f"  Chunks used: {context_result.get('chunks_used', 0)}")
        print(f"  Total tokens: {context_result.get('total_tokens', 0)}")
        print(f"  Context length: {len(context_result.get('context', ''))} chars")
        if context_result.get('context'):
            print(f"  Context preview: {context_result['context'][:300]}...")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
