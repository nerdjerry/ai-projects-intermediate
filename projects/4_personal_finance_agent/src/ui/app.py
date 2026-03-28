"""
Streamlit front-end for the Personal Finance Agent.

This module builds a three-tab web UI that communicates with the FastAPI
backend over HTTP.  It demonstrates a clean separation between the
**presentation layer** (this file) and the **business logic** (API + services).

Architecture Notes:
    - The UI is a *thin client* — it contains no financial logic.  All
      computations (summaries, insights) are performed server-side, keeping
      the front-end easy to replace or extend.
    - ``httpx`` is used instead of ``requests`` for its async support and
      timeout handling.
    - ``pandas`` is used only for charting convenience; data manipulation
      still happens in the backend.
"""

import streamlit as st
import httpx
import pandas as pd

# Base URL of the FastAPI backend (must be started separately)
API_BASE = "http://localhost:8003/api/v1"

# --- Page configuration ---
st.set_page_config(page_title="Personal Finance Agent", layout="wide")
st.title("💰 Personal Finance Agent")

# Create three top-level tabs for the main user workflows
tab_chat, tab_transactions, tab_dashboard = st.tabs(["Chat", "Add Transaction", "Dashboard"])

# ──────────────────────────────────────────────────────────────────────
# Tab 1: Chat — natural-language interaction with the finance agent
# ──────────────────────────────────────────────────────────────────────
with tab_chat:
    st.subheader("Chat with your Finance Agent")
    message = st.text_input("Ask about your finances")
    if st.button("Send"):
        if message.strip():
            try:
                # POST the user's message to the agent chat endpoint
                resp = httpx.post(
                    f"{API_BASE}/chat",
                    json={"message": message},
                    timeout=30.0,
                )
                resp.raise_for_status()
                data = resp.json()
                # Display the agent's reply
                st.write(data["reply"])
                # If the agent returned insights, show each one as an info box
                if data.get("insights"):
                    st.subheader("Insights")
                    for insight in data["insights"]:
                        st.info(insight)
            except httpx.HTTPError as exc:
                st.error(f"API error: {exc}")

# ──────────────────────────────────────────────────────────────────────
# Tab 2: Add Transaction — simple form for manual transaction entry
# ──────────────────────────────────────────────────────────────────────
with tab_transactions:
    st.subheader("Add Transaction")
    amount = st.number_input("Amount ($)", min_value=0.01, step=0.01)
    category = st.selectbox("Category", ["food", "transport", "entertainment", "utilities", "other"])
    description = st.text_input("Description")
    if st.button("Add"):
        try:
            # POST the new transaction to the backend for persistence
            resp = httpx.post(
                f"{API_BASE}/transactions",
                json={"amount": amount, "category": category, "description": description},
                timeout=30.0,
            )
            resp.raise_for_status()
            st.success("Transaction added!")
        except httpx.HTTPError as exc:
            st.error(f"API error: {exc}")

# ──────────────────────────────────────────────────────────────────────
# Tab 3: Dashboard — visual overview of spending data
# ──────────────────────────────────────────────────────────────────────
with tab_dashboard:
    st.subheader("Spending Dashboard")
    try:
        # GET the spending summary from the backend
        resp = httpx.get(f"{API_BASE}/summary", timeout=30.0)
        resp.raise_for_status()
        summary = resp.json()
        # Display key metrics side-by-side using Streamlit columns
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Spending", f"${summary['total_spending']:.2f}")
        with col2:
            st.metric("Transactions", summary["transaction_count"])
        # Render a bar chart of spending by category (if data exists)
        if summary.get("by_category"):
            df = pd.DataFrame(
                list(summary["by_category"].items()),
                columns=["Category", "Amount"],
            )
            st.bar_chart(df.set_index("Category"))
    except httpx.HTTPError:
        st.warning("API not running. Start the server first.")
