# Hybrid GraphRAG 🚀

A powerful **Hybrid RAG System** combining:

* 🔍 **Vector Search** using ChromaDB
* 🕸️ **Knowledge Graph Retrieval** using NetworkX
* ⚡ **Groq LLMs** for ultra-fast inference
* 🧠 **Query Routing** for intelligent retrieval selection

Inspired by modern production-grade GraphRAG architectures. 

---

# ✨ Features

* Semantic Search
* Knowledge Graph Traversal
* Hybrid Retrieval
* Intelligent Query Router
* Local Embeddings (Free)
* Groq Integration
* Production-style RAG Pipeline

---

# 🏗️ Architecture

```text
User Query
     │
     ▼
 Query Router
     │
 ┌───┴────┐
 ▼        ▼
Vector   Graph
Search   Search
 └───┬────┘
     ▼
 Context Merge
     ▼
   Groq LLM
     ▼
    Answer
```

---

# ⚙️ Tech Stack

* Python
* Groq
* ChromaDB
* NetworkX
* SentenceTransformers
* Rich Console

---

# 📦 Installation

```bash
pip install groq chromadb sentence-transformers networkx rich python-dotenv
```

---

# 🔑 Environment Variables

Create `.env`

```env
GROQ_API_KEY=your_api_key
```

Get API Key:

[Groq Console](https://console.groq.com?utm_source=chatgpt.com)

---

# ▶️ Run

```bash
python main.py
```

---

# 🧠 Query Types

### Vector Query

```text
What is the Premium Plan cost?
```

### Graph Query

```text
How does Premium Plan relate to support?
```

### Hybrid Query

```text
Explain Premium Plan benefits and refund policy.
```

---

# 🔥 Future Improvements

* PDF/DOCX ingestion
* Neo4j integration
* FastAPI backend
* Streamlit UI
* LangGraph agents
* Multi-hop reasoning
* Persistent storage

---

# 👨‍💻 Author

**Aviral Mittal**

AI • Data Science • GenAI • Agentic AI

---

# ⭐ Star This Repo

If you found this project useful, give it a ⭐ on GitHub.
