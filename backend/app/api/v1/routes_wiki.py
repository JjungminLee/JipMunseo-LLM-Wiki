from fastapi import APIRouter, HTTPException

from app.domain.models import WikiEntry
from app.services import wiki_service

router = APIRouter(prefix="/wiki", tags=["wiki"])


@router.get("/{slug}", response_model=WikiEntry)
def get_entry(slug: str) -> WikiEntry:
    entry = wiki_service.get_wiki_entry(slug)
    if entry is None:
        raise HTTPException(status_code=404, detail="wiki entry not found")
    return entry
