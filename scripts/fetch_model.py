"""Download the embedding model so it is on disk before the first request.

The weights are not a pip package, so nothing in requirements.txt puts them on
the server. Without this step the first user query pays for a download, and a
download that fails leaves the API answering from an unusable model. Render
runs this in buildCommand and the refresh workflow runs it before rebuilding
the corpus, so by the time either serves traffic the files are already local.

Only the ONNX graph and the tokenizer are fetched; the PyTorch weights in the
same repo are several times larger and nothing loads them any more.

Run from the repo root:
    python scripts/fetch_model.py [--force]
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    import certifi

    # Matches the embedder: corporate TLS interception breaks the default trust
    # store on some machines, and huggingface_hub gives no useful error for it.
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
except ImportError:
    pass

from huggingface_hub import snapshot_download

from src.corpus_pipeline.embedder import (
    MODEL_DIR,
    MODEL_FILES,
    MODEL_REPO,
    MODEL_REVISION,
    Embedder,
)

logger = logging.getLogger("fetch_model")


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Download the embedding model.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if the model directory already looks complete.",
    )
    args = parser.parse_args()

    complete = all((MODEL_DIR / name).exists() for name in MODEL_FILES)
    if complete and not args.force:
        logger.info("Model already present at %s", MODEL_DIR)
    else:
        if args.force and MODEL_DIR.exists():
            shutil.rmtree(MODEL_DIR)

        logger.info("Downloading %s at %s", MODEL_REPO, MODEL_REVISION[:8])
        snapshot_download(
            repo_id=MODEL_REPO,
            revision=MODEL_REVISION,
            local_dir=str(MODEL_DIR),
            allow_patterns=list(MODEL_FILES),
        )

    # A present-but-corrupt download is worth catching here rather than on the
    # first query, so load the model and embed something.
    try:
        embedder = Embedder()
        vector = embedder.encode(["warm up the session"])[0]
    except Exception as exc:
        logger.error("Model downloaded but failed to load: %s", exc)
        return 1

    logger.info(
        "Model ready at %s (dimension %d, norm %.4f)",
        MODEL_DIR,
        vector.shape[0],
        float((vector**2).sum() ** 0.5),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
