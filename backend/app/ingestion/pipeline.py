"""Scheduled ingestion: pull rule updates, diff against stored versions,
re-embed changed content into the vector store.

Run on a schedule (see APScheduler in requirements.txt) since tax/policy
rules change a few times a year, not continuously.
"""

from app.ingestion.crawlers.base import RuleCrawler


def run_ingestion(crawlers: list[RuleCrawler]) -> None:
    for crawler in crawlers:
        rules = crawler.fetch()
        # TODO: diff against app.infra.db, upsert changed LegalRule rows,
        # and re-embed into the vector store via app.retrieval.vector_store
        _ = rules
        raise NotImplementedError(f"ingestion not wired up yet ({crawler.source_name})")
