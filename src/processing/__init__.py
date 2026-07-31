"""
Phase 2: Document Processing & Indexing
Processing module for text cleaning, chunking, metadata enrichment, and embeddings.
"""

from .text_cleaner import TextCleaner
from .chunker import DocumentChunker
from .metadata_enricher import MetadataEnricher
from .pipeline import ProcessingPipeline, main
from .embedding_generator import EmbeddingGenerator
from .vector_database import VectorDatabase
from .knowledge_base import KnowledgeBase
from .embedding_pipeline import EmbeddingPipeline

__all__ = [
    'TextCleaner',
    'DocumentChunker',
    'MetadataEnricher',
    'ProcessingPipeline',
    'main',
    'EmbeddingGenerator',
    'VectorDatabase',
    'KnowledgeBase',
    'EmbeddingPipeline'
]
