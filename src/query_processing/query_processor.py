"""
Phase 4.1: Query Processing
Processes and classifies user queries before retrieval.
"""

import logging
from typing import Dict

from .query_classifier import QueryClassifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryProcessor:
    """Processes and classifies user queries."""
    
    def __init__(self):
        """Initialize query processor."""
        self.classifier = QueryClassifier()
        logger.info("Query processor initialized")
    
    def process(self, query: str) -> Dict:
        """
        Process a user query.
        
        Args:
            query: User query text
            
        Returns:
            Processed query with classification
        """
        if not query or not query.strip():
            return {
                'query': query,
                'processed': False,
                'error': 'Empty query'
            }
        
        # Clean query
        cleaned_query = self._clean_query(query)
        
        # Classify intent
        classification = self.classifier.classify(cleaned_query)
        
        # Determine if query should be processed
        should_process = classification['intent'] == 'factual'
        
        result = {
            'query': query,
            'cleaned_query': cleaned_query,
            'intent': classification['intent'],
            'confidence': classification['confidence'],
            'reason': classification['reason'],
            'should_process': should_process,
            'error': None
        }
        
        # Add standard response if not factual
        if not should_process:
            if classification['intent'] == 'advisory':
                result['standard_response'] = self.classifier.get_advisory_response()
            elif classification['intent'] == 'out_of_scope':
                result['standard_response'] = self.classifier.get_out_of_scope_response()
        
        return result
    
    def _clean_query(self, query: str) -> str:
        """Clean and normalize query text."""
        # Remove extra whitespace
        query = ' '.join(query.split())
        # Remove special characters but keep basic punctuation
        import re
        query = re.sub(r'[^\w\s.,?!]', '', query)
        return query.strip()


def main():
    """Main entry point for testing query processor."""
    processor = QueryProcessor()
    
    # Test queries
    test_queries = [
        "What is the expense ratio?",  # Factual
        "Should I invest in HDFC Mid Cap?",  # Advisory
        "Which is the best mutual fund?",  # Advisory
        "What is the minimum SIP amount?",  # Factual
        "What are the latest stock prices?",  # Out of scope
        "Show me the riskometer details",  # Factual
        "Is this a good investment?",  # Advisory
        "How do I download the factsheet?",  # Factual
        "What's the weather today?",  # Out of scope
    ]
    
    print("="*60)
    print("QUERY PROCESSOR TEST")
    print("="*60)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        
        result = processor.process(query)
        
        print(f"Intent: {result['intent']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Should process: {result['should_process']}")
        print(f"Reason: {result['reason']}")
        
        if result.get('standard_response'):
            print(f"Standard response: {result['standard_response']}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
