# 📊 Founder BI Agent

An AI-powered Business Intelligence Agent built on top of monday.com boards to help founders and executives quickly understand pipeline health, revenue performance, and deal risk.

This application integrates live with monday.com using API calls and provides real-time business insights through structured analytics and intelligent query parsing.

---

##  Features

### 🔗 Live monday.com Integration
- Fetches real-time data using monday GraphQL API
- No preloaded or cached data
- Supports multiple boards (Deals & Work Orders)

###  Data Normalization & Resilience
- Cleans inconsistent column names
- Handles missing/null values
- Converts probability and numeric fields safely
- Prevents crashes due to messy business data

### 📊 Business Intelligence Engine
- Total Pipeline Value
- Weighted Pipeline
- Average Deal Size
- Deal Risk Scoring
- Risk Distribution Visualization

###  Intelligent Query Parsing
- Supports natural language questions like:
  - "Which owner has the highest pipeline value?"
  - "Show pipeline for energy sector this quarter"
- Includes LLM-powered parsing (with rule-based fallback for reliability)

###  Production-Ready Stability
- Graceful fallback when OpenAI quota is exceeded
- Safe handling of API failures
- No application crashes under rate limits

---

##  Architecture Overview

User Query  
⬇  
Intent Parser (LLM + Rule-Based Fallback)  
⬇  
Live monday API Call  
⬇  
Data Cleaning & Normalization  
⬇  
Metrics Engine  
⬇  
Risk Engine  
⬇  
Executive Insight Generator  

---

##  Tech Stack

- Python
- Streamlit
- monday.com GraphQL API
- OpenAI (optional LLM parsing)
- Pandas
- Matplotlib

---

##  Environment Setup (Streamlit Secrets)

Add the following in Streamlit Cloud → Settings → Secrets:

```toml
OPENAI_API_KEY = "your_openai_key"
MONDAY_API_KEY = "your_monday_api_key"
DEALS_BOARD_ID = "your_deals_board_id"
WORK_ORDERS_BOARD_ID = "your_work_orders_board_id"
