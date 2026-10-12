from __future__ import annotations

from math import isfinite

from app.models.schemas import ShoppingRequirements


def _normalize(value: float | None, minimum: float = 0.0, maximum: float = 1.0) -> float:
    if value is None:
        return 0.0
    if not isfinite(value):
        return 0.0
    return max(0.0, min(1.0, (value - minimum) / (maximum - minimum) if maximum > minimum else 1.0))


def rank_products(requirements: ShoppingRequirements, products: list[dict], inventory: list[dict]) -> list[dict]:
    scored = []
    budget = requirements.budget
    min_ram = requirements.min_ram_gb or 0
    battery_requirement = requirements.battery_requirement_hours or 0
    for product in products:
        if budget is not None and product["price"] > budget:
            continue
        if product["ram_gb"] < min_ram:
            continue
        status = next((item for item in inventory if item["product_id"] == product["product_id"]), None)
        if status and status["stock_quantity"] <= 0:
            continue
        workload = 0.5
        if "python" in " ".join(requirements.use_cases).lower() or "machine learning" in " ".join(requirements.use_cases).lower():
            workload = 1.0 if "ryzen" in (product.get("processor") or "").lower() or "intel core i5" in (product.get("processor") or "").lower() or "i7" in (product.get("processor") or "").lower() or "i5" in (product.get("processor") or "").lower() else 0.7
        budget_fit = 1.0 if budget is None else max(0.0, 1.0 - (product["price"] / budget))
        ram_score = min(1.0, product["ram_gb"] / max(min_ram, 8))
        battery_score = min(1.0, product["battery_hours"] / max(battery_requirement, 8.0))
        value_score = 1.0 if product["storage_gb"] >= 512 else 0.7
        overall = 0.30 * workload + 0.25 * budget_fit + 0.20 * ram_score + 0.15 * battery_score + 0.10 * value_score
        reasons = []
        if product["ram_gb"] >= (requirements.preferred_ram_gb or min_ram):
            reasons.append("Satisfies preferred RAM requirement.")
        if product["price"] <= (budget or product["price"]):
            reasons.append("Fits the budget.")
        if product["battery_hours"] >= (battery_requirement or 0):
            reasons.append("Battery life supports extended use.")
        scored.append({
            "product_id": product["product_id"],
            "rank": 0,
            "score": round(overall, 4),
            "score_breakdown": {
                "workload": round(0.30 * workload, 4),
                "budget_fit": round(0.25 * budget_fit, 4),
                "ram": round(0.20 * ram_score, 4),
                "battery": round(0.15 * battery_score, 4),
                "value": round(0.10 * value_score, 4),
            },
            "reasons": reasons,
            "final_price": product["price"],
            "savings": 0.0,
            "availability": status["status"] if status else "unknown",
        })

    scored.sort(key=lambda item: item["score"], reverse=True)
    for idx, item in enumerate(scored, start=1):
        item["rank"] = idx
    return scored
