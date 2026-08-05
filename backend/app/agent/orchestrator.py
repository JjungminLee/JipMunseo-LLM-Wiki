"""Agent orchestration: retrieve -> ground -> call LLM (with tools) -> answer.

This is the only layer allowed to call the LLM. Services call into this
module; it never talks to the DB or vector store directly (that's
retrieval/infra's job) so prompt/tool logic stays swappable independent of
storage.
"""

from anthropic import Anthropic

from app.agent.prompts.system_prompt import SYSTEM_PROMPT
from app.agent.tools.tax_calculator import TOOL_SCHEMA, estimate_transfer_tax
from app.core.config import get_settings
from app.retrieval.retriever import retrieve

TOOLS = [TOOL_SCHEMA]


def answer_question(question: str) -> str:
    settings = get_settings()
    client = Anthropic(api_key=settings.anthropic_api_key)

    chunks = retrieve(question)
    context = "\n\n".join(
        f"[{c.source_kind}:{c.source_id}] {c.text}" for c in chunks
    )

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=[
            {
                "role": "user",
                "content": f"참고 자료:\n{context}\n\n질문: {question}",
            }
        ],
    )

    # TODO: handle tool_use blocks (dispatch estimate_transfer_tax) and
    # multi-turn tool-result round trips once retrieval is wired up.
    return "".join(
        block.text for block in response.content if block.type == "text"
    )
