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
* URL fetching, document chunking, and embedding generation run as in-process FastAPI background tasks after the ingest response.
* Tradeoff: this keeps local setup simple, but tasks are not durable across process restarts and share the API process. Production should use a persistent queue and separate workers.

### Token and Conversation Limits
* Text and URL values submitted to `POST /ingest` are limited to 2,000 characters. Extracted URL text is capped at 10,000 characters.
* Content is split into 500-token chunks with 80-token overlap using `tiktoken` (`cl100k_base`); a chunk may exceed the target by a few tokens to keep a Unicode character intact. LangChain is not required.
* The server keeps up to 20 recent user/assistant turns in a single in-memory array. The client sends only the current question; chat history is cleared when the backend process restarts.
* Before each LLM call, the server counts the system prompt, stored history, question, and retrieved context against a 7,168-token input budget, dropping the oldest complete turns first and then the lowest-ranked context as needed. The LLM response is capped at 1,024 tokens.
* `cl100k_base` is a practical tokenizer for budgeting, but is not NVIDIA Nemotron's tokenizer. The budget is deliberately conservative; exact provider-side token accounting may differ.
* Chat history is not stored in SQLite or indexed as embeddings. It remains in backend memory only and is lost on server restart.

### Scope and Limitations
* The ingest UI and API support plain text notes and URLs only. Fetched page text is stored in the embedding records; the content record retains the original URL.
* Chat history is local to the running backend process and shared by clients using that process. User accounts, durable chat transcripts, YouTube/PDF ingestion, and durable background jobs are outside the current implementation.

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
| POST | /ingest | Accepts a plain-text note or URL (maximum request value: 2,000 characters) and starts background embedding using Jina. |
| GET | /items | Retrieves paginated knowledge base items. |
| POST | /query | Executes vector similarity search, sends the recent conversation history and retrieved context to NVIDIA NIM, and returns cited answers. |
