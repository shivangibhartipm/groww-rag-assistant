"""
Resolve mutual fund scheme names mentioned in a query against the corpus.
"""

import logging
import re
from typing import Dict, List, Optional

from ..ingestion.config import SOURCE_URLS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Aliases map common/market names onto corpus scheme_name values.
# HDFC Equity Fund was rebranded as HDFC Flexi Cap Fund.
SCHEME_ALIASES = {
    "hdfc flexi cap": "HDFC Equity Fund",
    "hdfc flexi cap fund": "HDFC Equity Fund",
    "hdfc flexicap": "HDFC Equity Fund",
    "hdfc equity fund": "HDFC Equity Fund",
    "hdfc mid cap": "HDFC Mid Cap Fund",
    "hdfc midcap": "HDFC Mid Cap Fund",
    "hdfc mid cap fund": "HDFC Mid Cap Fund",
    "hdfc focused": "HDFC Focused Fund",
    "hdfc focused fund": "HDFC Focused Fund",
    "hdfc large cap": "HDFC Large Cap Fund",
    "hdfc largecap": "HDFC Large Cap Fund",
    "hdfc large cap fund": "HDFC Large Cap Fund",
    "hdfc elss": "HDFC ELSS Tax Saver Fund",
    "hdfc elss tax saver": "HDFC ELSS Tax Saver Fund",
    "hdfc elss tax saver fund": "HDFC ELSS Tax Saver Fund",
    "hdfc tax saver": "HDFC ELSS Tax Saver Fund",
}


class SchemeResolver:
    """Maps query text to known corpus schemes."""

    def __init__(self, source_urls: Optional[List[Dict]] = None):
        self.source_urls = source_urls or SOURCE_URLS
        self.corpus_schemes = {
            item["scheme_name"]: item
            for item in self.source_urls
            if item.get("source_type") != "static_knowledge"
        }
        # Longest aliases first so "hdfc elss tax saver fund" beats "hdfc elss"
        self._alias_patterns = sorted(
            SCHEME_ALIASES.items(),
            key=lambda x: len(x[0]),
            reverse=True,
        )
        logger.info("Scheme resolver initialized with %d corpus schemes", len(self.corpus_schemes))

    def resolve(self, query: str) -> Dict:
        """
        Resolve a scheme from the query.

        Returns:
            {
              'mentioned': bool,
              'scheme_name': Optional[str],
              'known': bool,
              'source_url': Optional[str],
              'raw_match': Optional[str],
            }
        """
        normalized = self._normalize(query)

        for alias, scheme_name in self._alias_patterns:
            if alias in normalized:
                meta = self.corpus_schemes.get(scheme_name)
                return {
                    "mentioned": True,
                    "scheme_name": scheme_name,
                    "known": meta is not None,
                    "source_url": meta.get("url") if meta else None,
                    "raw_match": alias,
                }

        # Fallback: direct corpus scheme name substring match
        for scheme_name, meta in sorted(
            self.corpus_schemes.items(),
            key=lambda x: len(x[0]),
            reverse=True,
        ):
            if self._normalize(scheme_name) in normalized:
                return {
                    "mentioned": True,
                    "scheme_name": scheme_name,
                    "known": True,
                    "source_url": meta.get("url"),
                    "raw_match": scheme_name,
                }

        # Detect an unknown HDFC scheme mention (e.g. a fund not in corpus)
        unknown = re.search(
            r"\bhdfc\s+[a-z0-9][a-z0-9\s\-]{2,40}?(?:fund)?\b",
            normalized,
        )
        if unknown:
            raw = unknown.group(0).strip()
            # Ignore generic phrases like "hdfc mutual fund"
            if raw not in {"hdfc mutual fund", "hdfc fund", "hdfc aum"}:
                return {
                    "mentioned": True,
                    "scheme_name": None,
                    "known": False,
                    "source_url": None,
                    "raw_match": raw,
                }

        return {
            "mentioned": False,
            "scheme_name": None,
            "known": False,
            "source_url": None,
            "raw_match": None,
        }

    def filter_chunks(self, chunks: List[Dict], scheme_name: str) -> List[Dict]:
        """Keep scheme pages/fact cards plus static knowledge that mentions the scheme."""
        if not scheme_name:
            return chunks

        filtered = []
        scheme_l = scheme_name.lower()
        for chunk in chunks:
            metadata = chunk.get("metadata", {}) or {}
            chunk_scheme = (metadata.get("scheme_name") or "").lower()
            source_type = metadata.get("source_type", "")
            content_type = metadata.get("content_type", "")
            text = (chunk.get("text") or "").lower()

            if chunk_scheme == scheme_l:
                filtered.append(chunk)
            elif (
                source_type == "static_knowledge" or content_type == "static_knowledge"
            ) and scheme_l in text:
                filtered.append(chunk)

        # Prefer compact fact cards when available for the scheme
        fact_cards = [
            c for c in filtered
            if (c.get("metadata") or {}).get("content_type") == "fact_card"
        ]
        if fact_cards:
            extras = [
                c for c in filtered
                if (c.get("metadata") or {}).get("content_type") != "fact_card"
            ]
            return fact_cards + extras
        return filtered

    @staticmethod
    def _normalize(text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        # Drop common plan suffixes so aliases still match
        text = re.sub(
            r"\b(direct\s+plan\s+growth|direct\s+growth|direct\s+plan|growth)\b",
            " ",
            text,
        )
        return re.sub(r"\s+", " ", text).strip()
