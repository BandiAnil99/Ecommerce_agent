from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class ProductRecord(BaseModel):
    product_id: str
    name: str
    brand: str
    category: str
    price: float
    discount_percent: float = 0.0
    ram_gb: int
    processor: str
    storage_gb: int
    storage_type: str
    battery_hours: float
    weight_kg: float
    stock_quantity: int
    delivery_days: int
    description: str
    warranty: str
    faq_document: str


class ShoppingRequirements(BaseModel):
    request_text: str
    budget: float | None = None
    category: str = "laptop"
    use_cases: list[str] = Field(default_factory=list)
    min_ram_gb: int | None = None
    preferred_ram_gb: int | None = None
    battery_requirement_hours: float | None = None
    mandatory_constraints: list[str] = Field(default_factory=list)
    preferences: list[str] = Field(default_factory=list)
    clarification_needed: bool = False
    clarification_question: str | None = None

    @field_validator("budget")
    @classmethod
    def validate_budget(cls, value):
        if value is not None and value <= 0:
            raise ValueError("Budget must be greater than zero.")
        return value


class ProductMatch(BaseModel):
    product_id: str
    score: float
    match_reason: str
    meets_budget: bool
    meets_ram: bool
    in_stock: bool
    missing_specs: list[str] = Field(default_factory=list)


class Recommendation(BaseModel):
    product_id: str
    rank: int
    score: float
    score_breakdown: dict[str, float]
    reasons: list[str]
    final_price: float
    savings: float
    availability: str


class AssistantResponse(BaseModel):
    requirements: ShoppingRequirements
    recommendations: list[Recommendation]
    comparison_data: list[dict[str, Any]]
    notes: list[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    request_text: str = Field(..., min_length=5)


class FAQRequest(BaseModel):
    question: str = Field(..., min_length=3)
    product_id: str | None = None


class FAQResponse(BaseModel):
    answer: str
    source_documents: list[str] = Field(default_factory=list)
    answer_confidence: str = "low"


class InventoryStatus(BaseModel):
    product_id: str
    in_stock: bool
    stock_quantity: int
    delivery_days: int
    status: str


class CartItemRequest(BaseModel):
    product_id: str
    quantity: int = Field(1, ge=1)
    confirmed: bool = False

    @field_validator("product_id")
    @classmethod
    def validate_product_id(cls, value):
        if not value or not value.strip():
            raise ValueError("Product ID is required.")
        return value.strip()


class CartPreviewRequest(BaseModel):
    cart_id: str | None = None
    items: list[CartItemRequest] = Field(default_factory=list)


class CartConfirmRequest(BaseModel):
    cart_id: str
    items: list[CartItemRequest]
    confirmed: bool = False


class CartPreviewResponse(BaseModel):
    cart_id: str
    valid: bool
    subtotal: float
    total: float
    savings: float
    message: str
    items: list[dict[str, Any]]


class CartResponse(BaseModel):
    cart_id: str
    status: str
    confirmed: bool
    total: float
    items: list[dict[str, Any]]


class ErrorResponse(BaseModel):
    detail: str


class HealthResponse(BaseModel):
    status: str
    ready: bool
