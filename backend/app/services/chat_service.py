"""Application layer: use cases around the chat/Q&A interaction."""

from app.agent.orchestrator import answer_question


def ask(question: str) -> str:
    if not question.strip():
        raise ValueError("question must not be empty")
    return answer_question(question)
