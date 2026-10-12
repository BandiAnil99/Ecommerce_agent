from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from app.agents.budget_agent import validate_budget_for_product
from app.agents.comparison_agent import compare_products
from app.agents.inventory_agent import check_inventory_for_products
from app.agents.recommendation_agent import recommend_products
from app.agents.requirement_agent import extract_requirements
from app.agents.search_agent import find_matching_products
from app.graph.state import WorkflowState


def analysis_node(state: WorkflowState) -> WorkflowState:
    requirements = extract_requirements(state["request_text"])
    state["requirements"] = requirements.model_dump()
    return state


def search_node(state: WorkflowState) -> WorkflowState:
    requirements = extract_requirements(state["request_text"])
    products = find_matching_products(state["db"], requirements)
    state["matched_products"] = [p.__dict__ for p in products]
    return state


def inventory_node(state: WorkflowState) -> WorkflowState:
    product_ids = [p["product_id"] for p in state.get("matched_products", [])]
    inventory = check_inventory_for_products(state["db"], product_ids)
    state["inventory"] = inventory
    state["filtered_products"] = [
        product for product in state.get("matched_products", [])
        if product["stock_quantity"] > 0 and (state["requirements"].get("budget") is None or product["price"] <= state["requirements"]["budget"])
    ]
    return state


def budget_node(state: WorkflowState) -> WorkflowState:
    if not state.get("filtered_products"):
        state["filtered_products"] = []
        return state
    validated = []
    for product in state["filtered_products"]:
        fits, _, final_price = validate_budget_for_product(product, extract_requirements(state["request_text"]))
        if fits:
            product["final_price"] = final_price
            validated.append(product)
    state["filtered_products"] = validated
    return state


def comparison_node(state: WorkflowState) -> WorkflowState:
    products = state.get("filtered_products", [])
    state["comparison"] = compare_products(products)
    return state


def recommendation_node(state: WorkflowState) -> WorkflowState:
    requirements = extract_requirements(state["request_text"])
    products = state.get("filtered_products", [])
    inventory = state.get("inventory", [])
    state["recommendation"] = recommend_products(requirements, products, inventory)
    return state


def selection_node(state: WorkflowState) -> WorkflowState:
    recs = state.get("recommendation", [])
    state["selected_product_id"] = recs[0]["product_id"] if recs else None
    return state


def cart_node(state: WorkflowState) -> WorkflowState:
    state["cart"] = {"selected_product_id": state.get("selected_product_id"), "confirmed": state.get("confirmation", False)}
    return state


def build_workflow() -> StateGraph:
    workflow = StateGraph(WorkflowState)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("search", search_node)
    workflow.add_node("inventory", inventory_node)
    workflow.add_node("budget", budget_node)
    workflow.add_node("comparison", comparison_node)
    workflow.add_node("recommendation", recommendation_node)
    workflow.add_node("selection", selection_node)
    workflow.add_node("cart", cart_node)
    workflow.add_edge(START, "analysis")
    workflow.add_edge("analysis", "search")
    workflow.add_edge("search", "inventory")
    workflow.add_edge("inventory", "budget")
    workflow.add_edge("budget", "comparison")
    workflow.add_edge("comparison", "recommendation")
    workflow.add_edge("recommendation", "selection")
    workflow.add_edge("selection", "cart")
    workflow.add_edge("cart", END)
    return workflow


def run_workflow(db: Any, request_text: str) -> dict[str, Any]:
    workflow = build_workflow().compile()
    initial = {"request_text": request_text, "db": db, "requirements": {}, "matched_products": [], "inventory": [], "filtered_products": [], "comparison": [], "recommendation": [], "selected_product_id": None, "confirmation": False, "cart": {}, "faq_query": None, "faq_answer": {}}
    result = workflow.invoke(initial)
    return result
