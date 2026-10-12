from __future__ import annotations

from typing import Any, TypedDict


class WorkflowState(TypedDict):
    request_text: str
    requirements: dict[str, Any]
    matched_products: list[dict]
    inventory: list[dict]
    filtered_products: list[dict]
    comparison: list[dict]
    recommendation: list[dict]
    selected_product_id: str | None
    confirmation: bool
    cart: dict[str, Any]
    faq_query: str | None
    faq_answer: dict[str, Any]
