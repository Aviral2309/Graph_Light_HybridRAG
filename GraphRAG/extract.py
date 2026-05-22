"""Unstrucured text becomes structured Graph Data"""

import json
import re
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq()

EXTRACTION_PROMPT = """
You are a knowledge graph extraction expert.

Read the text below and extract:

1. ENTITIES
   - Named things such as:
     - People
     - Organizations
     - Products
     - Concepts
     - Places
     - Events

2. RELATIONSHIPS
   - Connections between entities

Return ONLY valid JSON.
Do not include:
- explanations
- markdown
- code fences
- extra text

Expected Format:

{
  "entities": [
    {
      "id": "e1",
      "name": "Entity Name",
      "type": "Person | Organization | Product | Concept | Place | Event"
    }
  ],
  "relationships": [
    {
      "source": "e1",
      "target": "e2",
      "relation": "RELATION_TYPE"
    }
  ]
}

Rules:
- Use short, uppercase relation types
  Examples:
  - WORKS_AT
  - CREATED
  - ACQUIRED
  - USES
  - LOCATED_IN

- Every relationship must reference valid entity IDs
- Extract only information explicitly stated in the text
- Deduplicate repeated entities by reusing the same entity ID

TEXT:
{TEXT}
"""


def extract_graph_from_text(text: str) -> dict:
    """
    Send a document to Groq and extract:
    - entities
    - relationships

    Returns:
        {
            "entities": [...],
            "relationships": [...]
        }

    Returns empty lists if extraction fails.
    """

    # ------------------------------------------------------------------
    # Truncate large documents to stay within token/context limits
    # ------------------------------------------------------------------
    max_chars = 4000

    if len(text) > max_chars:
        text = text[:max_chars]
        print(f"⚠️ Document truncated to {max_chars} characters")

    # ------------------------------------------------------------------
    # Send request to LLM
    # ------------------------------------------------------------------
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": EXTRACTION_PROMPT + text,
            }
        ],
        temperature=0.1,  # Lower temperature → more structured output
        max_tokens=2000,  # Enough space for graph extraction JSON
    )

    # ------------------------------------------------------------------
    # Extract raw LLM response
    # ------------------------------------------------------------------
    raw = response.choices[0].message.content.strip()

    # ------------------------------------------------------------------
    # Remove markdown code fences if present
    # Example:
    # ```json
    # {...}
    # ```
    # ------------------------------------------------------------------
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    # ------------------------------------------------------------------
    # Parse JSON response
    # ------------------------------------------------------------------
    try:
        data = json.loads(raw)

        entities = data.get("entities", [])
        relationships = data.get("relationships", [])

        print(
            f"✅ Extracted {len(entities)} entities "
            f"and {len(relationships)} relationships"
        )

        return {
            "entities": entities,
            "relationships": relationships,
        }

    # ------------------------------------------------------------------
    # Handle malformed JSON safely
    # ------------------------------------------------------------------
    except json.JSONDecodeError as e:

        print(f"❌ JSON parse error: {e}")
        print(f"Raw response preview:\n{raw[:200]}")

        return {
            "entities": [],
            "relationships": [],
        }


def extract_from_folder(folder_path: str) -> dict:
    """
    Read all `.txt` files from a folder and extract
    a combined knowledge graph.

    Features:
    - Reads multiple text documents
    - Extracts entities + relationships
    - Deduplicates entities (case-insensitive)
    - Merges all relationships

    Returns:
        {
            "entities": [...],
            "relationships": [...]
        }
    """

    # ------------------------------------------------------------------
    # Store unique entities
    # key   -> lowercase entity name
    # value -> entity dictionary
    # ------------------------------------------------------------------
    all_entities = {}

    # Store all extracted relationships
    all_relationships = []

    # ------------------------------------------------------------------
    # Validate folder path
    # ------------------------------------------------------------------
    if not os.path.exists(folder_path):

        print(f"❌ Folder not found: {folder_path}")

        return {
            "entities": [],
            "relationships": [],
        }

    # ------------------------------------------------------------------
    # Get all .txt files
    # ------------------------------------------------------------------
    txt_files = [
        file_name for file_name in os.listdir(folder_path) if file_name.endswith(".txt")
    ]

    # ------------------------------------------------------------------
    # Handle empty folder
    # ------------------------------------------------------------------
    if not txt_files:

        print(f"❌ No .txt files found in {folder_path}")

        return {
            "entities": [],
            "relationships": [],
        }

    print(f"📂 Found {len(txt_files)} documents to process")

    # ------------------------------------------------------------------
    # Process each file
    # ------------------------------------------------------------------
    for filename in txt_files:

        filepath = os.path.join(folder_path, filename)

        print(f"\n📄 Processing: {filename}")

        # Read file content
        with open(filepath, "r", encoding="utf-8") as file:
            text = file.read()

        # Extract graph from document
        result = extract_graph_from_text(text)

        # --------------------------------------------------------------
        # Deduplicate entities by name (case-insensitive)
        # Example:
        # "OpenAI" across multiple files becomes one node
        # --------------------------------------------------------------
        for entity in result["entities"]:

            key = entity["name"].lower()

            if key not in all_entities:
                all_entities[key] = entity

        # --------------------------------------------------------------
        # Add relationships
        # --------------------------------------------------------------
        all_relationships.extend(result["relationships"])

    # ------------------------------------------------------------------
    # Convert entity dictionary → list
    # ------------------------------------------------------------------
    entities_list = list(all_entities.values())

    # ------------------------------------------------------------------
    # Final summary
    # ------------------------------------------------------------------
    print(
        f"\n📊 Total: "
        f"{len(entities_list)} unique entities, "
        f"{len(all_relationships)} relationships"
    )

    return {
        "entities": entities_list,
        "relationships": all_relationships,
    }
