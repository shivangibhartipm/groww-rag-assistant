"""
Structured fact extraction from Groww scheme pages.
Creates compact, high-signal fact cards used by the RAG index.
"""

import logging
import re
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FactExtractor:
    """Extracts FAQ-relevant facts from scheme page text."""

    PATTERNS = {
        "expense_ratio": [
            r"Expense ratio\s*([0-9]+(?:\.[0-9]+)?%)",
        ],
        "min_sip": [
            r"Min\.?\s*for\s*SIP\s*((?:Rs\.?\s*|₹)[\d,]+)",
            r"Minimum SIP Investment is set to\s*((?:Rs\.?\s*|₹)[\d,]+)",
        ],
        "exit_load": [
            r"(Exit load of \d+(?:\.\d+)?%\s+if redeemed within \d+\s*(?:day|days|month|months|year|years))",
            r"(Nil\s*\(lock-in period applies\))",
        ],
        "riskometer": [
            r"is rated\s+([A-Za-z ]+?)\s+risk",
            r"rated\s+([A-Za-z ]+?)\s+risk",
        ],
        "benchmark": [
            r"Fund benchmark\s*([A-Za-z0-9&() /\-]+?(?:Total Return Index|TRI))",
        ],
        "nav": [
            r"Latest NAV as of\s*([0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4})\s*is\s*((?:Rs\.?\s*|₹)[\d,\.]+)",
            r"NAV[: ]+\s*([0-9]{1,2}\s+[A-Za-z]+ '?[0-9]{2})\s*((?:Rs\.?\s*|₹)[\d,\.]+)",
        ],
        "aum": [
            r"Fund size \(AUM\)\s*((?:Rs\.?\s*|₹)[\d,\.]+\s*Cr)",
            r"Asset Under Management\(AUM\) of\s*((?:Rs\.?\s*|₹)[\d,\.]+\s*Cr)",
        ],
        "fund_manager": [
            r"([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)\s+is the Current Fund Manager",
        ],
    }

    # "Fund management CS Chirag Setalvad Jan 2013 - Present"
    MANAGER_TENURE_RE = re.compile(
        r"\b[A-Z]{2}\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)\s+"
        r"([A-Z][a-z]{2}\s+\d{4})\s*-\s*Present"
    )

    # The plan name Groww displays, which can differ from the corpus scheme_name
    # (HDFC Equity Fund is listed as HDFC Flexi Cap Direct Plan Growth).
    # Case-sensitive so the non-greedy group stops at the lowercase " fund." only.
    DISPLAY_NAME_RE = re.compile(
        r"is the Current Fund Manager of\s+(HDFC[A-Za-z0-9&'\-\. ]{2,60}?)\s+fund\."
    )

    def extract(self, text: str, metadata: Dict) -> Dict[str, Optional[str]]:
        """Extract structured facts from page text."""
        facts: Dict[str, Optional[str]] = {
            "scheme_name": metadata.get("scheme_name"),
            "expense_ratio": None,
            "min_sip": None,
            "exit_load": None,
            "riskometer": None,
            "benchmark": None,
            "nav": None,
            "aum": None,
            "lock_in": None,
            "fund_manager": None,
            "fund_managers": None,
            "display_name": None,
        }

        for field, patterns in self.PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if not match:
                    continue
                if field == "nav" and match.lastindex and match.lastindex >= 2:
                    facts[field] = f"{match.group(2)} (as of {match.group(1)})"
                elif field == "riskometer":
                    risk = match.group(1).strip().title()
                    if not risk.lower().endswith("risk"):
                        risk = f"{risk} Risk"
                    facts[field] = risk
                else:
                    facts[field] = match.group(1).strip()
                break

        display_match = self.DISPLAY_NAME_RE.search(text)
        if display_match:
            facts["display_name"] = display_match.group(1).strip()

        managers = self._extract_managers(text)
        if managers:
            facts["fund_managers"] = ", ".join(
                f"{name} (managing since {since})" for name, since in managers
            )
            if not facts["fund_manager"]:
                facts["fund_manager"] = managers[0][0]

        scheme_type = (metadata.get("scheme_type") or "").upper()
        scheme_name = metadata.get("scheme_name") or ""
        if scheme_type == "ELSS" or "ELSS" in scheme_name.upper():
            facts["lock_in"] = "3 years from the date of investment"
            if not facts["exit_load"]:
                facts["exit_load"] = "Nil (lock-in period applies)"

        return facts

    def _extract_managers(self, text: str) -> List[tuple]:
        """Collect (name, tenure start) pairs from the fund management section."""
        start = text.find("Fund management")
        section = text[start:] if start != -1 else text

        managers: List[tuple] = []
        seen = set()
        for match in self.MANAGER_TENURE_RE.finditer(section):
            name = match.group(1).strip()
            if name in seen:
                continue
            seen.add(name)
            managers.append((name, match.group(2).strip()))
        return managers

    def to_fact_card(self, facts: Dict[str, Optional[str]], source_url: str) -> str:
        """Render facts as a compact text card for indexing."""
        scheme = facts.get("scheme_name") or "Unknown scheme"
        display_name = facts.get("display_name")
        lines = [f"Scheme facts for {scheme}."]
        if display_name and display_name.lower() != scheme.lower():
            lines.append(
                f"{scheme} is listed on Groww as {display_name}. "
                f"{scheme} and {display_name} are the same scheme, so every fact "
                f"below applies to both names."
            )
        lines.append(f"Source URL: {source_url}.")
        mapping = [
            ("fund_manager", "Fund manager"),
            ("fund_managers", "Fund managers"),
            ("expense_ratio", "Expense ratio"),
            ("min_sip", "Minimum SIP amount"),
            ("exit_load", "Exit load"),
            ("lock_in", "ELSS lock-in period"),
            ("riskometer", "Riskometer classification"),
            ("benchmark", "Benchmark index"),
            ("nav", "Latest NAV"),
            ("aum", "Fund size (AUM)"),
        ]
        for key, label in mapping:
            value = facts.get(key)
            if value:
                lines.append(f"{label}: {value}.")

        lines.append(
            "For scheme-specific factual details such as fund manager, expense ratio, "
            "exit load, minimum SIP, riskometer and benchmark, refer to this scheme fact card."
        )
        return "\n".join(lines)

    def build_chunks(self, cleaning_results: List[Dict]) -> List[Dict]:
        """Create one fact-card chunk per scheme page."""
        chunks = []
        for result in cleaning_results:
            if not result.get("success"):
                continue
            metadata = dict(result.get("metadata") or {})
            if metadata.get("source_type") == "static_knowledge":
                continue

            text = result.get("cleaned_text") or ""
            facts = self.extract(text, metadata)
            source_url = result.get("url") or metadata.get("url")
            card = self.to_fact_card(facts, source_url)

            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_id": 0,
                "total_chunks": 1,
                "chunk_size": len(card.split()),
                "source_url": source_url,
                "content_type": "fact_card",
            })
            # Attach extracted values as searchable metadata strings
            for key, value in facts.items():
                if value and key != "scheme_name":
                    chunk_metadata[f"fact_{key}"] = value

            chunks.append({"text": card, "metadata": chunk_metadata})
            logger.info(
                "Fact card for %s: expense=%s sip=%s exit=%s risk=%s bench=%s",
                facts.get("scheme_name"),
                facts.get("expense_ratio"),
                facts.get("min_sip"),
                facts.get("exit_load"),
                facts.get("riskometer"),
                facts.get("benchmark"),
            )
        return chunks
