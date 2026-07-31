"""
Phase 2.4: Fetcher
Fetches HTML content from the 5 whitelisted Groww URLs.
"""

import requests
import logging
from typing import List, Dict
from datetime import datetime

from ..ingestion.config import SOURCE_URLS, CRAWL_DELAY_SECONDS, REQUEST_TIMEOUT, USER_AGENT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Use the OS certificate store so corporate TLS interception still verifies.
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    logger.warning("truststore not installed; using default certificate verification")


class Fetcher:
    """Fetches HTML content from URLs."""
    
    def __init__(self):
        """Initialize fetcher."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self.last_request_time = 0
    
    def fetch_all(self) -> List[Dict]:
        """
        Fetch all whitelisted URLs.
        
        Returns:
            List of fetch results with url, html, status, timestamp
        """
        results = []
        
        for url_config in SOURCE_URLS:
            result = self.fetch_single(url_config)
            results.append(result)
        
        successful = [r for r in results if r.get('success')]
        logger.info(f"Fetched {len(successful)}/{len(results)} URLs successfully")
        
        return results
    
    def fetch_single(self, url_config: Dict) -> Dict:
        """
        Fetch a single URL with rate limiting.
        
        Args:
            url_config: Dictionary with url and metadata
            
        Returns:
            Fetch result dictionary
        """
        url = url_config.get('url')
        
        # Handle static knowledge URLs
        if url.startswith('static://'):
            return self._fetch_static_knowledge(url, url_config)
        
        # Rate limiting
        import time
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < CRAWL_DELAY_SECONDS:
            time.sleep(CRAWL_DELAY_SECONDS - time_since_last)
        self.last_request_time = time.time()
        
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            return {
                'url': url,
                'html': response.text,
                'status_code': response.status_code,
                'success': True,
                'error': None,
                'timestamp': datetime.utcnow().isoformat(),
                'metadata': url_config
            }
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")
            return {
                'url': url,
                'html': None,
                'status_code': None,
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'metadata': url_config
            }
    
    def _fetch_static_knowledge(self, url: str, url_config: Dict) -> Dict:
        """
        Fetch static knowledge base content.
        
        Args:
            url: Static URL (e.g., static://hdfc_fund_facts)
            url_config: URL configuration
            
        Returns:
            Fetch result with static knowledge HTML
        """
        static_content = {
            'static://hdfc_fund_facts': """
            <html>
            <body>
            <h1>HDFC Mutual Fund - Statement Download Guide</h1>
            
            <h2>ELSS Lock-in Period (SEBI rule)</h2>
            <p>ELSS (Equity Linked Savings Scheme) funds have a mandatory lock-in period of 3 years from the date of investment.</p>
            <p>For HDFC ELSS Tax Saver Fund, units cannot be redeemed before completion of 3 years.</p>
            
            <h2>Download Statement Process</h2>
            <p>To download capital gains statement or account statement from HDFC Mutual Fund:</p>
            <ol>
            <li>Visit the HDFC Mutual Fund website (www.hdfcfund.com)</li>
            <li>Login to your investor account using PAN and password</li>
            <li>Navigate to the 'Statements' or 'Reports' section</li>
            <li>Select the statement type (Capital Gains, Account Statement, etc.)</li>
            <li>Choose the date range and folio number</li>
            <li>Click on 'Download' to get the PDF statement</li>
            </ol>
            <p>Alternatively, you can download statements from Groww app under the 'Portfolio' section.</p>
            </body>
            </html>
            """
        }
        
        content = static_content.get(url, '')
        
        return {
            'url': url,
            'html': content,
            'status_code': 200,
            'success': True,
            'error': None,
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': url_config
        }
    
    def close(self):
        """Close the session."""
        self.session.close()
