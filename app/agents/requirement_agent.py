from __future__ import annotations

import re

from app.models.schemas import ShoppingRequirements


def _extract_budget(text: str) -> float | None:
    normalized = text.lower().replace("inr", " rs ").replace("rupees", " rs ").replace("rupee", " rs ")
    normalized = normalize_currency_tokens(normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()

    patterns = [
        r"(?:under|below|within|max(?:imum)?\s*budget|budget(?:\s*of)?)\s*(?:rs\.?|inr)?\s*([0-9][0-9,\.]*)\s*(k)?\b",
        r"(?:rs\.?|inr)\s*([0-9][0-9,\.]*)",
        r"([0-9][0-9,\.]*)\s*(?:rs\.?|inr)",
        r"([0-9][0-9,\.]*)\s*k\b",
    ]

    candidates: list[float] = []
    for pattern in patterns:
        for match in re.finditer(pattern, normalized, flags=re.I):
            parts = match.groups()
            if not parts:
                continue
            value = str(parts[0]).replace(",", "")
            multiplier = 1000 if len(parts) > 1 and bool(parts[1]) else 1
            numeric = float(value) * multiplier
            if numeric > 0:
                candidates.append(numeric)

    return max(candidates) if candidates else None


def normalize_currency_tokens(text: str) -> str:
    text = text.replace("\u20b9", " rs ").replace("₹", " rs ")
    text = re.sub(r"(?i)(?:rs\.?|inr|rupees?|currency)\s*", " rs ", text)
    text = re.sub(r"(?i)(?:\?|\u20b9|₹)\s*(?=\d)", " rs ", text)
    text = re.sub(r"(?<=\d)\s*(?:\?|\u20b9|₹)", "", text)
    return text


def _extract_ram(text: str) -> int | None:
    match = re.search(r"(\d+)\s*(?:gb|gib)", text, flags=re.I)
    return int(match.group(1)) if match else None


def _extract_use_cases(text: str) -> list[str]:
    use_cases = []
    if "python" in text:
        use_cases.append("python programming")
    if "machine learning" in text or "ml" in text:
        use_cases.append("machine learning")
    if "online class" in text or "study" in text or "class" in text:
        use_cases.append("online classes")
    return use_cases


def extract_requirements(request_text: str) -> ShoppingRequirements:
    text = request_text.strip()
    if not text:
        raise ValueError("Request text cannot be empty.")

    lower = text.lower()
    budget = _extract_budget(lower)
    category = "laptop" if any(token in lower for token in ("laptop", "notebook", "computer")) else "laptop"
    use_cases = _extract_use_cases(lower)
    min_ram = _extract_ram(lower)
    preferred_ram = 16 if "16 gb" in lower or "16gb" in lower else min_ram
    battery_requirement = 8.0 if "battery" in lower or "battery life" in lower else None

    clarification_needed = False
    clarification_question = None
    if budget is None:
        clarification_needed = True
        clarification_question = "What is your maximum budget in rupees?"
    if not use_cases:
        clarification_needed = True
        clarification_question = clarification_question or "What are the primary tasks you need the laptop for?"
    if min_ram is None and preferred_ram is None:
        preferred_ram = 16
        min_ram = 16

    mandatory_constraints = []
    if budget is not None:
        mandatory_constraints.append(f"budget <= INR{budget:,.0f}")
    if min_ram is not None:
        mandatory_constraints.append(f"minimum RAM {min_ram}GB")
    if battery_requirement is not None:
        mandatory_constraints.append(f"battery life >= {battery_requirement} hours")

    return ShoppingRequirements(
        request_text=text,
        budget=budget,
        category=category,
        use_cases=use_cases,
        min_ram_gb=min_ram or preferred_ram,
        preferred_ram_gb=preferred_ram,
        battery_requirement_hours=battery_requirement,
        mandatory_constraints=mandatory_constraints,
        preferences=["Good battery life", "Portable and reliable for study and coding"],
        clarification_needed=clarification_needed,
        clarification_question=clarification_question,
    )
