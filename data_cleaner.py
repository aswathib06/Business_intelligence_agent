import pandas as pd

def clean_deals(deals):
    deals.columns = deals.columns.str.strip()

    if "Sector" in deals.columns:
        deals["Sector"] = deals["Sector"].astype(str).str.lower().str.strip()

    if "Deal Value" in deals.columns:
        deals["Deal Value"] = pd.to_numeric(deals["Deal Value"], errors="coerce")

    if "Expected Close Date" in deals.columns:
        deals["Expected Close Date"] = pd.to_datetime(
            deals["Expected Close Date"], errors="coerce"
        )

    return deals


def clean_work_orders(work_orders):
    work_orders.columns = work_orders.columns.str.strip()

    if "Sector" in work_orders.columns:
        work_orders["Sector"] = (
            work_orders["Sector"].astype(str).str.lower().str.strip()
        )

    if "Revenue" in work_orders.columns:
        work_orders["Revenue"] = pd.to_numeric(
            work_orders["Revenue"], errors="coerce"
        )

    return work_orders
