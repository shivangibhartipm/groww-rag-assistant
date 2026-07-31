"""
Phase 5.1: Advisory Query Detection & Refusal Handling
Detects advisory queries and generates appropriate refusal responses.
"""

import logging
from typing import Dict
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RefusalHandler:
    """Handles advisory query detection and refusal responses."""
    
    # Intent patterns, not bare keywords. Scoring loose keywords like "good" or
    # "and" both missed allocation questions and refused legitimate fact queries.
    ADVISORY_PATTERNS = [
        # Asking to be told what to do
        (r'\bshould\s+(i|we|one|someone)\b', 'asks what the user should do'),
        (r'\b(recommend|recommendation|suggest|advise|advice)\b', 'asks for a recommendation'),
        (r'\bwhat\s+(do\s+you\s+)?(think|advise)\b', 'asks for an opinion'),
        (r'\bhelp\s+me\s+(choose|pick|select|decide)\b', 'asks help choosing'),

        # How much to invest / how to split a portfolio
        (r'\bhow\s+much\b[\s\S]*\b(invest|put|allocate|buy|portfolio|corpus)\b',
         'asks how much to invest'),
        (r'\bhow\s+(do|should)\s+i\s+(split|divide|allocate|distribute)\b',
         'asks how to allocate'),
        (r'\bwhere\s+(should|to|do)\s+i?\s*invest\b', 'asks where to invest'),
        (r'\bhow\s+many\s+(funds?|schemes?)\b[\s\S]*\b(should|need|hold)\b',
         'asks how many funds to hold'),

        # Judgement on suitability
        (r'\bis\s+(it|this|that|hdfc)\b[\s\S]{0,40}?\b(good|bad|safe|risky|wise|worth|suitable)\b',
         'asks for a suitability judgement'),
        (r'\b(good|best|worst|better|ideal|right|safe)\s+'
         r'(fund|scheme|option|choice|investment|plan|mutual\s+fund)\b',
         'asks which fund is best'),
        (r'\bworth\s+(investing|buying|holding|it)\b', 'asks whether it is worth it'),
        (r'\bwhich\s+(fund|scheme|plan|one)\b[\s\S]*'
         r'\b(better|best|choose|pick|prefer|suitable|invest)\b',
         'asks which fund to choose'),
        (r'\bwhich\s+(is|are|one\s+is)\s+(better|best)\b', 'asks which is better'),

        # Comparing schemes against each other
        (r'\b(vs\.?|versus)\b', 'compares schemes'),
        (r'\bcompared?\s+to\b', 'compares schemes'),
        (r'\bbetter\s+than\b', 'compares schemes'),

        # Predicting performance
        (r'\b(future|expect|expected|predict|predicted|projected|forecast)\b'
         r'[\s\S]{0,40}\breturns?\b',
         'asks for predicted returns'),
        (r'\breturns?\b[\s\S]{0,40}'
         r'\b(future|expect|expected|predict|predicted|projected|forecast)\b',
         'asks for predicted returns'),
        (r'\bhow\s+much\s+(will|would|can|could)\s+i\s+(earn|get|make|gain)\b',
         'asks for predicted returns'),
        (r'\bwill\s+[\s\S]{0,40}\b(grow|rise|fall|beat|outperform|double)\b',
         'asks for a prediction'),
    ]
    
    # Financial topics that are adjacent to mutual funds but not answerable here.
    # These carry enough fund vocabulary to slip past DOMAIN_TERMS on their own.
    OFF_TOPIC_TERMS = [
        r'\bstocks?\b', r'\bshares?\b', r'\bequity\s+shares?\b',
        r'\bcrypto\w*\b', r'\bbitcoin\b',
        r'\breal\s+estate\b', r'\bproperty\b',
        r'\bfixed\s+deposits?\b', r'\bfds?\b', r'\brds?\b',
        r'\bppf\b', r'\bepf\b', r'\bnps\b',
        r'\binsurance\b', r'\bpolicy\s+premium\b',
        r'\bloans?\b', r'\bcredit\s+cards?\b', r'\bbank\s+accounts?\b',
        r'\btrading\b', r'\bdemat\b', r'\bipo\b', r'\bfutures?\s+and\s+options?\b',
        r'\bweather\b', r'\bpolitics\b', r'\bsports\b', r'\bentertainment\b',
    ]

    # Vocabulary that marks a question as being about mutual funds at all.
    # A blocklist can never enumerate every off-topic question ("what is the
    # capital of the UK?"), so anything with no term from this list is treated
    # as out of scope rather than being sent down the retrieval path.
    DOMAIN_TERMS = [
        r'\bmutual\s+funds?\b', r'\bfunds?\b', r'\bschemes?\b', r'\bplans?\b',
        r'\bsip\b', r'\bstp\b', r'\bswp\b', r'\blumpsum\b',
        r'\bnav\b', r'\baum\b', r'\bamc\b', r'\bnfo\b', r'\bfolio\b',
        r'\belss\b', r'\btax\s+saver\b', r'\block[-\s]?in\b',
        r'\bexpense\s+ratio\b', r'\bexit\s+load\b', r'\bentry\s+load\b',
        r'\briskometer\b', r'\brisk\s+(level|profile|rating)\b',
        r'\bbenchmark\b', r'\bindex\b',
        r'\bfund\s+manager\b', r'\bmanagers?\b',
        r'\bunits?\b', r'\bredeem\w*\b', r'\bredemption\b',
        r'\bcapital\s+gains?\b', r'\bstatements?\b', r'\bfactsheets?\b',
        r'\bportfolio\b', r'\bholdings?\b',
        r'\b(direct|regular|growth|dividend)\s+plan\b', r'\bidcw\b',
        r'\bcagr\b', r'\bxirr\b', r'\breturns?\b',
        r'\binvest\w*\b', r'\bkyc\b',
        r'\bhdfc\b', r'\bgroww\b', r'\bamfi\b', r'\bsebi\b',
        r'\b(large|mid|small|flexi|multi)[-\s]?cap\b', r'\bfocused\b',
        r'\bdownload\b',
    ]

    # Educational links
    AMFI_EDUCATION_LINK = "https://www.amfiindia.com/investor-education"
    SEBI_EDUCATION_LINK = "https://investor.sebi.gov.in/"
    
    def __init__(self):
        """Initialize refusal handler."""
        self._advisory_patterns = [
            (re.compile(pattern, re.IGNORECASE), reason)
            for pattern, reason in self.ADVISORY_PATTERNS
        ]
        self._off_topic = re.compile('|'.join(self.OFF_TOPIC_TERMS), re.IGNORECASE)
        self._domain = re.compile('|'.join(self.DOMAIN_TERMS), re.IGNORECASE)
        logger.info("Refusal handler initialized")
    
    def detect_advisory_query(self, query: str) -> Dict:
        """
        Detect if query is advisory in nature.
        
        Args:
            query: User query text
            
        Returns:
            Detection result with confidence and reason
        """
        matches = []
        reasons = []
        
        for pattern, reason in self._advisory_patterns:
            found = pattern.search(query)
            if found:
                matches.append(found.group(0).strip())
                if reason not in reasons:
                    reasons.append(reason)
        
        is_advisory = bool(matches)
        
        return {
            'query': query,
            'is_advisory': is_advisory,
            # A matched intent pattern is a strong signal on its own
            'confidence': 0.9 if is_advisory else 0.0,
            'reasons': reasons,
            'advisory_keywords': matches,
            'comparative_terms': [],
        }
    
    def detect_out_of_scope(self, query: str) -> Dict:
        """
        Detect if query is out of scope (mutual fund domain).
        
        Args:
            query: User query text
            
        Returns:
            Detection result
        """
        off_topic = [m for m in self._off_topic.findall(query) if m]
        if off_topic:
            return {
                'query': query,
                'is_out_of_scope': True,
                'matched_topics': off_topic,
                'basis': 'off_topic_term',
            }

        # No mutual fund vocabulary at all. Answering these means retrieving the
        # nearest fact card regardless, which is how "what is the capital of the
        # UK?" ended up being asked to pick a scheme and then answered against one.
        if not self._domain.search(query):
            return {
                'query': query,
                'is_out_of_scope': True,
                'matched_topics': [],
                'basis': 'no_domain_term',
            }

        return {
            'query': query,
            'is_out_of_scope': False,
            'matched_topics': [],
            'basis': None,
        }
    
    def should_refuse(self, query: str) -> Dict:
        """
        Determine if query should be refused.
        
        Args:
            query: User query text
            
        Returns:
            Refusal decision with reason
        """
        # Check for advisory
        advisory_result = self.detect_advisory_query(query)
        if advisory_result['is_advisory']:
            return {
                'should_refuse': True,
                'reason': 'advisory',
                'confidence': advisory_result['confidence'],
                'details': advisory_result
            }
        
        # Check for out-of-scope
        out_of_scope_result = self.detect_out_of_scope(query)
        if out_of_scope_result['is_out_of_scope']:
            return {
                'should_refuse': True,
                'reason': 'out_of_scope',
                'confidence': 0.9,
                'details': out_of_scope_result
            }
        
        return {
            'should_refuse': False,
            'reason': None,
            'confidence': 0.0,
            'details': None
        }
    
    def generate_refusal_response(self, refusal_result: Dict) -> str:
        """
        Generate appropriate refusal response.
        
        Args:
            refusal_result: Result from should_refuse()
            
        Returns:
            Formatted refusal response
        """
        reason = refusal_result['reason']
        
        if reason == 'advisory':
            return self._generate_advisory_refusal()
        elif reason == 'out_of_scope':
            return self._generate_out_of_scope_refusal()
        else:
            return "I cannot answer this query."
    
    def _generate_advisory_refusal(self) -> str:
        """Generate refusal response for advisory queries."""
        response = (
            "I can only provide factual information about mutual funds and cannot offer investment advice or recommendations.\n\n"
            f"For educational resources on mutual funds, please visit: {self.AMFI_EDUCATION_LINK}\n"
            f"For SEBI investor education: {self.SEBI_EDUCATION_LINK}"
        )
        return response
    
    def _generate_out_of_scope_refusal(self) -> str:
        """Generate refusal response for out-of-scope queries."""
        response = (
            "I can only answer questions about mutual funds. Your query is outside my scope.\n\n"
            f"For general financial education, please visit: {self.AMFI_EDUCATION_LINK}\n"
            f"For SEBI investor education: {self.SEBI_EDUCATION_LINK}"
        )
        return response


def main():
    """Main entry point for testing refusal handler."""
    handler = RefusalHandler()
    
    # Test queries
    test_queries = [
        "Should I invest in HDFC Mid Cap?",  # Advisory
        "Which is better - HDFC or SBI?",  # Advisory + comparative
        "What is the expense ratio?",  # Factual
        "What are the latest stock prices?",  # Out of scope
        "Recommend a good mutual fund",  # Advisory
        "What is the minimum SIP amount?",  # Factual
        "Is this a good investment?",  # Advisory
        "How do I download the factsheet?",  # Factual
        "What's the weather today?",  # Out of scope
        "HDFC vs SBI which is best?",  # Advisory + comparative
        "How much money to put in liquid fund if total portfolio is 7 lakhs?",  # Advisory
    ]
    
    print("="*60)
    print("REFUSAL HANDLER TEST")
    print("="*60)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        
        # Check if should refuse
        refusal_result = handler.should_refuse(query)
        
        print(f"Should refuse: {refusal_result['should_refuse']}")
        if refusal_result['should_refuse']:
            print(f"Reason: {refusal_result['reason']}")
            print(f"Confidence: {refusal_result['confidence']:.2f}")
            
            # Generate refusal response
            response = handler.generate_refusal_response(refusal_result)
            print(f"\nRefusal Response:")
            print(response)
        else:
            print("Query can be processed")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
