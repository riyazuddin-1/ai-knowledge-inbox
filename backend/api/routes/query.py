from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.controllers.query import answer_question
from shared.database.sql import database
from shared.schemas.response import StandardResponse

router = APIRouter(tags=["RAG Query"])

class QueryRequest(BaseModel):
  question: str


@router.post("/query", response_model=StandardResponse[dict])
def query_knowledge_base(payload: QueryRequest, db: Session = Depends(database)):
  answer = answer_question(payload.question)
  return StandardResponse(
      success=True,
      message="Query answered successfully.",
      data=answer
  )
