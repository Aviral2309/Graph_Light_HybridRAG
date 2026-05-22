import json
import re

from dotenv import load_dotenv
from groq import Groq

from graph_db import (
    get_driver,
    get_subgraph,
)

# ----------------------------------------------------------------------
# Environment Setup
# ----------------------------------------------------------------------

load_dotenv()

client = Groq()


# ----------------------------------------------------------------------
# Extract Query Entities
# ----------------------------------------------------------------------


def extract_query_entities(question: str) -> list[str]:
    """
    Extract important entities from a user question.

    Example:
        Input:
            "What did OpenAI build with Microsoft?"

        Output:
            ["OpenAI", "Microsoft"]
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": f"""
Extract the key entities from this question.

Entities may include:
- people
- organizations
- products
- places
- concepts

Return ONLY a JSON array of strings.
Do not include explanations.

Question:
{question}

Example Output:
["OpenAI", "GPT-4", "Microsoft"]
""",
            }
        ],
        temperature=0.1,
        max_tokens=200,
    )

    # ------------------------------------------------------------------
    # Extract raw response
    # ------------------------------------------------------------------
    raw = response.choices[0].message.content.strip()

    # Remove markdown code fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    # ------------------------------------------------------------------
    # Parse JSON safely
    # ------------------------------------------------------------------
    try:
        entities = json.loads(raw)

        if isinstance(entities, list):
            return [str(entity) for entity in entities]

        return []

    # ------------------------------------------------------------------
    # Fallback parser if JSON fails
    # ------------------------------------------------------------------
    except json.JSONDecodeError:

        return [
            entity.strip().strip('"') for entity in raw.split(",") if entity.strip()
        ]


# ----------------------------------------------------------------------
# Format Graph Context for LLM
# ----------------------------------------------------------------------


def format_graph_as_context(subgraph: dict) -> str:
    """
    Convert a graph subgraph into readable text.

    This performs better for reasoning compared to
    passing raw JSON or Cypher.
    """

    if not subgraph["nodes"] and not subgraph["links"]:

        return "No relevant information found in the knowledge graph."

    lines = []

    lines.append("=== Knowledge Graph Context ===\n")

    # ------------------------------------------------------------------
    # Entities
    # ------------------------------------------------------------------
    lines.append("Entities found:")

    for node in subgraph["nodes"]:

        lines.append(f" - {node['name']} " f"(type: {node['type']})")

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    lines.append("\nRelationships:")

    for link in subgraph["links"]:

        # Example:
        # OpenAI --CREATED--> GPT-4
        lines.append(
            f" - {link['source']} " f"--{link['relation']}--> " f"{link['target']}"
        )

    return "\n".join(lines)


# ----------------------------------------------------------------------
# Full GraphRAG Pipeline
# ----------------------------------------------------------------------


def answer_question(question: str) -> dict:
    """
    Full GraphRAG query pipeline.

    Steps:
    1. Extract entities from the question
    2. Retrieve relevant subgraph from Neo4j
    3. Convert graph into reasoning context
    4. Ask Groq to answer using only graph data

    Returns:
    {
        "answer": str,
        "entities": [...],
        "subgraph": {...}
    }
    """

    print(f"\n❓ Question: {question}")

    # ------------------------------------------------------------------
    # Step 1: Extract query entities
    # ------------------------------------------------------------------
    entities = extract_query_entities(question)

    print(f"🔍 Query entities: {entities}")

    if not entities:

        return {
            "answer": (
                "I could not identify any entities "
                "in your question. Please try rephrasing."
            ),
            "entities": [],
            "subgraph": {
                "nodes": [],
                "links": [],
            },
        }

    # ------------------------------------------------------------------
    # Step 2: Retrieve graph context
    # ------------------------------------------------------------------
    driver = get_driver()

    subgraph = get_subgraph(
        driver,
        entities,
        hops=2,
    )

    driver.close()

    print(
        f"📊 Subgraph: "
        f"{len(subgraph['nodes'])} nodes, "
        f"{len(subgraph['links'])} relationships"
    )

    # ------------------------------------------------------------------
    # Step 3: Convert graph → readable context
    # ------------------------------------------------------------------
    context = format_graph_as_context(subgraph)

    # ------------------------------------------------------------------
    # Step 4: Ask Groq to answer
    # ------------------------------------------------------------------
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """
You are a knowledge graph assistant.

Rules:
- Answer ONLY using the provided graph context
- Do not make up facts
- If the graph lacks information, say so clearly
- Cite relationships that support the answer
""",
            },
            {
                "role": "user",
                "content": f"""
{context}

Question:
{question}

Answer based ONLY on the graph context above:
""",
            },
        ],
        temperature=0.3,
        max_tokens=500,
    )

    # ------------------------------------------------------------------
    # Extract final answer
    # ------------------------------------------------------------------
    answer = response.choices[0].message.content.strip()

    print(f"💬 Answer Preview: {answer[:100]}...")

    return {
        "answer": answer,
        "entities": entities,
        "subgraph": subgraph,
    }
