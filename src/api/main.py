"""
Phase 6.3: Backend API
FastAPI backend for the Mutual Fund FAQ Assistant.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Mutual Fund FAQ Assistant API",
    description="RAG-based FAQ assistant for mutual fund schemes",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class QueryRequest(BaseModel):
    query: str

class SourceItem(BaseModel):
    url: str
    title: str
    subtitle: str

class QueryResponse(BaseModel):
    answer: str
    source: str
    sources: List[SourceItem] = []
    # Set when the question names no scheme and the user must pick one
    needs_scheme: bool = False
    scheme_options: List[str] = []
    last_updated: str
    chunks_retrieved: int
    tokens_used: int
    context_used: bool
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    message: str

class StatsResponse(BaseModel):
    indexed_chunks: int
    schemes: int

# Global pipeline instance (lazy loaded)
generation_pipeline = None


def get_pipeline():
    """Get or initialize the generation pipeline."""
    global generation_pipeline
    if generation_pipeline is None:
        try:
            from src.generation.generation_pipeline import GenerationPipeline
            from src.ingestion.config import VECTOR_INDEX_DIR
            generation_pipeline = GenerationPipeline(
                persist_directory=VECTOR_INDEX_DIR
            )
            logger.info("Generation pipeline initialized")
        except Exception as e:
            logger.error(f"Failed to initialize generation pipeline: {str(e)}")
            raise
    return generation_pipeline


def _apply_scheme_context(questions: List[str], resolver) -> List[str]:
    """
    Give scheme-less questions the nearest scheme named by a sibling question.

    Lets "Who is the fund manager and what is the expense ratio of HDFC Mid Cap
    Fund?" answer both parts about HDFC Mid Cap Fund. Questions that already name
    a scheme are left alone, including unknown ones, so they still get refused.
    """
    resolutions = [resolver.resolve(question) for question in questions]
    scheme_names = [resolution.get("scheme_name") for resolution in resolutions]

    contextual = []
    for index, question in enumerate(questions):
        if resolutions[index].get("mentioned"):
            contextual.append(question)
            continue
        neighbour = next(
            (name for name in reversed(scheme_names[:index]) if name), None
        ) or next((name for name in scheme_names[index + 1:] if name), None)
        contextual.append(
            f"{question.rstrip('? ')} for {neighbour}?" if neighbour else question
        )
    return contextual


def _describe_source(url: str, scheme: Optional[str]) -> SourceItem:
    """Turn a bare source URL into a titled entry for the sources panel."""
    if "groww.in" in url:
        title = scheme or url.rstrip("/").rsplit("/", 1)[-1].replace("-", " ").title()
        return SourceItem(url=url, title=title, subtitle="Groww scheme page")
    if "hdfcfund.com" in url:
        return SourceItem(
            url=url, title="HDFC Mutual Fund", subtitle="Investor services portal"
        )
    return SourceItem(url=url, title=url, subtitle="Reference")


def _answer_question(question: str, pipeline, refusal_handler) -> Dict:
    """Run refusal checks and the RAG pipeline for a single question."""
    refusal_result = refusal_handler.should_refuse(question)
    if refusal_result['should_refuse']:
        return {
            'answer': refusal_handler.generate_refusal_response(refusal_result),
            'source': '',
            'scheme': None,
            'needs_scheme': False,
            'scheme_options': [],
            'last_updated': '',
            'chunks_retrieved': 0,
            'tokens_used': 0,
            'context_used': False,
            'error': None,
        }

    result = pipeline.generate(question, top_k=3)

    if result.get('error'):
        logger.error(f"Generation error: {result['error']}")
        return {
            'answer': f"Error generating response: {result['error']}",
            'source': result.get('source') or '',
            'scheme': result.get('scheme'),
            'needs_scheme': False,
            'scheme_options': [],
            'last_updated': '',
            'chunks_retrieved': 0,
            'tokens_used': 0,
            'context_used': False,
            'error': result['error'],
        }

    return {
        'answer': result['response'],
        'source': result.get('source') or '',
        'scheme': result.get('scheme'),
        'needs_scheme': result.get('needs_scheme', False),
        'scheme_options': result.get('scheme_options', []),
        'last_updated': datetime.now().strftime("%Y-%m-%d"),
        'chunks_retrieved': result['chunks_retrieved'],
        'tokens_used': result['tokens_used'],
        'context_used': result['context_used'],
        'error': None,
    }


def _collect_sources(answers: List[Dict]) -> List[SourceItem]:
    """One entry per distinct source URL, in the order the answers cite them."""
    sources: List[SourceItem] = []
    seen = set()
    for answer in answers:
        url = answer.get('source')
        if url and url not in seen:
            seen.add(url)
            sources.append(_describe_source(url, answer.get('scheme')))
    return sources


def _combine_answers(questions: List[str], answers: List[Dict]) -> QueryResponse:
    """Merge per-question answers into one numbered response."""
    combined = "\n\n".join(
        f"{number}. {question}\n{answer['answer']}"
        for number, (question, answer) in enumerate(zip(questions, answers), start=1)
    )

    sources = []
    for answer in answers:
        if answer['source'] and answer['source'] not in sources:
            sources.append(answer['source'])

    # Only offer scheme buttons when the whole submission is waiting on one
    all_need_scheme = all(answer.get('needs_scheme') for answer in answers)

    return QueryResponse(
        answer=combined,
        source=", ".join(sources),
        sources=_collect_sources(answers),
        needs_scheme=all_need_scheme,
        scheme_options=answers[0].get('scheme_options', []) if all_need_scheme else [],
        last_updated=next(
            (a['last_updated'] for a in answers if a['last_updated']), ""
        ),
        chunks_retrieved=sum(a['chunks_retrieved'] for a in answers),
        tokens_used=sum(a['tokens_used'] for a in answers),
        context_used=any(a['context_used'] for a in answers),
        error=next((a['error'] for a in answers if a['error']), None),
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="API is running"
    )


@app.get("/stats", response_model=StatsResponse)
async def index_stats():
    """Size of the indexed corpus, shown in the sidebar."""
    try:
        pipeline = get_pipeline()
        indexer = pipeline.retrieval_pipeline.similarity_search.indexer
        return StatsResponse(
            indexed_chunks=indexer.get_stats().get("total_chunks", 0),
            schemes=len(pipeline.scheme_resolver.corpus_schemes),
        )
    except Exception as e:
        logger.error(f"Failed to read index stats: {str(e)}")
        return StatsResponse(indexed_chunks=0, schemes=0)


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process user query and return response.
    
    Args:
        request: Query request with user question
        
    Returns:
        Query response with answer, source, and metadata
    """
    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        logger.error("GROQ_API_KEY not found in environment")
        return QueryResponse(
            answer="GROQ_API_KEY not configured. Please set it in the environment.",
            source="",
            last_updated="",
            chunks_retrieved=0,
            tokens_used=0,
            context_used=False,
            error="GROQ_API_KEY not configured"
        )
    
    try:
        # Import query processing components
        from src.compliance.refusal_handler import RefusalHandler
        from src.query_processing.question_splitter import QuestionSplitter
        
        # Initialize components
        refusal_handler = RefusalHandler()
        pipeline = get_pipeline()
        
        # A submission may hold several questions; each is answered on its own
        questions = QuestionSplitter().split(request.query)
        logger.info(f"Answering {len(questions)} question(s)")
        
        to_answer = (
            _apply_scheme_context(questions, pipeline.scheme_resolver)
            if len(questions) > 1
            else questions
        )
        answers = [
            _answer_question(question, pipeline, refusal_handler)
            for question in to_answer
        ]
        
        if len(answers) == 1:
            answer = answers[0]
            return QueryResponse(
                answer=answer['answer'],
                source=answer['source'],
                sources=_collect_sources(answers),
                needs_scheme=answer['needs_scheme'],
                scheme_options=answer['scheme_options'],
                last_updated=answer['last_updated'],
                chunks_retrieved=answer['chunks_retrieved'],
                tokens_used=answer['tokens_used'],
                context_used=answer['context_used'],
                error=answer['error']
            )
        
        return _combine_answers(questions, answers)
    
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        return QueryResponse(
            answer="Module import error. Please ensure all required modules are installed.",
            source="",
            last_updated="",
            chunks_retrieved=0,
            tokens_used=0,
            context_used=False,
            error=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return QueryResponse(
            answer=f"Error processing query: {str(e)}",
            source="",
            last_updated="",
            chunks_retrieved=0,
            tokens_used=0,
            context_used=False,
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
