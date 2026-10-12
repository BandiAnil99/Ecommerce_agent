from __future__ import annotations

from app.models.schemas import ShoppingRequirements
from app.services.recommendation_service import rank_products


def recommend_products(requirements: ShoppingRequirements, products: list[dict], inventory: list[dict]) -> list[dict]:
    return rank_products(requirements, products, inventory)
