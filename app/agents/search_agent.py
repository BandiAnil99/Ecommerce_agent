from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.schemas import ShoppingRequirements
from app.tools.product_tools import search_products


def find_matching_products(db: Session, requirements: ShoppingRequirements) -> list:
    max_budget = requirements.budget
    min_ram = requirements.min_ram_gb
    products = search_products(
        db,
        category=requirements.category,
        max_budget=max_budget,
        min_ram=min_ram,
    )
    return products
