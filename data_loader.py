import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_data():
    deals_path = os.path.join(BASE_DIR, "Deal funnel Data.xlsx")
    work_orders_path = os.path.join(BASE_DIR, "Work_Order_Tracker Data.xlsx")

    deals = pd.read_excel(deals_path)
    work_orders = pd.read_excel(work_orders_path)

    return deals, work_orders
