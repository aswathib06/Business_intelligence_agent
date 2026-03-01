import pandas as pd

def pipeline_by_sector(deals, sector=None):
    df = deals.copy()

    if sector:
        df = df[df["Sector"] == sector.lower()]

    pipeline = (
        df.groupby("Stage")["Deal Value"]
        .sum()
        .reset_index()
        .sort_values(by="Deal Value", ascending=False)
    )

    return pipeline


def revenue_summary(work_orders, sector=None):
    df = work_orders.copy()

    if sector:
        df = df[df["Sector"] == sector.lower()]

    total_revenue = df["Revenue"].sum()
    avg_revenue = df["Revenue"].mean()

    return total_revenue, avg_revenue


def conversion_rate(deals):
    won = deals[deals["Stage"] == "Closed Won"]
    total = len(deals)

    if total == 0:
        return 0

    return round(len(won) / total * 100, 2)
