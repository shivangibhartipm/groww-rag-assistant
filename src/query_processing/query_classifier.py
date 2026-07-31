"""
Phase 4.1: Query Classification
Classifies user queries by intent: Factual vs. Advisory vs. Out-of-scope.
"""

import logging
from typing import Dict, List
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryClassifier:
    """Classifies user queries by intent."""
    
    # Factual query patterns
    FACTUAL_PATTERNS = [
        r'expense ratio',
        r'exit load',
        r'minimum (sip|investment)',
        r'lock[- ]in period',
        r'riskometer',
        r'benchmark',
        r'document download',
        r'factsheet',
        r'nav',
        r'aum',
        r'fund manager',
        r'launch date',
        r'scheme category',
        r'rating',
        r'portfolio',
        r'holding',
        r'allocation',
        r'sector',
        r'asset allocation',
        r'what is',
        r'how much',
        r'how many',
        r'list',
        r'show',
        r'details'
    ]
    
    # Advisory query patterns
    ADVISORY_PATTERNS = [
        r'should i invest',
        r'which fund (is )?better',
        r'which fund (should )?i (buy|invest)',
        r'recommend',
        r'advice',
        r'suggest',
        r'best fund',
        r'top fund',
        r'performance comparison',
        r'compare',
        r'good (investment|fund)',
        r'bad (investment|fund)',
        r'worth investing',
        r'will it (grow|perform)',
        r'future (return|performance)',
        r'expected return',
        r'profit',
        r'loss',
        r'risk.*return',
        r'high return'
    ]
    
    # Out-of-scope patterns
    OUT_OF_SCOPE_PATTERNS = [
        r'stock',
        r'equity share',
        r'direct stock',
        r'crypto',
        r'bitcoin',
        r'real estate',
        r'gold',
        r'fd',
        r'fixed deposit',
        r'ppf',
        r'epf',
        r'insurance',
        r'loan',
        r'credit card',
        r'bank account',
        r'trading',
        r'demat account',
        r'ipo',
        r'weather',
        r'news',
        r'politics',
        r'sports',
        r'entertainment'
    ]
    
    def __init__(self):
        """Initialize query classifier."""
        self.factual_regex = re.compile('|'.join(self.FACTUAL_PATTERNS), re.IGNORECASE)
        self.advisory_regex = re.compile('|'.join(self.ADVISORY_PATTERNS), re.IGNORECASE)
        self.out_of_scope_regex = re.compile('|'.join(self.OUT_OF_SCOPE_PATTERNS), re.IGNORECASE)
        logger.info("Query classifier initialized")
    
    def classify(self, query: str) -> Dict:
        """
        Classify query by intent.
        
        Args:
            query: User query text
            
        Returns:
            Classification result with intent and confidence
        """
        query_lower = query.lower()
        
        # Check for out-of-scope first
        if self.out_of_scope_regex.search(query):
            return {
                'query': query,
                'intent': 'out_of_scope',
                'confidence': 0.9,
                'reason': 'Query topic is outside mutual fund domain'
            }
        
        # Check for advisory patterns
        if self.advisory_regex.search(query):
            return {
                'query': query,
                'intent': 'advisory',
                'confidence': 0.85,
                'reason': 'Query asks for investment advice or recommendations'
            }
        
        # Check for factual patterns
        if self.factual_regex.search(query):
            return {
                'query': query,
                'intent': 'factual',
                'confidence': 0.8,
                'reason': 'Query asks for factual information'
            }
        
        # Default to factual if no patterns match
        return {
            'query': query,
            'intent': 'factual',
            'confidence': 0.5,
            'reason': 'No specific pattern detected, treating as factual'
        }
    
    def is_factual(self, query: str) -> bool:
        """Check if query is factual."""
        result = self.classify(query)
        return result['intent'] == 'factual'
    
    def is_advisory(self, query: str) -> bool:
        """Check if query is advisory."""
        result = self.classify(query)
        return result['intent'] == 'advisory'
    
    def is_out_of_scope(self, query: str) -> bool:
        """Check if query is out of scope."""
        result = self.classify(query)
        return result['intent'] == 'out_of_scope'
    
    def get_advisory_response(self) -> str:
        """Get standard response for advisory queries."""
        return "I can only provide factual information about mutual funds. I cannot give investment advice or recommendations. Please consult a SEBI-registered investment advisor for personalized guidance."
    
    def get_out_of_scope_response(self) -> str:
        """Get standard response for out-of-scope queries."""
        return "I can only answer questions about mutual funds. Your query is outside my scope. Please ask about mutual fund schemes, expense ratios, NAV, or other factual fund information."
