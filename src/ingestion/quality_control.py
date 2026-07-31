"""
Phase 1.3: Quality Control
Validation checks and source verification for ingested documents.
"""

import requests
import logging
from typing import Dict, List, Set
from difflib import SequenceMatcher
from urllib.parse import urlparse

from .config import OFFICIAL_SOURCES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QualityControl:
    """Quality control checks for ingested documents."""
    
    # Official domains
    OFFICIAL_DOMAINS = {
        'groww.in',
        'hdfcfund.com',
        'hdfcmutual.com',
        'amfiindia.com',
        'sebi.gov.in'
    }
    
    # Blocked domains (third-party aggregators, blogs)
    BLOCKED_DOMAINS = {
        'moneycontrol.com',
        'valueresearchonline.com',
        'morningstar.in',
        'etmoney.com',
        'zerodha.com',
        'kuvera.in',
        'paytmmoney.com'
    }
    
    # Minimum content requirements
    MIN_WORD_COUNT = 50
    MIN_TABLES = 0
    REQUIRED_FIELDS = ['url', 'main_text', 'timestamp']
    
    def __init__(self):
        """Initialize quality control."""
        self.validation_results = []
    
    def validate_document(self, document: Dict) -> Dict:
        """
        Run all quality control checks on a single document.
        
        Args:
            document: Document dictionary
            
        Returns:
            Validation result dictionary with pass/fail status
        """
        result = {
            'url': document.get('url'),
            'is_valid': True,
            'checks': {},
            'errors': []
        }
        
        # Run all checks
        result['checks']['url_accessible'] = self.check_url_accessibility(document)
        result['checks']['not_duplicate'] = self.check_duplicate_content(document)
        result['checks']['complete'] = self.check_document_completeness(document)
        result['checks']['official_source'] = self.verify_official_source(document)
        
        # Determine overall validity
        failed_checks = [k for k, v in result['checks'].items() if not v]
        
        if failed_checks:
            result['is_valid'] = False
            result['errors'] = failed_checks
            logger.warning(f"Document {document.get('url')} failed checks: {failed_checks}")
        else:
            logger.info(f"Document {document.get('url')} passed all quality checks")
        
        self.validation_results.append(result)
        return result
    
    def check_url_accessibility(self, document: Dict) -> bool:
        """
        Verify URL accessibility.
        
        Args:
            document: Document dictionary
            
        Returns:
            True if URL was accessible during fetch
        """
        # Check if document was successfully fetched
        error = document.get('error')
        status_code = document.get('status_code')
        
        if error:
            logger.warning(f"URL accessibility check failed: {error}")
            return False
        
        if status_code and status_code != 200:
            logger.warning(f"URL returned non-200 status: {status_code}")
            return False
        
        return True
    
    def check_duplicate_content(self, document: Dict, documents: List[Dict] = None) -> bool:
        """
        Check for duplicate content against other documents.
        
        Args:
            document: Document to check
            documents: List of other documents to compare against
            
        Returns:
            True if content is not duplicate
        """
        if documents is None:
            documents = []
        
        current_text = document.get('main_text', '')
        if not current_text:
            return False
        
        # Check similarity with other documents
        for other_doc in documents:
            if other_doc.get('url') == document.get('url'):
                continue  # Skip self
            
            other_text = other_doc.get('main_text', '')
            if not other_text:
                continue
            
            similarity = self._calculate_similarity(current_text, other_text)
            
            # If similarity > 90%, consider it duplicate
            if similarity > 0.9:
                logger.warning(f"Duplicate content detected between {document.get('url')} "
                             f"and {other_doc.get('url')} (similarity: {similarity:.2f})")
                return False
        
        return True
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate text similarity using SequenceMatcher.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity ratio between 0 and 1
        """
        return SequenceMatcher(None, text1, text2).ratio()
    
    def check_document_completeness(self, document: Dict) -> bool:
        """
        Validate document has all required fields and minimum content.
        
        Args:
            document: Document dictionary
            
        Returns:
            True if document is complete
        """
        errors = []
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in document or not document[field]:
                errors.append(f"Missing required field: {field}")
        
        # Check minimum word count
        main_text = document.get('main_text', '')
        word_count = len(main_text.split()) if main_text else 0
        
        if word_count < self.MIN_WORD_COUNT:
            errors.append(f"Insufficient content: {word_count} words (minimum: {self.MIN_WORD_COUNT})")
        
        # Check for extracted content
        if not document.get('tables') and not document.get('lists'):
            # Not strictly required, but log as warning
            logger.info(f"Document {document.get('url')} has no tables or lists")
        
        if errors:
            logger.warning(f"Document completeness check failed: {errors}")
            return False
        
        return True
    
    def verify_official_source(self, document: Dict) -> bool:
        """
        Ensure source is from official AMC, AMFI, or SEBI.
        
        Args:
            document: Document dictionary
            
        Returns:
            True if source is official
        """
        url = document.get('url', '')
        
        if not url:
            logger.warning("No URL provided for source verification")
            return False
        
        # Parse domain from URL
        try:
            domain = urlparse(url).netloc.lower()
            # Remove www. prefix if present
            domain = domain.replace('www.', '')
        except Exception as e:
            logger.error(f"Error parsing URL {url}: {e}")
            return False
        
        # Check against blocked domains
        for blocked in self.BLOCKED_DOMAINS:
            if blocked in domain:
                logger.error(f"Source from blocked domain: {domain}")
                return False
        
        # Check against official domains
        is_official = any(official in domain for official in self.OFFICIAL_DOMAINS)
        
        if is_official:
            logger.info(f"Source verified as official: {domain}")
            return True
        else:
            logger.warning(f"Source not from official domain: {domain}")
            return False
    
    def validate_batch(self, documents: List[Dict]) -> Dict:
        """
        Validate a batch of documents.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            Summary of validation results
        """
        logger.info(f"Starting batch validation for {len(documents)} documents")
        
        valid_docs = []
        invalid_docs = []
        
        for doc in documents:
            result = self.validate_document(doc)
            
            if result['is_valid']:
                valid_docs.append(doc)
            else:
                invalid_docs.append({
                    'document': doc,
                    'validation_result': result
                })
        
        summary = {
            'total': len(documents),
            'valid': len(valid_docs),
            'invalid': len(invalid_docs),
            'valid_urls': [d.get('url') for d in valid_docs],
            'invalid_details': invalid_docs
        }
        
        logger.info(f"Batch validation complete: {summary['valid']}/{summary['total']} valid")
        
        return summary
    
    def get_validation_report(self) -> Dict:
        """
        Generate a report of all validation results.
        
        Returns:
            Summary report dictionary
        """
        if not self.validation_results:
            return {'message': 'No validation results available'}
        
        total = len(self.validation_results)
        valid = sum(1 for r in self.validation_results if r['is_valid'])
        invalid = total - valid
        
        # Count failures by check type
        failure_counts = {}
        for result in self.validation_results:
            if not result['is_valid']:
                for error in result['errors']:
                    failure_counts[error] = failure_counts.get(error, 0) + 1
        
        return {
            'total_validated': total,
            'valid_count': valid,
            'invalid_count': invalid,
            'pass_rate': f"{(valid/total)*100:.1f}%" if total > 0 else "0%",
            'failure_breakdown': failure_counts,
            'invalid_urls': [r['url'] for r in self.validation_results if not r['is_valid']]
        }
