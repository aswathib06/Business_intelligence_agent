import pandas as pd
from config import DEALS_PATH, WORK_ORDERS_PATH

def load_data():
    deals = pd.read_excel(DEALS_PATH)
    work_orders = pd.read_excel(WORK_ORDERS_PATH)
    return deals, work_orders
