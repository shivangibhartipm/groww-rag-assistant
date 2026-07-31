"""
Phase 1.2: Content Extraction
Extracts main content from HTML, removing navigation and non-relevant elements.
"""

from bs4 import BeautifulSoup, Tag
import logging
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentExtractor:
    """Extracts and cleans content from HTML pages."""
    
    # Tags to remove (navigation, footer, etc.)
    REMOVE_TAGS = [
        'nav', 'navbar', 'header', 'footer', 'aside', 'sidebar',
        'script', 'style', 'noscript', 'iframe', 'svg',
        'button', 'input', 'form', 'select', 'textarea',
        'advertisement', 'ad', 'banner', 'cookie'
    ]
    
    # Classes/IDs to remove
    REMOVE_CLASSES = [
        'nav', 'navbar', 'navigation', 'menu', 'sidebar',
        'footer', 'header', 'banner', 'advertisement', 'ad',
        'cookie', 'popup', 'modal', 'social', 'share'
    ]
    
    def __init__(self):
        """Initialize content extractor."""
        pass
    
    def extract_content(self, html_content: str, url: str = None) -> Dict:
        """
        Extract main content from HTML.
        
        Args:
            html_content: Raw HTML string
            url: Source URL (for logging)
            
        Returns:
            Dictionary containing extracted text, tables, lists, and metadata
        """
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Remove unwanted elements
        self._remove_unwanted_elements(soup)
        
        # Extract different content types
        main_text = self._extract_main_text(soup)
        tables = self._extract_tables(soup)
        lists = self._extract_lists(soup)
        structured_data = self._extract_structured_data(soup)
        
        result = {
            'url': url,
            'main_text': main_text,
            'tables': tables,
            'lists': lists,
            'structured_data': structured_data,
            'word_count': len(main_text.split()) if main_text else 0
        }
        
        logger.info(f"Extracted content from {url}: {result['word_count']} words, "
                   f"{len(tables)} tables, {len(lists)} lists")
        
        return result
    
    def _remove_unwanted_elements(self, soup: BeautifulSoup):
        """
        Remove navigation, footer, and non-relevant elements.
        
        Args:
            soup: BeautifulSoup object
        """
        # Remove by tag name
        for tag_name in self.REMOVE_TAGS:
            for element in soup.find_all(tag_name):
                element.decompose()
        
        # Remove by class/id
        for class_name in self.REMOVE_CLASSES:
            # Remove by class
            for element in soup.find_all(class_=lambda x: x and class_name in str(x).lower()):
                element.decompose()
            # Remove by id
            for element in soup.find_all(id=lambda x: x and class_name in str(x).lower()):
                element.decompose()
    
    def _extract_main_text(self, soup: BeautifulSoup) -> str:
        """
        Extract main text content.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Extracted text string
        """
        # Try to find main content area
        main_content = (
            soup.find('main') or
            soup.find('article') or
            soup.find('div', class_=lambda x: x and 'content' in str(x).lower()) or
            soup.find('div', id=lambda x: x and 'content' in str(x).lower()) or
            soup.body
        )
        
        if main_content:
            # Get text and clean it
            text = main_content.get_text(separator=' ', strip=True)
            # Normalize whitespace
            text = ' '.join(text.split())
            return text
        
        return ""
    
    def _extract_tables(self, soup: BeautifulSoup) -> list:
        """
        Extract tables from HTML.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of table data as dictionaries
        """
        tables_data = []
        
        for table in soup.find_all('table'):
            table_info = {
                'headers': [],
                'rows': []
            }
            
            # Extract headers
            header_row = table.find('tr')
            if header_row:
                for th in header_row.find_all(['th', 'td']):
                    table_info['headers'].append(th.get_text(strip=True))
            
            # Extract data rows
            for row in table.find_all('tr')[1:]:  # Skip header row
                row_data = []
                for cell in row.find_all(['td', 'th']):
                    row_data.append(cell.get_text(strip=True))
                if row_data:
                    table_info['rows'].append(row_data)
            
            if table_info['rows']:
                tables_data.append(table_info)
        
        return tables_data
    
    def _extract_lists(self, soup: BeautifulSoup) -> list:
        """
        Extract lists from HTML.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of list items
        """
        lists_data = []
        
        for list_elem in soup.find_all(['ul', 'ol']):
            list_items = []
            for li in list_elem.find_all('li'):
                text = li.get_text(strip=True)
                if text:
                    list_items.append(text)
            
            if list_items:
                lists_data.append({
                    'type': list_elem.name,
                    'items': list_items
                })
        
        return lists_data
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> Dict:
        """
        Extract structured data (meta tags, title, etc.).
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Dictionary of structured data
        """
        structured = {
            'title': '',
            'meta_description': '',
            'meta_keywords': '',
            'headings': []
        }
        
        # Title
        title_tag = soup.find('title')
        if title_tag:
            structured['title'] = title_tag.get_text(strip=True)
        
        # Meta tags
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            structured['meta_description'] = meta_desc['content']
        
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            structured['meta_keywords'] = meta_keywords['content']
        
        # Headings
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            structured['headings'].append({
                'level': heading.name,
                'text': heading.get_text(strip=True)
            })
        
        return structured
