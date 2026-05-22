# ⚡ LightRAG — GraphRAG at 1/6000th the Cost

A lightweight, local-first implementation of **GraphRAG** using **LightRAG**, **Gemini 2.5 Flash**, and **knowledge graphs** for intelligent document querying.

This project transforms plain text documents into a connected knowledge graph and enables advanced retrieval through graph traversal + vector search — without requiring Neo4j, Docker, or expensive infrastructure.

---

# 🚀 Features

- 🧠 Knowledge Graph based Retrieval-Augmented Generation
- 📄 Entity & Relationship Extraction using Gemini 2.5 Flash
- 🔍 Multi-mode intelligent querying
- ⚡ Fast and lightweight local storage
- 💾 No external database required
- 📊 Graph-based semantic reasoning
- 🧩 Hybrid Graph + Vector Retrieval
- 🌐 Optional FastAPI server
- 📂 Batch document ingestion support
- 🛠 Fully free-tier compatible

---

# 🏗 Architecture

```text
TXT Documents
      │
      ▼
[ LightRAG Ingestion ]
      │
      ├── Entity + Relationship Extraction
      ├── Chunk Embeddings
      └── Graph Construction
      │
      ▼
Local Storage
(graphml + vector DB + KV stores)
      │
      ▼
Graph Traversal + Vector Search
      │
      ▼
Gemini 2.5 Flash
      │
      ▼
Final Grounded Answer
```

---

# 📌 Query Modes

LightRAG supports multiple retrieval strategies:

| Mode | Description |
|------|-------------|
| `naive` | Pure vector search |
| `local` | Entity + neighborhood traversal |
| `global` | Community-level summaries |
| `hybrid` | Combines local + global |
| `mix` | Graph + vector retrieval together |

---

# 🛠 Tech Stack

## Backend
- Python
- LightRAG
- Gemini 2.5 Flash
- Gemini Embeddings
- FastAPI

## Storage
- GraphML
- NanoVectorDB
- JSON KV Stores

## Tools
- UV Package Manager
- Async Python

---

# 📂 Project Structure

```bash
lightrag-project/
│
├── src/
│   ├── tokenizer.py
│   ├── rag_engine.py
│   ├── ingest.py
│   ├── ingest_folder.py
│   ├── query.py
│   └── server.py
│
├── data/               # Input text files
├── rag_storage/        # Generated graph & vector stores
│
├── .env
└── pyproject.toml
```

---

# ⚙️ Setup

## 1️⃣ Clone Repository

```bash
git clone <your-repo-url>
cd lightrag-project
```

---

## 2️⃣ Install Dependencies

```bash
uv add "lightrag-hku==1.4.15" "google-genai" "python-dotenv"
```

---

## 3️⃣ Configure Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

---

# 📥 Ingest Documents

Place `.txt` files inside the `data/` folder.

### Ingest Single File

```bash
PYTHONPATH=. uv run src/ingest.py data/sample.txt
```

### Ingest Entire Folder

```bash
PYTHONPATH=. uv run src/ingest_folder.py data/
```

---

# 🔍 Query the Knowledge Graph

## Default (Mix Mode)

```bash
PYTHONPATH=. uv run src/query.py "What is the relationship between Mumbai and the Indian economy?"
```

## Specific Query Modes

```bash
PYTHONPATH=. uv run src/query.py "your question" naive
PYTHONPATH=. uv run src/query.py "your question" local
PYTHONPATH=. uv run src/query.py "your question" global
PYTHONPATH=. uv run src/query.py "your question" hybrid
PYTHONPATH=. uv run src/query.py "your question" mix
```

---

# 🌐 FastAPI Server

## Install

```bash
uv add fastapi "uvicorn[standard]"
```

## Run API

```bash
PYTHONPATH=. uv run uvicorn src.server:app --reload --port 8000
```

---

# 📡 API Example

## POST `/query`

```json
{
  "question": "What are the main themes?",
  "mode": "global"
}
```

---

# 💡 Why LightRAG?

Traditional RAG systems only retrieve semantically similar chunks.

LightRAG builds a **knowledge graph** during ingestion:

```text
[Entity] ----RELATION----> [Entity]
```

This enables:
- Multi-hop reasoning
- Context-aware retrieval
- Better long-document understanding
- Connected information synthesis

---

# 📊 Generated Storage

After ingestion:

```bash
rag_storage/
├── graph_chunk_entity_relation.graphml
├── vdb_entities.json
├── vdb_relationships.json
├── vdb_chunks.json
└── kv_store_*.json
```

---

# 🔥 Use Cases

- AI Knowledge Assistants
- Enterprise Document Intelligence
- Research Paper Exploration
- Legal & Medical Knowledge Systems
- Personal Knowledge Bases
- AI Agents with Memory
- Multi-document reasoning systems

---

# 🧠 Key Concepts Demonstrated

- GraphRAG
- Knowledge Graphs
- Hybrid Retrieval
- LLM Engineering
- Vector Search
- Graph Traversal
- Agentic Retrieval
- Async AI Pipelines
- AI Infrastructure Design

---

# 📈 Future Improvements

- Web UI Dashboard
- Multi-file source attribution
- Streaming responses
- Graph visualization
- Reranking models
- Local embedding support
- PDF ingestion
- Agentic workflows

---

# ⭐ Why This Project Stands Out

✅ Graph-based RAG  
✅ Real-world AI system design  
✅ Production-ready architecture  
✅ Uses modern GenAI stack  
✅ Portfolio + resume worthy  
✅ Cost-efficient GraphRAG implementation  

---

# 👨‍💻 Author

**Aviral Mittal**  
AI • GenAI • Data Science • Full Stack AI Systems

---

# 📜 License

MIT License

---

# 🌟 Acknowledgements

Inspired by GraphRAG research and built using:
- LightRAG
- Gemini API
- Modern Graph-based Retrieval techniques
