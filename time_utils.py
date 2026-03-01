import pandas as pd
from datetime import datetime


# -------------------------------------------------
# Helper: Safe Date Parsing
# -------------------------------------------------
def ensure_datetime(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
    """
    Converts a column to datetime safely.
    Handles messy formats automatically.
    """
    df[date_column] = pd.to_datetime(
        df[date_column],
        errors="coerce",
        infer_datetime_format=True,
    )
    return df


# -------------------------------------------------
# Get Current Quarter Info
# -------------------------------------------------
def get_current_quarter():
    """
    Returns:
        (year, quarter_number)
    Example:
        (2026, 1)
    """
    today = datetime.today()
    quarter = (today.month - 1) // 3 + 1
    return today.year, quarter


# -------------------------------------------------
# Get Quarter Date Range
# -------------------------------------------------
def get_quarter_range(year: int, quarter: int):
    """
    Returns start_date and end_date for given quarter.
    """
    start_month = 3 * (quarter - 1) + 1
    start_date = datetime(year, start_month, 1)

    if quarter == 4:
        end_date = datetime(year, 12, 31)
    else:
        end_date = datetime(year, start_month + 3, 1) - pd.Timedelta(days=1)

    return start_date, end_date


# -------------------------------------------------
# Filter: This Quarter
# -------------------------------------------------
def filter_this_quarter(df: pd.DataFrame, date_column: str):
    """
    Filters dataframe for current quarter.
    """
    df = ensure_datetime(df, date_column)

    year, quarter = get_current_quarter()
    start_date, end_date = get_quarter_range(year, quarter)

    filtered = df[
        (df[date_column] >= start_date) &
        (df[date_column] <= end_date)
    ]

    return filtered


# -------------------------------------------------
# Filter: Last Quarter
# -------------------------------------------------
def filter_last_quarter(df: pd.DataFrame, date_column: str):
    """
    Filters dataframe for previous quarter.
    """
    df = ensure_datetime(df, date_column)

    year, quarter = get_current_quarter()

    if quarter == 1:
        quarter = 4
        year -= 1
    else:
        quarter -= 1

    start_date, end_date = get_quarter_range(year, quarter)

    filtered = df[
        (df[date_column] >= start_date) &
        (df[date_column] <= end_date)
    ]

    return filtered


# -------------------------------------------------
# Filter: Year-to-Date (YTD)
# -------------------------------------------------
def ytd_filter(df: pd.DataFrame, date_column: str):
    """
    Filters dataframe from Jan 1 to today.
    """
    df = ensure_datetime(df, date_column)

    today = datetime.today()
    start_date = datetime(today.year, 1, 1)

    filtered = df[
        (df[date_column] >= start_date) &
        (df[date_column] <= today)
    ]

    return filtered
