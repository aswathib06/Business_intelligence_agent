import streamlit as st
from data_loader import load_data
from data_cleaner import clean_deals, clean_work_orders
from analytics import pipeline_by_sector, revenue_summary, conversion_rate
from intelligence import risk_scoring, sector_performance_index

st.title("🚀 Founder BI Agent (CSV Version)")

deals, work_orders = load_data()
deals = clean_deals(deals)
work_orders = clean_work_orders(work_orders)

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

if menu == "Pipeline Analysis":
    sector = st.text_input("Enter sector (optional)")
    result = pipeline_by_sector(deals, sector)
    st.dataframe(result)

elif menu == "Revenue Summary":
    sector = st.text_input("Enter sector (optional)")
    total, avg = revenue_summary(work_orders, sector)
    st.write(f"Total Revenue: {total}")
    st.write(f"Average Revenue: {avg}")

elif menu == "Conversion Rate":
    rate = conversion_rate(deals)
    st.write(f"Conversion Rate: {rate}%")

elif menu == "Risk Analysis":
    risk_df = risk_scoring(deals)
    st.dataframe(risk_df)

elif menu == "Sector Performance Index":
    perf = sector_performance_index(deals, work_orders)
    st.dataframe(perf)
