import streamlit as st
from data_loader import load_data
from data_cleaner import clean_deals, clean_work_orders
from analytics import pipeline_by_sector, revenue_summary, conversion_rate
from intelligence import risk_scoring, sector_performance_index

st.title("Founder BI Agent")

deals, work_orders = load_data()
deals = clean_deals(deals)
work_orders = clean_work_orders(work_orders)

# 🔍 TEMPORARY DEBUG LINE
st.write("Deal Columns:", deals.columns)
st.write("Work Order Columns:", work_orders.columns)

menu = st.sidebar.selectbox(
    "Select Analysis",
    [
        "Pipeline Analysis",
        "Revenue Summary",
        "Conversion Rate",
        "Risk Analysis",
        "Sector Performance Index",
    ],
)
