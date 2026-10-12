from __future__ import annotations

from app.models.schemas import ShoppingRequirements
from app.tools.budget_tools import calculate_discounted_price, validate_budget


def validate_budget_for_product(product: dict, requirements: ShoppingRequirements) -> tuple[bool, float | None, float]:
    price = product["price"]
    budget = requirements.budget
    fits, delta = validate_budget(price, budget)
    final_price, savings = calculate_discounted_price(price, product.get("discount_percent", 0.0))
    return fits, delta, final_price
