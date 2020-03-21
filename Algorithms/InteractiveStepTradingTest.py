import StepTrading as st
import sys
import configparser
if __name__ == '__main__':
    config_file = sys.argv[1]
    company_list = sys.argv[2]
    config = configparser.ConfigParser()
    config.read(config_file)
    response = 0
    while response != 7 :
        company = input("Enter the symbol of the company:\n")
        response = int( input("1.Process LTP\n2.View historical orders\n3.View Buy orders\n4.View Sell orders\n5.Approve Buy orders\n6.Approve Sell orders\n7.Exit\n") )
        print(response, type(response))
        if response == 1:
            st.process_current_price(config,company)
        elif response == 2:
            st.view_historical_orders(company)
        elif response == 3:
            st.view_pending_order(company,True)
        elif response == 4:
            st.view_pending_order(company,False)
        elif response == 5:
            price = float(input("Input price\n"))
            quantity = input("Input quantity\n")
            st.approve_pending_order(company,True,price,quantity)
        elif response == 6:
            price = float(input("Input price\n"))
            quantity = input("Input quantity\n")
            st.approve_pending_order(company,False,price,quantity)
