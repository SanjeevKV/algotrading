import BucketTrading as bt
import sys
import configparser

sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()) )
import Placeholder.Locations as Locations
import Placeholder.Keywords as Keywords

if __name__ == '__main__':
    config_file = sys.argv[1]
    with open(config_file) as file:
        stock_variables = yaml.full_load(file)
    response = 0
    while response != 4 :
        company = input("Enter the symbol of the company:\n")
        response = int( input("1.Process LTP\n2.View Tables\n3.Approve Orders\n4.Exit\n") )
        print(response, type(response))
        if response == 1:
            bt.process(stock_variables,company)
        elif response == 2:
            table = int( input("Table 1. Pending Orders\n2.Approved Buffer\n3.Approved\n4.Squared Off\n") )
            if table == 1:
                bt.show_company(company, Locations.PENDING_ORDERS)
            elif table == 2:
                bt.show_company(company, Locations.APPROVED_BUFFER_ORDERS)
            elif table == 3:
                bt.show_company(company, Locations.APPROVED_ORDERS)
            elif table == 4:
                bt.show_company(company, Locations.SQUARED_ORDERS)
        elif response == 3:
            bt.approve_order(company, Locations.APPROVED_BUFFER_ORDERS)
