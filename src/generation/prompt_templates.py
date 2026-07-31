"""
Phase 3.3: Prompt Templates
System and user prompt templates for facts-only responses.
"""

import logging
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PromptTemplates:
    """Prompt templates for RAG generation."""
    
    SYSTEM_PROMPT = """You are a factual mutual fund assistant. Your role is to provide accurate, concise information based ONLY on the provided context.

STRICT RULES:
1. Provide ONLY factual information from the context
2. If the question names a specific scheme, answer ONLY about that scheme. Never substitute a different scheme.
3. Related-fund lists or comparison tables in the context are NOT facts about the asked scheme — ignore them.
4. For process/how-to questions (for example downloading statements), answer from the process guide in the context even if no scheme is named.
5. DO NOT give investment advice, recommendations, or opinions
6. DO NOT suggest which funds to buy or sell
7. DO NOT compare funds or make performance predictions
8. Keep responses to MAXIMUM 3 sentences
9. Do NOT invent facts (including lock-in periods) that are not explicitly in the context
10. If the answer is not in the context, say exactly: "I don't have information about this in my database."

Response format:
[Your 1-3 sentence factual answer]

Example:
The HDFC Mid Cap Fund has an expense ratio of 1.85% as per the latest factsheet."""

    USER_PROMPT_TEMPLATE = """Context:
{context}

Question: {query}

If the question names a scheme, answer ONLY about that scheme using facts from its context.
If the question is a process/how-to question, answer using the process steps in the context.
If those facts are missing, say you don't have the information."""

    @staticmethod
    def get_system_prompt() -> str:
        """Get the system prompt."""
        return PromptTemplates.SYSTEM_PROMPT
    
    @staticmethod
    def get_user_prompt(query: str, context: str) -> str:
        """
        Get the user prompt with query and context.
        
        Args:
            query: User question
            context: Retrieved context
            
        Returns:
            Formatted user prompt
        """
        return PromptTemplates.USER_PROMPT_TEMPLATE.format(
            context=context,
            query=query
        )
    
    @staticmethod
    def clean_response(response: str) -> str:
        """
        Strip inline source citations from a generated answer.
        
        Citations are returned separately in the API's `sources` field and
        rendered in their own panel, so the prose should not repeat them.
        
        Args:
            response: Generated response
            
        Returns:
            Response without "Source:" lines
        """
        lines = [
            line for line in response.split('\n')
            if not line.strip().lower().startswith('source:')
        ]
        return '\n'.join(lines).strip()
