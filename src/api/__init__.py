"""
Phase 6.3: Backend API
FastAPI backend for the Mutual Fund FAQ Assistant.
"""

from .main import app, health_check, process_query

__all__ = [
    'app',
    'health_check',
    'process_query'
]
