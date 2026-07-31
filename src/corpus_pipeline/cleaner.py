"""
Phase 2.6: Cleaner
Cleans and normalizes text, removing HTML tags and special characters.
Consumes output from Extractor (main_text).
"""

import re
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Cleaner:
    """Cleans and normalizes text."""
    
    # Financial patterns to preserve (including Indian numbering like ₹1,00,858.31)
    FINANCIAL_PATTERNS = {
        'percentage': r'\d+\.?\d*%',
        'currency': r'(?:Rs\.?|₹|\$)\s*\d+(?:[,\.]\d+)*\s*(?:Cr|Lakh|Lakhs)?',
        'ratio': r'\d+\.?\d*:\d+\.?\d*',
        'date': r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}\s+[A-Za-z]+\s+\'?\d{2,4}',
        'number': r'\d+(?:[,\.]\d+)+',
    }
    
    def __init__(self):
        """Initialize cleaner."""
        self.preserved_patterns = []
    
    def clean_all(self, extraction_results: List[Dict]) -> List[Dict]:
        """
        Clean all extraction results.
        
        Args:
            extraction_results: List of extraction results from Extractor
            
        Returns:
            List of cleaning results with cleaned text
        """
        results = []
        
        for extraction_result in extraction_results:
            if not extraction_result.get('success'):
                logger.warning(f"Skipping failed extraction: {extraction_result.get('url')}")
                continue
            
            result = self.clean_single(extraction_result)
            results.append(result)
        
        logger.info(f"Cleaned {len(results)} documents")
        return results
    
    def clean_single(self, extraction_result: Dict) -> Dict:
        """
        Clean a single extraction result.
        
        Args:
            extraction_result: Extraction result with main_text
            
        Returns:
            Cleaning result with cleaned_text
        """
        main_text = extraction_result.get('main_text', '')
        url = extraction_result.get('url')
        
        if not main_text:
            return {
                'url': url,
                'success': False,
                'error': 'No text to clean',
                'cleaned_text': '',
                'metadata': extraction_result.get('metadata', {})
            }
        
        cleaned_text = self.clean(main_text)
        
        return {
            'url': url,
            'success': True,
            'error': None,
            'cleaned_text': cleaned_text,
            'word_count': len(cleaned_text.split()) if cleaned_text else 0,
            'tables': extraction_result.get('tables', []),
            'lists': extraction_result.get('lists', []),
            'metadata': extraction_result.get('metadata', {})
        }
    
    def clean(self, text: str) -> str:
        """Clean text by removing unwanted characters and normalizing."""
        if not text:
            return ""
        
        # Normalize currency symbols to ASCII-safe form for reliable indexing/LLM use
        text = text.replace('₹', 'Rs. ')
        text = text.replace('�', '')
        
        # Preserve financial patterns
        text = self._preserve_patterns(text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'&[a-z]+;', ' ', text)
        text = re.sub(r'&#[0-9]+;', ' ', text)
        
        # Remove special characters but keep common punctuation and currency markers
        text = re.sub(r'[^a-zA-Z0-9\s.,:;?!()\[\]{}\-/@_$%\'\"]', ' ', text)
        text = re.sub(r'([.,:;?!]){2,}', r'\1', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Restore patterns
        text = self._restore_patterns(text)
        
        return text
    
    def _preserve_patterns(self, text: str) -> str:
        """Replace financial patterns with placeholders."""
        self.preserved_patterns = []
        idx = 0
        
        for pattern_name, pattern in self.FINANCIAL_PATTERNS.items():
            for match in re.finditer(pattern, text):
                placeholder = f"__PRESERVED_{idx}__"
                self.preserved_patterns.append({
                    'placeholder': placeholder,
                    'original': match.group()
                })
                text = text.replace(match.group(), placeholder, 1)
                idx += 1
        
        return text
    
    def _restore_patterns(self, text: str) -> str:
        """Restore preserved financial patterns."""
        for preserved in reversed(self.preserved_patterns):
            text = text.replace(preserved['placeholder'], preserved['original'])
        self.preserved_patterns = []
        return text
