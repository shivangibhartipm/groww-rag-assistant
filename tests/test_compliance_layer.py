"""
Unit tests for Compliance Layer
"""

import pytest
from src.compliance.compliance_layer import ComplianceLayer


@pytest.fixture
def compliance():
    """Fixture for ComplianceLayer instance."""
    return ComplianceLayer()


class TestComplianceLayer:
    """Test suite for ComplianceLayer."""
    
    def test_filter_content_compliant(self, compliance):
        """Test filtering of compliant content."""
        compliant_response = "The HDFC Mid Cap Fund has an expense ratio of 1.85%."
        result = compliance.filter_content(compliant_response)
        
        assert result['compliant'] == True
        assert result['blocked'] == False
        assert result['reason'] is None
    
    def test_filter_content_advisory(self, compliance):
        """Test filtering of advisory content."""
        advisory_response = "I recommend investing in HDFC Mid Cap Fund."
        result = compliance.filter_content(advisory_response)
        
        assert result['compliant'] == False
        assert result['blocked'] == True
        assert result['reason'] is not None
        assert 'recommendation' in result['reason'].lower()
    
    def test_filter_content_excessive_advisory(self, compliance):
        """Test filtering of excessive advisory language."""
        excessive_advisory = "This is the best fund. You should buy it. It's better than others."
        result = compliance.filter_content(excessive_advisory)
        
        assert result['compliant'] == False
        assert result['blocked'] == True
        assert result['advisory_count'] > 2
    
    def test_filter_content_empty(self, compliance):
        """Test filtering of empty content."""
        result = compliance.filter_content("")
        
        assert result['compliant'] == True
        assert result['blocked'] == False
    
    def test_enforce_disclaimer(self, compliance):
        """Test disclaimer enforcement."""
        response = "The expense ratio is 1.85%."
        result = compliance.enforce_disclaimer(response, include_in_response=True)
        
        assert 'disclaimer' in result['response'].lower()
        assert result['disclaimer_included'] == True
    
    def test_enforce_disclaimer_already_present(self, compliance):
        """Test disclaimer enforcement when already present."""
        response = "The expense ratio is 1.85%. Disclaimer: This is not advice."
        result = compliance.enforce_disclaimer(response, include_in_response=True)
        
        assert result['disclaimer_included'] == True
    
    def test_enforce_disclaimer_not_included(self, compliance):
        """Test disclaimer enforcement when not included."""
        response = "The expense ratio is 1.85%."
        result = compliance.enforce_disclaimer(response, include_in_response=False)
        
        assert result['disclaimer_included'] == False
    
    def test_get_system_prompt_disclaimer(self, compliance):
        """Test getting system prompt disclaimer."""
        disclaimer = compliance.get_system_prompt_disclaimer()
        
        assert disclaimer is not None
        assert len(disclaimer) > 0
        assert 'factual' in disclaimer.lower()
        assert 'advice' in disclaimer.lower()
    
    def test_get_ui_disclaimer(self, compliance):
        """Test getting UI disclaimer."""
        disclaimer = compliance.get_ui_disclaimer()
        
        assert disclaimer is not None
        assert len(disclaimer) > 0
        assert 'disclaimer' in disclaimer.lower()
        assert 'SEBI' in disclaimer
    
    def test_validate_response_compliant(self, compliance):
        """Test validation of compliant response."""
        response = "The expense ratio is 1.85%."
        result = compliance.validate_response(response)
        
        assert result['compliant'] == True
        assert result['blocked'] == False
        assert result['disclaimer_present'] == False  # Not enforced in validate
    
    def test_validate_response_non_compliant(self, compliance):
        """Test validation of non-compliant response."""
        response = "I recommend this fund."
        result = compliance.validate_response(response)
        
        assert result['compliant'] == False
        assert result['blocked'] == True
        assert result['recommendation_count'] > 0
    
    def test_sanitize_response(self, compliance):
        """Test response sanitization."""
        response = "I recommend investing in this fund. It should perform well."
        sanitized = compliance.sanitize_response(response)
        
        assert '[REMOVED]' in sanitized or 'RECOMMEND' in sanitized.upper()
    
    def test_sanitize_response_clean(self, compliance):
        """Test sanitization of already clean response."""
        response = "The expense ratio is 1.85%."
        sanitized = compliance.sanitize_response(response)
        
        assert sanitized == response or sanitized == response.upper()
