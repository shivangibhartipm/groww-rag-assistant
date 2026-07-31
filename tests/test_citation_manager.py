"""
Unit tests for Citation Manager
"""

import pytest
from src.query_processing.citation_manager import CitationManager


@pytest.fixture
def manager():
    """Fixture for CitationManager instance."""
    return CitationManager()


@pytest.fixture
def sample_chunks():
    """Fixture for sample chunks."""
    return [
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


class TestCitationManager:
    """Test suite for CitationManager."""
    
    def test_select_source_with_chunks(self, manager, sample_chunks):
        """Test source selection from chunks."""
        result = manager.select_source(sample_chunks)
        
        assert result['source_url'] is not None
        assert result['confidence'] > 0
        assert result['reason'] is not None
    
    def test_select_source_empty_chunks(self, manager):
        """Test source selection with empty chunks."""
        result = manager.select_source([])
        
        assert result['source_url'] is None
        assert result['confidence'] == 0.0
        assert 'No chunks' in result['reason']
    
    def test_select_source_no_sources(self, manager):
        """Test source selection with chunks but no sources."""
        chunks = [
            {
                'text': 'Some text',
                'metadata': {},
                'score': 0.8
            }
        ]
        result = manager.select_source(chunks)
        
        assert result['source_url'] is None
        assert result['confidence'] == 0.0
    
    def test_extract_sources(self, manager, sample_chunks):
        """Test source extraction from chunks."""
        sources = manager._extract_sources(sample_chunks)
        
        assert len(sources) == 2  # 2 unique sources
        assert any(s['url'] == 'https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth' for s in sources)
        assert any(s['url'] == 'https://hdfcfund.com/factsheet/hdfc-mid-cap' for s in sources)
    
    def test_is_official_document(self, manager):
        """Test official document detection."""
        official_url = "https://hdfcfund.com/factsheet/hdfc-mid-cap"
        non_official_url = "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
        
        chunks = [
            {
                'text': 'Official factsheet available',
                'metadata': {'source_url': official_url},
                'score': 0.8
            }
        ]
        
        assert manager._is_official_document(official_url, chunks) == True
        assert manager._is_official_document(non_official_url, chunks) == False
    
    def test_calculate_recency_score(self, manager):
        """Test recency score calculation."""
        recent_date = "2024-01-15"
        old_date = "2023-01-15"
        
        recent_score = manager._calculate_recency_score(recent_date)
        old_score = manager._calculate_recency_score(old_date)
        
        assert recent_score >= old_score
        assert recent_score > 0.5
        assert old_score <= 0.5
    
    def test_format_citation(self, manager):
        """Test citation formatting."""
        source_url = "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
        last_updated = "2024-01-15"
        
        citation = manager.format_citation(source_url, last_updated)
        
        assert source_url in citation
        assert last_updated in citation
        assert "Source:" in citation
    
    def test_format_url_shortening(self, manager):
        """Test URL shortening for display."""
        long_url = "https://very-long-domain-name.com/very/long/path/that/needs/to/be/shortened"
        formatted = manager._format_url(long_url, max_length=40)
        
        assert len(formatted) <= 40
        assert "..." in formatted or len(formatted) == len(long_url)
    
    def test_validate_link_valid(self, manager):
        """Test link validation for valid URL."""
        result = manager.validate_link("https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth")
        
        assert result['valid'] == True
        assert len(result['errors']) == 0
    
    def test_validate_link_missing(self, manager):
        """Test link validation for missing URL."""
        result = manager.validate_link("")
        
        assert result['valid'] == False
        assert any('missing' in error.lower() for error in result['errors'])
    
    def test_validate_link_invalid_format(self, manager):
        """Test link validation for invalid URL format."""
        result = manager.validate_link("not-a-valid-url")
        
        assert result['valid'] == False
        assert len(result['errors']) > 0
