"""
Phase 3.3: LLM Client
Groq API client for fast inference with Llama 3 8B model.
"""

import logging
from typing import Dict, Optional
import os
import ssl

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logging.warning("groq not installed. Install with: pip install groq")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _build_http_client():
    """Build an httpx client that trusts the OS certificate store when possible."""
    import httpx

    try:
        import truststore
        ctx = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        logger.info("Using OS trust store for Groq TLS")
        return httpx.Client(verify=ctx, timeout=60.0)
    except Exception as e:
        logger.warning(f"truststore unavailable ({e}); falling back to default TLS")
        return httpx.Client(timeout=60.0)


class GroqLLMClient:
    """Groq API client for LLM inference."""
    
    def __init__(self, model: str = "llama-3.1-8b-instant", api_key: str = None):
        """
        Initialize Groq LLM client.
        
        Args:
            model: Model name (llama3-8b-8192, mixtral-8x7b-32768, etc.)
            api_key: Groq API key (if None, reads from GROQ_API_KEY env var)
        """
        if not GROQ_AVAILABLE:
            raise ImportError("groq not installed. Install with: pip install groq")
        
        self.model = model
        
        if api_key is None:
            api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        self.client = Groq(api_key=api_key, http_client=_build_http_client())
        logger.info(f"Groq LLM client initialized with model: {model}")
    
    def generate(self, messages: list, temperature: float = 0.0, max_tokens: int = 500) -> str:
        """
        Generate response from Groq API.
        
        Args:
            messages: List of message dictionaries (role, content)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=60.0
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            raise
    
    def generate_with_context(self, query: str, context: str, system_prompt: str = None) -> str:
        """
        Generate response with query and context.
        
        Args:
            query: User query
            context: Retrieved context
            system_prompt: System prompt for the LLM
            
        Returns:
            Generated response
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        user_message = f"Context:\n{context}\n\nQuestion: {query}"
        messages.append({"role": "user", "content": user_message})
        
        return self.generate(messages)
