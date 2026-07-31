"""
Phase 3.1-3.2: Retrieval & Context Assembly
Query processing, similarity search, and context assembly for RAG pipeline.
"""

from .query_processor import QueryProcessor
from .similarity_search import SimilaritySearch
from .context_assembly import ContextAssembly
from .retrieval_pipeline import RetrievalPipeline, main

__all__ = [
    'QueryProcessor',
    'SimilaritySearch',
    'ContextAssembly',
    'RetrievalPipeline',
    'main'
]
