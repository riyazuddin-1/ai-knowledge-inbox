from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import database
from app.schemas.assistant import QueryRequest
from app.schemas.envelope import StandardResponse
from app.services.rag import answer_question

router = APIRouter(prefix="", tags=["RAG Assistant"])

@router.post("/query", response_model=StandardResponse[dict])
def query_knowledge_base(
    payload: QueryRequest,
    db: Session = Depends(database),
):
    try:
        answer = answer_question(question=payload.question)
        return StandardResponse(
            success=True,
            message="Query answered successfully.",
            data=answer,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
