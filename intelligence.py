import pandas as pd
from datetime import datetime

def risk_scoring(deals):
    df = deals.copy()

    today = datetime.today()

    if "Expected Close Date" in df.columns:
        df["Days_Open"] = (today - df["Expected Close Date"]).dt.days

    def assign_risk(row):
        if row.get("Stage") == "Proposal" and row.get("Days_Open", 0) > 30:
            return "High Risk"
        if row.get("Deal Value", 0) > 1000000 and pd.isna(row.get("Expected Close Date")):
            return "High Risk"
        return "Normal"

    df["Risk_Level"] = df.apply(assign_risk, axis=1)

    return df[["Deal Name", "Stage", "Deal Value", "Risk_Level"]]


def sector_performance_index(deals, work_orders):
    sector_revenue = work_orders.groupby("Sector")["Revenue"].sum()
    sector_pipeline = deals.groupby("Sector")["Deal Value"].sum()

    performance = pd.concat(
        [sector_revenue, sector_pipeline], axis=1
    ).fillna(0)

    performance.columns = ["Revenue", "Pipeline"]

    performance["Score"] = (
        (performance["Revenue"] / performance["Revenue"].max()) * 0.5
        + (performance["Pipeline"] / performance["Pipeline"].max()) * 0.5
    )

    performance = performance.sort_values(by="Score", ascending=False)

    return performance.reset_index()
