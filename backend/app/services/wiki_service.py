"""Application layer: use cases around wiki entries.

Talks to infra (DB) and returns domain models. Routers should never touch
infra directly — this indirection is what lets us change storage (e.g. add
a cache) without touching API contracts.
"""

from app.domain.models import WikiEntry


def get_wiki_entry(slug: str) -> WikiEntry | None:
    # TODO: fetch from Postgres via app.infra.db once schema exists
    raise NotImplementedError(f"get_wiki_entry({slug}) not wired up yet")


def list_wiki_entries(category: str | None = None) -> list[WikiEntry]:
    # TODO: fetch from Postgres via app.infra.db once schema exists
    raise NotImplementedError("list_wiki_entries() not wired up yet")
