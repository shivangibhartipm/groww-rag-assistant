"""
Unit tests for Response Formatter
"""

import pytest
from src.query_processing.response_formatter import ResponseFormatter


@pytest.fixture
def formatter():
    """Fixture for ResponseFormatter instance."""
    return ResponseFormatter()


class TestResponseFormatter:
    """Test suite for ResponseFormatter."""
    
    def test_format_response_basic(self, formatter):
        """Test basic response formatting."""
        answer = "The HDFC Mid Cap Fund has an expense ratio of 1.85%."
        source_url = "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
        
        result = formatter.format_response(answer, source_url)
        
        assert result['formatted_response'] is not None
        assert source_url in result['formatted_response']
        assert result['source_present'] == True
        assert result['sentence_count'] <= 3
    
    def test_format_response_with_last_updated(self, formatter):
        """Test response formatting with last updated date."""
        answer = "The HDFC Mid Cap Fund has an expense ratio of 1.85%."
        source_url = "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
        last_updated = "2024-01-15"
        
        result = formatter.format_response(answer, source_url, last_updated)
        
        assert last_updated in result['formatted_response']
        assert result['last_updated'] == last_updated
    
    def test_enforce_sentence_limit(self, formatter):
        """Test sentence limit enforcement."""
        long_answer = (
            "The HDFC Mid Cap Fund has an expense ratio of 1.85%. "
            "The minimum SIP amount is ₹500. "
            "The fund category is mid-cap. "
            "The exit load is 1% if redeemed within 1 year."
        )
        
        limited = formatter._enforce_sentence_limit(long_answer, max_sentences=3)
        sentence_count = formatter._count_sentences(limited)
        
        assert sentence_count <= 3
    
    def test_count_sentences(self, formatter):
        """Test sentence counting."""
        text = "The HDFC Mid Cap Fund has an expense ratio of 1.85%. The minimum SIP amount is ₹500."
        count = formatter._count_sentences(text)
        assert count == 2
    
    def test_performance_query_detection(self, formatter):
        """Test performance query detection."""
        performance_queries = [
            "What is the performance of this fund?",
            "What are the returns?",
            "Compare the performance",
            "What is the CAGR?"
        ]
        
        for query in performance_queries:
            result = formatter.format_response(
                "Some answer",
                "https://example.com",
                query=query
            )
            assert result['is_performance_query'] == True
    
    def test_non_performance_query(self, formatter):
        """Test non-performance query."""
        result = formatter.format_response(
            "The expense ratio is 1.85%",
            "https://example.com",
            query="What is the expense ratio?"
        )
        assert result['is_performance_query'] == False
    
    def test_validate_response_valid(self, formatter):
        """Test validation of valid response."""
        result = formatter.format_response(
            "The expense ratio is 1.85%.",
            "https://example.com"
        )
        validation = formatter.validate_response(result)
        assert validation['valid'] == True
        assert len(validation['errors']) == 0
    
    def test_validate_response_invalid_sentence_count(self, formatter):
        """Test validation with invalid sentence count."""
        # Create a response with too many sentences
        result = formatter.format_response(
            "Sentence 1. Sentence 2. Sentence 3. Sentence 4.",
            "https://example.com"
        )
        # Manually set sentence count to test validation
        result['sentence_count'] = 4
        result['sentence_valid'] = False
        
        validation = formatter.validate_response(result)
        assert validation['valid'] == False
        assert any('sentence' in error.lower() for error in validation['errors'])
    
    def test_validate_response_missing_source(self, formatter):
        """Test validation with missing source."""
        result = formatter.format_response(
            "The expense ratio is 1.85%.",
            ""
        )
        validation = formatter.validate_response(result)
        assert validation['valid'] == False
        assert any('source' in error.lower() for error in validation['errors'])
    
    def test_format_performance_response(self, formatter):
        """Test performance-specific response formatting."""
        source_url = "https://example.com/factsheet"
        response = formatter.format_performance_response(source_url)
        
        assert "factsheet" in response.lower()
        assert source_url in response
