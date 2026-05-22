import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from extract import extract_from_folder
from graph_db import (
    clear_graph,
    get_driver,
    get_full_graph,
    load_graph,
)
from rag import answer_question

# ----------------------------------------------------------------------
# Environment Setup
# ----------------------------------------------------------------------

load_dotenv()


# ----------------------------------------------------------------------
# FastAPI App
# ----------------------------------------------------------------------

app = FastAPI(
    title="GraphRAG API",
    version="1.0.0",
)


# ----------------------------------------------------------------------
# CORS Configuration
# ----------------------------------------------------------------------
# Required because:
# Frontend  -> localhost:5173
# Backend   -> localhost:8000
#
# Browsers block cross-origin requests unless CORS is enabled.
# ----------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------------------------------------
# Request Models
# ----------------------------------------------------------------------


class QueryRequest(BaseModel):
    """
    Request body for querying the graph.
    """

    question: str


class IngestRequest(BaseModel):
    """
    Request body for document ingestion.
    """

    folder_path: str = "documents"

    # Clear existing graph before ingesting new data
    clear_first: bool = True


# ----------------------------------------------------------------------
# Root Endpoint
# ----------------------------------------------------------------------


@app.get("/")
def root():
    """
    Health check endpoint.
    """

    return {"status": "GraphRAG API is running"}


# ----------------------------------------------------------------------
# Document Ingestion Endpoint
# ----------------------------------------------------------------------


@app.post("/api/ingest")
def ingest_documents(request: IngestRequest):
    """
    Ingest `.txt` documents into the knowledge graph.

    Pipeline:
    1. Read documents
    2. Extract entities + relationships
    3. Store graph in Neo4j

    Expected runtime:
        ~30–60 seconds depending on document count
    """

    try:
        # --------------------------------------------------------------
        # Extract graph data from documents
        # --------------------------------------------------------------
        extracted = extract_from_folder(request.folder_path)

        # Validate extraction results
        if not extracted["entities"]:

            raise HTTPException(
                status_code=422,
                detail=(
                    f"No entities extracted. "
                    f"Check that '{request.folder_path}' "
                    f"contains valid .txt files."
                ),
            )

        # --------------------------------------------------------------
        # Connect to Neo4j
        # --------------------------------------------------------------
        driver = get_driver()

        # Optionally clear graph
        if request.clear_first:
            clear_graph(driver)

        driver.close()

        # --------------------------------------------------------------
        # Load graph into Neo4j
        # --------------------------------------------------------------
        load_graph(extracted)

        return {
            "status": "success",
            "entities_count": len(extracted["entities"]),
            "relationships_count": len(extracted["relationships"]),
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# ----------------------------------------------------------------------
# Full Graph Endpoint
# ----------------------------------------------------------------------


@app.get("/api/graph")
def get_graph():
    """
    Return the complete knowledge graph.

    Response Format:
    {
        "nodes": [...],
        "links": [...]
    }

    Compatible with:
        react-force-graph-2d
    """

    try:
        driver = get_driver()

        graph = get_full_graph(driver)

        driver.close()

        return graph

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# ----------------------------------------------------------------------
# Query Endpoint
# ----------------------------------------------------------------------


@app.post("/api/query")
def query_graph(request: QueryRequest):
    """
    Ask a question against the GraphRAG system.

    Pipeline:
    1. Extract entities from question
    2. Retrieve relevant subgraph
    3. Generate grounded answer

    Response:
    {
        "answer": "...",
        "entities": [...],
        "subgraph": {...}
    }
    """

    # --------------------------------------------------------------
    # Validate input
    # --------------------------------------------------------------
    if not request.question.strip():

        raise HTTPException(
            status_code=422,
            detail="Question cannot be empty",
        )

    try:
        result = answer_question(request.question)

        return result

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# ----------------------------------------------------------------------
# Clear Graph Endpoint
# ----------------------------------------------------------------------


@app.delete("/api/graph")
def delete_graph():
    """
    Delete all nodes and relationships
    from the Neo4j database.
    """

    try:
        driver = get_driver()

        clear_graph(driver)

        driver.close()

        return {"status": "Graph cleared"}

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )
