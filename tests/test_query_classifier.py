"""
Unit tests for Query Classifier
"""

import pytest
from src.query_processing.query_classifier import QueryClassifier


@pytest.fixture
def classifier():
    """Fixture for QueryClassifier instance."""
    return QueryClassifier()


class TestQueryClassifier:
    """Test suite for QueryClassifier."""
    
    def test_factual_query_detection(self, classifier):
        """Test detection of factual queries."""
        factual_queries = [
            "What is the expense ratio?",
            "What is the minimum SIP amount?",
            "Show me the riskometer details",
            "What is the fund category?",
            "List the holdings"
        ]
        
        for query in factual_queries:
            result = classifier.classify(query)
            assert result['intent'] == 'factual'
            assert result['confidence'] > 0.5
    
    def test_advisory_query_detection(self, classifier):
        """Test detection of advisory queries."""
        advisory_queries = [
            "Should I invest in HDFC Mid Cap?",
            "Which fund is better?",
            "Recommend a good mutual fund",
            "Is this a good investment?",
            "What should I buy?"
        ]
        
        for query in advisory_queries:
            result = classifier.classify(query)
            assert result['intent'] == 'advisory'
            assert result['confidence'] > 0.5
    
    def test_out_of_scope_detection(self, classifier):
        """Test detection of out-of-scope queries."""
        out_of_scope_queries = [
            "What are the latest stock prices?",
            "What's the weather today?",
            "How to buy crypto?",
            "Best real estate investments",
            "Fixed deposit rates"
        ]
        
        for query in out_of_scope_queries:
            result = classifier.classify(query)
            assert result['intent'] == 'out_of_scope'
    
    def test_is_factual_method(self, classifier):
        """Test is_factual helper method."""
        assert classifier.is_factual("What is the expense ratio?") == True
        assert classifier.is_factual("Should I invest?") == False
    
    def test_is_advisory_method(self, classifier):
        """Test is_advisory helper method."""
        assert classifier.is_advisory("Should I invest?") == True
        assert classifier.is_advisory("What is the expense ratio?") == False
    
    def test_is_out_of_scope_method(self, classifier):
        """Test is_out_of_scope helper method."""
        assert classifier.is_out_of_scope("What are stock prices?") == True
        assert classifier.is_out_of_scope("What is the expense ratio?") == False
    
    def test_advisory_response(self, classifier):
        """Test advisory response generation."""
        response = classifier.get_advisory_response()
        assert "investment advice" in response.lower()
        assert "SEBI" in response
    
    def test_out_of_scope_response(self, classifier):
        """Test out-of-scope response generation."""
        response = classifier.get_out_of_scope_response()
        assert "mutual funds" in response.lower()
        assert "outside my scope" in response.lower()
