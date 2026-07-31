"""
Integration tests for end-to-end pipeline testing
"""

import pytest
from unittest.mock import Mock, patch
from src.query_processing.query_processor import QueryProcessor
from src.compliance.refusal_handler import RefusalHandler
from src.query_processing.response_formatter import ResponseFormatter
from src.query_processing.citation_manager import CitationManager


class TestIntegrationFactualQueries:
    """Integration tests for factual queries through the full pipeline."""
    
    @pytest.fixture
    def components(self):
        """Fixture for pipeline components."""
        return {
            'query_processor': QueryProcessor(),
            'refusal_handler': RefusalHandler(),
            'response_formatter': ResponseFormatter(),
            'citation_manager': CitationManager()
        }
    
    def test_factual_query_pipeline(self, components):
        """Test full pipeline for factual query: Query → Classification → Response."""
        query = "What is the expense ratio of HDFC Mid Cap Fund?"
        
        # Step 1: Query processing
        processed = components['query_processor'].process(query)
        assert processed['should_process'] == True
        assert processed['intent'] == 'factual'
        
        # Step 2: Refusal check
        refusal = components['refusal_handler'].should_refuse(query)
        assert refusal['should_refuse'] == False
        
        # Step 3: Simulate retrieval (mock)
        mock_chunks = [
            {
                'text': 'The HDFC Mid Cap Fund has an expense ratio of 1.85%.',
                'metadata': {
                    'source_url': 'https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth',
                    'last_updated': '2024-01-15'
                },
                'score': 0.85
            }
        ]
        
        # Step 4: Source selection
        source = components['citation_manager'].select_source(mock_chunks)
        assert source['source_url'] is not None
        
        # Step 5: Response formatting
        answer = "The HDFC Mid Cap Fund has an expense ratio of 1.85%."
        formatted = components['response_formatter'].format_response(
            answer,
            source['source_url'],
            source['last_updated'],
            query
        )
        
        assert formatted['formatted_response'] is not None
        assert source['source_url'] in formatted['formatted_response']
        assert formatted['sentence_valid'] == True
    
    def test_exit_load_query_pipeline(self, components):
        """Test pipeline for exit load query."""
        query = "What is the exit load for HDFC Equity Fund?"
        
        processed = components['query_processor'].process(query)
        assert processed['intent'] == 'factual'
        
        refusal = components['refusal_handler'].should_refuse(query)
        assert refusal['should_refuse'] == False
    
    def test_sip_query_pipeline(self, components):
        """Test pipeline for SIP query."""
        query = "What is the minimum SIP amount?"
        
        processed = components['query_processor'].process(query)
        assert processed['intent'] == 'factual'
        
        refusal = components['refusal_handler'].should_refuse(query)
        assert refusal['should_refuse'] == False


class TestIntegrationAdvisoryQueries:
    """Integration tests for advisory queries through the full pipeline."""
    
    @pytest.fixture
    def components(self):
        """Fixture for pipeline components."""
        return {
            'query_processor': QueryProcessor(),
            'refusal_handler': RefusalHandler()
        }
    
    def test_advisory_query_refusal_pipeline(self, components):
        """Test full pipeline for advisory query: Query → Classification → Refusal."""
        query = "Should I invest in HDFC Mid Cap Fund?"
        
        # Step 1: Query processing
        processed = components['query_processor'].process(query)
        assert processed['intent'] == 'advisory'
        assert processed['should_process'] == False
        
        # Step 2: Refusal check
        refusal = components['refusal_handler'].should_refuse(query)
        assert refusal['should_refuse'] == True
        assert refusal['reason'] == 'advisory'
        
        # Step 3: Generate refusal response
        refusal_response = components['refusal_handler'].generate_refusal_response(refusal)
        
        assert "investment advice" in refusal_response.lower()
        assert "AMFI" in refusal_response or "SEBI" in refusal_response
    
    def test_which_better_query_refusal(self, components):
        """Test pipeline for 'which is better' query."""
        query = "Which is better - HDFC or SBI?"
        
        processed = components['query_processor'].process(query)
        assert processed['intent'] == 'advisory'
        
        refusal = components['refusal_handler'].should_refuse(query)
        assert refusal['should_refuse'] == True
    
    def test_recommend_query_refusal(self, components):
        """Test pipeline for recommendation query."""
        query = "Recommend a good mutual fund"
        
        processed = components['query_processor'].process(query)
        assert processed['intent'] == 'advisory'
        
        refusal = components['refusal_handler'].should_refuse(query)
        assert refusal['should_refuse'] == True


class TestIntegrationPerformanceQueries:
    """Integration tests for performance queries."""
    
    @pytest.fixture
    def components(self):
        """Fixture for pipeline components."""
        return {
            'response_formatter': ResponseFormatter()
        }
    
    def test_performance_query_factsheet_link(self, components):
        """Test pipeline for performance query → Factsheet link."""
        query = "What is the performance of this fund?"
        source_url = "https://hdfcfund.com/factsheet/hdfc-mid-cap"
        
        # Format response for performance query
        formatted = components['response_formatter'].format_response(
            "Some answer",
            source_url,
            query=query
        )
        
        assert formatted['is_performance_query'] == True
        assert "factsheet" in formatted['formatted_response'].lower()
    
    def test_return_query_factsheet_link(self, components):
        """Test pipeline for return query."""
        query = "What are the returns?"
        source_url = "https://example.com/factsheet"
        
        formatted = components['response_formatter'].format_response(
            "Some answer",
            source_url,
            query=query
        )
        
        assert formatted['is_performance_query'] == True


class TestIntegrationEdgeCases:
    """Integration tests for edge cases."""
    
    @pytest.fixture
    def components(self):
        """Fixture for pipeline components."""
        return {
            'query_processor': QueryProcessor(),
            'refusal_handler': RefusalHandler()
        }
    
    def test_unknown_scheme_query(self, components):
        """Test query for unknown scheme."""
        query = "What is the expense ratio of Unknown Fund XYZ?"
        
        processed = components['query_processor'].process(query)
        # Should still be treated as factual even if scheme unknown
        assert processed['intent'] == 'factual'
    
    def test_ambiguous_query(self, components):
        """Test ambiguous query."""
        query = "What about HDFC?"
        
        processed = components['query_processor'].process(query)
        # Should be treated as factual (default)
        assert processed['intent'] == 'factual'
    
    def test_empty_query(self, components):
        """Test empty query."""
        query = ""
        
        processed = components['query_processor'].process(query)
        assert processed['error'] == 'Empty query'
        assert processed['should_process'] == False
    
    def test_whitespace_only_query(self, components):
        """Test whitespace-only query."""
        query = "   "
        
        processed = components['query_processor'].process(query)
        assert processed['error'] == 'Empty query'
    
    def test_out_of_scope_query(self, components):
        """Test out-of-scope query."""
        query = "What are the latest stock prices?"
        
        processed = components['query_processor'].process(query)
        assert processed['intent'] == 'out_of_scope'
        
        refusal = components['refusal_handler'].should_refuse(query)
        assert refusal['should_refuse'] == True
        assert refusal['reason'] == 'out_of_scope'


class TestIntegrationCompliance:
    """Integration tests for compliance across the pipeline."""
    
    @pytest.fixture
    def components(self):
        """Fixture for pipeline components."""
        from src.compliance.compliance_layer import ComplianceLayer
        return {
            'compliance': ComplianceLayer(),
            'response_formatter': ResponseFormatter()
        }
    
    def test_compliance_check_on_response(self, components):
        """Test compliance check on generated response."""
        response = "The HDFC Mid Cap Fund has an expense ratio of 1.85%."
        
        # Filter content
        filter_result = components['compliance'].filter_content(response)
        assert filter_result['compliant'] == True
        
        # Format response
        formatted = components['response_formatter'].format_response(
            response,
            "https://example.com"
        )
        
        # Validate
        validation = components['response_formatter'].validate_response(formatted)
        assert validation['valid'] == True
    
    def test_compliance_blocks_advisory_response(self, components):
        """Test compliance blocking advisory response."""
        response = "I recommend investing in HDFC Mid Cap Fund."
        
        filter_result = components['compliance'].filter_content(response)
        assert filter_result['compliant'] == False
        assert filter_result['blocked'] == True
    
    def test_disclaimer_inclusion(self, components):
        """Test disclaimer inclusion in final response."""
        response = "The expense ratio is 1.85%."
        
        result = components['compliance'].enforce_disclaimer(response, include_in_response=True)
        assert result['disclaimer_included'] == True
        assert 'disclaimer' in result['response'].lower()
