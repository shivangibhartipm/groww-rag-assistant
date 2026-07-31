"""
Phase 2.5: Extractor
Extracts main content from HTML, removing navigation and non-relevant elements.
Consumes output from Fetcher (HTML content).
"""

from bs4 import BeautifulSoup
import logging
import re
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Extractor:
    """Extracts main content from HTML."""
    
    # Tags to remove
    REMOVE_TAGS = [
        'nav', 'header', 'footer', 'aside',
        'script', 'style', 'noscript', 'iframe', 'svg',
        'input', 'form', 'select', 'textarea'
    ]
    
    # Class/ID tokens to remove. Matched as whole tokens (separated by -, _ or
    # whitespace) so names like "shadow" or "loaded" are not treated as ads.
    REMOVE_CLASS_TOKENS = [
        'nav', 'navbar', 'navigation', 'menu', 'sidebar',
        'footer', 'header', 'banner', 'advertisement', 'ad', 'ads',
        'cookie', 'popup', 'modal', 'social', 'share'
    ]
    
    _CLASS_TOKEN_RE = re.compile(
        r'(?:^|[-_\s])(?:' + '|'.join(REMOVE_CLASS_TOKENS) + r')(?:$|[-_\s])',
        re.IGNORECASE,
    )
    
    def extract_all(self, fetch_results: List[Dict]) -> List[Dict]:
        """
        Extract content from all fetch results.
        
        Args:
            fetch_results: List of fetch results from Fetcher
            
        Returns:
            List of extraction results with extracted text and metadata
        """
        results = []
        
        for fetch_result in fetch_results:
            if not fetch_result.get('success'):
                logger.warning(f"Skipping failed fetch: {fetch_result.get('url')}")
                continue
            
            result = self.extract_single(fetch_result)
            results.append(result)
        
        logger.info(f"Extracted content from {len(results)} documents")
        return results
    
    def extract_single(self, fetch_result: Dict) -> Dict:
        """
        Extract content from a single fetch result.
        
        Args:
            fetch_result: Fetch result with HTML
            
        Returns:
            Extraction result with main_text, tables, lists, metadata
        """
        html = fetch_result.get('html')
        url = fetch_result.get('url')
        
        if not html:
            return {
                'url': url,
                'success': False,
                'error': 'No HTML content',
                'main_text': '',
                'tables': [],
                'lists': [],
                'metadata': fetch_result.get('metadata', {})
            }
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        self._remove_unwanted_elements(soup)
        
        # Extract content
        main_text = self._extract_main_text(soup)
        tables = self._extract_tables(soup)
        lists = self._extract_lists(soup)
        
        return {
            'url': url,
            'success': True,
            'error': None,
            'main_text': main_text,
            'tables': tables,
            'lists': lists,
            'word_count': len(main_text.split()) if main_text else 0,
            'metadata': fetch_result.get('metadata', {})
        }
    
    def _remove_unwanted_elements(self, soup):
        """Remove navigation, footer, and non-relevant elements."""
        for tag_name in self.REMOVE_TAGS:
            for element in soup.find_all(tag_name):
                element.decompose()
        
        for element in soup.find_all(class_=self._matches_removed_token):
            element.decompose()
        for element in soup.find_all(id=self._matches_removed_token):
            element.decompose()
    
    def _matches_removed_token(self, value) -> bool:
        """True if a class/id attribute contains a blocked whole token."""
        if not value:
            return False
        if isinstance(value, (list, tuple)):
            value = ' '.join(value)
        return bool(self._CLASS_TOKEN_RE.search(str(value)))
    
    def _extract_main_text(self, soup) -> str:
        """Extract main text content from the richest content container."""
        candidates = []
        candidates.extend(soup.find_all('main'))
        candidates.extend(soup.find_all('article'))
        candidates.extend(soup.find_all('div', class_=lambda x: x and 'content' in str(x).lower()))
        candidates.extend(soup.find_all('div', id=lambda x: x and 'content' in str(x).lower()))
        if soup.body:
            candidates.append(soup.body)
        
        best_text = ""
        for candidate in candidates:
            text = ' '.join(candidate.get_text(separator=' ', strip=True).split())
            if len(text) > len(best_text):
                best_text = text
        
        return best_text
    
    def _extract_tables(self, soup) -> list:
        """Extract tables from HTML."""
        tables_data = []
        
        for table in soup.find_all('table'):
            table_info = {'headers': [], 'rows': []}
            
            header_row = table.find('tr')
            if header_row:
                for th in header_row.find_all(['th', 'td']):
                    table_info['headers'].append(th.get_text(strip=True))
            
            for row in table.find_all('tr')[1:]:
                row_data = []
                for cell in row.find_all(['td', 'th']):
                    row_data.append(cell.get_text(strip=True))
                if row_data:
                    table_info['rows'].append(row_data)
            
            if table_info['rows']:
                tables_data.append(table_info)
        
        return tables_data
    
    def _extract_lists(self, soup) -> list:
        """Extract lists from HTML."""
        lists_data = []
        
        for list_elem in soup.find_all(['ul', 'ol']):
            list_items = []
            for li in list_elem.find_all('li'):
                text = li.get_text(strip=True)
                if text:
                    list_items.append(text)
            
            if list_items:
                lists_data.append({'type': list_elem.name, 'items': list_items})
        
        return lists_data
