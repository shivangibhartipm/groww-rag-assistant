"""
Phase 4.2: Response Formatting
Formats responses with structure, source citation, and footer.
"""

import logging
from typing import Dict, Optional
import re
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Formats responses with structure, source citation, and footer."""
    
    # Performance-related query patterns
    PERFORMANCE_PATTERNS = [
        r'performance',
        r'return',
        r'profit',
        r'gain',
        r'growth',
        r'compare.*performance',
        r'best performing',
        r'worst performing',
        r'past.*year',
        r'1 year return',
        r'3 year return',
        r'5 year return',
        r'annualized return',
        r'cagr',
        r'nav growth',
        r'fund performance'
    ]
    
    def __init__(self):
        """Initialize response formatter."""
        self.performance_regex = re.compile('|'.join(self.PERFORMANCE_PATTERNS), re.IGNORECASE)
        logger.info("Response formatter initialized")
    
    def format_response(self, 
                       answer: str, 
                       source_url: str, 
                       last_updated: Optional[str] = None,
                       query: Optional[str] = None) -> Dict:
        """
        Format response with structure, source, and footer.
        
        Args:
            answer: Generated answer text
            source_url: Source URL
            last_updated: Last updated date (YYYY-MM-DD format)
            query: Original query (for performance detection)
            
        Returns:
            Formatted response with validation results
        """
        # Check if this is a performance query
        is_performance = False
        if query and self.performance_regex.search(query):
            is_performance = True
            logger.info("Performance query detected, returning factsheet link")
            answer = "For performance information, please refer to the official factsheet."
        
        # Enforce sentence limit
        limited_answer = self._enforce_sentence_limit(answer, max_sentences=3)
        
        # Validate sentence count
        sentence_count = self._count_sentences(limited_answer)
        sentence_valid = sentence_count <= 3
        
        # Build formatted response
        formatted_parts = []
        formatted_parts.append(limited_answer)
        formatted_parts.append("")  # Empty line
        formatted_parts.append(f"Source: {source_url}")
        
        # Add footer with last updated date
        if last_updated:
            formatted_parts.append("")
            formatted_parts.append(f"Last updated from sources: {last_updated}")
        else:
            # Use current date if not provided
            current_date = datetime.now().strftime("%Y-%m-%d")
            formatted_parts.append("")
            formatted_parts.append(f"Last updated from sources: {current_date}")
        
        formatted_response = "\n".join(formatted_parts)
        
        # Validate source presence
        source_present = bool(source_url)
        
        return {
            'formatted_response': formatted_response,
            'answer': limited_answer,
            'source_url': source_url,
            'last_updated': last_updated,
            'sentence_count': sentence_count,
            'sentence_valid': sentence_valid,
            'source_present': source_present,
            'is_performance_query': is_performance
        }
    
    def _enforce_sentence_limit(self, text: str, max_sentences: int = 3) -> str:
        """
        Enforce maximum sentence limit.
        
        Args:
            text: Input text
            max_sentences: Maximum number of sentences
            
        Returns:
            Text with sentence limit enforced
        """
        # Split by sentence delimiters
        sentences = re.split(r'[.!?]+', text)
        
        # Filter empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Take only first max_sentences
        limited_sentences = sentences[:max_sentences]
        
        # Reconstruct
        result = '. '.join(limited_sentences)
        if result and not result.endswith('.'):
            result += '.'
        
        return result
    
    def _count_sentences(self, text: str) -> int:
        """
        Count sentences in text.
        
        Args:
            text: Input text
            
        Returns:
            Number of sentences
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return len(sentences)
    
    def validate_response(self, formatted_response: Dict) -> Dict:
        """
        Validate formatted response against constraints.
        
        Args:
            formatted_response: Formatted response dictionary
            
        Returns:
            Validation results
        """
        validation = {
            'valid': True,
            'errors': []
        }
        
        # Check sentence count
        if not formatted_response['sentence_valid']:
            validation['valid'] = False
            validation['errors'].append(
                f"Sentence count ({formatted_response['sentence_count']}) exceeds limit of 3"
            )
        
        # Check source presence
        if not formatted_response['source_present']:
            validation['valid'] = False
            validation['errors'].append("Source URL is missing")
        
        return validation
    
    def format_performance_response(self, source_url: str) -> str:
        """
        Format response for performance queries (direct factsheet link).
        
        Args:
            source_url: Source URL (factsheet link)
            
        Returns:
            Formatted performance response
        """
        formatted = f"For performance information, please refer to the official factsheet.\n\nSource: {source_url}\n\nLast updated from sources: {datetime.now().strftime('%Y-%m-%d')}"
        return formatted


def main():
    """Main entry point for testing response formatter."""
    formatter = ResponseFormatter()
    
    # Test cases
    test_cases = [
        {
            'answer': 'The HDFC Mid Cap Fund has an expense ratio of 1.85%. The minimum SIP amount is ₹500. The fund category is mid-cap.',
            'source_url': 'https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth',
            'query': 'What is the expense ratio?'
        },
        {
            'answer': 'This fund has given 15% returns in the last year. It has outperformed its benchmark. The 3-year return is 12%.',
            'source_url': 'https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth',
            'query': 'What is the performance of this fund?'
        },
        {
            'answer': 'The exit load is 1% if redeemed within 1 year. There is no exit load after 1 year.',
            'source_url': 'https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth',
            'query': 'What is the exit load?'
        }
    ]
    
    print("="*60)
    print("RESPONSE FORMATTER TEST")
    print("="*60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Query: {test['query']}")
        print(f"Answer: {test['answer']}")
        print("-" * 60)
        
        result = formatter.format_response(
            test['answer'],
            test['source_url'],
            query=test['query']
        )
        
        print(f"Formatted Response:")
        print(result['formatted_response'])
        print(f"\nValidation:")
        print(f"  Sentence count: {result['sentence_count']} (valid: {result['sentence_valid']})")
        print(f"  Source present: {result['source_present']}")
        print(f"  Performance query: {result['is_performance_query']}")
        
        validation = formatter.validate_response(result)
        print(f"  Overall valid: {validation['valid']}")
        if validation['errors']:
            for error in validation['errors']:
                print(f"    Error: {error}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
