import logging

from fastapi import APIRouter, HTTPException

from app.core.memory import add_chat_turn, get_chat_history
from app.schemas.assistant import QueryRequest
from app.schemas.envelope import StandardResponse
from app.services.rag import answer_question

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["RAG Assistant"])

@router.post("/query", response_model=StandardResponse[dict])
def query_knowledge_base(
    payload: QueryRequest,
):
    try:
        answer = answer_question(
            question=payload.question,
            history=get_chat_history(),
        )
        add_chat_turn(payload.question.strip(), answer["answer"])
        return StandardResponse(
            success=True,
            message="Query answered successfully.",
            data=answer,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as exc:
        logger.exception("Knowledge-base query failed.")
        raise HTTPException(
            status_code=500,
            detail="Unable to answer the question right now.",
        ) from exc
