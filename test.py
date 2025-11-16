import json
import requests
import time
import numpy as np

URL = "http://fx-trading-game-leicester-challenge.westeurope.azurecontainer.io:443/"
TRADER_ID = "UpFoeHN6WBCJ0jZ1ZGqtFATY6qeN1spB"

history = [] 

class Side:
    BUY = "buy"
    SELL = "sell"

def get_price():
    try:
        api_url = URL + "/price/EURGBP"
        res = requests.get(api_url)
        res.raise_for_status()
        return json.loads(res.content.decode('utf-8'))["price"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching price: {e}")
        return None

def get_inventory(trader_id):
    try:
        api_url = URL + "/positions/" + trader_id
        res = requests.get(api_url)
        res.raise_for_status()
        return json.loads(res.content.decode('utf-8'))
    except requests.exceptions.RequestException as e:
        print(f"Error fetching inventory: {e}")
        return None

def trade(trader_id, qty, side):
    try:
        api_url = URL + "/trade/EURGBP"
        data = {"trader_id": trader_id, "quantity": qty, "side": side}
        res = requests.post(api_url, json=data)
        res.raise_for_status()
        resp_json = json.loads(res.content.decode('utf-8'))
        if resp_json["success"]:
            return resp_json["price"]
    except requests.exceptions.RequestException as e:
        print(f"Error executing trade: {e}")
    return None

# Calculate and display the value of the current inventory
def calcInvValue(trader_id):
    tmp = get_inventory(trader_id)
    convert = get_price()
    if tmp and convert:
        eur_value = tmp["EUR"] / convert
        total_value = tmp["GBP"] + eur_value
        print(f"Value : £{total_value:.2f}")

# Return the latest 'size' amount of data from the history
def getWindow(data, size):
    if size >= len(data):
        return data
    return data[-size:]

# Helper function to determine if the trend gradient is significant
def is_trend_significant(gradient, threshold=0.00001):
    return abs(gradient) > threshold

# Basic position sizing based on risk management
def position_sizing(account_balance, risk_percent=0.01):
    risk_amount = account_balance * risk_percent
    return risk_amount

# Manage inventory to prevent large imbalances
def manage_inventory(trader_id):
    inventory = get_inventory(trader_id)
    if inventory:
        eur_balance = inventory["EUR"]
        gbp_balance = inventory["GBP"]

        # Implement logic to balance your EUR and GBP positions
        if eur_balance > gbp_balance * 1.5:
            trade(trader_id, eur_balance * 0.1, Side.SELL)  # Sell some EUR
        elif gbp_balance > eur_balance * 1.5:
            trade(trader_id, gbp_balance * 0.1, Side.BUY)   # Buy some EUR

# Process function with enhanced trading logic
def process(i):
    current_price = get_price()
    if current_price:
        history.append({"time": time.time(), "EURGBP": current_price})

        # Calculate small and large windows of price history
        small_window = getWindow(history, 5)
        large_window = getWindow(history, 30)

        # Calculate gradients for small and large windows
        sg = np.polyfit([i["time"] for i in small_window], [i["EURGBP"] for i in small_window], 1)[0]
        lg = np.polyfit([i["time"] for i in large_window], [i["EURGBP"] for i in large_window], 1)[0]

        print(f"Grad s: {sg}, Grad l: {lg}")

        # Check if trends are significant and execute trades accordingly
        if is_trend_significant(sg) and is_trend_significant(lg):
            if sg > 0 and lg > 0:  # Both gradients positive, buy
                trad = trade(TRADER_ID, 100000, Side.BUY)
                print(f"Bought at: {trad}")
            elif sg < 0 and lg < 0:  # Both gradients negative, sell
                trad = trade(TRADER_ID, 100000, Side.SELL)
                print(f"Sold at: {trad}")

        # Manage the inventory after trading
        manage_inventory(TRADER_ID)
        calcInvValue(TRADER_ID)

if __name__ == '__main__':
    # Initial trades for testing
    for i in range(0, 4):
        trade(TRADER_ID, 100000, Side.BUY)
        time.sleep(1)

    print(f"Expected to trade at: {str(get_price())}")
    print(f"Effectively traded at: {trade(TRADER_ID, 100, Side.BUY)}")

    # Main loop to process trades
    for i in range(0, 100):
        process(i)
        time.sleep(1)
