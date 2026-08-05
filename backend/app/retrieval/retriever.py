"""RAG retrieval over legal rules and field insights.

Retrieves both kinds and keeps them distinct so the agent layer can cite
"법령 기준" (rule) separately from "현장 인사이트" (practitioner note) instead of
blending them into one unsourced answer.
"""

from app.core.config import get_settings
from app.retrieval.vector_store import get_vector_client


class RetrievedChunk:
    def __init__(self, text: str, source_id: str, source_kind: str, score: float):
        self.text = text
        self.source_id = source_id       # LegalRule.id or FieldInsight.id
        self.source_kind = source_kind   # "rule" | "insight"
        self.score = score


def retrieve(query: str, top_k: int = 8) -> list[RetrievedChunk]:
    """Embed `query` and fetch the closest rule/insight chunks.

    TODO: wire up an embedding model call + Qdrant search once the
    collection is populated by the ingestion pipeline.
    """
    settings = get_settings()
    _ = get_vector_client()
    raise NotImplementedError(
        f"retrieve() not wired up yet (collection={settings.qdrant_collection})"
    )
