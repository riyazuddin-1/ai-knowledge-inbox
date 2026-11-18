import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints.inbox import router as inbox_router
from app.api.v1.endpoints.assistant import router as assistant_router
from app.core.database import Base, SessionLocal, engine
from app.core.memory import fetch_vector_data_into_memory
from app.services.ai import AI
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
  try:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
      fetch_vector_data_into_memory(db)
    finally:
      db.close()
  except Exception:
    logger.exception("Backend startup initialization failed.")
    raise

  try:
    yield
  finally:
    try:
      AI.close()
    except Exception:
      logger.exception("Could not close AI provider clients during shutdown.")
      raise


app = FastAPI(title="AI Knowledge Inbox API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(inbox_router)
app.include_router(assistant_router)


@app.get("/health")
def health_check():
  return {"status": "ok"}
