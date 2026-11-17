# backend/api/server.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.query import router as query_router
from api.routes.content import router as content_router
from shared.database.sql import Base, SessionLocal, engine
from shared.memory import init_vector_store


@asynccontextmanager
async def lifespan(app: FastAPI):
  # 1. Create SQLite tables if they don't exist
  Base.metadata.create_all(bind=engine)

  # 2. Hydrate in-memory vector store from SQLite
  db = SessionLocal()
  try:
    init_vector_store(db)
  finally:
    db.close()

  yield


app = FastAPI(title="AI Knowledge Inbox API", lifespan=lifespan)

# Allow React dev server to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(content_router)
app.include_router(query_router)


@app.get("/health")
def health_check():
  return {"status": "ok"}
