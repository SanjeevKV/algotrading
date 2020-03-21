import pathlib
import os

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.absolute()
HISTORY = os.path.join(PROJECT_ROOT, "History")
BUY_ORDERS = os.path.join(PROJECT_ROOT, "Orders", "Buy")
SELL_ORDERS = os.path.join(PROJECT_ROOT, "Orders", "Sell")
BOUGHT_ORDERS = os.path.join(PROJECT_ROOT, "Orders", "Bought")
SOLD_ORDERS = os.path.join(PROJECT_ROOT, "Orders", "Sold")
CSV_EXTENSION = '.csv'