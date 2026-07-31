"""Rebuild the Groww corpus and refuse to publish an unusable index.

CorpusPipeline degrades quietly in ways that matter for an unattended job: a
failed embedder load is swallowed into a warning, and a partial scrape still
clears and rebuilds the index. Both produce a corpus that answers questions
wrongly instead of raising, so each case is turned into a non-zero exit here.
The scheduled workflow only commits when this script succeeds.

Run from the repo root:
    python scripts/refresh_corpus.py [--clean]
"""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.corpus_pipeline.pipeline import CorpusPipeline
from src.ingestion.config import SOURCE_URLS, VECTOR_INDEX_DIR

logger = logging.getLogger("refresh_corpus")

# One fact card per scheme page plus one static knowledge chunk
EXPECTED_CHUNKS = len(SOURCE_URLS)
SMOKE_QUERY = "What is the expense ratio of HDFC Mid Cap Fund?"
SMOKE_EXPECTS = "HDFC Mid Cap Fund"


def find_problems(summary: Dict, pipeline: CorpusPipeline) -> List[str]:
    """Reasons the freshly built corpus should not be published."""
    problems = []

    fetch = summary["phases"]["2.4_fetcher"]
    if fetch["successful"] < fetch["total"]:
        problems.append(
            f"only {fetch['successful']}/{fetch['total']} sources fetched"
        )

    indexed = (summary.get("final_stats") or {}).get("total_chunks", 0)
    if indexed < EXPECTED_CHUNKS:
        problems.append(f"indexed {indexed} chunks, expected {EXPECTED_CHUNKS}")

    # Catches an index that built cleanly but retrieves the wrong scheme
    results = pipeline.test_query(SMOKE_QUERY).get("results") or []
    top_text = results[0].get("text", "") if results else ""
    if SMOKE_EXPECTS not in top_text:
        problems.append(f"smoke query did not retrieve {SMOKE_EXPECTS!r}")

    return problems


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    parser = argparse.ArgumentParser(
        description="Rebuild and verify the Groww corpus."
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help=(
            "Delete the vector store before rebuilding. Indexer.clear() leaves "
            "orphaned segment directories behind, which pile up over daily runs."
        ),
    )
    args = parser.parse_args()

    if args.clean:
        store = REPO_ROOT / VECTOR_INDEX_DIR
        if store.exists():
            logger.info("Removing %s for a clean rebuild", store)
            shutil.rmtree(store)

    pipeline = CorpusPipeline(skip_embeddings=False)

    # Checked before scraping: without a working embedder there is no point
    # spending minutes fetching pages. Run scripts/fetch_model.py first.
    if pipeline.skip_embeddings:
        logger.error("Embedder or indexer unavailable; leaving the index alone")
        return 1

    summary = pipeline.run(rebuild_index=True)

    problems = find_problems(summary, pipeline)
    if problems:
        for problem in problems:
            logger.error("Corpus rejected: %s", problem)
        return 1

    stats = summary["final_stats"]
    logger.info(
        "Corpus refreshed: %s chunks in %s",
        stats["total_chunks"],
        stats["persist_directory"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
