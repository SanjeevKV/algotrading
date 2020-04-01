SYMBOL = "symbol"
PRICE = "price" # Limit price
ORDER_TYPE = "order_type" # Buy/Sell
QUANTITY = "quantity" # PRINCIPAL / BUY_PRICE
TRIGGER_PRICE = "trigger_price" # Trigger price after which the order is supposed to execute
ORDER_ID = "order_id"
EXECUTED_PRICE = "executed_price"

BUY_ORDER = "buy"
SELL_ORDER = "sell"

PENDING_ORDER_COLUMNS = [SYMBOL, ORDER_ID, PRICE, QUANTITY, TRIGGER_PRICE, ORDER_TYPE]
EXECUTED_ORDER_COLUMS = [SYMBOL, ORDER_ID, EXECUTED_PRICE, QUANTITY, ORDER_TYPE]

NAME = "name"
PRINCIPAL = "principal"
PRICE_DELTA = "price_delta"
PROFIT_DELTA = "profit_delta"
TRIGGER_DELTA = "trigger_delta"
PATIENCE = "patience"