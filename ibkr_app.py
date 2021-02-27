from ib_insync import *
from os import listdir, remove
from time import sleep
import pickle
from helper_functions import *
import pandas as pd

# Define your variables here ###########################################################################################
sampling_rate = 1 # How often, in seconds, to check for inputs from Dash?
# For TWS Paper account, default port is 7497
# For IBG Paper account, default port is 4002
port = 7497
# choose your master id. Mine is 10645. You can use whatever you want, just set it in API Settings within TWS or IBG.
master_client_id = 54321
# choose your dedicated id just for orders. I picked 1111.
orders_client_id = 12345
# account number: you'll need to fill in yourself. The below is one of my paper trader account numbers.
acc_number = 'DU3524272'

# Create an IB app; i.e., an instance of the IB() class from the ib_insync package
ib = IB()
# Connect your app to a running instance of IBG or TWS
# ib.disconnect()
ib.connect(host='127.0.0.1', port=port, clientId=master_client_id)

# Make sure you're connected -- stay in this while loop until ib.isConnected() is True.
while not ib.isConnected():
    sleep(.01)

# If connected, script exits the while loop and prints a success message
print('Connection Successful!')

# Request current time
current_time = ib.reqCurrentTime()

# Print current time
print('Current time is: {}'.format(current_time))

# Prepare a dataframe of 'currency_pair_history.csv' when there are some errors.
df_error = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume', 'average', 'barCount'])

# Main while loop of the app. Stay in this loop until the app is stopped by the user.
while True:
    # If the app finds a file named 'currency_pair.txt' in the current directory, enter this code block.
    if 'currency_pair.txt' in listdir():
        with open('currency_pair.txt', 'r') as f:
            currency_pair = f.read()

        remove('currency_pair.txt')

        try:
            contract = Forex(currency_pair)
            bars = ib.reqHistoricalData(contract,
                                        endDateTime='',
                                        durationStr='30 D',
                                        barSizeSetting='1 hour',
                                        whatToShow='MIDPOINT',
                                        useRTH=True
                                        )
            df = util.df(bars)

            if type(df).__name__ == 'NoneType':
                df_error.to_csv('currency_pair_history.csv')
            else:
                df.to_csv('currency_pair_history.csv')
        except AssertionError:
            df_error.to_csv('currency_pair_history.csv')

        # pass -- not return -- because this function doesn't return a value. It's called for what it does. In computer
        #   science, we say that it's called for its 'side effects'.
        pass

    # If there's a file named trade_order.p in listdir(), then enter the loop below.
    if 'trade_order.p' in listdir():

        trd_ordr = pickle.load(open('trade_order.p', 'rb'))

        trade_currency = trd_ordr['trade_currency']
        action = trd_ordr['action']
        total_quantity = trd_ordr['trade_amt']

        contract = Forex(trade_currency)
        order = MarketOrder(action=action,
                            totalQuantity=total_quantity)
        order.account = acc_number

        # Create a special instance of IB() JUST for entering orders.
        # The reason for this is because the way that Interactive Brokers automatically provides valid order IDs to
        #   ib_insync is not trustworthy enough to really rely on. It's best practice to set aside a dedicated client ID
        #   to ONLY be used for submitting orders, and close the connection when the order is successfully submitted.

        ib_orders = IB()
        ib_orders.connect(host='127.0.0.1', port=port, clientId=orders_client_id)
        new_order = ib_orders.placeOrder(contract, order)

        # The new_order object returned by the call to ib_orders.placeOrder() that you've written is an object of class
        #   `trade` that is kept continually updated by the `ib_insync` machinery. It's a market order; as such, it will
        #   be filled immediately.
        # In this while loop, we wait for confirmation that new_order filled.
        # while not new_order.orderStatus.status == 'Filled':
        #     ib_orders.sleep(0)
            # we use ib_orders.sleep(0) from the ib_insync module because the async socket connection
            # is not built for the normal time.sleep() function.

        # your code goes here
        remove('trade_order.p')
        ib_orders.disconnect()
        # pass: same reason as above.
        pass

    # sleep, for the while loop.
    ib.sleep(sampling_rate)
