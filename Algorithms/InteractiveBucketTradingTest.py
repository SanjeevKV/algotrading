import BucketTrading as bt
import sys
import configparser
import yaml
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()) )
import Placeholder.Locations as Locations
import Placeholder.Keywords as Keywords

print(Keywords.PENDING_ORDER_COLUMNS)
print(Keywords.EXECUTED_ORDER_COLUMS)
if __name__ == '__main__':
    config_file = sys.argv[1]
    with open(config_file) as file:
        stock_variables = yaml.full_load(file)
    response = 0
    while response != 4 :
        company = input("Enter the symbol of the company:\n")
        response = int( input("1.Process LTP\n2.View Tables\n3.Approve Orders\n4.Exit\n") )
        #print(response, type(response))
        if response == 1:
            bt.process(stock_variables,company)
        elif response == 2:
            table = int( input("Table 1. Pending Orders\n2.Approved Buffer\n3.Approved\n4.Squared Off\n") )
            output = 1
            if table == 1:
                output = bt.get_pending_orders(company)
            elif table == 2:
                output = bt.get_approved_buffer_orders(company)
            elif table == 3:
                output = bt.get_approved_orders(company)
            elif table == 4:
                output = bt.get_squared_orders(company)
            print(output)
        elif response == 3:
            bt.approve_order(company, Locations.APPROVED_BUFFER_ORDERS)
