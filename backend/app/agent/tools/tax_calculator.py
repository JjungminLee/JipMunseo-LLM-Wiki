"""Example agent tool: rough transfer-tax (양도소득세) estimate.

A placeholder brackets table, not tax advice — real rates depend on holding
period, number of owned homes, and regulated-area status, all of which
should come from LegalRule records rather than being hardcoded here long-term.
"""

TOOL_SCHEMA = {
    "name": "estimate_transfer_tax",
    "description": "양도차익 기준으로 양도소득세를 개략적으로 추정합니다. 참고용이며 법적 효력이 없습니다.",
    "input_schema": {
        "type": "object",
        "properties": {
            "gain_krw": {"type": "number", "description": "양도차익 (원)"},
            "holding_years": {"type": "number", "description": "보유 기간 (년)"},
        },
        "required": ["gain_krw", "holding_years"],
    },
}


def estimate_transfer_tax(gain_krw: float, holding_years: float) -> dict:
    # TODO: replace with rates sourced from LegalRule(category=TRANSFER_TAX)
    rate = 0.6 if holding_years < 1 else 0.4 if holding_years < 2 else 0.24
    return {
        "estimated_tax_krw": round(gain_krw * rate),
        "rate_applied": rate,
        "disclaimer": "참고용 추정치이며 실제 세액은 법령 및 개인 상황에 따라 다릅니다.",
    }
