from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.agents.faq_agent import answer_faq
from app.agents.requirement_agent import extract_requirements
from app.agents.recommendation_agent import recommend_products
from app.agents.search_agent import find_matching_products
from app.agents.inventory_agent import check_inventory_for_products
from app.agents.comparison_agent import compare_products
from app.models.database import SessionLocal
from app.models.schemas import AssistantResponse, ChatRequest, FAQRequest, FAQResponse, ShoppingRequirements

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/chat")
def chat(request: ChatRequest) -> dict:
    request_text = request.request_text
    requirements = extract_requirements(request_text)
    db = SessionLocal()
    try:
        products = find_matching_products(db, requirements)
        inventory = check_inventory_for_products(db, [p.product_id for p in products])
        eligible = []
        for product in products:
            if product.price <= (requirements.budget or product.price) and product.ram_gb >= (requirements.min_ram_gb or 0) and product.stock_quantity > 0:
                eligible.append(
                    {
                        "product_id": product.product_id,
                        "name": product.name,
                        "price": product.price,
                        "ram_gb": product.ram_gb,
                        "battery_hours": product.battery_hours,
                        "stock_quantity": product.stock_quantity,
                        "processor": product.processor,
                        "storage_gb": product.storage_gb,
                        "delivery_days": product.delivery_days,
                    }
                )
        recommendations = recommend_products(requirements, eligible, inventory)
        comparison = compare_products(eligible)
        response = {
            "requirements": requirements.model_dump(),
            "recommendations": recommendations,
            "comparison_data": comparison,
            "notes": ["Products were filtered using budget and RAM constraints before ranking."] if eligible else ["No eligible products were found in the current catalog."],
        }
        return response
    finally:
        db.close()


@router.post("/recommend")
def recommend(request: ShoppingRequirements) -> dict:
    db = SessionLocal()
    try:
        products = find_matching_products(db, request)
        inventory = check_inventory_for_products(db, [p.product_id for p in products])
        eligible = []
        for product in products:
            if product.price <= (request.budget or product.price) and product.ram_gb >= (request.min_ram_gb or 0) and product.stock_quantity > 0:
                eligible.append(
                    {
                        "product_id": product.product_id,
                        "name": product.name,
                        "price": product.price,
                        "ram_gb": product.ram_gb,
                        "battery_hours": product.battery_hours,
                        "stock_quantity": product.stock_quantity,
                        "processor": product.processor,
                        "storage_gb": product.storage_gb,
                        "delivery_days": product.delivery_days,
                    }
                )
        return {"recommendations": recommend_products(request, eligible, inventory)}
    finally:
        db.close()


@router.post("/faq")
def faq(request: FAQRequest) -> FAQResponse:
    result = answer_faq(request.question, request.product_id)
    return FAQResponse(**result)
