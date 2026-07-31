"""
Phase 4.3: Citation Management
Manages source selection and citation formatting for responses.
"""

import logging
from typing import Dict, List, Optional
import re
from datetime import datetime
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CitationManager:
    """Manages source selection and citation formatting."""
    
    # Official AMC document patterns
    OFFICIAL_DOCUMENT_PATTERNS = [
        r'factsheet',
        r'scheme.*document',
        r'kim',
        r'sid',
        r'amc.*official',
        r'registrar',
        r'official.*website'
    ]
    
    def __init__(self):
        """Initialize citation manager."""
        self.official_regex = re.compile('|'.join(self.OFFICIAL_DOCUMENT_PATTERNS), re.IGNORECASE)
        logger.info("Citation manager initialized")
    
    def select_source(self, chunks: List[Dict]) -> Dict:
        """
        Select the most relevant source from retrieved chunks.
        
        Args:
            chunks: List of retrieved chunks with metadata
            
        Returns:
            Selected source with metadata
        """
        if not chunks:
            return {
                'source_url': None,
                'confidence': 0.0,
                'reason': 'No chunks available'
            }
        
        # Extract unique sources with their metadata
        sources = self._extract_sources(chunks)
        
        if not sources:
            return {
                'source_url': None,
                'confidence': 0.0,
                'reason': 'No sources found in chunks'
            }
        
        # Score sources based on relevance and recency
        scored_sources = self._score_sources(sources, chunks)
        
        # Sort by score (highest first)
        scored_sources.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top source
        selected = scored_sources[0]
        
        return {
            'source_url': selected['url'],
            'confidence': selected['score'],
            'reason': selected['reason'],
            'is_official': selected['is_official'],
            'last_updated': selected.get('last_updated')
        }
    
    def _extract_sources(self, chunks: List[Dict]) -> List[Dict]:
        """
        Extract unique sources from chunks.
        
        Args:
            chunks: List of chunks
            
        Returns:
            List of unique sources with metadata
        """
        sources = {}
        
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            source_url = metadata.get('source_url')
            
            if not source_url:
                continue
            
            if source_url not in sources:
                sources[source_url] = {
                    'url': source_url,
                    'chunk_count': 0,
                    'total_score': 0.0,
                    'last_updated': metadata.get('last_updated'),
                    'is_official': False
                }
            
            sources[source_url]['chunk_count'] += 1
            sources[source_url]['total_score'] += chunk.get('score', 0)
        
        return list(sources.values())
    
    def _score_sources(self, sources: List[Dict], chunks: List[Dict]) -> List[Dict]:
        """
        Score sources based on relevance and recency.
        
        Args:
            sources: List of sources
            chunks: Original chunks for context
            
        Returns:
            List of sources with scores
        """
        for source in sources:
            score = 0.0
            reasons = []
            
            # Factor 1: Average relevance score (40%)
            if source['chunk_count'] > 0:
                avg_score = source['total_score'] / source['chunk_count']
                score += avg_score * 0.4
                reasons.append(f"Avg relevance: {avg_score:.3f}")
            
            # Factor 2: Chunk count (more chunks = more relevant) (20%)
            chunk_factor = min(source['chunk_count'] / 5.0, 1.0)  # Cap at 5 chunks
            score += chunk_factor * 0.2
            reasons.append(f"Chunk count: {source['chunk_count']}")
            
            # Factor 3: Official document preference (30%)
            if self._is_official_document(source['url'], chunks):
                source['is_official'] = True
                score += 0.3
                reasons.append("Official AMC document")
            
            # Factor 4: Recency (10%)
            if source.get('last_updated'):
                recency_score = self._calculate_recency_score(source['last_updated'])
                score += recency_score * 0.1
                reasons.append(f"Recent: {source['last_updated']}")
            
            source['score'] = score
            source['reason'] = ', '.join(reasons)
        
        return sources
    
    def _is_official_document(self, url: str, chunks: List[Dict]) -> bool:
        """
        Check if source is an official AMC document.
        
        Args:
            url: Source URL
            chunks: Chunks for context
            
        Returns:
            True if official document
        """
        # Check URL for official patterns
        if self.official_regex.search(url):
            return True
        
        # Check chunks for official document references
        for chunk in chunks:
            if chunk.get('metadata', {}).get('source_url') == url:
                text = chunk.get('text', '').lower()
                if self.official_regex.search(text):
                    return True
        
        return False
    
    def _calculate_recency_score(self, date_str: str) -> float:
        """
        Calculate recency score based on date.
        
        Args:
            date_str: Date string (YYYY-MM-DD format)
            
        Returns:
            Recency score (0.0 to 1.0)
        """
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            days_old = (datetime.now() - date).days
            
            # Score decreases with age (0-30 days = 1.0, 30-90 = 0.5, 90+ = 0.0)
            if days_old <= 30:
                return 1.0
            elif days_old <= 90:
                return 0.5
            else:
                return 0.0
        except:
            return 0.0
    
    def format_citation(self, source_url: str, last_updated: Optional[str] = None) -> str:
        """
        Format citation for display.
        
        Args:
            source_url: Source URL
            last_updated: Last updated date
            
        Returns:
            Formatted citation
        """
        # Format URL for display (shorten if too long)
        formatted_url = self._format_url(source_url)
        
        citation = f"Source: {formatted_url}"
        
        if last_updated:
            citation += f"\nLast updated: {last_updated}"
        
        return citation
    
    def _format_url(self, url: str, max_length: int = 60) -> str:
        """
        Format URL for display (shorten if too long).
        
        Args:
            url: Source URL
            max_length: Maximum length for display
            
        Returns:
            Formatted URL
        """
        if len(url) <= max_length:
            return url
        
        # Truncate URL and add ellipsis
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path
        
        if len(domain) + len(path) > max_length:
            # Show domain + truncated path
            available = max_length - len(domain) - 4
            if available > 10:
                path = path[:available] + '...'
            else:
                path = '...'
        
        return f"{domain}{path}"
    
    def validate_link(self, url: str) -> Dict:
        """
        Validate source link (basic validation).
        
        Args:
            url: Source URL
            
        Returns:
            Validation result
        """
        result = {
            'valid': True,
            'errors': []
        }
        
        # Check if URL is present
        if not url:
            result['valid'] = False
            result['errors'].append('URL is missing')
            return result
        
        # Check URL format
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                result['valid'] = False
                result['errors'].append('Invalid URL format')
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f'URL parsing error: {str(e)}')
        
        return result


def main():
    """Main entry point for testing citation manager."""
    manager = CitationManager()
    
    # Test chunks
    test_chunks = [
        {
            'text': 'The HDFC Mid Cap Fund has an expense ratio of 1.85%',
            'metadata': {
                'source_url': 'https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth',
                'last_updated': '2024-01-15'
            },
            'score': 0.85
        },
        {
            'text': 'Official factsheet available for download',
            'metadata': {
                'source_url': 'https://hdfcfund.com/factsheet/hdfc-mid-cap',
                'last_updated': '2024-02-01'
            },
            'score': 0.75
        },
        {
            'text': 'Minimum SIP amount is ₹500',
            'metadata': {
                'source_url': 'https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth',
                'last_updated': '2024-01-15'
            },
            'score': 0.80
        }
    ]
    
    print("="*60)
    print("CITATION MANAGER TEST")
    print("="*60)
    
    # Test source selection
    print("\nSource Selection:")
    print("-" * 60)
    selected = manager.select_source(test_chunks)
    print(f"Selected URL: {selected['source_url']}")
    print(f"Confidence: {selected['confidence']:.3f}")
    print(f"Reason: {selected['reason']}")
    print(f"Is Official: {selected['is_official']}")
    print(f"Last Updated: {selected['last_updated']}")
    
    # Test citation formatting
    print("\nCitation Formatting:")
    print("-" * 60)
    citation = manager.format_citation(selected['source_url'], selected['last_updated'])
    print(citation)
    
    # Test link validation
    print("\nLink Validation:")
    print("-" * 60)
    validation = manager.validate_link(selected['source_url'])
    print(f"Valid: {validation['valid']}")
    if validation['errors']:
        for error in validation['errors']:
            print(f"  Error: {error}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
