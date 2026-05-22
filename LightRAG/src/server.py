from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    HTTPException,
)

from pydantic import BaseModel

from lightrag import QueryParam

from src.rag_engine import build_rag

# ----------------------------------------------------------------------
# Global RAG Instance
# ----------------------------------------------------------------------

rag = None


# ----------------------------------------------------------------------
# FastAPI Lifespan Management
# ----------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize LightRAG when the API starts
    and finalize storage on shutdown.
    """

    global rag

    # ------------------------------------------------------------------
    # Build RAG engine
    # ------------------------------------------------------------------
    rag = build_rag()

    # ------------------------------------------------------------------
    # Initialize storage systems
    # ------------------------------------------------------------------
    await rag.initialize_storages()

    yield

    # ------------------------------------------------------------------
    # Cleanup storage
    # ------------------------------------------------------------------
    await rag.finalize_storages()


# ----------------------------------------------------------------------
# FastAPI App
# ----------------------------------------------------------------------

app = FastAPI(
    title="LightRAG API",
    lifespan=lifespan,
)


# ----------------------------------------------------------------------
# Supported Query Modes
# ----------------------------------------------------------------------

VALID_MODES = [
    "naive",
    "local",
    "global",
    "hybrid",
    "mix",
]


# ----------------------------------------------------------------------
# Request Models
# ----------------------------------------------------------------------


class QueryRequest(BaseModel):
    """
    Request body for querying LightRAG.
    """

    question: str

    mode: str = "mix"


class QueryResponse(BaseModel):
    """
    API response format.
    """

    answer: str

    mode: str


# ----------------------------------------------------------------------
# Query Endpoint
# ----------------------------------------------------------------------


@app.post(
    "/query",
    response_model=QueryResponse,
)
async def query(req: QueryRequest):
    """
    Query the LightRAG system.

    Supported modes:
    - naive
    - local
    - global
    - hybrid
    - mix
    """

    # ------------------------------------------------------------------
    # Validate query mode
    # ------------------------------------------------------------------
    if req.mode not in VALID_MODES:

        raise HTTPException(
            status_code=400,
            detail=("Invalid mode. " f"Choose from: " f"{', '.join(VALID_MODES)}"),
        )

    # ------------------------------------------------------------------
    # Execute query
    # ------------------------------------------------------------------
    result = await rag.aquery(
        req.question,
        param=QueryParam(
            mode=req.mode,
        ),
    )

    # ------------------------------------------------------------------
    # Return response
    # ------------------------------------------------------------------
    return QueryResponse(
        answer=result,
        mode=req.mode,
    )


# ----------------------------------------------------------------------
# Health Check Endpoint
# ----------------------------------------------------------------------


@app.get("/health")
async def health():
    """
    Health check endpoint.
    """

    return {"status": "ok"}
