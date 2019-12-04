import ConfigParser
import sys
import pandas as pd
import os
import math
import random

history_location = '../History/'
buy_orders_location = '../Orders/Buy/'
sell_orders_location = '../Orders/Sell/'
bought_orders_location = '../Orders/Bought/'
sold_orders_location = '../Orders/Sold/'
extension = '.csv'

def get_historical_orders_from_file(company):
    '''
    Returns a dataFrame containing all the information about active lots from a file
    :param company:
    :return:
    '''
    df = pd.read_csv(history_location+company+extension) if os.path.isfile(history_location + company + extension) else \
        pd.DataFrame(columns=["symbol","buy_price","quantity","selling_price_threshold","trigger_price","trigger"])
    return df

def get_historical_orders(company,storage):
    '''
    Returns a dataFrame containing all the information about active lots from any storage interface
    :param company:
    :param storage:
    :return:
    '''
    if storage == 1:
        df = get_historical_orders_from_file(company)
        df.sort_values('buy_price',ascending=True,inplace=True)
        df['cumulative_quantity'] = df['quantity'].cumsum()
        return df

def get_current_price(company):
    '''
    Returns the LTP of a particular company - Real time
    :param company:
    :return:
    '''
    current_price = float(raw_input("LTP of " + company + " :"))
    return current_price

def get_orders_in_range(config,historical_orders,company,current_price):
    '''
    Only active orders within a certain %age of LTP are returned
    :param config:
    :param historical_orders:
    :param company:
    :param current_price:
    :return:
    '''
    orders_in_range = historical_orders[(historical_orders['buy_price'] > (current_price - current_price *
                                                                           float(config.get("RANGE",company)))) &
                                        (historical_orders['selling_price_threshold'] < (current_price + current_price *
                                                                                         float(config.get("RANGE",company))))]
    return orders_in_range

def set_new_global_triggers(historical_orders,current_price):
    '''
    Trigger for a particular lot is set whenever the LTP is greater than the lot's trigger_price
    :param historical_orders:
    :param current_price:
    :return:
    '''
    for i in range(len(historical_orders)):
        if current_price > historical_orders['trigger_price'][i]:
            historical_orders.iloc[i,list(historical_orders.columns).index('trigger')] = True

def set_new_range_triggers(orders_in_range):
    '''
    1. Trigger for a lot is set when there are no lots at a lesser price but at least one lot with higher price
    2. Trigger for a lot is set when there are at least 2 lots with higher price
    :param orders_in_range:
    :return:
    '''
    print orders_in_range
    print len(orders_in_range)
    orders_in_range.reset_index(inplace=True)
    for i in range(len(orders_in_range)):
        if len(orders_in_range[orders_in_range['selling_price_threshold'] > orders_in_range['selling_price_threshold'][i]]) > 0 and len(orders_in_range[orders_in_range['buy_price'] < orders_in_range['buy_price'][i]]) < 1:
            orders_in_range.iloc[i,list(orders_in_range.columns).index('trigger')] = True
        if len(orders_in_range[orders_in_range['selling_price_threshold'] > orders_in_range['selling_price_threshold'][i]]) > 1:
            orders_in_range.iloc[i,list(orders_in_range.columns).index('trigger')] = True

def set_sell_orders(config,company,historical_orders,current_price):
    '''
    Sell orders are placed for a lot only when the lot is triggered to be sold
    1. Sell the lot if triggered even if the current_price is lower than the selling_price_threshold
    2. If there are lots with selling_price_threshold < current_price place a consolidated single sell order
    :param historical_orders:
    :param current_price:
    :return:
    '''
    if not os.path.isfile(sell_orders_location + company + '.csv'):
        print "The file for the company " + company + "does not exist, filling with only columns"
        df = pd.DataFrame(columns=["order_id","quantity","sell_price","sltp"])
        df.to_csv(sell_orders_location + company + ".csv" ,index=False)

    lots_sellable = len(historical_orders[historical_orders['selling_price_threshold'] < current_price])
    print "*********************"

    pending_sell_order = pd.read_csv(sell_orders_location + company + '.csv')
    pending_sell_price = pending_sell_order['sell_price'][0] if len(pending_sell_order) > 0 else -1

    if len(historical_orders) > 0:
        if lots_sellable == 0:
            if historical_orders['trigger'][0] == True:
                print "Sell the first lot with LP : " , historical_orders['selling_price_threshold'][0] , "and SLTP : " , \
                      historical_orders['trigger_price'][0]
                if pending_sell_price != historical_orders['selling_price_threshold'][0]:
                    place_new_sell_order(config,company,historical_orders['selling_price_threshold'][0],historical_orders["cumulative_quantity"][0])
            else:
                print "Nothing to sell for now"
        else:
            print "Sell the " , lots_sellable , "lots with a cumulative shares of " , historical_orders["cumulative_quantity"][lots_sellable-1] , " at a LP of " , historical_orders['selling_price_threshold'][lots_sellable-1] , " and a SLTP of " , \
            historical_orders['trigger_price'][lots_sellable-1]
            if pending_sell_price != historical_orders['selling_price_threshold'][lots_sellable-1]:
                place_new_sell_order(config,company,historical_orders['selling_price_threshold'][lots_sellable-1],historical_orders["cumulative_quantity"][lots_sellable-1])

def place_new_buy_order(config,company,buy_price):
    '''
    Erases the existing buy orders of a company and places a new buy order
    :param config:
    :param company:
    :param buy_price:
    :return:
    '''
    df = pd.DataFrame(columns=["order_id","quantity","buy_price","sltp"])
    current_lot_worth = float(config.get("PRINCIPAL",company)) * float(config.get("IRR",company))
    current_lot_size = math.floor(current_lot_worth/buy_price)
    sltp = buy_price - buy_price * float(config.get("TRIGGER_LIMIT",company))
    #API call to place order
    order = [random.randint(0,10),current_lot_size,buy_price,sltp]
    df.loc[0] = order
    df.to_csv(buy_orders_location + company + '.csv',index=False)


def place_new_sell_order(config,company,sell_price,quantity):
    '''
    Place sell order after removing the existing sell orders
    :param config:
    :param company:
    :param sell_price:
    :param quantity:
    :return:
    '''
    df = pd.DataFrame(columns=["order_id","quantity","sell_price","sltp"])
    sltp = sell_price + sell_price * float(config.get("TRIGGER_LIMIT",company))
    #API call to place sell order and cancel the existing one
    order = [random.randint(0,10),quantity,sell_price,sltp]
    df.loc[0] = order
    df.to_csv(sell_orders_location + company + '.csv',index=False)

def set_buy_orders(config,company,orders_in_range,current_price):
    '''
    1. Do not buy if there are higher as well as lower orders
    2. Buy at the current price if there are no higher or lower orders
    3. Buy at a lower price if there is only a lot at higher price
    4. Buy at a higher price if there is only a lot at lower price
    :param config:
    :param company:
    :param orders_in_range:
    :param current_price:
    :return:
    '''
    lower_orders = orders_in_range[orders_in_range["buy_price"] < current_price]
    higher_orders = orders_in_range[orders_in_range["buy_price"] > current_price]
    lowest_high = min(higher_orders["buy_price"]) if len(higher_orders) > 0 else -1
    highest_low = max(lower_orders["buy_price"]) if len(lower_orders) > 0 else -1
    print "###########",lowest_high,highest_low

    if not os.path.isfile(buy_orders_location + company + '.csv'):
        print "The file for the company " + company + "does not exist, filling with only columns"
        df = pd.DataFrame(columns=["order_id","quantity","buy_price","sltp"])
        df.to_csv(buy_orders_location + company + ".csv" ,index=False)

    pending_buy_order = pd.read_csv(buy_orders_location + company + '.csv')
    pending_buy_price = pending_buy_order['buy_price'][0] if len(pending_buy_order) > 0 else -1

    if lowest_high > 0 and highest_low > 0:
        print "Nothing to buy at the moment"
    elif highest_low == -1 and lowest_high == -1:
        print "Buy at current_price as LP"
        if pending_buy_price != current_price:
            place_new_buy_order(config,company,current_price)
    elif highest_low == -1:
        print "Buy a lot at ", (lowest_high - lowest_high * float(config.get("PRICE_DELTA",company))), " of " , (float(config.get("PRINCIPAL",company)) *
                                                                                                          float(config.get("IRR",company))) / (lowest_high - lowest_high * float(config.get("PRICE_DELTA",company)))
        if pending_buy_price != (lowest_high - lowest_high * float(config.get("PRICE_DELTA",company))):
            place_new_buy_order(config,company,lowest_high - lowest_high * float(config.get("PRICE_DELTA",company)))
    else:
        print "Buy a lot at ", (highest_low + highest_low * float(config.get("PRICE_DELTA",company))), " of " , (float(config.get("PRINCIPAL",company)) *
                                                                                                          float(config.get("IRR",company))) / (highest_low - highest_low * float(config.get("PRICE_DELTA",company)))
        if pending_buy_price != (highest_low + highest_low * float(config.get("PRICE_DELTA",company))):
            place_new_buy_order(config,company,highest_low + highest_low * float(config.get("PRICE_DELTA",company)))

def process_current_price(config,company):
    '''
    Steps to be taken when LTP is refreshed
    :param config:
    :param company:
    :return:
    '''
    current_price = get_current_price(company) #API call to get the LTP
    process_approved_buy_orders(config,company)
    process_approved_sell_orders(company)
    historical_orders = get_historical_orders(company,1)
    orders_in_range = get_orders_in_range(config,historical_orders,company,current_price)
    set_new_global_triggers(historical_orders,current_price)
    set_new_range_triggers(orders_in_range)
    historical_orders.to_csv(history_location + company + extension,index=False) #Write after the triggers are set
    set_sell_orders(config,company,historical_orders,current_price)
    set_buy_orders(config,company,orders_in_range,current_price)

def process_approved_buy_orders(config,company):
    #API call to check the success of order_id and the following code is executed only in case of success
    df = pd.read_csv(bought_orders_location + company + extension) if os.path.isfile(bought_orders_location + company + extension) else []
    historical_orders = get_historical_orders(company,1)
    historical_orders = historical_orders[["symbol","buy_price","quantity","selling_price_threshold","trigger_price","trigger"]]
    if len(df) > 0:
        buy_price = df["price"][0]
        quantity = df["quantity"][0]
        selling_price_threshold = buy_price + buy_price * float(config.get("PRICE_DELTA",company))
        trigger_price = selling_price_threshold + selling_price_threshold * float(config.get("TRIGGER_LIMIT",company)) * float(config.get("TRIGGER",company))
        historical_orders.loc[len(historical_orders)] = [company,buy_price,quantity,selling_price_threshold,trigger_price,False]
    historical_orders.to_csv(history_location + company + extension,index=False)
    df = pd.DataFrame(columns=["symbol","price","quantity"])
    df.to_csv(bought_orders_location + company + extension, index=False)

def view_pending_order(company,buy):
    if buy:
        df = pd.read_csv(buy_orders_location + company + extension) if os.path.isfile(buy_orders_location + company + extension) else \
            pd.DataFrame(columns=["order_id","quantity","buy_price","sltp"])
        print df
    else:
        df = pd.read_csv(sell_orders_location + company + extension) if os.path.isfile(sell_orders_location + company + extension) else \
            pd.DataFrame(columns=["order_id","quantity","sell_price","sltp"])
        print df

def view_historical_orders(company):
    historical_orders = get_historical_orders(company,1)
    print historical_orders

def approve_pending_order(company,buy,price,quantity):
    df = pd.DataFrame(data=[[company,price,quantity]],columns=["symbol","price","quantity"])
    if buy:
        df.to_csv(bought_orders_location + company + extension,index=False)
        df = pd.DataFrame(columns=["order_id","quantity","buy_price","sltp"])
        df.to_csv(buy_orders_location + company + ".csv" ,index=False)
    else:
        df.to_csv(sold_orders_location + company + extension, index=False)
        df = pd.DataFrame(columns=["order_id","quantity","sell_price","sltp"])
        df.to_csv(sell_orders_location + company + ".csv" ,index=False)

def process_approved_sell_orders(company):
    df = pd.read_csv(sold_orders_location + company + extension) if os.path.isfile(sold_orders_location + company + extension) else []
    historical_orders = get_historical_orders(company,1)
    if len(df) > 0:
        quantity = df["quantity"][0]
        historical_orders_to_retain = historical_orders[historical_orders["cumulative_quantity"] > quantity]
        historical_orders_to_retain = historical_orders_to_retain[["symbol","buy_price","quantity","selling_price_threshold","trigger_price","trigger"]]
        historical_orders_to_retain.to_csv(history_location + company + extension,index=False)
    df = pd.DataFrame(columns=["symbol","price","quantity"])
    df.to_csv(sold_orders_location + company + extension, index=False)

if __name__ == '__main__':
    '''
    Driver Program    
    '''
    config_file = sys.argv[1]
    company_list = sys.argv[2]
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    companies = config.get("COMPANIES",company_list).split(',')
    for company in companies:
        process_current_price(config,company)