"""Thin wrapper around the vector DB client.

Kept separate from retriever.py so the embedding backend (Qdrant here) can be
swapped without touching retrieval/ranking logic.
"""

from qdrant_client import QdrantClient

from app.core.config import get_settings


def get_vector_client() -> QdrantClient:
    settings = get_settings()
    return QdrantClient(url=settings.qdrant_url)
