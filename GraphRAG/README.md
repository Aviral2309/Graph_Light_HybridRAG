# GraphRAG Explorer 🚀

An end-to-end **GraphRAG (Graph Retrieval-Augmented Generation)** system built using **Python, FastAPI, Neo4j, Groq LLM, React, and Vite**.
This project transforms unstructured documents into an interactive **knowledge graph** and enables intelligent multi-hop reasoning through a chat interface.

Built for learning, portfolio projects, AI engineering practice, and real-world knowledge systems. 

---

## ✨ Features

* 📄 Extract entities & relationships from text documents using LLMs
* 🧠 Build a connected knowledge graph with Neo4j AuraDB
* 🔍 Multi-hop GraphRAG querying
* 💬 Chat with your knowledge graph
* 🌐 Interactive graph visualization
* ⚡ FastAPI backend + React frontend
* ☁️ Fully free-tier compatible setup
* 🛠 Production-style architecture

---

## 🏗 Tech Stack

### Backend

* Python
* FastAPI
* Groq API (`llama-3.3-70b-versatile`)
* Neo4j AuraDB
* UV package manager

### Frontend

* React + Vite
* react-force-graph-2d

---

## 📌 What is GraphRAG?

Unlike traditional RAG systems that rely only on vector similarity, GraphRAG stores knowledge as interconnected entities and relationships.

Example:

```text
[OpenAI] --CREATED--> [GPT-4]
[GPT-4] --USED_BY--> [Microsoft Copilot]
```

This allows the system to perform **relationship-aware reasoning** and answer complex multi-hop queries effectively. 

---

## ⚙️ Architecture

```text
Documents
   ↓
Entity & Relationship Extraction (LLM)
   ↓
Neo4j Knowledge Graph
   ↓
Graph Query Engine
   ↓
FastAPI Backend
   ↓
React Visualization + Chat UI
```



---

## 📂 Project Structure

```bash
graphrag-project/
│
├── documents/              # Input text files
├── extract.py              # Entity extraction
├── graph_db.py             # Neo4j operations
├── rag.py                  # GraphRAG query engine
├── main.py                 # FastAPI backend
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── GraphView.jsx
│   │   └── ChatPanel.jsx
│   └── package.json
│
├── .env
└── pyproject.toml
```

---

## 🚀 Setup

### 1️⃣ Clone Repository

```bash
git clone <your-repo-url>
cd graphrag-project
```

---

### 2️⃣ Install Backend Dependencies

```bash
uv add fastapi uvicorn neo4j groq python-dotenv
```

---

### 3️⃣ Configure Environment Variables

Create `.env`

```env
GROQ_API_KEY=your_api_key
NEO4J_URI=neo4j+s://xxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

---

### 4️⃣ Start Backend

```bash
uv run uvicorn main:app --reload --port 8000
```

---

### 5️⃣ Setup Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 📥 Ingest Documents

Add `.txt` files inside the `documents/` folder.

Then click:

```text
⬆ Ingest Documents
```

The system will:

* Extract entities
* Detect relationships
* Build the knowledge graph
* Store data in Neo4j

---

## 💡 Example Queries

```text
Who founded OpenAI?
How is GitHub connected to Microsoft?
What products use OpenAI models?
What AI models compete with GPT-4?
```

---

## 🧠 Core Components

| File            | Purpose                           |
| --------------- | --------------------------------- |
| `extract.py`    | Extracts entities & relationships |
| `graph_db.py`   | Handles Neo4j graph operations    |
| `rag.py`        | GraphRAG reasoning pipeline       |
| `main.py`       | FastAPI API server                |
| `GraphView.jsx` | Interactive graph visualization   |
| `ChatPanel.jsx` | Graph chat interface              |

---

## 🔥 Why This Project Matters

This project demonstrates:

* LLM engineering
* Knowledge graphs
* Graph databases
* Retrieval systems
* Full-stack AI development
* AI system design
* Production-ready architecture
* Agentic AI concepts

Perfect for:

* Resume projects
* AI/ML internships
* GenAI portfolios
* Hackathons
* AI engineering interviews

---

## 📈 Future Improvements

* Hybrid Vector + Graph RAG
* Incremental ingestion
* Community detection
* Entity normalization
* Source tracking
* Graph export functionality



---

## 🖼 Preview

* Interactive knowledge graph visualization
* Relationship-aware AI chatbot
* Live graph traversal
* Highlighted subgraphs for answers

---

## 🤝 Contributing

Pull requests and improvements are welcome.

If you find this useful, give it a ⭐ on GitHub.

---

## 📜 License

MIT License

---

## 👨‍💻 Author

**Aviral Mittal**
AI • Data Science • GenAI • Full Stack AI Systems

---

## ⭐ Project Highlights

✅ GraphRAG from scratch
✅ Neo4j integration
✅ Multi-hop reasoning
✅ Interactive graph UI
✅ FastAPI + React architecture
✅ Real-world AI system design

---

Built with ❤️ using GraphRAG concepts and modern AI engineering workflows.
