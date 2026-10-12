from __future__ import annotations

import os
from typing import Any

import pandas as pd
import requests
import streamlit as st

DEFAULT_API_URL = os.getenv("SHOPPING_ASSISTANT_API_URL", "http://127.0.0.1:8765")

with st.sidebar.expander("Connection settings"):
    API_URL = st.text_input("FastAPI Base URL", value=DEFAULT_API_URL).rstrip("/")


def request_recommendations(request_text: str) -> None:
    try:
        response = requests.post(
            f"{API_URL}/assistant/chat",
            json={"request_text": request_text},
            timeout=20,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        st.error(f"Could not get recommendations: {exc}")
        return
    st.session_state["assistant_response"] = response.json()


@st.cache_data(ttl=60)
def fetch_products() -> list[dict[str, Any]]:
    response = requests.get(f"{API_URL}/products", params={"page": 1, "page_size": 20}, timeout=10)
    response.raise_for_status()
    payload = response.json()
    return payload.get("items", [])


st.title("Agentic Shopping Assistant")
st.caption("Sample database: illustrative laptop recommendations only")

with st.container(border=True):
    st.subheader("What are you shopping for?")
    request_text = st.text_area(
        "Describe your shopping need",
        value="I need a laptop under ₹60,000 for Python programming, machine learning basics, and online classes. I prefer 16 GB RAM and good battery life.",
        height=120,
        label_visibility="collapsed",
    )
    st.button(
        "Get recommendations",
        type="primary",
        on_click=request_recommendations,
        args=(request_text,),
    )

if "assistant_response" in st.session_state:
    response = st.session_state["assistant_response"]
    try:
        catalog_by_id = {product["product_id"]: product for product in fetch_products()}
    except requests.RequestException as exc:
        catalog_by_id = {}
        st.warning(f"Product details are unavailable: {exc}")

    left, right = st.columns([1, 2])
    with left:
        with st.container(border=True):
            st.subheader("Your requirements")
            requirements = response.get("requirements", {})
            st.write(f"**Budget:** {requirements.get('budget') or 'Not specified'}")
            st.write(f"**Use cases:** {', '.join(requirements.get('use_cases', [])) or 'Not specified'}")
            st.write(f"**Minimum RAM:** {requirements.get('min_ram_gb') or 'Not specified'} GB")
    with right:
        st.subheader("Recommended laptops")
        recommendations = response.get("recommendations", [])
        if recommendations:
            for product in recommendations:
                details = catalog_by_id.get(product.get("product_id"), {})
                price = product.get("final_price", details.get("price"))
                with st.container(border=True):
                    st.markdown(f"### {details.get('name', product.get('product_id', 'Laptop'))}")
                    st.caption(f"{product.get('product_id', '')} · Rank #{product.get('rank', '-')}")
                    metrics = st.columns(3)
                    metrics[0].metric("Price", f"₹{price:,.0f}" if price is not None else "Unavailable")
                    metrics[1].metric("RAM", f"{details.get('ram_gb', '-')} GB")
                    metrics[2].metric("Battery", f"{details.get('battery_hours', '-')} hrs")
                    reasons = product.get("reasons", [])
                    if reasons:
                        st.write(" ".join(reasons))
        else:
            st.info("No laptops matched those requirements. Try raising your budget or lowering the RAM requirement.")
    for note in response.get("notes", []):
        st.caption(note)

with st.expander("Browse the laptop catalog", expanded="assistant_response" not in st.session_state):
    st.caption("Compare the sample products currently available in the catalog.")
    try:
        products = fetch_products()
        if products:
            df = pd.DataFrame(products)
            columns = [column for column in ("product_id", "name", "price", "ram_gb", "battery_hours", "stock_quantity") if column in df]
            st.dataframe(df[columns], use_container_width=True, hide_index=True)
        else:
            st.info("The catalog is currently empty.")
    except requests.RequestException as exc:
        st.warning(f"Could not load the catalog: {exc}")

st.subheader("Have a product question?")
with st.form("faq_form"):
    question = st.text_input("Ask about a product or laptop feature")
    ask_faq = st.form_submit_button("Ask FAQ")
if ask_faq and question:
    try:
        resp = requests.post(f"{API_URL}/assistant/faq", json={"question": question}, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        st.write(data.get("answer", ""))
        st.caption(f"Sources: {data.get('source_documents', [])}")
    except requests.RequestException as exc:
        st.error(f"Could not get an FAQ answer: {exc}")
