"""
Phase 3.3: Response Generator
Generates factual responses using Groq LLM with retrieved context.
"""

import logging
from typing import Dict, Optional

from .llm_client import GroqLLMClient
from .prompt_templates import PromptTemplates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResponseGenerator:
    """Generates factual responses using Groq LLM."""
    
    def __init__(self, model: str = "llama3-8b-8192", api_key: str = None):
        """
        Initialize response generator.
        
        Args:
            model: Groq model name
            api_key: Groq API key
        """
        self.llm_client = GroqLLMClient(model=model, api_key=api_key)
        self.prompt_templates = PromptTemplates()
        logger.info("Response generator initialized")
    
    def generate_response(self, query: str, context: str, source_url: str) -> Dict:
        """
        Generate a factual response based on query and context.
        
        Args:
            query: User query
            context: Retrieved context
            source_url: Source URL to cite
            
        Returns:
            Generated response with metadata
        """
        if not context:
            return {
                'response': "I don't have information about this in my database.",
                'source': source_url,
                'error': None,
                'context_used': False
            }
        
        try:
            # Get prompts
            system_prompt = self.prompt_templates.get_system_prompt()
            user_prompt = self.prompt_templates.get_user_prompt(query, context)
            
            # Generate response
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            raw_response = self.llm_client.generate(messages, temperature=0.0, max_tokens=200)
            
            # Citations are returned separately, so keep the prose URL-free
            cleaned_response = self.prompt_templates.clean_response(raw_response)
            
            # Enforce sentence limit (3 sentences max)
            final_response = self._enforce_sentence_limit(cleaned_response, max_sentences=3)
            
            return {
                'response': final_response,
                'source': source_url,
                'error': None,
                'context_used': True,
                'raw_response': raw_response
            }
            
        except Exception as e:
            logger.error(f"Response generation error: {str(e)}")
            return {
                'response': "I encountered an error generating a response. Please try again.",
                'source': source_url,
                'error': str(e),
                'context_used': False
            }
    
    def _enforce_sentence_limit(self, text: str, max_sentences: int = 3) -> str:
        """
        Enforce maximum sentence limit.
        
        Args:
            text: Input text
            max_sentences: Maximum number of sentences
            
        Returns:
            Text with sentence limit enforced
        """
        import re
        
        # Split on sentence end punctuation that is followed by whitespace/end,
        # so domains like groww.in are not treated as sentence breaks.
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        return ' '.join(sentences[:max_sentences]).strip()
    
    def generate_with_retrieval(self, query: str, retrieval_result: Dict) -> Dict:
        """
        Generate response using retrieval result.
        
        Args:
            query: User query
            retrieval_result: Result from retrieval pipeline
            
        Returns:
            Generated response
        """
        # Extract context and source from retrieval result
        context = retrieval_result.get('context', '')
        sources = retrieval_result.get('sources', [])
        source_url = sources[0] if sources else "Unknown"
        
        return self.generate_response(query, context, source_url)
