"""
Phase 1.2 & 1.3: Data Ingestion Pipeline
Orchestrates web scraping, content extraction, quality control, and document storage.
"""

import logging
from typing import List, Dict

from .config import SOURCE_URLS
from .web_scraper import WebScraper
from .document_storage import DocumentStorage
from .content_extractor import ContentExtractor
from .quality_control import QualityControl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Main pipeline for data ingestion from mutual fund scheme pages."""
    
    def __init__(self):
        """Initialize the ingestion pipeline components."""
        self.scraper = WebScraper()
        self.storage = DocumentStorage()
        self.extractor = ContentExtractor()
        self.qc = QualityControl()
        logger.info("Ingestion pipeline initialized")
    
    def run(self, url_configs: List[Dict] = None) -> Dict:
        """
        Run the complete ingestion pipeline.
        
        Args:
            url_configs: List of URL configurations (uses SOURCE_URLS if not provided)
            
        Returns:
            Summary dictionary with pipeline results
        """
        if url_configs is None:
            url_configs = SOURCE_URLS
        
        logger.info(f"Starting ingestion pipeline for {len(url_configs)} URLs")
        
        # Step 1: Fetch pages
        logger.info("Step 1: Fetching web pages...")
        fetch_results = self.scraper.fetch_multiple_pages(url_configs)
        
        successful_fetches = [r for r in fetch_results if r.get('error') is None]
        failed_fetches = [r for r in fetch_results if r.get('error') is not None]
        
        logger.info(f"Fetched {len(successful_fetches)}/{len(fetch_results)} pages successfully")
        
        # Step 2: Extract content from successful fetches
        logger.info("Step 2: Extracting content from HTML...")
        extracted_documents = []
        
        for result in successful_fetches:
            html_content = result.get('content')
            if html_content:
                extracted = self.extractor.extract_content(html_content, result.get('url'))
                # Merge extraction results with original metadata
                result.update(extracted)
                extracted_documents.append(result)
        
        logger.info(f"Extracted content from {len(extracted_documents)} documents")
        
        # Step 3: Quality Control
        logger.info("Step 3: Running quality control checks...")
        qc_summary = self.qc.validate_batch(extracted_documents)
        valid_documents = qc_summary['valid_urls']
        invalid_details = qc_summary['invalid_details']
        
        logger.info(f"Quality control: {qc_summary['valid']}/{qc_summary['total']} documents passed")
        
        # Filter only valid documents for storage
        valid_documents_data = [doc for doc in extracted_documents 
                               if doc.get('url') in valid_documents]
        
        # Step 4: Store documents
        logger.info("Step 4: Storing valid documents...")
        saved_paths = self.storage.save_documents(valid_documents_data)
        
        # Step 5: Generate summary
        summary = {
            'total_urls': len(url_configs),
            'successful_fetches': len(successful_fetches),
            'failed_fetches': len(failed_fetches),
            'documents_extracted': len(extracted_documents),
            'documents_passed_qc': qc_summary['valid'],
            'documents_failed_qc': qc_summary['invalid'],
            'documents_saved': len(saved_paths),
            'failed_urls': [r.get('url') for r in failed_fetches],
            'qc_failed_urls': [d['document'].get('url') for d in invalid_details],
            'saved_paths': saved_paths,
            'qc_report': self.qc.get_validation_report()
        }
        
        logger.info(f"Pipeline completed: {summary}")
        
        # Cleanup
        self.scraper.close()
        
        return summary
    
    def run_single_url(self, url: str, metadata: Dict = None) -> Dict:
        """
        Run pipeline for a single URL.
        
        Args:
            url: URL to process
            metadata: Additional metadata to attach
            
        Returns:
            Result dictionary
        """
        if metadata is None:
            metadata = {}
        
        config = {'url': url, **metadata}
        
        logger.info(f"Running pipeline for single URL: {url}")
        
        # Fetch
        result = self.scraper.fetch_page(url)
        
        if result.get('error'):
            logger.error(f"Failed to fetch {url}: {result['error']}")
            self.scraper.close()
            return result
        
        # Extract
        html_content = result.get('content')
        if html_content:
            extracted = self.extractor.extract_content(html_content, url)
            result.update(extracted)
        
        # Merge metadata
        result.update(metadata)
        
        # Store
        saved_path = self.storage.save_document(result)
        result['saved_path'] = saved_path
        
        self.scraper.close()
        
        return result


def main():
    """Main entry point for running the ingestion pipeline."""
    pipeline = IngestionPipeline()
    summary = pipeline.run()
    
    print("\n" + "="*50)
    print("INGESTION PIPELINE SUMMARY")
    print("="*50)
    print(f"Total URLs: {summary['total_urls']}")
    print(f"Successful Fetches: {summary['successful_fetches']}")
    print(f"Failed Fetches: {summary['failed_fetches']}")
    print(f"Documents Extracted: {summary['documents_extracted']}")
    print(f"Documents Passed QC: {summary['documents_passed_qc']}")
    print(f"Documents Failed QC: {summary['documents_failed_qc']}")
    print(f"Documents Saved: {summary['documents_saved']}")
    
    if summary['failed_urls']:
        print(f"\nFailed Fetch URLs:")
        for url in summary['failed_urls']:
            print(f"  - {url}")
    
    if summary['qc_failed_urls']:
        print(f"\nFailed Quality Control URLs:")
        for url in summary['qc_failed_urls']:
            print(f"  - {url}")
    
    # Print QC report
    qc_report = summary.get('qc_report', {})
    if qc_report and qc_report.get('total_validated', 0) > 0:
        print(f"\nQuality Control Report:")
        print(f"  Pass Rate: {qc_report.get('pass_rate', 'N/A')}")
        if qc_report.get('failure_breakdown'):
            print(f"  Failure Breakdown:")
            for failure, count in qc_report['failure_breakdown'].items():
                print(f"    - {failure}: {count}")
    
    print("="*50)


if __name__ == "__main__":
    main()
