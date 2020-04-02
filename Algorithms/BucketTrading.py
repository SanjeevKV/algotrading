import yaml
import sys
import pandas as pd
import os
import math
import random
import pathlib
from random import seed
from random import randint

seed(1)

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
    #print( os.stat(Locations.PENDING_ORDERS).st_size )
    pending_orders = pd.read_csv(Locations.PENDING_ORDERS) if \
                        os.path.isfile( Locations.PENDING_ORDERS ) and os.stat(Locations.PENDING_ORDERS).st_size > 0 else \
                        pd.DataFrame(columns=Keywords.PENDING_ORDER_COLUMNS)
    pending_orders_company = pending_orders[pending_orders[Keywords.SYMBOL] == company]
    return pending_orders_company

def get_approved_orders(company):
    """
        Returns all the approved orders corresponding to a particular company
        These are the orders that are approved in the exchange but not yet squared off
        Square off - Happens when a buy order meets its profitable sell order or vice versa in case of short-positions
    """
    approved_orders = pd.read_csv(Locations.APPROVED_ORDERS) if \
                        os.path.isfile( os.path.join(Locations.APPROVED_ORDERS) ) and os.stat(Locations.PENDING_ORDERS).st_size > 0 else \
                        pd.DataFrame(columns=Keywords.EXECUTED_ORDER_COLUMS)
    approved_orders_company = approved_orders[approved_orders[Keywords.SYMBOL] == company]
    return approved_orders_company

def get_approved_buffer_orders(company):
    """
        Returns all the approved orders corresponding to a particular company still in the buffer (Not yet removed from pending and added to approved orders)
        These are the orders that are approved in the exchange but not yet squared off
        Square off - Happens when a buy order meets its profitable sell order or vice versa in case of short-positions
    """
    approved_buffer_orders = pd.read_csv(Locations.APPROVED_BUFFER_ORDERS) if \
                        os.path.isfile( os.path.join(Locations.APPROVED_BUFFER_ORDERS) ) and os.stat(Locations.APPROVED_BUFFER_ORDERS).st_size > 0 else \
                        pd.DataFrame(columns=Keywords.EXECUTED_ORDER_COLUMS)
    approved_buffer_orders_company = approved_buffer_orders[approved_buffer_orders[Keywords.SYMBOL] == company]
    return approved_buffer_orders_company

def get_squared_orders(company):
    """
        Returns all the squared-off orders corresponding to a particular company
        These are the orders that are approved and also squared-off by it's equal (quantity) and opposite order
        Square off - Happens when a buy order meets its profitable sell order or vice versa in case of short-positions
    """
    squared_orders = pd.read_csv(Locations.SQUARED_ORDERS) if \
                        os.path.isfile( os.path.join(Locations.SQUARED_ORDERS) ) and os.stat(Locations.PENDING_ORDERS).st_size > 0 else \
                        pd.DataFrame(columns=Keywords.EXECUTED_ORDER_COLUMS)
    squared_orders_company = squared_orders[squared_orders[Keywords.SYMBOL] == company]
    return squared_orders_company

def delete_pending_approved_orders(company):
    """
        Deletes orders from pending_orders once they are approved and populated in ApprovedBuffer
    """
    approved_buffer_orders_company = get_approved_buffer_orders(company)[Keywords.ORDER_ID]
    pending_orders_company = get_pending_orders(company)
    pending_orders_company = pending_orders_company[~pending_orders_company[Keywords.ORDER_ID].isin(approved_buffer_orders_company)]
    update_company(company, Locations.PENDING_ORDERS, pending_orders_company)
    return pending_orders_company

def delete_pending_redundant_orders(stock_variables, company, ltp):
    """
        Deletes redundant orders from pending_orders once it has more than 2 pending orders for a company - 
        That is, one order in either direction
    """
    #ltp = get_ltp(company)
    pending_orders_company = get_pending_orders(company)
    upper_thresh = ltp + ltp * float(stock_variables[company][Keywords.PRICE_DELTA]) * \
                    float(stock_variables[company][Keywords.PATIENCE])
    lower_thresh = ltp - ltp * float(stock_variables[company][Keywords.PRICE_DELTA]) * \
                    float(stock_variables[company][Keywords.PATIENCE])
    
    print("Thresholds", lower_thresh, upper_thresh)
    # orders_to_delete = pending_orders_company[(pending_orders_company[Keywords.PRICE] < lower_thresh) | 
    #                                             (pending_orders_company[Keywords.PRICE] > upper_thresh)]
    orders_to_retain = pending_orders_company[(pending_orders_company[Keywords.PRICE] >= lower_thresh) & 
                                                (pending_orders_company[Keywords.PRICE] <= upper_thresh)]
    higher_than_ltp = orders_to_retain[orders_to_retain[Keywords.PRICE] >= ltp].sort_values(Keywords.PRICE, ascending = True)
    lower_than_ltp = orders_to_retain[orders_to_retain[Keywords.PRICE] < ltp].sort_values(Keywords.PRICE, ascending = False)

    if len(higher_than_ltp) > 1:
        higher_than_ltp = higher_than_ltp.iloc[0]

    if len(lower_than_ltp) > 1:
        lower_than_ltp = lower_than_ltp.iloc[0]

    orders_to_retain = pd.concat((higher_than_ltp, lower_than_ltp))
    orders_to_delete = pending_orders_company[~pending_orders_company[Keywords.ORDER_ID].isin(orders_to_retain[Keywords.ORDER_ID])]
    
    update_company(company, Locations.PENDING_ORDERS, orders_to_retain)
    print("Orders Retained\n", orders_to_retain)
    print("Redundant Orders to delete\n", orders_to_delete)
    return orders_to_delete, pending_orders_company

def add_pending_approved_orders(company):
    """
        Takes orders from ApprovedBuffer and adds them to Approved
    """
    approved_orders_company = get_approved_orders(company)
    approved_buffer_orders_company = get_approved_buffer_orders(company)
    approved_orders_company = pd.concat([approved_orders_company, approved_buffer_orders_company], axis = 0)
    update_company(company, Locations.APPROVED_ORDERS, approved_orders_company)
    return approved_orders_company

def delete_approved_buffer_orders(company):
    """
        Deletes orders from ApprovedBuffer - Typically done after the orders from Pending are deleted and added to Approved
    """
    approved_buffer_orders_company = get_approved_buffer_orders(company)
    approved_buffer_orders_company = approved_buffer_orders_company[0:0]
    update_company(company, Locations.APPROVED_BUFFER_ORDERS, approved_buffer_orders_company)
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
            update_company(company, Locations.SQUARED_ORDERS, square_off_approved_orders)
            update_company(company, Locations.APPROVED_ORDERS, approved_orders_company)
            return square_off_approved_orders, approved_orders_company
        else:
            raise ValueError(sum_sold_quantity, "Sold order does not fully cancel the profitable Bought orders", sum_bought_quantity)

def place_new_order(stock_variables, company, pending_orders_company, ltp, order_type, price = -1, quantity = -1):
    #ltp = get_ltp(company)
    #pending_orders_company = get_pending_orders(company)
    difference_from_ltp = abs(ltp - price) / min(ltp, price)

    if difference_from_ltp > float(stock_variables[company][Keywords.PRICE_DELTA]) * \
                                     float(stock_variables[company][Keywords.PATIENCE]):
                                        return pending_orders_company

    order_id  = randint(0,50000)

    if quantity == -1:
        quantity = float(stock_variables[company][Keywords.PRINCIPAL]) / price
    
    if order_type  == Keywords.BUY_ORDER:
        trigger_price = price - price * float(stock_variables[company][Keywords.TRIGGER_DELTA])
    else:
        trigger_price = price + price * float(stock_variables[company][Keywords.TRIGGER_DELTA])

    pending_orders_company = pd.concat( (pending_orders_company,pd.DataFrame([ [company, order_id, price, quantity,
                                 trigger_price, order_type] ], columns=Keywords.PENDING_ORDER_COLUMNS) ) )
    return  pending_orders_company

def out_of_range(stock_variables, company, price, ltp):
    """
        Binary test - Checks whether the price is out of range from ltp (Highly unlikely to hit / Hit other orders before this order)
    """
    patience = float(stock_variables[company][Keywords.PATIENCE])
    price_delta = float(stock_variables[company][Keywords.PRICE_DELTA])
    diff = abs(ltp - price) / price
    if diff > patience * price_delta:
        return True
    return False

def get_prices_in_range(stock_variables, company, price, ltp):
    """
        Returns a pair (p1, p2) of prices which are closest to ltp but an integral multiple difference of PRICE_DELTA
        from price
    """
    price_delta = float(stock_variables[company][Keywords.PRICE_DELTA])
    diff = abs(ltp - price) / price
    p1 = math.floor(diff / price_delta)
    p2 = math.ceil(diff / price_delta)
    if ltp > price:
        return (price + price * p1 * price_delta, price + price * p2 * price_delta)
    else:
        return (price - price * p2 * price_delta, price - price * p1 * price_delta)

def  add_pending_orders(stock_variables,company, ltp):
    """
        Place new orders for a company, if required
    """

    #ltp = get_ltp(company)
    pending_orders_company = get_pending_orders(company)
    approved_orders_company = get_approved_orders(company)
    #print(stock_variables[company])
    price_delta_company = float(stock_variables[company][Keywords.PRICE_DELTA])
    trigger_delta_company = float(stock_variables[company][Keywords.TRIGGER_DELTA])
    profit_delta_company = float(stock_variables[company][Keywords.PROFIT_DELTA])

    # No outstanding lots
    if len(approved_orders_company) == 0 and len(pending_orders_company) == 0:
        price_1 = ltp + ltp * float(stock_variables[company][Keywords.PROFIT_DELTA])
        price_2 = ltp - ltp * float(stock_variables[company][Keywords.PROFIT_DELTA])
        pending_orders_company = place_new_order(stock_variables, company, pending_orders_company, ltp, Keywords.BUY_ORDER, price_1)
        pending_orders_company = place_new_order(stock_variables, company, pending_orders_company, ltp, Keywords.BUY_ORDER, price_2)

    elif len(approved_orders_company) == 1:
        existing_order_price = approved_orders_company[Keywords.PRICE]
        higher_buy_price = existing_order_price + existing_order_price * float(stock_variables[company][Keywords.PRICE_DELTA])
        lower_buy_price = existing_order_price - existing_order_price * float(stock_variables[company][Keywords.PRICE_DELTA])
        if out_of_range(stock_variables, company, existing_order_price, ltp):
            price_1, price_2 = get_prices_in_range(stock_variables, company, pending_orders_company, existing_order_price, ltp)
            pending_orders_company = place_new_order(stock_variables, company, pending_orders_company, ltp, Keywords.BUY_ORDER, price_1)
            pending_orders_company = place_new_order(stock_variables, company, pending_orders_company, ltp, Keywords.BUY_ORDER, price_2)
        else:
            pending_orders_company = place_new_order(stock_variables, company, pending_orders_company, ltp, Keywords.BUY_ORDER, higher_buy_price)
            pending_orders_company = place_new_order(stock_variables, company, pending_orders_company, ltp, Keywords.BUY_ORDER, lower_buy_price)    

    elif len(approved_orders_company) > 1:
        #Lots bought at a price lesser than ltp
        profitable_lots_at_ltp = approved_orders_company[(approved_orders_company[Keywords.ORDER_TYPE] == Keywords.BUY_ORDER) &
                                     (approved_orders_company[Keywords.PRICE] < ltp)].sort_values(Keywords.PRICE, ascending = False)
        #Lots bought at a price higher than ltp
        unprofitable_lots_at_ltp = approved_orders_company[(approved_orders_company[Keywords.ORDER_TYPE] == Keywords.BUY_ORDER) &
                                     (approved_orders_company[Keywords.PRICE] > ltp)].sort_values(Keywords.PRICE, ascending = True)
        
        if len(profitable_lots_at_ltp) > 0:
            #At least one lot is bought at a price lesser than the ltp
            if len(unprofitable_lots_at_ltp) == 0:
                #All lots are bought at a price lesser than ltp
                buy_price = profitable_lots_at_ltp[Keywords.PRICE][0] + \
                                profitable_lots_at_ltp[Keywords.PRICE][0] * float(stock_variables[company][Keywords.PRICE_DELTA])
                #At least one lot should always be in contention
                profitable_lots_at_ltp = profitable_lots_at_ltp[1:]

            sell_quantity = profitable_lots_at_ltp[Keywords.QUANTITY].sum()
            sell_price = profitable_lots_at_ltp[Keywords.PRICE][0] + \
                            profitable_lots_at_ltp[Keywords.PRICE][0] * float(stock_variables[company][Keywords.PROFIT_DELTA])
            buy_price = profitable_lots_at_ltp[Keywords.PRICE][-1] - \
                            profitable_lots_at_ltp[Keywords.PRICE][-1] * float(stock_variables[company][Keywords.PRICE_DELTA])
        elif len(unprofitable_lots_at_ltp) > 0:
            sell_quantity = unprofitable_lots_at_ltp[Keywords.QUANTITY][0]
            sell_price = unprofitable_lots_at_ltp[Keywords.PRICE][0] + \
                            unprofitable_lots_at_ltp[Keywords.PRICE][0] * float(stock_variables[company][Keywords.PROFIT_DELTA])
            buy_price = unprofitable_lots_at_ltp[Keywords.PRICE][0] - \
                            unprofitable_lots_at_ltp[Keywords.PRICE][0] * float(stock_variables[company][Keywords.PRICE_DELTA])

        if out_of_range(stock_variables, company,buy_price, ltp):
            price_1, price_2 = get_prices_in_range(stock_variables, company, buy_price, ltp)
            pending_orders_company = place_new_order(stock_variables, company, pending_orders_company, ltp, Keywords.BUY_ORDER, price_1)
            pending_orders_company = place_new_order(stock_variables, company, pending_orders_company, ltp, Keywords.BUY_ORDER, price_2)
            pending_orders_company = place_new_order(stock_variables, company, pending_orders_company, ltp, Keywords.SELL_ORDER, price_1, sell_quantity)
        else:    
            pending_orders_company = place_new_order(stock_variables, company, pending_orders_company, ltp, Keywords.BUY_ORDER, buy_price)
            pending_orders_company = place_new_order(stock_variables, company, pending_orders_company, ltp, Keywords.SELL_ORDER, sell_price, sell_quantity)
        

    update_company(company, Locations.PENDING_ORDERS, pending_orders_company)
    print("Added Pending Orders\n", pending_orders_company)
    return pending_orders_company

def approve_order(company):
    order_id = int(input("Enter OrderID which you want to approve"))
    executed_price = float(input("Enter the executed price at which the order was executed"))
    pending_orders_company = get_pending_orders(company)
    approved_buffer_orders_company = get_approved_buffer_orders(company)
    executed_order = pending_orders_company[pending_orders_company[Keywords.ORDER_ID] == order_id]
    executed_order[Keywords.EXECUTED_PRICE] = executed_price
    approved_buffer_orders_company = pd.concat((approved_buffer_orders_company, executed_order))
    update_company(company, Locations.APPROVED_BUFFER_ORDERS, approved_buffer_orders_company)
    return approved_buffer_orders_company


def process(stock_variables, company):
    ltp = get_ltp(company)
    delete_pending_approved_orders(company)
    delete_pending_redundant_orders(stock_variables, company, ltp)
    delete_approved_buffer_orders(company)
    square_off_approved_orders(company)
    add_pending_orders(stock_variables,company, ltp)
    add_pending_approved_orders(company)

def update_company(company, table, updated_company):
    current_table = pd.read_csv(table)
    current_table_trimmed = current_table[current_table[Keywords.SYMBOL] != company]
    updated_table = pd.concat( (current_table_trimmed, updated_company) )
    updated_table.to_csv(table, index = False)

# def show_company(company, table):
#     table = pd.read_csv(table)
#     table = table[table[Keywords.SYMBOL] == company]
#     table.show()

if __name__ == '__main__':
    '''
    Driver Program    
    '''
    config_file = sys.argv[1]

    with open(config_file) as file:
        stock_variables = yaml.full_load(file)

    for company in stock_variables.keys():
        process(stock_variables,company)