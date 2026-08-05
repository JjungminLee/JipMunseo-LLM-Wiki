"""Base interface for law/policy source crawlers.

Each government source (법제처, 국세청, 국토교통부 등) gets its own crawler
implementing `fetch()`. Keeping this as a small interface means adding a new
source is additive, not a change to the pipeline.
"""

from abc import ABC, abstractmethod

from app.domain.models import LegalRule


class RuleCrawler(ABC):
    source_name: str

    @abstractmethod
    def fetch(self) -> list[LegalRule]:
        """Fetch the current set of rules from this source."""
