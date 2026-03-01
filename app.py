import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import matplotlib.pyplot as plt
from openai import OpenAI


# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------

st.set_page_config(page_title="Founder BI Agent", layout="wide")

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
MONDAY_API_KEY = st.secrets["MONDAY_API_KEY"]
DEALS_BOARD_ID = st.secrets["DEALS_BOARD_ID"]
WORK_ORDERS_BOARD_ID = st.secrets["WORK_ORDERS_BOARD_ID"]

client = OpenAI(api_key=OPENAI_API_KEY)


# ---------------------------------------------------
# MONDAY DATA FETCH
# ---------------------------------------------------

def fetch_board_data(board_id):
    url = "https://api.monday.com/v2"
    headers = {"Authorization": MONDAY_API_KEY}
    query = f"""
    query {{
      boards(ids: {board_id}) {{
        items_page(limit: 500) {{
          items {{
            name
            column_values {{
              text
              column {{ title }}
            }}
          }}
        }}
      }}
    }}
    """

    response = requests.post(url, json={"query": query}, headers=headers)
    data = response.json()

    items = data["data"]["boards"][0]["items_page"]["items"]

    rows = []
    for item in items:
        row = {"Item Name": item["name"]}
        for col in item["column_values"]:
            row[col["column"]["title"]] = col["text"]
        rows.append(row)

    return pd.DataFrame(rows)


# ---------------------------------------------------
# DATA CLEANING
# ---------------------------------------------------

def normalize_columns(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df


def clean_probability(df, column="closure_probability"):
    if column in df.columns:
        df[column] = (
            df[column]
            .astype(str)
            .str.replace("%", "")
        )
        df[column] = pd.to_numeric(df[column], errors="coerce") / 100
    return df


# ---------------------------------------------------
# TIME UTILITIES
# ---------------------------------------------------

def filter_this_quarter(df, date_column):
    df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
    today = datetime.today()
    quarter = (today.month - 1) // 3 + 1
    start_month = 3 * (quarter - 1) + 1
    start_date = datetime(today.year, start_month, 1)

    return df[df[date_column] >= start_date]


# ---------------------------------------------------
# METRICS ENGINE
# ---------------------------------------------------

def pipeline_metrics(df):
    total_deals = len(df)
    total_value = df["deal_value"].astype(float).sum()
    weighted_pipeline = (
        df["deal_value"].astype(float) *
        df["closure_probability"].astype(float)
    ).sum()

    avg_deal_size = total_value / total_deals if total_deals else 0

    return {
        "Total Deals": total_deals,
        "Total Pipeline Value": round(total_value, 2),
        "Weighted Pipeline": round(weighted_pipeline, 2),
        "Average Deal Size": round(avg_deal_size, 2)
    }


# ---------------------------------------------------
# RISK ENGINE
# ---------------------------------------------------

def calculate_risk(df):
    df["deal_value"] = pd.to_numeric(df["deal_value"], errors="coerce")
    df["closure_probability"] = pd.to_numeric(df["closure_probability"], errors="coerce")

    df["risk_score"] = (
        (1 - df["closure_probability"]) * 0.6 +
        (df["deal_value"] / df["deal_value"].max()) * 0.4
    )

    return df


# ---------------------------------------------------
# INTENT PARSER (LLM)
# ---------------------------------------------------

def parse_query(query):
    prompt = f"""
    Extract:
    - intent (pipeline, risk, revenue)
    - sector (if mentioned)
    - timeframe (if mentioned)

    Return JSON only.
    Question: {query}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return json.loads(response.choices[0].message.content)


# ---------------------------------------------------
# INSIGHT GENERATOR
# ---------------------------------------------------

def generate_insight(metrics):
    prompt = f"""
    Generate executive summary using:
    {metrics}

    Include:
    - Summary
    - Risk observation
    - Recommendation
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content


# ---------------------------------------------------
# UI
# ---------------------------------------------------

st.title("📊 Founder BI Agent")

query = st.text_input("Ask your business question")

if st.button("Run Analysis"):

    deals = fetch_board_data(DEALS_BOARD_ID)
    work_orders = fetch_board_data(WORK_ORDERS_BOARD_ID)

    deals = normalize_columns(deals)
    deals = clean_probability(deals)

    parsed = parse_query(query)

    if parsed.get("sector") and "sector/service" in deals.columns:
        deals = deals[
            deals["sector/service"]
            .str.lower()
            .str.contains(parsed["sector"].lower(), na=False)
        ]

    metrics = pipeline_metrics(deals)
    deals = calculate_risk(deals)

    insight = generate_insight(metrics)

    st.subheader("📌 KPIs")
    st.json(metrics)

    st.subheader("📈 Risk Distribution")
    fig, ax = plt.subplots()
    ax.hist(deals["risk_score"].dropna())
    st.pyplot(fig)

    st.subheader("🧠 Executive Insight")
    st.write(insight)
