"""
Unit tests for Refusal Handler
"""

import pytest
from src.compliance.refusal_handler import RefusalHandler


@pytest.fixture
def handler():
    """Fixture for RefusalHandler instance."""
    return RefusalHandler()


class TestRefusalHandler:
    """Test suite for RefusalHandler."""
    
    def test_advisory_query_detection(self, handler):
        """Test detection of advisory queries."""
        advisory_queries = [
            "Should I invest in HDFC Mid Cap?",
            "Which is better - HDFC or SBI?",
            "Recommend a good mutual fund",
            "Is this a good investment?",
            "What should I buy?",
            "How much money to put in liquid fund if total portfolio is 7 lakhs?",
            "How much should I invest in HDFC Large Cap Fund?",
            "Where should I invest 5 lakhs?",
            "Help me choose a fund",
            "HDFC Mid Cap vs HDFC Large Cap",
        ]
        
        for query in advisory_queries:
            result = handler.detect_advisory_query(query)
            assert result['is_advisory'] == True, query
            assert result['confidence'] > 0.5
    
    def test_non_advisory_query_detection(self, handler):
        """Test detection of non-advisory queries."""
        non_advisory_queries = [
            "What is the expense ratio?",
            "What is the minimum SIP amount?",
            "Show me the riskometer details",
            "What is the minimum sip?",
            "How much is the minimum SIP amount for HDFC Mid Cap Fund?",
            "What is the portfolio turnover of HDFC Mid Cap Fund?",
        ]
        
        for query in non_advisory_queries:
            result = handler.detect_advisory_query(query)
            assert result['is_advisory'] == False, query
    
    def test_out_of_scope_detection(self, handler):
        """Test detection of out-of-scope queries."""
        out_of_scope_queries = [
            "What are the latest stock prices?",
            "What's the weather today?",
            "How to buy crypto?",
            "Best real estate investments"
        ]
        
        for query in out_of_scope_queries:
            result = handler.detect_out_of_scope(query)
            assert result['is_out_of_scope'] == True
    
    def test_should_refuse_advisory(self, handler):
        """Test should_refuse for advisory queries."""
        result = handler.should_refuse("Should I invest in HDFC?")
        assert result['should_refuse'] == True
        assert result['reason'] == 'advisory'
    
    def test_should_refuse_out_of_scope(self, handler):
        """Test should_refuse for out-of-scope queries."""
        result = handler.should_refuse("What are stock prices?")
        assert result['should_refuse'] == True
        assert result['reason'] == 'out_of_scope'
    
    def test_should_not_refuse_factual(self, handler):
        """Test should_refuse for factual queries."""
        result = handler.should_refuse("What is the expense ratio?")
        assert result['should_refuse'] == False
        assert result['reason'] is None
    
    def test_advisory_refusal_response(self, handler):
        """Test advisory refusal response generation."""
        refusal_result = {
            'should_refuse': True,
            'reason': 'advisory',
            'confidence': 0.8,
            'details': None
        }
        response = handler.generate_refusal_response(refusal_result)
        assert "investment advice" in response.lower()
        assert "amfi" in response.lower()
        assert "SEBI" in response
    
    def test_out_of_scope_refusal_response(self, handler):
        """Test out-of-scope refusal response generation."""
        refusal_result = {
            'should_refuse': True,
            'reason': 'out_of_scope',
            'confidence': 0.9,
            'details': None
        }
        response = handler.generate_refusal_response(refusal_result)
        assert "mutual funds" in response.lower()
        assert "outside my scope" in response.lower()
