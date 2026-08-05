from fastapi import APIRouter

from app.api.v1.routes_chat import router as chat_router
from app.api.v1.routes_wiki import router as wiki_router

router = APIRouter(prefix="/api/v1")
router.include_router(wiki_router)
router.include_router(chat_router)
