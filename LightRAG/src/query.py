import asyncio
import sys

from lightrag import QueryParam

from src.rag_engine import build_rag

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
# Run Query
# ----------------------------------------------------------------------


async def run_query(
    question: str,
    mode: str = "mix",
) -> None:
    """
    Query the LightRAG system.

    Modes:
    - naive   -> simple retrieval
    - local   -> local graph retrieval
    - global  -> global graph retrieval
    - hybrid  -> graph + vector retrieval
    - mix     -> balanced retrieval strategy
    """

    # ------------------------------------------------------------------
    # Validate mode
    # ------------------------------------------------------------------
    if mode not in VALID_MODES:

        print(f"❌ Invalid mode '{mode}'.\n" f"Choose from: {', '.join(VALID_MODES)}")

        sys.exit(1)

    # ------------------------------------------------------------------
    # Build RAG instance
    # ------------------------------------------------------------------
    rag = build_rag()

    # ------------------------------------------------------------------
    # Initialize storage
    # ------------------------------------------------------------------
    await rag.initialize_storages()

    # ------------------------------------------------------------------
    # Query Header
    # ------------------------------------------------------------------
    print(f"\n[Mode: {mode}] " f"{question}\n" f"{'─' * 60}")

    # ------------------------------------------------------------------
    # Execute query
    # ------------------------------------------------------------------
    result = await rag.aquery(
        question,
        param=QueryParam(
            mode=mode,
        ),
    )

    # ------------------------------------------------------------------
    # Print response
    # ------------------------------------------------------------------
    print(result)

    # ------------------------------------------------------------------
    # Finalize storage
    # ------------------------------------------------------------------
    await rag.finalize_storages()


# ----------------------------------------------------------------------
# CLI Entry Point
# ----------------------------------------------------------------------

if __name__ == "__main__":

    # --------------------------------------------------------------
    # Validate CLI arguments
    # --------------------------------------------------------------
    if len(sys.argv) < 2:

        print("Usage:\n" "uv run src/query.py " "'your question' [mode]")

        print(f"\nAvailable Modes:\n" f"{', '.join(VALID_MODES)} " f"(default: mix)")

        sys.exit(1)

    # --------------------------------------------------------------
    # Parse arguments
    # --------------------------------------------------------------
    question = sys.argv[1]

    mode = sys.argv[2] if len(sys.argv) > 2 else "mix"

    # --------------------------------------------------------------
    # Run query
    # --------------------------------------------------------------
    asyncio.run(run_query(question, mode))
