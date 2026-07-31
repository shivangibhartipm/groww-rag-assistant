"""
Phase 2.1: Text Preprocessing - Cleaning Pipeline
Cleans text by removing HTML tags, special characters, and normalizing whitespace.
"""

import re
import logging
from typing import str as StringType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextCleaner:
    """Cleans and normalizes text for processing."""
    
    # Financial terms and symbols to preserve
    FINANCIAL_PATTERNS = {
        'percentage': r'\d+\.?\d*%',
        'currency': r'₹\s*\d+[,\.]?\d*|\$\s*\d+[,\.]?\d*',
        'ratio': r'\d+\.?\d*:\d+\.?\d*',
        'date': r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}',
        'time': r'\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?',
        'number': r'\d+[,\.]?\d*',
        'fund_code': r'[A-Z]{2,4}\d{3,4}',
    }
    
    def __init__(self):
        """Initialize text cleaner."""
        self.preserved_patterns = []
    
    def clean(self, text: str) -> str:
        """
        Clean text by removing unwanted characters and normalizing.
        
        Args:
            text: Raw text string
            
        Returns:
            Cleaned text string
        """
        if not text:
            return ""
        
        # Step 1: Preserve financial patterns
        text = self._preserve_financial_patterns(text)
        
        # Step 2: Remove HTML tags
        text = self._remove_html_tags(text)
        
        # Step 3: Remove special characters (excluding preserved)
        text = self._remove_special_characters(text)
        
        # Step 4: Normalize whitespace
        text = self._normalize_whitespace(text)
        
        # Step 5: Restore preserved patterns
        text = self._restore_financial_patterns(text)
        
        return text
    
    def _preserve_financial_patterns(self, text: str) -> str:
        """
        Replace financial patterns with placeholders.
        
        Args:
            text: Input text
            
        Returns:
            Text with patterns replaced by placeholders
        """
        self.preserved_patterns = []
        placeholder_index = 0
        
        for pattern_name, pattern in self.FINANCIAL_PATTERNS.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                placeholder = f"__PRESERVED_{placeholder_index}__"
                self.preserved_patterns.append({
                    'placeholder': placeholder,
                    'original': match.group(),
                    'pattern_name': pattern_name
                })
                text = text.replace(match.group(), placeholder, 1)
                placeholder_index += 1
        
        return text
    
    def _restore_financial_patterns(self, text: str) -> str:
        """
        Restore preserved financial patterns.
        
        Args:
            text: Text with placeholders
            
        Returns:
            Text with original patterns restored
        """
        for preserved in reversed(self.preserved_patterns):
            text = text.replace(preserved['placeholder'], preserved['original'])
        
        self.preserved_patterns = []
        return text
    
    def _remove_html_tags(self, text: str) -> str:
        """
        Remove HTML tags from text.
        
        Args:
            text: Text with HTML tags
            
        Returns:
            Text without HTML tags
        """
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Remove HTML entities
        text = re.sub(r'&[a-z]+;', ' ', text)
        text = re.sub(r'&#[0-9]+;', ' ', text)
        
        return text
    
    def _remove_special_characters(self, text: str) -> str:
        """
        Remove special characters while preserving basic punctuation.
        
        Args:
            text: Input text
            
        Returns:
            Text with special characters removed
        """
        # Keep alphanumeric, basic punctuation, and spaces
        # Preserve: . , : ; ? ! ( ) [ ] { } - / @
        text = re.sub(r'[^a-zA-Z0-9\s.,:;?!()\[\]{}\-/@_]', ' ', text)
        
        # Remove multiple punctuation marks
        text = re.sub(r'([.,:;?!]){2,}', r'\1', text)
        
        return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace in text.
        
        Args:
            text: Input text
            
        Returns:
            Text with normalized whitespace
        """
        # Replace all whitespace (tabs, newlines, etc.) with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Trim leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def clean_batch(self, texts: list) -> list:
        """
        Clean a batch of texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            List of cleaned text strings
        """
        return [self.clean(text) for text in texts]
