from fastapi import APIRouter
from pydantic import BaseModel

from app.services import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str


@router.post("", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    return AskResponse(answer=chat_service.ask(req.question))
