"""
Phase 1.2: Web Scraper Implementation
Handles web scraping with rate limiting and respectful crawling.
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import Dict, Optional
from datetime import datetime

from .config import CRAWL_DELAY_SECONDS, REQUEST_TIMEOUT, USER_AGENT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebScraper:
    """Web scraper for mutual fund scheme pages with rate limiting."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self.last_request_time = 0
    
    def _respect_rate_limit(self):
        """Ensure respectful crawling with delays between requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < CRAWL_DELAY_SECONDS:
            sleep_time = CRAWL_DELAY_SECONDS - time_since_last_request
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def fetch_page(self, url: str) -> Optional[Dict]:
        """
        Fetch a single page with rate limiting.
        
        Args:
            url: URL to fetch
            
        Returns:
            Dictionary containing url, status_code, content, error (if any), timestamp
        """
        self._respect_rate_limit()
        
        try:
            logger.info(f"Fetching URL: {url}")
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            return {
                'url': url,
                'status_code': response.status_code,
                'content': response.text,
                'error': None,
                'timestamp': datetime.utcnow().isoformat(),
                'content_type': response.headers.get('Content-Type', 'unknown')
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return {
                'url': url,
                'status_code': None,
                'content': None,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'content_type': None
            }
    
    def fetch_multiple_pages(self, url_configs: list) -> list:
        """
        Fetch multiple pages sequentially with rate limiting.
        
        Args:
            url_configs: List of dictionaries containing url and metadata
            
        Returns:
            List of fetch results with metadata merged
        """
        results = []
        
        for config in url_configs:
            url = config.get('url')
            if not url:
                logger.warning(f"Skipping config without URL: {config}")
                continue
            
            result = self.fetch_page(url)
            
            # Merge metadata from config
            result.update({
                k: v for k, v in config.items() 
                if k != 'url'
            })
            
            results.append(result)
        
        return results
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """
        Parse HTML content using BeautifulSoup.
        
        Args:
            html_content: Raw HTML string
            
        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html_content, 'lxml')
    
    def close(self):
        """Close the session."""
        self.session.close()
