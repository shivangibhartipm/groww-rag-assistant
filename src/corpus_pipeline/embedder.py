"""
Phase 2.8: Embedder
Turns text into vectors with all-MiniLM-L6-v2 running on ONNX Runtime.
Consumes output from Chunker (chunks with text).

sentence-transformers was dropped in favour of ONNX Runtime for two reasons:
PyTorch holds roughly 500 MB resident, which does not fit the 512 MB the
backend is deployed on, and on Linux the default torch wheel drags in the CUDA
libraries for a GPU no deployment target has. The weights are identical, so
vectors produced here match the ones already in the index. ONNX Runtime also
arrives as a ChromaDB dependency, so this removes a dependency rather than
adding one.

There is deliberately no fallback path. An earlier version dropped to
hash-based vectors when the model would not load, which cannot match a real
index but kept the API answering, so a failed model load surfaced as confident
answers about the wrong scheme instead of an outage.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

try:
    import certifi
    # Prefer certifi CA bundle so Groq/httpx TLS verification keeps working.
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
    os.environ.setdefault("CURL_CA_BUNDLE", certifi.where())
except ImportError:
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_REPO = "sentence-transformers/all-MiniLM-L6-v2"

# Pinned so a re-download can never hand the API vectors the committed index was
# not built with. Bumping this means rebuilding data/vector_index.
MODEL_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"

MODEL_FILES = ("onnx/model.onnx", "tokenizer.json")
MODEL_DIR = Path(__file__).resolve().parents[2] / "models" / "all-MiniLM-L6-v2"

# From the model's sentence_bert_config.json, which is what sentence-transformers
# applied when the index was built. The shipped tokenizer.json disagrees: it
# carries truncation and fixed padding at 128, so the overrides in __init__ are
# what keep long chunks embedding the same way they did before.
MAX_SEQ_LENGTH = 256
EMBEDDING_DIM = 384


class EmbedderUnavailable(RuntimeError):
    """The embedding model could not be loaded, so no query can be answered."""


class Embedder:
    """Generates embeddings for chunks."""

    def __init__(
        self,
        model_name: str = MODEL_REPO,
        model_dir: Optional[Path] = None,
        batch_size: int = 32,
    ):
        """Load the ONNX model, or raise EmbedderUnavailable trying."""
        self.model_name = model_name
        self.model_dir = Path(model_dir) if model_dir else MODEL_DIR
        self.batch_size = batch_size
        self.embedding_dim = EMBEDDING_DIM

        missing = [n for n in MODEL_FILES if not (self.model_dir / n).exists()]
        if missing:
            raise EmbedderUnavailable(
                f"Missing {', '.join(missing)} under {self.model_dir}. "
                "Run: python scripts/fetch_model.py"
            )

        try:
            import onnxruntime as ort
            from tokenizers import Tokenizer
        except ImportError as exc:
            raise EmbedderUnavailable(f"Embedding runtime not installed: {exc}") from exc

        try:
            self.tokenizer = Tokenizer.from_file(str(self.model_dir / "tokenizer.json"))
            self.tokenizer.enable_truncation(max_length=MAX_SEQ_LENGTH)
            self.tokenizer.enable_padding()

            options = ort.SessionOptions()
            # One thread keeps the memory floor down and costs nothing on the
            # handful of short texts this ever embeds at once.
            options.intra_op_num_threads = 1
            options.inter_op_num_threads = 1

            self.session = ort.InferenceSession(
                str(self.model_dir / "onnx" / "model.onnx"),
                sess_options=options,
                providers=["CPUExecutionProvider"],
            )
            self._input_names = {i.name for i in self.session.get_inputs()}
        except Exception as exc:
            raise EmbedderUnavailable(f"Failed to load {model_name}: {exc}") from exc

        logger.info(f"Model loaded from {self.model_dir}. Dimension: {self.embedding_dim}")

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        """Embed texts into L2-normalised vectors, one row each."""
        if not texts:
            return np.zeros((0, self.embedding_dim), dtype=np.float32)

        batches = [
            self._encode_batch(list(texts[i:i + self.batch_size]))
            for i in range(0, len(texts), self.batch_size)
        ]
        return np.vstack(batches)

    def _encode_batch(self, texts: List[str]) -> np.ndarray:
        # Empty strings tokenize to just the special tokens, which the mean pool
        # below would divide by a near-zero count.
        encodings = self.tokenizer.encode_batch([t if t.strip() else " " for t in texts])

        attention_mask = np.array([e.attention_mask for e in encodings], dtype=np.int64)
        inputs = {
            "input_ids": np.array([e.ids for e in encodings], dtype=np.int64),
            "attention_mask": attention_mask,
            "token_type_ids": np.array([e.type_ids for e in encodings], dtype=np.int64),
        }
        inputs = {k: v for k, v in inputs.items() if k in self._input_names}

        token_embeddings = self.session.run(None, inputs)[0]

        # modules.json for this model is Transformer -> Pooling(mean) -> Normalize.
        # Padding is masked out of both the sum and the divisor.
        mask = attention_mask[:, :, None].astype(np.float32)
        summed = (token_embeddings * mask).sum(axis=1)
        counts = np.clip(mask.sum(axis=1), 1e-9, None)
        vectors = summed / counts

        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        return (vectors / np.clip(norms, 1e-12, None)).astype(np.float32)

    def embed_all(self, chunks: List[Dict]) -> List[Dict]:
        """
        Generate embeddings for all chunks.

        Args:
            chunks: List of chunk dictionaries from Chunker

        Returns:
            List of chunks with embeddings added
        """
        texts = [chunk.get('text', '') for chunk in chunks]

        logger.info(f"Generating embeddings for {len(texts)} chunks")
        embeddings = self.encode(texts)

        # Attach embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk['embedding'] = embedding.tolist()

        logger.info(f"Generated embeddings for {len(chunks)} chunks")
        return chunks

    def get_embedding_dimension(self) -> int:
        """Get embedding dimension."""
        return self.embedding_dim
