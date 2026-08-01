"""
Phase 3.3: LLM Client
Groq API client for fast inference with the GPT-OSS 120B model.
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

# Groq shuts down llama-3.1-8b-instant and llama-3.3-70b-versatile on 2026-08-16.
# https://console.groq.com/docs/deprecations
DEFAULT_MODEL = "openai/gpt-oss-120b"

# GPT-OSS is a reasoning model: it spends tokens thinking before it answers, and
# those tokens come out of the same budget as the answer. Too small a budget and
# the reply is truncated to nothing.
DEFAULT_MAX_COMPLETION_TOKENS = 1024


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
    
    def __init__(self, model: str = DEFAULT_MODEL, api_key: str = None):
        """
        Initialize Groq LLM client.
        
        Args:
            model: Model name (openai/gpt-oss-120b, openai/gpt-oss-20b, etc.)
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
    
    def generate(self,
                 messages: list,
                 temperature: float = 0.0,
                 max_completion_tokens: int = DEFAULT_MAX_COMPLETION_TOKENS,
                 reasoning_effort: Optional[str] = "low") -> str:
        """
        Generate response from Groq API.
        
        Args:
            messages: List of message dictionaries (role, content)
            temperature: Sampling temperature
            max_completion_tokens: Token ceiling, covering reasoning and answer
            reasoning_effort: low/medium/high; None for non-reasoning models
            
        Returns:
            Generated response text
        """
        # GPT-OSS rejects reasoning_format and instead puts its thinking in a
        # separate `reasoning` field, so `content` is already answer-only.
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_completion_tokens": max_completion_tokens,
            "include_reasoning": False,
            "timeout": 60.0,
        }
        if reasoning_effort:
            params["reasoning_effort"] = reasoning_effort
        
        try:
            response = self.client.chat.completions.create(**params)
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            raise
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError(
                "Groq returned an empty message; reasoning may have exhausted "
                f"max_completion_tokens={max_completion_tokens}"
            )
        
        return content
    
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
