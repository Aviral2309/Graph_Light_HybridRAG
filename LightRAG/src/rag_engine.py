import os
from functools import partial

from dotenv import load_dotenv

from lightrag import (
    LightRAG,
    QueryParam,
)

from lightrag.base import EmbeddingFunc

from lightrag.llm.gemini import (
    gemini_embed,
    gemini_model_complete,
)

from src.tokenizer import make_tokenizer

# ----------------------------------------------------------------------
# Environment Setup
# ----------------------------------------------------------------------

load_dotenv()


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

LLM_MODEL = "gemini-2.5-flash"

EMBED_MODEL = "gemini-embedding-001"

WORKING_DIR = "rag_storage"


# ----------------------------------------------------------------------
# Build LightRAG Instance
# ----------------------------------------------------------------------


def build_rag() -> LightRAG:
    """
    Create and configure a LightRAG instance.

    Components:
    - Gemini LLM
    - Gemini embeddings
    - Custom tokenizer
    - Persistent storage directory
    """

    # ------------------------------------------------------------------
    # LLM Completion Function
    # ------------------------------------------------------------------
    llm_func = partial(
        gemini_model_complete,
        api_key=GEMINI_API_KEY,
    )

    # ------------------------------------------------------------------
    # Embedding Function
    # ------------------------------------------------------------------
    embed_func = EmbeddingFunc(
        embedding_dim=3072,
        max_token_size=2048,
        func=partial(
            gemini_embed.func,
            api_key=GEMINI_API_KEY,
        ),
    )

    # ------------------------------------------------------------------
    # Initialize LightRAG
    # ------------------------------------------------------------------
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=llm_func,
        llm_model_name=LLM_MODEL,
        embedding_func=embed_func,
        tokenizer=make_tokenizer(),
    )

    return rag
