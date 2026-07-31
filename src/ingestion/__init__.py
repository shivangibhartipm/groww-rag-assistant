"""
Phase 1: Data Collection & Corpus Preparation
Ingestion module for web scraping and data collection.
"""

from .config import AMC_NAME, OFFICIAL_SOURCES, SOURCE_URLS, DATA_DIR, RAW_DATA_DIR
from .web_scraper import WebScraper
from .document_storage import DocumentStorage
from .content_extractor import ContentExtractor
from .quality_control import QualityControl
from .pipeline import IngestionPipeline, main

__all__ = [
    'AMC_NAME',
    'OFFICIAL_SOURCES', 
    'SOURCE_URLS',
    'DATA_DIR',
    'RAW_DATA_DIR',
    'WebScraper',
    'DocumentStorage',
    'ContentExtractor',
    'QualityControl',
    'IngestionPipeline',
    'main'
]
