# Phase-Wise Architecture: Mutual Fund FAQ Assistant

## Overview
This document outlines the detailed phase-wise architecture for building a Retrieval-Augmented Generation (RAG)-based FAQ assistant for mutual fund schemes. The system prioritizes accuracy, compliance, and transparency over conversational intelligence.

---

## Phase 1: Data Collection & Corpus Preparation

### 1.1 Source Selection
- **Select Asset Management Company (AMC)**: Choose one AMC (e.g., HDFC Mutual Fund, ICICI Prudential, SBI Mutual Fund)
- **Identify Official Sources**:
  - AMC official website
  - AMFI (Association of Mutual Funds in India)
  - SEBI (Securities and Exchange Board of India)
- **Curate URL List**:
  - https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth
  - https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth
  - https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth
  - https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth
  - https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth

### 1.2 Data Ingestion Pipeline
- **Web Scraper Implementation**:
  - Use `requests` + `BeautifulSoup` or `scrapy` for static pages
  - Use `selenium` or `playwright` for dynamic content if needed
  - Implement rate limiting and respectful crawling
- **Document Storage**:
  - Store raw HTML/JSON in `data/raw/` directory
  - Maintain metadata: URL, crawl timestamp, source type
- **Content Extraction**:
  - Extract main content from HTML
  - Remove navigation, footer, and non-relevant elements
  - Preserve tables, lists, and structured data

### 1.3 Quality Control
- **Validation Checks**:
  - Verify URL accessibility
  - Check for duplicate content
  - Validate document completeness
- **Source Verification**:
  - Ensure all sources are official (AMC, AMFI, SEBI)
  - Reject third-party blogs or aggregator sites

---

## Phase 2: Document Processing & Indexing

### 2.1 Text Preprocessing
- **Cleaning Pipeline**:
  - Remove HTML tags and special characters
  - Normalize whitespace
  - Handle special financial terms and symbols
- **Chunking Strategy**:
  - Split documents into semantically meaningful chunks (200-500 tokens)
  - Preserve context boundaries (paragraphs, sections)
  - Overlap chunks by 10-20% for context continuity
- **Metadata Enrichment**:
  - Attach source URL to each chunk
  - Add document type (factsheet, KIM, FAQ, etc.)
  - Include scheme name and category if applicable

### 2.2 Embedding Generation
- **Embedding Model Selection**:
  - Use lightweight, efficient model (`sentence-transformers/all-MiniLM-L6-v2`,
    served through ONNX Runtime rather than PyTorch — see Phase 9.2)
  - Alternative: OpenAI `text-embedding-3-small` if API access available
- **Batch Processing**:
  - Generate embeddings for all chunks
  - Store in vector format (e.g., numpy arrays)
- **Embedding Storage**:
  - Use vector database (ChromaDB, FAISS, or Weaviate)
  - Local storage preferred for privacy and cost
  - Index: `data/vector_index/`

### 2.3 Knowledge Base Construction
- **Vector Index Structure**:
  - Document ID
  - Chunk ID
  - Embedding vector
  - Source URL
  - Metadata (document type, scheme, last updated)
- **Index Optimization**:
  - Configure similarity search parameters (top-k, threshold)
  - Implement efficient retrieval algorithms (HNSW, IVF)

### 2.4 Corpus Pipeline Sub-Phases
**Implementation Order: 2.4 → 2.5 → 2.6 → 2.7 → 2.8 → 2.9**

- **2.4 Fetcher**:
  - Fetch HTML content from whitelisted Groww URLs
  - Implement rate limiting (2-second delay)
  - Return HTML with metadata (URL, timestamp, status)

- **2.5 Extractor**:
  - Extract main content from HTML
  - Remove navigation, footer, scripts, ads
  - Preserve tables, lists, and structured data
  - Output: main_text, tables, lists

- **2.6 Cleaner**:
  - Remove HTML tags and special characters
  - Normalize whitespace
  - Preserve financial patterns (%, ₹, dates, ratios)
  - Output: cleaned_text

- **2.7 Chunker**:
  - Split documents into 200-500 token chunks
  - Preserve paragraph/section boundaries
  - 15% overlap between chunks for context continuity
  - Output: chunks with metadata (chunk_id, source_url)

- **2.8 Embedder**:
  - Generate embeddings with `all-MiniLM-L6-v2` on ONNX Runtime, applying mean
    pooling and L2 normalisation over the model's own output (Phase 9.2)
  - Model revision is pinned; weights are fetched by `scripts/fetch_model.py`
  - Raises `EmbedderUnavailable` rather than degrading to unusable vectors
  - Batch processing for efficiency
  - Output: chunks with embedding vectors

- **2.9 Indexer**:
  - Build ChromaDB vector index
  - Store at `data/vector_index/`
  - Support similarity search with top-k and threshold
  - Output: queryable vector index

---

## Phase 3: RAG Pipeline Implementation

### 3.1 Retrieval Component
- **Query Processing**:
  - Accept user query as input
  - Generate query embedding using same model as corpus
- **Similarity Search**:
  - Perform vector similarity search in vector database
  - Retrieve top-k relevant chunks (k=3-5)
  - Apply relevance threshold (e.g., cosine similarity > 0.7)
- **Source Tracking**:
  - Extract source URLs from retrieved chunks
  - Rank chunks by relevance score

### 3.2 Context Assembly
- **Context Window Construction**:
  - Concatenate retrieved chunks into context
  - Limit context length to model's token limit
  - Preserve chunk boundaries and source information
- **Context Optimization**:
  - Remove redundant information across chunks
  - Prioritize recent information if dates available

### 3.3 Generation Component
- **LLM Selection**:
  - Use Groq API with Llama 3.1 8B model for fast, cost-effective inference
  - Groq provides high-speed inference with low latency
  - Model: llama-3.1-8b-instant or mixtral-8x7b-32768
- **Prompt Engineering**:
  - System prompt: Facts-only, no advice, concise responses
  - User prompt: Query + retrieved context
  - Output format: Response + source link + footer
- **Response Generation**:
  - Generate answer based on retrieved context
  - Enforce 3-sentence limit
  - Include exactly one source citation

---

## Phase 4: Query Processing & Response Generation

### 4.1 Query Classification
- **Intent Detection**:
  - Classify query as: Factual vs. Advisory vs. Out-of-scope
  - Use rule-based classification or lightweight classifier
- **Factual Query Patterns**:
  - Expense ratio, exit load, minimum SIP
  - Lock-in period, riskometer, benchmark
  - Document download processes
- **Advisory Query Patterns**:
  - "Should I invest?", "Which fund is better?"
  - Performance comparisons, return calculations

### 4.2 Response Formatting
- **Structure**:
  ```
  <Answer (max 3 sentences)>
  
  Source: <URL>
  
  Last updated from sources: <YYYY-MM-DD>
  ```
- **Constraints Enforcement**:
  - Sentence count validation
  - Source link presence check
  - Footer inclusion
- **Performance Queries**:
  - Detect performance-related queries
  - Return direct link to official factsheet only
  - No calculations or comparisons

### 4.3 Citation Management
- **Source Selection**:
  - Select most relevant source from retrieved chunks
  - Prefer official AMC documents over general guidance
  - Use most recent source if multiple available
- **Link Validation**:
  - Ensure source links are accessible
  - Format URLs for display

---

## Phase 5: Refusal Handling & Compliance

### 5.1 Advisory Query Detection
- **Intent patterns** (not bare keywords): detect asks for recommendations,
  suitability judgements, portfolio allocation ("how much to put/invest"),
  scheme comparisons (`vs` / `versus` / `better than`), and predicted returns.
- **Classification Logic**:
  - If advisory pattern detected → refuse immediately (before scheme
    clarification or retrieval)
  - If out-of-scope → refuse with educational link
  - Bare factual asks with no scheme named → scheme clarification (Phase 6)

### 5.2 Refusal Response Generation
- **Template**:
  ```
  I can only provide factual information about mutual funds and cannot offer investment advice or recommendations.
  
  For educational resources, please visit: <AMFI/SEBI educational link>
  ```
- **Educational Links**:
  - AMFI investor education: https://www.amfiindia.com/investor-education
  - SEBI investor education: https://investor.sebi.gov.in/

### 5.3 Compliance Layer
- **Content Filtering**:
  - Post-generation check for advisory language
  - Block responses containing recommendations
- **Disclaimer Enforcement**:
  - Ensure UI displays disclaimer prominently
  - Include disclaimer in system prompt

---

## Phase 6: User Interface Development

Reference design: `screens/GrowwRAGScreen.png`.

### 6.1 Frontend Architecture
- **Technology Stack**:
  - Framework: Next.js (App Router) + TypeScript
  - Styling: Tailwind CSS with Groww green tokens (`#00b386`)
  - Runtime: React client components for chat state; Next.js route handlers proxy the FastAPI backend
- **Location**: `frontend/` (sibling to the Python backend)
- **Design Principles**:
  - Facts-only chat surface with compliance pills and a persistent disclaimer
  - Multi-question submissions answered as numbered blocks in one card
  - Official sources shown as structured cards with View links
  - Questions naming no scheme prompt the user to pick one instead of guessing
  - Chat history, feedback and saved answers persisted in `localStorage`

### 6.2 UI Layout
```
┌──────────────┬──────────────────────────────────────────────────┐
│ Groww AI     │  Mutual Fund Assistant                           │
│ [+ New Chat] │  Facts Only · No Investment Advice · SEBI        │
│              │                                                  │
│ Recent Chats │  [ Ask anything about mutual funds...  🎤  ➤ ]  │
│  · ...       │  Popular: Fund Manager · Expense Ratio · ...     │
│              │                                                  │
│ Saved Answers│        ┌ user bubble (right) ┐                   │
│ About        │        └─────────────────────┘                   │
│              │  ┌ bot avatar ────────────────────────────────┐  │
│              │  │ Answer card (numbered Q&A)                 │  │
│              │  │ Sources (n)  [scheme · View]               │  │
│              │  │ Helpful · Not Helpful · Copy · Share · Save│  │
│ ┌ Facts Only┐│  │ You may also ask → follow-up cards         │  │
│ └───────────┘│  └────────────────────────────────────────────┘  │
│ Guest User   │  Groww AI can make mistakes. Verify from docs.   │
└──────────────┴──────────────────────────────────────────────────┘
```

Every sidebar control is interactive: New Chat, each recent chat (select or
delete), and the two entries that open dialogs. Nothing is rendered as a
decorative row. Deleting a chat also prunes its feedback and bookmarks, and
always leaves one chat in place to land on.

### 6.3 UI Components
| Component | Responsibility |
|---|---|
| `Sidebar` | Brand, New Chat, recent chats with delete, Saved Answers, About, Facts Only card, Guest User |
| `AssistantHeader` | Title, subtitle, compliance pills |
| `AskBar` | Multi-line question input, optional voice dictation, send |
| `QuickChips` | Popular Questions strip |
| `Conversation` | User bubbles, assistant cards, loading state, empty state |
| `AnswerCard` | Parses multi-question answers into headings and prose |
| `SourcesPanel` | Structured source list with View buttons |
| `FeedbackRow` | Helpful / Not Helpful / Copy / Share / Save |
| `FollowUps` | Contextual "You may also ask" suggestions |
| `SchemeChoice` | Scheme buttons shown when a question named no fund |
| `Modal` | Shared dialog shell (backdrop click and Escape to close) |
| `ConfirmDialog` | Confirmation for destructive actions such as deleting a chat |
| `SavedAnswersDialog` | Bookmarked answers with Open chat and Remove |
| `AboutDialog` | Corpus stats, what the assistant answers and refuses |

### 6.4 Backend Integration
- **Browser → Next.js** (same origin, no CORS):
  - `POST /api/query` → proxies to FastAPI `POST /query`
  - `GET /api/stats` → proxies to FastAPI `GET /stats`
- **Backend URL**: `BACKEND_URL` in `frontend/.env.local` (default `http://127.0.0.1:8000`)
- **Query response shape**:
  ```json
  {
    "answer": "1. Who is the fund manager of HDFC Mid Cap Fund?\nChirag Setalvad.\n\nSource: https://groww.in/...",
    "source": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "sources": [
      {
        "url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
        "title": "HDFC Mid Cap Fund",
        "subtitle": "Groww scheme page"
      }
    ],
    "needs_scheme": false,
    "scheme_options": [],
    "last_updated": "2026-07-31",
    "chunks_retrieved": 4,
    "tokens_used": 812,
    "context_used": true,
    "error": null
  }
  ```
- **Scheme clarification**: when the question names no fund and is not a
  process question, the pipeline skips retrieval and returns
  `needs_scheme: true` with `scheme_options` listing the corpus schemes. The UI
  renders these as buttons that re-ask the original question with the chosen
  fund appended. Multi-question submissions still inherit a scheme from a
  sibling question first, so only genuinely ambiguous asks prompt. Advisory and
  out-of-scope queries are refused first, so they never reach this prompt.
- **Stats response shape**:
  ```json
  { "indexed_chunks": 6, "schemes": 5 }
  ```

### 6.5 Running the Frontend
```bash
# Terminal 1 — FastAPI backend
uvicorn src.api.main:app --reload --port 8000

# Terminal 2 — Next.js frontend
cd frontend
npm install
npm run dev          # http://localhost:3000
```

---

## Phase 7: Testing & Validation

### 7.1 Unit Testing
- **Test Components**:
  - Document ingestion pipeline
  - Chunking logic
  - Embedding generation
  - Retrieval accuracy
  - Response generation
  - Refusal handling
- **Test Framework**:
  - `pytest` for Python backend
  - Next.js / React Testing Library for the frontend

### 7.2 Integration Testing
- **End-to-End Tests**:
  - Query → Retrieval → Generation → Response
  - Advisory query → Refusal
  - Performance query → Factsheet link
- **Test Cases**:
  - Factual queries (expense ratio, exit load, SIP)
  - Advisory queries (should I invest, which is better)
  - Edge cases (unknown schemes, ambiguous queries)

### 7.3 Quality Assurance
- **Accuracy Validation**:
  - Manual verification of 50+ sample queries
  - Cross-check responses against source documents
- **Compliance Check**:
  - Verify no advisory content in responses
  - Ensure all responses have source citations
  - Check footer inclusion
- **Performance Testing**:
  - Response time < 3 seconds
  - Retrieval accuracy > 85%

---

## Phase 8: Scheduled Corpus Refresh

Expense ratios, exit loads and fund managers change on the Groww pages, so the
corpus is rebuilt on a schedule rather than by hand.

### 8.1 Schedule
- **Workflow**: `.github/workflows/refresh-corpus.yml`
- **Cadence**: daily at **09:30 IST**, expressed as `cron: "0 4 * * *"` because
  GitHub schedules are UTC only and IST is UTC+5:30
- **Manual runs**: `workflow_dispatch` is enabled for an on-demand refresh
- **Caveats**:
  - GitHub queues scheduled jobs and may start them late under load; they never
    start early, so treat 09:30 as the earliest time
  - Scheduled workflows are suspended after 60 days without repository activity
  - A `concurrency` group prevents two rebuilds racing for the same commit

### 8.2 Job Steps
1. Check out the repository
2. Install Python 3.11 and `requirements.txt` (pip cached)
3. Restore the cached `models/` directory (keyed on the pinned model revision)
4. Run `python scripts/fetch_model.py`, a no-op on a cache hit
5. Run `python scripts/refresh_corpus.py --clean`
6. Commit `data/processed/` and `data/vector_index/` back to the repository

Step 4 is what keeps the corpus and the API in agreement: both embed with the
same pinned revision, so a scheduled rebuild cannot quietly reindex the corpus
under different weights than the backend serves with.

### 8.3 Verification Gate
`scripts/refresh_corpus.py` wraps `CorpusPipeline` because the pipeline degrades
quietly in ways that would otherwise publish a broken index. It exits non-zero,
leaving the committed index untouched, when any of these hold:

| Check | Failure it catches |
|---|---|
| `pipeline.skip_embeddings` is set | Embedder or indexer failed to initialise, including a missing or corrupt model download |
| Fetched sources < configured sources | A partial scrape rebuilding a thinned-out index |
| Indexed chunks < `len(SOURCE_URLS)` | Fact cards silently dropped |
| Smoke query fails to retrieve its scheme | An index that built cleanly but retrieves the wrong fund |

The first runs before the scrape, so a broken environment fails in seconds
instead of after fetching every page. `CorpusPipeline` swallows an
`EmbedderUnavailable` into a warning and sets `skip_embeddings`, which is why
the check is on that flag rather than on the exception.

`--clean` deletes `data/vector_index/` before rebuilding. `Indexer.clear()` only
drops the collection and leaves orphaned segment directories behind, which would
otherwise accumulate in the repository on every daily run.

### 8.4 Publishing
The commit step is skipped when `data/processed/` is byte-identical, so an
unchanged scheme page produces no commit. The rebuilt index carries fresh
ChromaDB record UUIDs on every run and would otherwise churn the history daily.

Deployments read `data/vector_index/` straight from the repository, so a
successful refresh reaches production on the next deploy. The pipeline never
calls the LLM, so the job needs no `GROQ_API_KEY` — only outbound access to
`groww.in` and HuggingFace.

---

## Phase 9: Deployment

Two independently deployed services: the FastAPI backend on **Render** and the
Next.js frontend on **Vercel**, both tracking the same GitHub repository. Both
run on the providers' free plans.

### 9.1 Topology

```
Browser
   │  HTTPS
   ▼
Vercel  ── Next.js app + /api/* route handlers ──┐
   (frontend/ as Root Directory)                 │ server-to-server
                                                 │ BACKEND_URL
                                                 ▼
                                    Render ── FastAPI (uvicorn)
                                                 │
                                                 ├── data/vector_index (from git)
                                                 └── Groq API (llama-3.1-8b-instant)
```

The browser never calls Render. `frontend/app/api/query/route.ts` and
`.../stats/route.ts` proxy server-side, so the backend URL and any future
credentials stay off the client and CORS never enters the picture.

No managed database is needed. The vector store is a 0.45 MB ChromaDB directory
committed to the repository, so the backend reads it straight from its checkout.

### 9.2 The 512 MB Constraint

Render's free instance provides **512 MB RAM / 0.1 CPU**. The backend did not
originally fit. `sentence-transformers` pulled in PyTorch purely to run a 90 MB
embedding model, and paying would not have helped: Render's Starter plan
($7/month) is *also* 512 MB, so the first tier with headroom was Standard at
$25/month. The default Linux `torch` wheel compounded it by bundling several GB
of CUDA libraries for a GPU no free instance has.

`src/corpus_pipeline/embedder.py` now runs `all-MiniLM-L6-v2` on ONNX Runtime
instead. Measured on the same machine, before and after:

| Stage | With PyTorch | With ONNX Runtime |
|---|---|---|
| Baseline interpreter | 27 MB | 22 MB |
| After loading the serving path and model | 472 MB | 211 MB |
| After answering one query | **517 MB** | **227 MB** |

That leaves roughly 285 MB of headroom on the free instance. `onnxruntime` was
already installed as a ChromaDB dependency, so the swap removed a dependency
tree rather than adding one; only `tokenizers` is genuinely new.

**The existing index stayed valid.** The ONNX export carries identical weights,
so vectors are unchanged to within float rounding — cosine similarity against
the `sentence-transformers` output is 1.0 across short, long and truncated
inputs, with a maximum element-wise difference of 1.6e-07. All eight retrieval
smoke queries return the same fact cards from the already-committed
`data/vector_index`, so no rebuild was required.

Two details the port has to get right, both encoded in `embedder.py`:

- **Pooling.** `modules.json` for this model is Transformer → Pooling(mean) →
  Normalize. The ONNX graph only covers the Transformer, so mean pooling over
  the attention mask and L2 normalisation are applied by hand afterwards.
- **Sequence length.** The shipped `tokenizer.json` carries truncation and
  fixed padding at 128 tokens, but `sentence_bert_config.json` — what
  `sentence-transformers` actually applied when the index was built — sets 256.
  `__init__` overrides the tokenizer to 256, without which long chunks would
  embed differently than they did originally.

### 9.2.1 No Fallback Path

The embedder previously dropped to MD5 hash vectors when the model failed to
load. Those vectors cannot match an index built from real embeddings, and
because `use_fallback` defaulted to `True` the whole way down
`RetrievalPipeline` → `QueryProcessor` → `Embedder`, a failed load surfaced not
as an outage but as confident answers about the wrong scheme. `/health` stayed
green throughout, and `similarity_search.py` applies no scheme metadata filter
that would have caught it.

That path is gone. `Embedder` raises `EmbedderUnavailable` naming the missing
files and the command that fixes them, and the `use_fallback` parameter has been
removed from every caller. A backend that cannot embed now refuses to start,
which is the correct outcome for a service whose answers are compliance-relevant.

### 9.2.2 Model Provisioning

The weights are not on PyPI, so `pip install` never puts them on the server.
`scripts/fetch_model.py` downloads the ONNX graph and tokenizer into `models/`
(gitignored, ~90 MB) and then loads them once to prove the download is usable.

It runs in Render's `buildCommand` and as a workflow step before the corpus
rebuild. Doing it at build time rather than lazily means the first request does
not wait on a download, a corrupt or blocked download fails the deploy instead
of the answers, and serving needs no network access to HuggingFace at all.

The revision is pinned to `1110a243…` in `embedder.py`. The corpus index and
the serving embedder must come from the same weights, so bumping that constant
means rebuilding `data/vector_index`.

### 9.3 Backend on Render

Configuration lives in `render.yaml` as a Render Blueprint:

| Setting | Value | Why |
|---|---|---|
| `runtime` | `python` | Native Python runtime, no Dockerfile needed |
| `plan` | `free` | 512 MB / 0.1 CPU, 750 instance-hours per month |
| `region` | `singapore` | Closest to India; Render defaults to Oregon |
| `buildCommand` | `pip install -r requirements.txt && python scripts/fetch_model.py` | Runtime dependencies, then the model weights, which are not a pip package |
| `startCommand` | `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT` | Render injects `$PORT`; the hardcoded `8000` in `__main__` never applies |
| `healthCheckPath` | `/health` | Does not build the pipeline, so it passes without waiting on the model |
| `GROQ_API_KEY` | `sync: false` | Set in the dashboard, never committed |

The Python version comes from `.python-version` (3.11). This matters: Render
defaults new services to Python 3.14, which this dependency set predates.

Setup steps:
1. Render → **New** → **Blueprint** → connect this repository. Render reads
   `render.yaml` and provisions the service.
2. Set `GROQ_API_KEY` on the service's Environment page.
3. Wait for the first build, then confirm `GET /health` responds and
   `GET /stats` returns `{"indexed_chunks": 6, "schemes": 5}`.

Working directory matters: `load_dotenv()` and the relative `data/vector_index`
path both resolve against the process CWD. Render runs from the repository
root, which is what the code expects. A wrong CWD does not error — ChromaDB
silently creates an empty index and every answer becomes "no information".

### 9.4 Frontend on Vercel

| Setting | Value |
|---|---|
| Root Directory | `frontend` |
| Framework Preset | Next.js (auto-detected) |
| Build / Install | Defaults (`next build`, `npm install`) |
| Environment Variable | `BACKEND_URL` = the Render service URL, no trailing slash |

`BACKEND_URL` is read server-side, so it must **not** be prefixed with
`NEXT_PUBLIC_` and must be set for the environments you deploy (Production and
Preview).

Because Root Directory is `frontend`, Vercel ignores commits that only touch
paths outside it — the daily corpus commits from Phase 8 do not trigger
pointless frontend rebuilds.

`app/api/query/route.ts` declares `maxDuration = 60` and aborts its upstream
fetch at 55s. Vercel terminates a route handler that overruns its limit, which
would surface as a platform error page rather than the handled 503 the UI knows
how to render. Section 9.7 covers why that 60s ceiling interacts badly with a
cold Render instance.

### 9.5 First Deploy Order

Render must exist before Vercel can be configured, because Vercel needs the
backend URL:

1. Push the repository to GitHub (the root is not yet a git repository).
2. Deploy the backend on Render via the Blueprint and note its URL.
3. Verify `/health` and `/stats` directly against that URL.
4. Deploy the frontend on Vercel with `BACKEND_URL` pointing at it.
5. Ask a factual question end to end, then an advisory one, and confirm the
   refusal path still fires.

### 9.6 Continuous Deployment

Both platforms redeploy on push to the default branch, which closes the loop
with Phase 8:

```
09:30 IST  GitHub Actions rebuilds and verifies the corpus
           └─ commits data/ only when the scheme facts changed
              └─ Render redeploys with the fresh index
                 └─ Vercel skips the build (nothing under frontend/ changed)
```

A refused corpus rebuild commits nothing, so a bad scrape can never reach
production.

### 9.7 Cold Starts

Render free instances spin down after **15 minutes** without traffic, and two
delays then stack on the next request:

1. Container spin-up, roughly 1 minute.
2. Lazy pipeline construction in `get_pipeline()`, which loads the embedding
   model on the first `/query` or `/stats`. This is a local ONNX session over
   files already on disk from the build, not a download, so it is seconds
   rather than the minute-plus a cold HuggingFace fetch would cost.

Combined, the first request after idle can exceed the 60s ceiling on Vercel's
route handler, so the user sees a handled 503 rather than an answer.

Two things soften this. The frontend calls `/stats` on page load, so opening the
app starts warming the backend before anyone types. And a keep-alive ping from
an external scheduler every 10–14 minutes prevents spin-down entirely — Render
grants 750 instance-hours per month, and a month of continuous uptime is 720,
so a single always-on free service stays within the allowance.

### 9.8 Operational Notes

- **Cost**: Render free covers the backend and Vercel Hobby covers the
  frontend, so the running cost is zero. Vercel Hobby is licensed for
  non-commercial use.
- **Exposure**: the Render URL is public and unauthenticated. Anyone who finds
  it can spend the Groq quota. A shared secret header checked by FastAPI and
  sent by the Next.js proxy would close this.
- **CORS**: `allow_origins=["*"]` with `allow_credentials=True` is currently
  set. Browsers reject that combination outright, and nothing needs it now that
  all traffic is server-to-server; it should be narrowed or removed.
- **Secrets**: `GROQ_API_KEY` lives in Render's environment settings and in the
  local `.env`, which the root `.gitignore` excludes. It is never needed by
  Vercel or by the Phase 8 workflow.
- **Throughput**: 0.1 CPU is shared and slow. Expect several seconds per query
  once warm, dominated by query embedding and the Groq round trip.

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│  (Next.js + TypeScript + Tailwind)                           │
│  - Sidebar · Ask bar · Popular chips                         │
│  - Conversation · Answer card · Sources · Feedback           │
│  - Compliance pills · Facts Only disclaimer                  │
└────────────────────┬────────────────────────────────────────┘
                     │ Same-origin /api/* proxies
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  (FastAPI)                                                   │
│  - Question splitting · Scheme resolution                    │
│  - Query Classification · Retrieval · Generation             │
│  - Structured sources · /stats                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    RAG Pipeline                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Query      │    │  Retrieval   │    │ Generation   │  │
│  │ Processing   │───▶│   Engine     │───▶│   Engine      │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                  │                   │            │
│         ▼                  ▼                   ▼            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Intent     │    │   Vector     │    │    LLM       │  │
│  │ Classifier   │    │   Database   │    │  (GPT/Llama) │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Knowledge Base                            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Document   │    │   Chunking   │    │  Embedding   │  │
│  │   Store      │───▶│   Engine     │───▶│   Model      │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
│  Sources: AMC, AMFI, SEBI documents                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Stack Summary

### Backend
- **Language**: Python 3.11 (pinned in `.python-version`)
- **Web Framework**: FastAPI
- **RAG Components**:
  - Hand-rolled orchestration in `src/`, no LangChain or LlamaIndex
  - `all-MiniLM-L6-v2` on ONNX Runtime for embeddings
  - ChromaDB for vector storage
- **LLM**: Llama 3.1 8B Instant via the Groq API

### Frontend
- **Framework**: Next.js (App Router) + TypeScript + React
- **Styling**: Tailwind CSS (Groww green design tokens)
- **Location**: `frontend/`

### Data Storage
- **Vector DB**: ChromaDB (local) or FAISS
- **Document Store**: Local file system (JSON/Parquet)

### DevOps
- **Version Control**: Git
- **Environment**: Virtual environment (venv/conda)
- **Testing**: pytest
- **Scheduling**: GitHub Actions cron, daily at 09:30 IST (Phase 8)
- **Hosting**: Render (FastAPI backend) + Vercel (Next.js frontend), Phase 9

---

## Project Structure

```
RAGAssistantGroww/
├── .github/
│   └── workflows/
│       └── refresh-corpus.yml  # Daily 09:30 IST corpus rebuild
├── data/
│   ├── raw/              # Raw scraped documents
│   ├── processed/        # Cleaned and chunked documents
│   └── vector_index/     # Vector database
├── models/               # Embedding weights, gitignored, fetched at build
├── scripts/
│   ├── fetch_model.py    # Downloads the pinned ONNX model and tokenizer
│   └── refresh_corpus.py # Guarded rebuild used by the scheduler
├── src/
│   ├── corpus_pipeline/  # Fetch, extract, chunk, embed, index
│   ├── query_processing/ # Scheme resolution, question splitting
│   ├── retrieval/        # Vector search and context assembly
│   ├── generation/       # LLM integration and generation
│   └── api/              # FastAPI endpoints (/query, /stats, /health)
├── frontend/             # Next.js UI (App Router + Tailwind)
│   ├── app/              # Pages and /api proxy routes
│   ├── components/       # Sidebar, AskBar, Conversation, ...
│   └── lib/              # Types, API client, answer parser
├── screens/
│   └── GrowwRAGScreen.png
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
│   ├── problemstatement.md
│   └── architecture.md   # This document
├── render.yaml           # Render Blueprint for the backend service
├── .python-version       # Pins Python 3.11 for Render
├── requirements.txt      # Runtime dependencies (API + corpus pipeline)
├── requirements-dev.txt  # pytest and the legacy Streamlit UI
├── README.md
└── .env                  # GROQ_API_KEY, excluded by .gitignore
```

---

## Security & Privacy Considerations

### Data Privacy
- No collection of PII (PAN, Aadhaar, phone, email)
- No account numbers or OTPs
- Local processing preferred over cloud APIs

### Compliance
- No investment advice or recommendations
- Source attribution for all responses
- Clear disclaimer in UI

### Access Control
- Rate limiting on API endpoints
- Input sanitization to prevent injection attacks
- HTTPS for all communications

---

## Success Metrics

### Functional Metrics
- **Accuracy**: >85% correct factual responses
- **Retrieval Precision**: >80% relevant chunks in top-3
- **Response Time**: <3 seconds per query
- **Refusal Accuracy**: 100% for advisory queries

### Compliance Metrics
- **Source Citation**: 100% of responses include source link
- **Disclaimer**: Always visible in UI
- **Advisory Content**: 0% advisory responses

### User Experience Metrics
- **UI Clarity**: Clean, minimal interface
- **Example Quality**: 3 relevant example questions
- **Error Handling**: Graceful failure messages

---

## Future Enhancements (Out of Scope)

1. **Multi-AMC Support**: Expand beyond single AMC
2. **Natural Language Queries**: Support conversational follow-ups
3. **Document Updates**: Automated re-crawling and re-indexing
4. **Analytics**: Query logging and popular topics
5. **Multi-language Support**: Support regional languages
6. **Mobile App**: Native mobile application

---

## Conclusion

This architecture provides a phased approach to building a compliant, accurate, and user-friendly mutual fund FAQ assistant. The system prioritizes factual accuracy over conversational intelligence, ensuring users receive only verified, source-backed information without any advisory bias.
