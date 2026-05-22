import os
import json
import networkx as nx
import chromadb
from dotenv import load_dotenv

from chromadb.utils import embedding_functions
from groq import Groq

from rich.console import Console
from rich.panel import Panel

load_dotenv()

console = Console()

# Load API key
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set in environment")

# Groq client
client = Groq(api_key=GROQ_API_KEY)

# Free / fast Groq model
MODEL = "llama-3.3-70b-versatile"


# Step 1 — Initialise the ChromaDB vector store


def build_vector_store():
    """
    Creates an in-memory ChromaDB collection with a
    SentenceTransformer embedding function.

    No API key needed — embeddings run locally.
    """

    chroma_client = chromadb.Client()

    # Local embedding model (free)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    collection = chroma_client.create_collection(
        name="hybrid_rag_docs",
        embedding_function=ef,
    )

    return collection


# Step 2 — Initialise the knowledge graph


def build_knowledge_graph():
    """
    Returns an empty directed graph.

    Nodes  = entities
             (concepts, products, policies, people)

    Edges  = labelled relationships between entities
    """

    graph = nx.DiGraph()

    return graph


# Step 3 — Extract entities and ingest documents


def extract_entities_and_relations(text: str) -> list[dict]:
    """
    Sends a document chunk to the LLM and extracts
    (entity, relation, target) triples as JSON.

    These triples become directed edges
    in the knowledge graph.
    """

    prompt = f"""
Extract the key entities and relationships from the text below.

Return ONLY a JSON array.
No explanation.
No markdown.
No code fences.

Each item must have exactly these keys:
- "entity"   : subject
- "relation" : relationship
- "target"   : object

Text:
{text}

JSON array:
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You extract structured knowledge graph triples.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )

    raw = response.choices[0].message.content.strip()

    # Remove markdown fences if model adds them
    if raw.startswith("```"):
        raw = raw.split("```")[1]

        if raw.startswith("json"):
            raw = raw[4:]

    raw = raw.strip()

    try:
        triples = json.loads(raw)

        if isinstance(triples, list):
            return triples

        return []

    except json.JSONDecodeError:
        return []


def ingest_documents(documents: list[dict], collection, graph: nx.DiGraph):
    """
    Ingest documents into:
    1. ChromaDB vector store
    2. Knowledge graph

    Each document must contain:
    - id
    - text
    """

    console.print("[bold blue]Ingesting documents...[/bold blue]")

    for doc in documents:

        doc_id = doc["id"]
        text = doc["text"]

        # ---------------------------------------------------
        # 1. Add raw text to ChromaDB
        # ---------------------------------------------------

        collection.add(
            documents=[text],
            ids=[doc_id],
        )

        # ---------------------------------------------------
        # 2. Extract KG triples
        # ---------------------------------------------------

        triples = extract_entities_and_relations(text)

        for triple in triples:

            entity = triple.get("entity", "").strip()
            relation = triple.get("relation", "").strip()
            target = triple.get("target", "").strip()

            if entity and relation and target:

                # Add nodes
                if not graph.has_node(entity):
                    graph.add_node(entity)

                if not graph.has_node(target):
                    graph.add_node(target)

                # Add edge
                graph.add_edge(entity, target, relation=relation, source_doc=doc_id)

        console.print(
            f"[green]✓[/green] {doc_id} — " f"{len(triples)} relations extracted"
        )

    console.print(
        f"\n[bold green]Ingestion complete.[/bold green]\n"
        f"Graph: {graph.number_of_nodes()} nodes, "
        f"{graph.number_of_edges()} edges"
    )


# Step 4 — Vector Retriever


def vector_retrieve(query: str, collection, top_k: int = 3) -> list[str]:
    """
    Queries ChromaDB for the most semantically
    similar document chunks.

    Returns:
        List of retrieved text chunks.
    """

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
    )

    # ChromaDB returns:
    # {
    #   "documents": [[doc1, doc2, ...]]
    # }

    chunks = results["documents"][0] if results["documents"] else []

    return chunks


# Step 5 — Graph Retriever


def identify_query_entities(query: str) -> list[str]:
    """
    Extract important entities from the user query.

    Returns:
        List of entity names.
    """

    prompt = f"""
Identify the key entities (nouns, concepts, products, policies)
in this query.

Return ONLY a JSON array of strings.
No explanation.
No markdown.

Query:
{query}

JSON array:
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Extract key entities from user queries."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )

    raw = response.choices[0].message.content.strip()

    # Remove markdown fences if present
    if raw.startswith("```"):

        raw = raw.split("```")[1]

        if raw.startswith("json"):
            raw = raw[4:]

    raw = raw.strip()

    try:
        entities = json.loads(raw)

        if isinstance(entities, list):
            return [str(e) for e in entities]

        return []

    except json.JSONDecodeError:
        return []


def graph_retrieve(query: str, graph: nx.DiGraph) -> list[str]:
    """
    Retrieve graph relationships relevant to the query.

    Returns:
        List of relationship strings.
    """

    entities = identify_query_entities(query)

    graph_facts = []

    for entity in entities:

        # Check exact entity match
        if graph.has_node(entity):

            # Outgoing relationships
            for neighbor in graph.successors(entity):

                edge_data = graph.get_edge_data(entity, neighbor)

                relation = edge_data.get("relation", "related_to")

                fact = f"{entity} --[{relation}]--> {neighbor}"

                graph_facts.append(fact)

            # Incoming relationships
            for predecessor in graph.predecessors(entity):

                edge_data = graph.get_edge_data(predecessor, entity)

                relation = edge_data.get("relation", "related_to")

                fact = f"{predecessor} --[{relation}]--> {entity}"

                graph_facts.append(fact)

    return list(set(graph_facts))


# Step 6 — Query Router


def route_query(query: str) -> str:
    """
    Decide which retrieval strategy to use.

    Returns one of:
    - "vector"
    - "graph"
    - "hybrid"
    """

    prompt = f"""
You are a query router for a hybrid RAG system.

Classify the query below into exactly one retrieval mode.

Modes:

vector
- Direct factual lookup
- Specific definition/value/fact

Examples:
- What is the return window?
- What does the Premium plan cost?

graph
- Relational or multi-hop question
- Asks how entities connect

Examples:
- How does pricing affect support options?
- Relationship between refund policy and subscription type?

hybrid
- Needs BOTH factual retrieval and relationship reasoning

Examples:
- Explain how cancellation policy works and what plans it applies to.
- Give me a full overview of Premium subscriber benefits.

Return ONLY one word:
vector
graph
hybrid

Query:
{query}

Mode:
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a retrieval routing system."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )

    decision = response.choices[0].message.content.strip().lower()

    # Safety fallback
    if decision not in ("vector", "graph", "hybrid"):
        decision = "hybrid"

    return decision


# Step 7 — Full Hybrid RAG Query Pipeline


def query(
    user_query: str,
    collection,
    graph: nx.DiGraph,
    top_k: int = 3,
) -> dict:
    """
    Full Hybrid RAG pipeline.

    Steps:
    1. Route query
    2. Retrieve context
    3. Assemble prompt
    4. Generate answer

    Returns:
        {
            "query": str,
            "mode": str,
            "context": str,
            "answer": str
        }
    """

    # ---------------------------------------------------
    # Step 1 — Route Query
    # ---------------------------------------------------

    mode = route_query(user_query)

    console.print(f"\n[bold yellow]Router decision:[/bold yellow] {mode}")

    # ---------------------------------------------------
    # Step 2 — Retrieve Context
    # ---------------------------------------------------

    vector_chunks = []
    graph_lines = []

    # Vector retrieval
    if mode in ("vector", "hybrid"):

        vector_chunks = vector_retrieve(user_query, collection, top_k=top_k)

    # Graph retrieval
    if mode in ("graph", "hybrid"):

        graph_lines = graph_retrieve(user_query, graph)

    # ---------------------------------------------------
    # Step 3 — Assemble Context
    # ---------------------------------------------------

    context_parts = []

    if vector_chunks:

        context_parts.append("--- Retrieved Documents ---")

        context_parts.extend(vector_chunks)

    if graph_lines:

        context_parts.append("--- Knowledge Graph Relationships ---")

        context_parts.extend(graph_lines)

    full_context = "\n".join(context_parts)

    if not full_context.strip():
        full_context = "No relevant context found."

    # ---------------------------------------------------
    # Step 4 — Generate Final Answer
    # ---------------------------------------------------

    answer_prompt = f"""
You are a helpful assistant.

Answer the question using ONLY the provided context.

If the context does not contain enough information,
say so clearly.

Context:
{full_context}

Question:
{user_query}

Answer:
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": ("You answer questions strictly " "from retrieved context."),
            },
            {"role": "user", "content": answer_prompt},
        ],
        temperature=0.2,
    )

    answer = response.choices[0].message.content.strip()

    # ---------------------------------------------------
    # Return structured output
    # ---------------------------------------------------

    return {
        "query": user_query,
        "mode": mode,
        "context": full_context,
        "answer": answer,
    }


# Step 8 — Sample Data and Test Runner

SAMPLE_DOCUMENTS = [
    {
        "id": "doc_pricing",
        "text": (
            "The Basic Plan costs Rs.299 per month and includes "
            "email support and 5GB storage. "
            "The Premium Plan costs Rs.799 per month and includes "
            "priority support, 50GB storage, and access to "
            "advanced analytics. "
            "The Enterprise Plan costs Rs.2999 per month and "
            "includes a dedicated account manager, unlimited "
            "storage, and custom SLAs."
        ),
    },
    {
        "id": "doc_refund",
        "text": (
            "Our refund policy allows full refunds within 7 days "
            "of purchase for all plans. "
            "Premium Plan subscribers get a 14-day refund window "
            "as part of their subscription benefits. "
            "Refunds are processed within 3 to 5 business days "
            "to the original payment method."
        ),
    },
    {
        "id": "doc_support",
        "text": (
            "Email support is available to all plan subscribers "
            "with a 24-hour response time. "
            "Priority support is exclusive to Premium Plan "
            "subscribers and guarantees a 2-hour response time. "
            "Dedicated account managers are assigned to "
            "Enterprise Plan subscribers and are available "
            "Monday through Friday, 9 AM to 6 PM IST."
        ),
    },
]


def main():

    # ---------------------------------------------------
    # Initialise systems
    # ---------------------------------------------------

    collection = build_vector_store()

    graph = build_knowledge_graph()

    # ---------------------------------------------------
    # Ingest sample documents
    # ---------------------------------------------------

    ingest_documents(SAMPLE_DOCUMENTS, collection, graph)

    # ---------------------------------------------------
    # Test queries
    # ---------------------------------------------------

    test_queries = [
        # Expected: vector
        "What is the cost of the Premium Plan?",
        # Expected: graph
        "How does the Premium Plan relate to support?",
        # Expected: hybrid
        (
            "Give me a complete overview of what "
            "Premium Plan subscribers get, including "
            "support and refund terms."
        ),
    ]

    # ---------------------------------------------------
    # Run test queries
    # ---------------------------------------------------

    for q in test_queries:

        result = query(q, collection, graph)

        console.print(
            Panel(
                f"[bold]Query:[/bold]\n"
                f"{result['query']}\n\n"
                f"[bold]Mode:[/bold]\n"
                f"{result['mode']}\n\n"
                f"[bold]Answer:[/bold]\n"
                f"{result['answer']}",
                title="[cyan]Hybrid RAG Result[/cyan]",
                border_style="cyan",
            )
        )


# ---------------------------------------------------
# Entry Point
# ---------------------------------------------------

if __name__ == "__main__":
    main()
