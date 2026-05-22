import asyncio
import sys

from pathlib import Path

from src.rag_engine import build_rag

# ----------------------------------------------------------------------
# Ingest File into LightRAG
# ----------------------------------------------------------------------


async def ingest_file(path: str) -> None:
    """
    Read a text file and ingest it into LightRAG.

    Steps:
    1. Validate file existence
    2. Read file contents
    3. Initialize RAG storage
    4. Insert document into graph/vector store
    5. Finalize storage
    """

    file = Path(path)

    # ------------------------------------------------------------------
    # Validate file path
    # ------------------------------------------------------------------
    if not file.exists():

        print(f"❌ File not found: {path}")

        sys.exit(1)

    # ------------------------------------------------------------------
    # Read file content
    # ------------------------------------------------------------------
    text = file.read_text(encoding="utf-8")

    print(f"📄 Ingesting: {file.name} " f"({len(text):,} characters)")

    # ------------------------------------------------------------------
    # Build RAG instance
    # ------------------------------------------------------------------
    rag = build_rag()

    # ------------------------------------------------------------------
    # Initialize storage systems
    # ------------------------------------------------------------------
    await rag.initialize_storages()

    # ------------------------------------------------------------------
    # Insert document
    # ------------------------------------------------------------------
    await rag.ainsert(
        text,
        file_paths=str(file),
    )

    # ------------------------------------------------------------------
    # Finalize storage
    # ------------------------------------------------------------------
    await rag.finalize_storages()

    print("✅ Done. Knowledge graph updated.")


# ----------------------------------------------------------------------
# CLI Entry Point
# ----------------------------------------------------------------------

if __name__ == "__main__":

    # --------------------------------------------------------------
    # Validate command-line arguments
    # --------------------------------------------------------------
    if len(sys.argv) < 2:

        print("Usage:\n" "uv run src/ingest.py <path/to/file.txt>")

        sys.exit(1)

    # --------------------------------------------------------------
    # Run ingestion
    # --------------------------------------------------------------
    asyncio.run(ingest_file(sys.argv[1]))
