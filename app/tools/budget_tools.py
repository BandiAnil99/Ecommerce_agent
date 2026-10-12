from __future__ import annotations


def calculate_discounted_price(price: float, discount_percent: float) -> tuple[float, float]:
    discount_percent = max(0.0, float(discount_percent or 0.0))
    discount_amount = price * (discount_percent / 100.0)
    final_price = max(0.0, price - discount_amount)
    return final_price, discount_amount


def validate_budget(price: float, budget: float | None) -> tuple[bool, float | None]:
    if budget is None:
        return True, None
    if price <= budget:
        return True, budget - price
    return False, budget - price
