import pathlib
import os

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.absolute()

PENDING_ORDERS = os.path.join(PROJECT_ROOT, "Orders", "Pending.csv")
PENDING_BUFFER_ORDERS = os.path.join(PROJECT_ROOT, "Orders", "PendingBuffer.csv")
APPROVED_ORDERS = os.path.join(PROJECT_ROOT, "Orders", "Approved.csv")
APPROVED_BUFFER_ORDERS = os.path.join(PROJECT_ROOT, "Orders", "ApprovedBuffer.csv")
SQUARED_ORDERS = os.path.join(PROJECT_ROOT, "Orders", "Squared.csv")