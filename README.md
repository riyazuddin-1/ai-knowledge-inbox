# AI Knowledge Inbox
A minimal RAG pipeline for knowledge base that can answer to questions based on the data provided as source.

## Quickstart & Local Setup
### Prerequisites
 * Python 3.11+ with uv package manager
 * Node.js 18+ and npm
### Backend Setup (server/)
Navigate to the server directory, install dependencies via uv, and configure your environment:
cd server
uv sync

#### Create a .env file in the server/ root:
```
DATABASE_URL="sqlite_db"

JINA_API_KEY="jina_your_api_key_here"
NVIDIA_API_KEY="nvapi-your_api_key_here"
```

#### Start the FastAPI development server:
```
uv run python -m uvicorn app.api.main:app --reload
```

Backend runs at [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Frontend Setup (client/)
Navigate to the client directory, install packages, and launch the Vite development server:
```
cd client
npm install
npm run dev
```

Frontend runs at [http://localhost:5173](http://localhost:5173)

## Design Decisions & Tradeoffs
### In-Memory Vector Search
* Loads vector embeddings from SQLite into a NumPy array in RAM at startup for cosine similarity calculation.
* Tradeoff: Delivers sub-millisecond similarity lookups and zero external database dependencies. For larger datasets or multi-tenant deployments, RAM constraints and startup time would require migrating to a persistent vector index (e.g., Vespa, ChromaDB, or pgvector).

### OpenAI Compatibility
* The application has provider-independent AIClient adapter(app/services/ai.py) that communicates with external models through standard OpenAI-compatible REST APIs. This simplifies business logic and SDK dependency.

| Used for | Provider | Model
|---|---|---|
| Embeddings | Jina AI | jina-embeddings-v3
| LLM Generation | NVIDIA NIM | nvidia/nemotron-3.5-lightning-30b-a3b

### Asynchronous Background Processing
* Handles url parsing, document chunking and embedding generation via lightweight asynchronous background tasks.
* Tradeoff: API response is quick, but for prod requires separate deployment of tasks as event functions that can be triggered via queues.

## Project Structure
```
project/
├── client/                  # React Frontend
│   └── src/
│       ├── api/             # Unwrapped API client modules
│       └── components/      # Modular UI (Sidebar, Chat, InfiniteScroll,...)
└── server/                  # FastAPI Backend
    ├── pyproject.toml
    └── src/app/
        ├── api/v1/endpoints # REST Endpoints (/ingest, /items, /query)
        ├── core/            # Config, SQLite engine, NumPy vector similarity index
        ├── models/          # SQLAlchemy ORM models
        ├── repositories/    # Data access layer
        ├── schemas/         # Pydantic validation schemas & StandardResponse envelope
        ├── services/        # Business logic & AI adapter
        └── workers/tasks    # Background tasks for url parsing, async chunking & embedding
```

## API Contract
All endpoints adhere to a standardized StandardResponse envelope (success, message, data, pagination):
| Method | Endpoint | Description |
|---|---|---|
| POST | /ingest | Ingests text, and URLs; triggers background vector embedding using Jina. |
| GET | /items | Retrieves paginated knowledge base items. |
| POST | /query | Executes vector similarity search and queries NVIDIA NIM to return cited answers. |
