"""
Phase 3.3: Generation Pipeline
Orchestrates LLM-based response generation with retrieved context.
"""

import logging
from typing import Dict, List, Optional

from .llm_client import DEFAULT_MODEL
from .response_generator import ResponseGenerator
from ..retrieval.retrieval_pipeline import RetrievalPipeline
from ..query_processing.scheme_resolver import SchemeResolver
from ..query_processing.citation_manager import CitationManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


NO_INFO_RESPONSE = "I don't have information about this in my database."
CLARIFY_PROMPT = (
    "Which scheme is your question about? "
    "Please pick one of the funds I have information on:"
)


class GenerationPipeline:
    """Orchestrates the generation component of RAG pipeline."""
    
    def __init__(self, 
                 model: str = DEFAULT_MODEL,
                 api_key: str = None,
                 collection_name: str = "groww_corpus",
                 persist_directory: str = None):
        """
        Initialize generation pipeline.
        
        Args:
            model: Groq model name
            api_key: Groq API key
            collection_name: Name of the vector collection
            persist_directory: Directory for vector database
        """
        self.retrieval_pipeline = RetrievalPipeline(
            collection_name=collection_name,
            persist_directory=persist_directory
        )
        self.response_generator = ResponseGenerator(model=model, api_key=api_key)
        self.scheme_resolver = SchemeResolver()
        self.citation_manager = CitationManager()
        
        logger.info("Generation pipeline initialized")
    
    def generate(self, query: str, top_k: int = 5) -> Dict:
        """
        Generate a complete response for a query.
        
        Args:
            query: User query
            top_k: Number of chunks to retrieve
            
        Returns:
            Complete response with metadata
        """
        logger.info(f"Generating response for query: {query[:50]}...")
        
        scheme = self.scheme_resolver.resolve(query)
        process_query = self._is_process_query(query)
        
        # Unknown fund mentioned → do not invent an answer from other schemes
        if scheme["mentioned"] and not scheme["known"]:
            return self._no_info_result(
                query,
                reason=f"Unknown scheme mentioned: {scheme.get('raw_match')}"
            )
        
        # No scheme named → ask which fund rather than answering about a random one.
        # Process questions (statement downloads) apply to every scheme, so they pass.
        if not scheme["mentioned"] and not process_query:
            return self._needs_scheme_result(query)
        
        # Retrieve more candidates when we need to filter by scheme
        retrieve_k = max(top_k, 8) if scheme.get("scheme_name") else top_k
        retrieval_result = self.retrieval_pipeline.retrieve(query, top_k=retrieve_k)
        
        chunks = list(retrieval_result.get('results') or [])
        
        # Always make static knowledge available for process / scheme-scoped queries,
        # even when vector search returns nothing above threshold.
        if scheme.get("scheme_name") or process_query:
            static_chunks = self.retrieval_pipeline.similarity_search.indexer.get_by_metadata(
                {"source_type": "static_knowledge"}
            )
            if not static_chunks:
                static_chunks = self.retrieval_pipeline.similarity_search.indexer.get_by_metadata(
                    {"content_type": "static_knowledge"}
                )
            merged = {c.get('id'): c for c in chunks}
            for chunk in static_chunks:
                merged[chunk.get('id')] = chunk
            chunks = list(merged.values())
        
        if not chunks:
            return self._no_info_result(query, reason=retrieval_result.get('error') or 'No relevant chunks found')
        
        if scheme.get("scheme_name"):
            chunks = self.scheme_resolver.filter_chunks(chunks, scheme["scheme_name"])
            if not chunks:
                return self._no_info_result(
                    query,
                    reason=f"No chunks for scheme {scheme['scheme_name']}",
                    source=scheme.get("source_url"),
                )
        elif process_query:
            # Prefer the statement-download guide for process questions
            static_only = [
                c for c in chunks
                if (c.get('metadata') or {}).get('source_type') == 'static_knowledge'
                or (c.get('metadata') or {}).get('content_type') == 'static_knowledge'
            ]
            if static_only:
                chunks = static_only
        
        context_result = self.retrieval_pipeline.context_assembly.assemble_context(chunks)
        
        if not context_result.get('context'):
            return self._no_info_result(query, source=scheme.get("source_url"))
        
        # Prefer the scheme's own Groww page when answering scheme-specific facts
        source_url = scheme.get("source_url") or self._select_source(
            context_result.get('chunks') or chunks,
            fallback=None,
        )
        if process_query and not scheme.get("source_url"):
            source_url = "https://www.hdfcfund.com/"
        
        generation_result = self.response_generator.generate_response(
            query,
            context_result['context'],
            source_url
        )
        
        response_text = generation_result['response']
        
        # Reject cross-scheme answers (e.g. answering ELSS Tax Saver for Flexi Cap)
        if scheme.get("scheme_name") and self._mentions_other_scheme(
            response_text, scheme["scheme_name"]
        ):
            logger.warning(
                "Rejected cross-scheme answer for %s", scheme["scheme_name"]
            )
            return self._no_info_result(
                query,
                reason="Cross-scheme answer rejected",
                source=scheme.get("source_url") or source_url,
            )
        
        if NO_INFO_RESPONSE.lower() in response_text.lower() and scheme.get("source_url"):
            source_url = scheme["source_url"]
            response_text = NO_INFO_RESPONSE
        
        final_result = {
            'query': query,
            'response': response_text,
            'source': source_url,
            'context_used': generation_result['context_used'],
            'chunks_retrieved': context_result['chunks_used'],
            'tokens_used': context_result['total_tokens'],
            'error': generation_result.get('error'),
            'scheme': scheme.get('scheme_name'),
        }
        
        logger.info(f"Response generated: {len(final_result['response'])} chars")
        return final_result
    
    def _is_process_query(self, query: str) -> bool:
        q = query.lower()
        keywords = [
            "download", "statement", "capital gains", "account statement",
            "how to get", "how do i get", "report"
        ]
        return any(k in q for k in keywords)
    
    def _mentions_other_scheme(self, answer: str, expected_scheme: str) -> bool:
        """True if answer clearly names a different corpus scheme."""
        answer_l = answer.lower()
        expected_l = expected_scheme.lower()
        for name in self.scheme_resolver.corpus_schemes:
            if name.lower() == expected_l:
                continue
            if name.lower() in answer_l:
                return True
        return False
    
    def _select_source(self, chunks: List[Dict], fallback: Optional[str] = None) -> str:
        selected = self.citation_manager.select_source(chunks)
        url = selected.get('source_url') or fallback
        if url and str(url).startswith('static://'):
            return "https://www.hdfcfund.com/"
        return url or fallback or "Unknown"
    
    def _needs_scheme_result(self, query: str) -> Dict:
        """Ask which fund the question is about instead of guessing one."""
        options = sorted(self.scheme_resolver.corpus_schemes)
        logger.info("Clarification requested: no scheme named in query")
        return {
            'query': query,
            'response': f"{CLARIFY_PROMPT}\n" + "\n".join(
                f"- {name}" for name in options
            ),
            'source': None,
            'needs_scheme': True,
            'scheme_options': options,
            'context_used': False,
            'chunks_retrieved': 0,
            'tokens_used': 0,
            'error': None,
        }
    
    def _no_info_result(self, query: str, reason: str = None, source: str = None) -> Dict:
        if reason:
            logger.info("No-info response: %s", reason)
        source_url = source or ""
        return {
            'query': query,
            'response': NO_INFO_RESPONSE,
            'source': source_url or None,
            'context_used': False,
            'chunks_retrieved': 0,
            'tokens_used': 0,
            'error': None,
        }


def main():
    """Main entry point for testing generation pipeline."""
    import os
    if not os.getenv("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY environment variable not set")
        print("Please set it with: export GROQ_API_KEY=your_api_key")
        return
    
    pipeline = GenerationPipeline()
    
    test_queries = [
        "What is the expense ratio?",
        "What is the minimum investment amount?",
        "What is the fund category?"
    ]
    
    print("="*60)
    print("GENERATION PIPELINE TEST")
    print("="*60)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        
        result = pipeline.generate(query, top_k=3)
        
        print(f"Response:\n{result['response']}")
        print(f"\nMetadata:")
        print(f"  Chunks retrieved: {result['chunks_retrieved']}")
        print(f"  Tokens used: {result['tokens_used']}")
        print(f"  Context used: {result['context_used']}")
        if result.get('error'):
            print(f"  Error: {result['error']}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
