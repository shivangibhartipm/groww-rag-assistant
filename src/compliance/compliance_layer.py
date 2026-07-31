"""
Phase 5.3: Compliance Layer
Content filtering and disclaimer enforcement for regulatory compliance.
"""

import logging
from typing import Dict, List
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComplianceLayer:
    """Enforces compliance through content filtering and disclaimer enforcement."""
    
    # Advisory language patterns to block
    ADVISORY_PATTERNS = [
        r'\bshould\b',
        r'\bbetter\b',
        r'\brecommend\b',
        r'\badvice\b',
        r'\bbest\b',
        r'\bworst\b',
        r'\bgood\b',
        r'\bbad\b',
        r'\btop\b',
        r'\bsuggest\b',
        r'\bworth\b',
        r'\bprefer\b',
        r'\bchoose\b',
        r'\bideal\b',
        r'\boptimal\b',
        r'\bperfect\b'
    ]
    
    # Recommendation patterns to block
    RECOMMENDATION_PATTERNS = [
        r'\bi (recommend|suggest|advise)\b',
        r'\bwe (recommend|suggest|advise)\b',
        r'\b(recommended|suggested|advised)\b',
        r'\bgood (investment|choice|option)\b',
        r'\bbad (investment|choice|option)\b',
        r'\bhigh return\b',
        r'\blow risk\b',
        r'\bsafe investment\b',
        r'\bguaranteed return\b'
    ]
    
    # Disclaimer text
    DISCLAIMER_TEXT = (
        "Disclaimer: This system provides factual information about mutual funds "
        "and does not constitute investment advice. Please consult a SEBI-registered "
        "investment advisor for personalized guidance."
    )
    
    # System prompt disclaimer
    SYSTEM_PROMPT_DISCLAIMER = (
        "IMPORTANT: You are a factual mutual fund assistant. You must NOT provide "
        "investment advice, recommendations, or opinions. Only provide factual information "
        "from the provided context. If asked for advice, politely refuse and direct users "
        "to educational resources."
    )
    
    def __init__(self):
        """Initialize compliance layer."""
        self.advisory_regex = re.compile('|'.join(self.ADVISORY_PATTERNS), re.IGNORECASE)
        self.recommendation_regex = re.compile('|'.join(self.RECOMMENDATION_PATTERNS), re.IGNORECASE)
        logger.info("Compliance layer initialized")
    
    def filter_content(self, response: str) -> Dict:
        """
        Post-generation check for advisory language and recommendations.
        
        Args:
            response: Generated response text
            
        Returns:
            Filtering result with compliance status
        """
        if not response:
            return {
                'compliant': True,
                'blocked': False,
                'reason': None,
                'filtered_response': response
            }
        
        # Check for advisory language
        advisory_matches = self.advisory_regex.findall(response)
        advisory_count = len(advisory_matches)
        
        # Check for recommendation patterns
        recommendation_matches = self.recommendation_regex.findall(response)
        recommendation_count = len(recommendation_matches)
        
        # Determine if response should be blocked
        blocked = False
        reasons = []
        
        if recommendation_count > 0:
            blocked = True
            reasons.append(f"Contains recommendation language: {', '.join(recommendation_matches)}")
        
        if advisory_count > 2:  # Allow some advisory words but block if excessive
            blocked = True
            reasons.append(f"Excessive advisory language: {', '.join(advisory_matches)}")
        
        result = {
            'compliant': not blocked,
            'blocked': blocked,
            'reason': '; '.join(reasons) if reasons else None,
            'filtered_response': response,
            'advisory_count': advisory_count,
            'recommendation_count': recommendation_count
        }
        
        if blocked:
            logger.warning(f"Response blocked: {result['reason']}")
        
        return result
    
    def enforce_disclaimer(self, response: str, include_in_response: bool = True) -> Dict:
        """
        Ensure disclaimer is included in response.
        
        Args:
            response: Response text
            include_in_response: Whether to append disclaimer to response
            
        Returns:
            Response with disclaimer
        """
        if include_in_response:
            # Check if disclaimer is already present
            if 'disclaimer' not in response.lower():
                response_with_disclaimer = f"{response}\n\n{self.DISCLAIMER_TEXT}"
            else:
                response_with_disclaimer = response
        else:
            response_with_disclaimer = response
        
        return {
            'response': response_with_disclaimer,
            'disclaimer_included': 'disclaimer' in response_with_disclaimer.lower(),
            'disclaimer_text': self.DISCLAIMER_TEXT
        }
    
    def get_system_prompt_disclaimer(self) -> str:
        """Get disclaimer for system prompt."""
        return self.SYSTEM_PROMPT_DISCLAIMER
    
    def get_ui_disclaimer(self) -> str:
        """Get disclaimer for UI display."""
        return self.DISCLAIMER_TEXT
    
    def validate_response(self, response: str) -> Dict:
        """
        Complete validation of response for compliance.
        
        Args:
            response: Response text
            
        Returns:
            Complete validation result
        """
        # Step 1: Content filtering
        filter_result = self.filter_content(response)
        
        # Step 2: Disclaimer enforcement
        disclaimer_result = self.enforce_disclaimer(response, include_in_response=False)
        
        # Step 3: Overall compliance check
        compliant = filter_result['compliant']
        
        return {
            'compliant': compliant,
            'blocked': filter_result['blocked'],
            'block_reason': filter_result['reason'],
            'disclaimer_present': disclaimer_result['disclaimer_included'],
            'advisory_count': filter_result['advisory_count'],
            'recommendation_count': filter_result['recommendation_count'],
            'filtered_response': filter_result['filtered_response'],
            'disclaimer_text': disclaimer_result['disclaimer_text']
        }
    
    def sanitize_response(self, response: str) -> str:
        """
        Sanitize response by removing non-compliant content.
        
        Args:
            response: Response text
            
        Returns:
            Sanitized response
        """
        # Remove recommendation phrases
        sanitized = self.recommendation_regex.sub('[REMOVED]', response)
        
        # Reduce advisory language
        advisory_words = self.advisory_regex.findall(sanitized)
        for word in advisory_words:
            sanitized = sanitized.replace(word, word.upper())
        
        return sanitized


def main():
    """Main entry point for testing compliance layer."""
    compliance = ComplianceLayer()
    
    # Test responses
    test_responses = [
        "The HDFC Mid Cap Fund has an expense ratio of 1.85%.",  # Compliant
        "I recommend investing in HDFC Mid Cap Fund.",  # Non-compliant (recommendation)
        "This is a good investment option for you.",  # Non-compliant (good investment)
        "The fund should perform well in the future.",  # Borderline (should)
        "For performance information, please refer to the factsheet.",  # Compliant
        "We suggest you should buy this fund.",  # Non-compliant (suggest + should)
    ]
    
    print("="*60)
    print("COMPLIANCE LAYER TEST")
    print("="*60)
    
    for i, response in enumerate(test_responses, 1):
        print(f"\nTest {i}:")
        print(f"Response: {response}")
        print("-" * 60)
        
        # Validate response
        validation = compliance.validate_response(response)
        
        print(f"Compliant: {validation['compliant']}")
        print(f"Blocked: {validation['blocked']}")
        if validation['blocked']:
            print(f"Block reason: {validation['block_reason']}")
        print(f"Advisory count: {validation['advisory_count']}")
        print(f"Recommendation count: {validation['recommendation_count']}")
        
        # Test disclaimer
        disclaimer_result = compliance.enforce_disclaimer(response)
        print(f"Disclaimer included: {disclaimer_result['disclaimer_included']}")
    
    # Test system prompt disclaimer
    print("\n" + "="*60)
    print("SYSTEM PROMPT DISCLAIMER")
    print("="*60)
    print(compliance.get_system_prompt_disclaimer())
    
    # Test UI disclaimer
    print("\n" + "="*60)
    print("UI DISCLAIMER")
    print("="*60)
    print(compliance.get_ui_disclaimer())
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
