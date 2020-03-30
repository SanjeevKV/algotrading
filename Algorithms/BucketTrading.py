import yaml
import sys
import pandas as pd
import os
import math
import random
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()) )
import Placeholder.Locations as Locations
import Placeholder.Keywords as Keywords

def get_ltp(company):
    '''
    Returns the LTP of a particular company - Real time
    :param company:
    :return:
    '''
    ltp = float(input("LTP of " + company + " :"))
    return ltp

def get_pending_orders(company):
    """
        Returns all the pending orders corresponding to a particular company
        These are the orders which are placed with the broker but not yet executed
    """
    pending_orders = pd.read_csv(Locations.PENDING_ORDERS)
    pending_orders_company = pending_orders[pending_orders[Keywords.SYMBOL] == company]
    return pending_orders_company

def get_approved_orders(company):
    """
        Returns all the approved orders corresponding to a particular company
        These are the orders that are approved in the exchange but not yet squared off
        Square off - Happens when a buy order meets its profitable sell order or vice versa in case of short-positions
    """
    approved_orders = pd.read_csv(Locations.APPROVED_ORDERS)
    approved_orders_company = approved_orders[approved_orders[Keywords.SYMBOL] == company]
    return approved_orders_company

def get_approved_buffer_orders(company):
    """
        Returns all the approved orders corresponding to a particular company still in the buffer (Not yet removed from pending and added to approved orders)
        These are the orders that are approved in the exchange but not yet squared off
        Square off - Happens when a buy order meets its profitable sell order or vice versa in case of short-positions
    """
    approved_buffer_orders = pd.read_csv(Locations.APPROVED_BUFFER_ORDERS)
    approved_buffer_orders_company = approved_buffer_orders[approved_buffer_orders[Keywords.SYMBOL] == company]
    return approved_buffer_orders_company

def get_squared_orders(company):
    """
        Returns all the squared-off orders corresponding to a particular company
        These are the orders that are approved and also squared-off by it's equal (quantity) and opposite order
        Square off - Happens when a buy order meets its profitable sell order or vice versa in case of short-positions
    """
    squared_orders = pd.read_csv(Locations.SQUARED_ORDERS)
    squared_orders_company = squared_orders[squared_orders[Keywords.SYMBOL] == company]
    return squared_orders_company

def delete_pending_approved_orders(company):
    """
        Deletes orders from pending_orders once they are approved and populated in ApprovedBuffer
    """
    approved_buffer_orders_company = get_approved_buffer_orders(company)[Keywords.ORDER_ID]
    pending_orders_company = get_pending_orders(company)
    pending_orders_company = pending_orders_company[~pending_orders_company[Keywords.ORDER_ID].isin(approved_buffer_orders_company)]
    return pending_orders_company

def delete_pending_redundant_orders(company):
    """
        Deletes redundant orders from pending_orders once it has more than 2 pending orders for a company - 
        That is, one order in either direction
    """
    pass

def add_pending_approved_orders(company):
    """
        Takes orders from ApprovedBuffer and adds them to Approved
    """
    approved_orders_company = get_approved_orders(company)
    approved_buffer_orders_company = get_approved_buffer_orders(company)
    approved_orders_company = pd.concat([approved_orders_company, approved_buffer_orders_company], axis = 0)
    return approved_orders_company

def delete_approved_buffer_orders(company):
    """
        Deletes orders from ApprovedBuffer - Typically done after the orders from Pending are deleted and added to Approved
    """
    approved_buffer_orders_company = get_approved_buffer_orders(company)
    approved_buffer_orders_company = approved_buffer_orders_company[0:0]
    return approved_buffer_orders_company

def square_off_approved_orders(company):
    """
        Maps buy orders of a company with the corresponding sell orders or vice versa once both the kinda orders are present in Approved
        Deletes the profitable buy orders once a corresponding matching (quantity) sold order is found
    """
    approved_orders_company = get_approved_orders(company)
    sold_orders = approved_orders_company[approved_orders_company[Keywords.ORDER_TYPE] == Keywords.SELL_ORDER]
    bought_orders = approved_orders_company[approved_orders_company[Keywords.ORDER_TYPE] == Keywords.BUY_ORDER]
    if len(sold_orders) > 0:
        mean_sold_price = sold_orders[Keywords.PRICE].mean()
        sum_sold_quantity = sold_orders[Keywords.QUANTITY].sum()
        matching_bought_orders = bought_orders[bought_orders[Keywords.PRICE] < mean_sold_price]
        sum_bought_quantity = matching_bought_orders[Keywords.QUANTITY].sum()
        if sum_bought_quantity == sum_sold_quantity:
            orders_to_drop = pd.concat((matching_bought_orders[Keywords.ORDER_ID], sold_orders[Keywords.ORDER_ID]))
            squared_off_approved_orders = approved_orders_company[approved_orders_company[Keywords.ORDER_ID].isin(orders_to_drop)]
            approved_orders_company = approved_orders_company[~approved_orders_company[Keywords.ORDER_ID].isin(orders_to_drop)]
            return square_off_approved_orders, approved_orders_company
        else:
            raise ValueError(sum_sold_quantity, "Sold order does not fully cancel the profitable Bought orders", sum_bought_quantity)

def place_new_order(stock_variables, company, order_type, price = -1, quantity = -1):
    pass

def  add_pending_orders(stock_variables,company):
    """
        Place new orders for a company, if required
    """

    ltp = get_ltp(company)
    pending_orders_company = get_pending_orders(company)
    approved_orders_company = get_approved_orders(company)
    price_delta_company = float(stock_variables[company][Keywords.PRICE_DELTA])
    trigger_delta_company = float(stock_variables[company][Keywords.TRIGGER_DELTA])
    profit_delta_company = float(stock_variables[company][Keywords.PROFIT_DELTA])

    # No outstanding lots
    if len(approved_orders_company) == 0:
        pending_orders_company = place_new_order(stock_variables, company, ltp, Keywords.BUY_ORDER)

    elif len(approved_orders_company) == 1:
        existing_order_price = approved_orders_company[Keywords.PRICE]
        higher_buy_price = existing_order_price + existing_order_price * float(stock_variables[company][Keywords.PRICE_DELTA])
        lower_buy_price = existing_order_price - existing_order_price * float(stock_variables[company][Keywords.PRICE_DELTA])
        pending_orders_company = place_new_order(stock_variables, company, higher_buy_price, Keywords.BUY_ORDER)
        pending_orders_company = place_new_order(stock_variables, company, lower_buy_price, Keywords.BUY_ORDER)    

    else:
        profitable_lots_at_ltp = approved_orders_company[approved_orders_company[Keywords.ORDER_TYPE] == Keywords.BUY_ORDER &
                                     approved_orders_company[Keywords.PRICE] < ltp].sort_values(Keywords.PRICE, ascending = False)
        unprofitable_lots_at_ltp = approved_orders_company[approved_orders_company[Keywords.ORDER_TYPE] == Keywords.BUY_ORDER &
                                     approved_orders_company[Keywords.PRICE] > ltp].sort_values(Keywords.PRICE, ascending = True)
        if len(profitable_lots_at_ltp) > 0:
            if len(unprofitable_lots_at_ltp) == 0:
                buy_price = profitable_lots_at_ltp[Keywords.PRICE][0] + \
                                profitable_lots_at_ltp[Keywords.PRICE][0] * float(stock_variables[company][Keywords.PRICE_DELTA])
                profitable_lots_at_ltp = profitable_lots_at_ltp[1:]
            sell_quantity = profitable_lots_at_ltp[Keywords.QUANTITY].sum()
            sell_price = profitable_lots_at_ltp[Keywords.PRICE][0] + \
                            profitable_lots_at_ltp[Keywords.PRICE][0] * float(stock_variables[company][Keywords.PROFIT_DELTA])
            buy_price = profitable_lots_at_ltp[Keywords.PRICE][-1] - \
                            profitable_lots_at_ltp[Keywords.PRICE][-1] * float(stock_variables[company][Keywords.PRICE_DELTA])
        else:
            sell_quantity = unprofitable_lots_at_ltp[Keywords.QUANTITY][0]
            sell_price = unprofitable_lots_at_ltp[Keywords.PRICE][0] + \
                            unprofitable_lots_at_ltp[Keywords.PRICE][0] * float(stock_variables[company][Keywords.PROFIT_DELTA])
            buy_price = unprofitable_lots_at_ltp[Keywords.PRICE][0] - \
                            unprofitable_lots_at_ltp[Keywords.PRICE][0] * float(stock_variables[company][Keywords.PRICE_DELTA])

        pending_orders_company = place_new_order(stock_variables, company, Keywords.BUY_ORDER, buy_price)
        pending_orders_company = place_new_order(stock_variables, company, Keywords.SELL_ORDER, sell_price, sell_quantity)

        return pending_orders_company

if __name__ == '__main__':
    '''
    Driver Program    
    '''
    config_file = sys.argv[1]

    with open(config_file) as file:
        stock_variables = yaml.full_load(file)

    for company in stock_variables.keys():
        process_current_price(stock_variables,company)