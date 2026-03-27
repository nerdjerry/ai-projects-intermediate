"""Streamlit UI for the Personal Finance Agent."""
import streamlit as st
import httpx
import pandas as pd

API_BASE = "http://localhost:8003/api/v1"

st.set_page_config(page_title="Personal Finance Agent", layout="wide")
st.title("💰 Personal Finance Agent")

tab_chat, tab_transactions, tab_dashboard = st.tabs(["Chat", "Add Transaction", "Dashboard"])

with tab_chat:
    st.subheader("Chat with your Finance Agent")
    message = st.text_input("Ask about your finances")
    if st.button("Send"):
        if message.strip():
            try:
                resp = httpx.post(
                    f"{API_BASE}/chat",
                    json={"message": message},
                    timeout=30.0,
                )
                resp.raise_for_status()
                data = resp.json()
                st.write(data["reply"])
                if data.get("insights"):
                    st.subheader("Insights")
                    for insight in data["insights"]:
                        st.info(insight)
            except httpx.HTTPError as exc:
                st.error(f"API error: {exc}")

with tab_transactions:
    st.subheader("Add Transaction")
    amount = st.number_input("Amount ($)", min_value=0.01, step=0.01)
    category = st.selectbox("Category", ["food", "transport", "entertainment", "utilities", "other"])
    description = st.text_input("Description")
    if st.button("Add"):
        try:
            resp = httpx.post(
                f"{API_BASE}/transactions",
                json={"amount": amount, "category": category, "description": description},
                timeout=30.0,
            )
            resp.raise_for_status()
            st.success("Transaction added!")
        except httpx.HTTPError as exc:
            st.error(f"API error: {exc}")

with tab_dashboard:
    st.subheader("Spending Dashboard")
    try:
        resp = httpx.get(f"{API_BASE}/summary", timeout=30.0)
        resp.raise_for_status()
        summary = resp.json()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Spending", f"${summary['total_spending']:.2f}")
        with col2:
            st.metric("Transactions", summary["transaction_count"])
        if summary.get("by_category"):
            df = pd.DataFrame(
                list(summary["by_category"].items()),
                columns=["Category", "Amount"],
            )
            st.bar_chart(df.set_index("Category"))
    except httpx.HTTPError:
        st.warning("API not running. Start the server first.")
