"""
Split a user submission containing several questions into individual questions.
"""

import logging
import re
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuestionSplitter:
    """Breaks multi-question input into separately answerable questions."""

    # Bound fan-out so one submission cannot trigger unlimited LLM calls
    MAX_QUESTIONS = 5
    MIN_WORDS = 2

    _LIST_MARKER_RE = re.compile(r"^\s*(?:\d+[\.\)]|[-*•])\s*")

    # Keeps the '?' with the question it terminates
    _SENTENCE_RE = re.compile(r"[^?]+\?|[^?]+$")

    # "... and what is ..." starts a new question; "... and exit load" does not
    _CONJUNCTION_RE = re.compile(
        r"\s*[,;]?\s*\b(?:and|also|&)\b\s+"
        r"(?=(?:what|which|who|whom|whose|when|where|how|why|do|does|did|is|are"
        r"|can|could|should|will|would|has|have)\b)",
        re.IGNORECASE,
    )

    def split(self, text: str) -> List[str]:
        """Return the individual questions in `text`, in the order asked."""
        if not text or not text.strip():
            return []

        questions: List[str] = []
        for line in re.split(r"[\r\n]+", text):
            line = self._LIST_MARKER_RE.sub("", line).strip()
            if not line:
                continue
            for sentence in self._SENTENCE_RE.findall(line):
                for part in self._CONJUNCTION_RE.split(sentence):
                    part = self._LIST_MARKER_RE.sub("", part).strip()
                    if self._is_answerable(part):
                        questions.append(self._tidy(part))

        deduped: List[str] = []
        seen = set()
        for question in questions:
            key = question.lower().rstrip("?. ")
            if key not in seen:
                seen.add(key)
                deduped.append(question)

        if len(deduped) > self.MAX_QUESTIONS:
            logger.info(
                "Capping %d detected questions at %d", len(deduped), self.MAX_QUESTIONS
            )
            deduped = deduped[: self.MAX_QUESTIONS]

        # A single question means the original text, untouched
        return deduped or [text.strip()]

    @staticmethod
    def _tidy(part: str) -> str:
        """Make a mid-sentence fragment read as a standalone question."""
        part = part[0].upper() + part[1:]
        return part if part.endswith("?") else f"{part.rstrip('.')}?"

    def _is_answerable(self, part: str) -> bool:
        """Filter out trailing fragments like 'Thanks' or stray punctuation."""
        words = re.findall(r"[A-Za-z0-9]+", part)
        return len(words) >= self.MIN_WORDS
