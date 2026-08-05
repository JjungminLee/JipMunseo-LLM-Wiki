"""Core domain entities for JipMunSeo.

Three content kinds are modeled separately because they change on different
cadences and need different trust/citation handling:
  - PolicyRule / TaxRule: law-derived, versioned by effective date
  - FieldInsight: human, experience-derived, never auto-updated
  - WikiEntry: the composed article a user reads, linking the two above
"""

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel


class RuleCategory(str, Enum):
    ACQUISITION_TAX = "acquisition_tax"        # 취득세
    TRANSFER_TAX = "transfer_tax"               # 양도소득세
    COMPREHENSIVE_REAL_ESTATE_TAX = "comprehensive_real_estate_tax"  # 종합부동산세
    RENTAL_POLICY = "rental_policy"             # 임대차 정책
    LOAN_REGULATION = "loan_regulation"         # 대출/LTV/DSR 규제
    RECONSTRUCTION_POLICY = "reconstruction_policy"  # 재건축/재개발


class LegalRule(BaseModel):
    """A single law/regulation clause, versioned by effective date."""

    id: str
    category: RuleCategory
    title: str
    summary: str
    legal_basis: str          # e.g. "지방세법 제11조"
    effective_from: date
    effective_until: date | None = None
    source_url: str
    last_verified_at: datetime


class FieldInsight(BaseModel):
    """Practitioner knowledge from actual transactions or site visits (임장)."""

    id: str
    region: str                # e.g. "서울 강동구 고덕동"
    property_type: str         # e.g. "아파트", "재건축 예정 단지"
    observed_at: date
    author: str
    note: str
    related_rule_ids: list[str] = []


class WikiEntry(BaseModel):
    """The composed article surfaced to the user: rule + practitioner context."""

    id: str
    slug: str
    title: str
    body_markdown: str
    rule_ids: list[str] = []
    insight_ids: list[str] = []
    updated_at: datetime
