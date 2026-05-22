import asyncio
import sys

from pathlib import Path

from src.rag_engine import build_rag

# ----------------------------------------------------------------------
# Ingest All TXT Files from a Folder
# ----------------------------------------------------------------------


async def ingest_folder(folder: str) -> None:
    """
    Ingest all `.txt` documents from a folder into LightRAG.

    Steps:
    1. Find all text files
    2. Initialize LightRAG storage
    3. Insert each document
    4. Finalize storage
    """

    folder_path = Path(folder)

    # ------------------------------------------------------------------
    # Find all TXT files
    # ------------------------------------------------------------------
    txt_files = sorted(folder_path.glob("*.txt"))

    # ------------------------------------------------------------------
    # Handle empty folder
    # ------------------------------------------------------------------
    if not txt_files:

        print(f"❌ No .txt files found in: {folder}")

        sys.exit(1)

    print(f"📂 Found {len(txt_files)} files")

    # ------------------------------------------------------------------
    # Build RAG instance
    # ------------------------------------------------------------------
    rag = build_rag()

    # ------------------------------------------------------------------
    # Initialize storage
    # ------------------------------------------------------------------
    await rag.initialize_storages()

    # ------------------------------------------------------------------
    # Process each document
    # ------------------------------------------------------------------
    for file in txt_files:

        text = file.read_text(encoding="utf-8")

        print(f"📄 Ingesting: {file.name}")

        await rag.ainsert(
            text,
            file_paths=str(file),
        )

    # ------------------------------------------------------------------
    # Finalize storage
    # ------------------------------------------------------------------
    await rag.finalize_storages()

    print(f"\n✅ All {len(txt_files)} " f"documents ingested successfully.")


# ----------------------------------------------------------------------
# CLI Entry Point
# ----------------------------------------------------------------------

if __name__ == "__main__":

    # Default folder = "data"
    folder = sys.argv[1] if len(sys.argv) > 1 else "data"

    asyncio.run(ingest_folder(folder))
