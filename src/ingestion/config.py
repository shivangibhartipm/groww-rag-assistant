"""
Phase 1.1: Source Selection Configuration
Defines the data sources for the Mutual Fund FAQ Assistant.
"""

# Selected Asset Management Company
AMC_NAME = "HDFC Mutual Fund"

# Official Sources
OFFICIAL_SOURCES = {
    "amc": "HDFC Mutual Fund",
    "amfi": "Association of Mutual Funds in India",
    "sebi": "Securities and Exchange Board of India"
}

# Curated URL List - HDFC Mutual Fund Schemes from Groww
SOURCE_URLS = [
    {
        "url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
        "scheme_name": "HDFC Mid Cap Fund",
        "scheme_type": "Mid Cap",
        "plan": "Direct Growth",
        "source_type": "scheme_page"
    },
    {
        "url": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
        "scheme_name": "HDFC Equity Fund",
        "scheme_type": "Equity",
        "plan": "Direct Growth",
        "source_type": "scheme_page"
    },
    {
        "url": "https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth",
        "scheme_name": "HDFC Focused Fund",
        "scheme_type": "Focused",
        "plan": "Direct Growth",
        "source_type": "scheme_page"
    },
    {
        "url": "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
        "scheme_name": "HDFC ELSS Tax Saver Fund",
        "scheme_type": "ELSS",
        "plan": "Direct Plan Growth",
        "source_type": "scheme_page"
    },
    {
        "url": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
        "scheme_name": "HDFC Large Cap Fund",
        "scheme_type": "Large Cap",
        "plan": "Direct Growth",
        "source_type": "scheme_page"
    },
    {
        "url": "static://hdfc_fund_facts",
        "scheme_name": "HDFC Fund Facts",
        "scheme_type": "General",
        "plan": "N/A",
        "source_type": "static_knowledge"
    }
]

# Data storage paths
DATA_DIR = "data"
RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_DIR = "data/processed"
VECTOR_INDEX_DIR = "data/vector_index"

# Crawl settings
CRAWL_DELAY_SECONDS = 2  # Respectful crawling delay
REQUEST_TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
