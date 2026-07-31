"""
Phase 1.2: Document Storage
Handles storage of raw HTML/JSON documents with metadata.
"""

import json
import os
from pathlib import Path
from typing import Dict, List
import logging

from .config import RAW_DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentStorage:
    """Handles storage of scraped documents with metadata."""
    
    def __init__(self, storage_dir: str = RAW_DATA_DIR):
        """
        Initialize document storage.
        
        Args:
            storage_dir: Directory to store raw documents
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Document storage initialized at: {self.storage_dir}")
    
    def save_document(self, document: Dict) -> str:
        """
        Save a single document as JSON file.
        
        Args:
            document: Dictionary containing url, content, metadata
            
        Returns:
            Path to saved file
        """
        # Generate filename from URL
        url = document.get('url', '')
        filename = self._url_to_filename(url)
        filepath = self.storage_dir / filename
        
        # Save as JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(document, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved document: {filepath}")
        return str(filepath)
    
    def save_documents(self, documents: List[Dict]) -> List[str]:
        """
        Save multiple documents.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            List of saved file paths
        """
        saved_paths = []
        
        for doc in documents:
            try:
                path = self.save_document(doc)
                saved_paths.append(path)
            except Exception as e:
                logger.error(f"Error saving document {doc.get('url')}: {str(e)}")
        
        logger.info(f"Saved {len(saved_paths)}/{len(documents)} documents")
        return saved_paths
    
    def load_document(self, filename: str) -> Dict:
        """
        Load a single document from storage.
        
        Args:
            filename: Name of the file to load
            
        Returns:
            Document dictionary
        """
        filepath = self.storage_dir / filename
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_all_documents(self) -> List[Dict]:
        """
        Load all documents from storage.
        
        Returns:
            List of document dictionaries
        """
        documents = []
        
        for filepath in self.storage_dir.glob('*.json'):
            try:
                doc = self.load_document(filepath.name)
                documents.append(doc)
            except Exception as e:
                logger.error(f"Error loading {filepath}: {str(e)}")
        
        logger.info(f"Loaded {len(documents)} documents from storage")
        return documents
    
    def get_document_metadata(self) -> List[Dict]:
        """
        Get metadata for all stored documents without loading full content.
        
        Returns:
            List of metadata dictionaries
        """
        metadata_list = []
        
        for filepath in self.storage_dir.glob('*.json'):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    doc = json.load(f)
                    # Extract only metadata, exclude large content
                    metadata = {
                        'url': doc.get('url'),
                        'scheme_name': doc.get('scheme_name'),
                        'scheme_type': doc.get('scheme_type'),
                        'plan': doc.get('plan'),
                        'source_type': doc.get('source_type'),
                        'status_code': doc.get('status_code'),
                        'error': doc.get('error'),
                        'timestamp': doc.get('timestamp'),
                        'content_type': doc.get('content_type'),
                        'content_length': len(doc.get('content', '')) if doc.get('content') else 0
                    }
                    metadata_list.append(metadata)
            except Exception as e:
                logger.error(f"Error reading metadata from {filepath}: {str(e)}")
        
        return metadata_list
    
    def _url_to_filename(self, url: str) -> str:
        """
        Convert URL to safe filename.
        
        Args:
            url: URL string
            
        Returns:
            Safe filename string
        """
        # Remove protocol
        url = url.replace('https://', '').replace('http://', '')
        
        # Replace special characters with underscores
        safe_chars = []
        for char in url:
            if char.isalnum() or char in ['-', '_', '.', '/']:
                if char == '/':
                    safe_chars.append('_')
                else:
                    safe_chars.append(char)
            else:
                safe_chars.append('_')
        
        filename = ''.join(safe_chars)
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        return filename
    
    def clear_storage(self):
        """Clear all documents from storage."""
        for filepath in self.storage_dir.glob('*.json'):
            filepath.unlink()
        logger.info(f"Cleared all documents from {self.storage_dir}")
