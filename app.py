import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import matplotlib.pyplot as plt
from openai import OpenAI, RateLimitError
import time


# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------

st.set_page_config(page_title="Founder BI Agent", layout="wide")

OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", None)
MONDAY_API_KEY = st.secrets.get("MONDAY_API_KEY", None)
DEALS_BOARD_ID = st.secrets.get("DEALS_BOARD_ID", None)
WORK_ORDERS_BOARD_ID = st.secrets.get("WORK_ORDERS_BOARD_ID", None)

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


# ---------------------------------------------------
# MONDAY DATA FETCH
# ---------------------------------------------------

def fetch_board_data(board_id):
    if not MONDAY_API_KEY:
        st.error("Monday API key not configured.")
        return pd.DataFrame()

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
# METRICS ENGINE
# ---------------------------------------------------

def pipeline_metrics(df):

    # Try to detect correct deal value column
    value_column = None
    for col in df.columns:
        if "value" in col:
            value_column = col
            break

    if not value_column:
        return {"Error": "No deal value column found"}

    df[value_column] = pd.to_numeric(df[value_column], errors="coerce")

    prob_column = None
    for col in df.columns:
        if "prob" in col:
            prob_column = col
            break

    if prob_column:
        df[prob_column] = pd.to_numeric(df[prob_column], errors="coerce")
    else:
        df["temp_prob"] = 1
        prob_column = "temp_prob"

    total_deals = len(df)
    total_value = df[value_column].sum()
    weighted_pipeline = (df[value_column] * df[prob_column]).sum()
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

    value_column = next((col for col in df.columns if "value" in col), None)
    prob_column = next((col for col in df.columns if "prob" in col), None)

    if not value_column:
        return df

    df[value_column] = pd.to_numeric(df[value_column], errors="coerce")

    if prob_column:
        df[prob_column] = pd.to_numeric(df[prob_column], errors="coerce")
    else:
        df["temp_prob"] = 1
        prob_column = "temp_prob"

    max_value = df[value_column].max() or 1

    df["risk_score"] = (
        (1 - df[prob_column]) * 0.6 +
        (df[value_column] / max_value) * 0.4
    )

    return df


# ---------------------------------------------------
# RULE-BASED PARSER (Fallback)
# ---------------------------------------------------

def rule_based_parse(query):
    query = query.lower()

    intent = "pipeline"
    if "risk" in query:
        intent = "risk"
    elif "revenue" in query:
        intent = "revenue"

    sector = None
    if "energy" in query:
        sector = "energy"
    elif "healthcare" in query:
        sector = "healthcare"
    elif "manufacturing" in query:
        sector = "manufacturing"

    timeframe = "this_quarter" if "quarter" in query else None

    return {
        "intent": intent,
        "sector": sector,
        "timeframe": timeframe
    }


# ---------------------------------------------------
# INTENT PARSER (LLM SAFE)
# ---------------------------------------------------

def parse_query(query):
    if client is None:
        return rule_based_parse(query)

    prompt = f"""
    Extract:
    - intent (pipeline, risk, revenue)
    - sector (if mentioned)
    - timeframe (if mentioned)

    Return JSON only.
    Question: {query}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        return json.loads(response.choices[0].message.content)

    except RateLimitError:
        st.warning("⚠️ OpenAI rate limit exceeded. Using rule-based parsing.")
        return rule_based_parse(query)

    except Exception:
        st.warning("⚠️ AI parsing failed. Using rule-based fallback.")
        return rule_based_parse(query)


# ---------------------------------------------------
# INSIGHT GENERATOR (SAFE)
# ---------------------------------------------------

def generate_insight(metrics):

    if client is None:
        return f"""
        Summary:
        Total pipeline value is {metrics.get('Total Pipeline Value', 0)}.

        Risk:
        Review high value deals with low probability.

        Recommendation:
        Focus on converting medium-to-high probability deals.
        """

    prompt = f"""
    Generate executive summary using:
    {metrics}

    Include:
    - Summary
    - Risk observation
    - Recommendation
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        return response.choices[0].message.content

    except RateLimitError:
        return "⚠️ AI service temporarily unavailable. Showing rule-based summary."

    except Exception:
        return "⚠️ AI insight generation failed."


# ---------------------------------------------------
# UI
# ---------------------------------------------------

st.title("📊 Founder BI Agent")

query = st.text_input("Ask your business question")

if st.button("Run Analysis"):

    deals = fetch_board_data(DEALS_BOARD_ID)
    work_orders = fetch_board_data(WORK_ORDERS_BOARD_ID)

    if deals.empty:
        st.error("No deal data found.")
        st.stop()

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
