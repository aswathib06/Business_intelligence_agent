import pandas as pd


def pipeline_by_sector(deals, sector=None):
    df = deals.copy()

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # Filter by sector if provided
    if sector and "sector" in df.columns:
        df = df[df["sector"] == sector.lower()]

    # Check required columns exist
    if "stage" not in df.columns or "deal value" not in df.columns:
        return pd.DataFrame({"Error": ["Required columns (stage, deal value) not found in dataset."]})

    pipeline = (
        df.groupby("stage")["deal value"]
        .sum()
        .reset_index()
        .sort_values(by="deal value", ascending=False)
    )

    return pipeline


def revenue_summary(work_orders, sector=None):
    df = work_orders.copy()

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # Filter by sector if provided
    if sector and "sector" in df.columns:
        df = df[df["sector"] == sector.lower()]

    if "revenue" not in df.columns:
        return 0, 0

    total_revenue = df["revenue"].sum()
    avg_revenue = df["revenue"].mean()

    return total_revenue, avg_revenue


def conversion_rate(deals):
    df = deals.copy()

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    if "stage" not in df.columns:
        return 0

    won = df[df["stage"] == "closed won"]
    total = len(df)

    if total == 0:
        return 0

    return round(len(won) / total * 100, 2)
