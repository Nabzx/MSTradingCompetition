# python -m pip install requests

import json
import requests
import time
import numpy as np

URL = "http://fx-trading-game-leicester-challenge.westeurope.azurecontainer.io:443/"
TRADER_ID = "UpFoeHN6WBCJ0jZ1ZGqtFATY6qeN1spB"

history = [] # [{"time":unixTime, "EURGBP":float}, {"time":unixTime, "EURGBP":float}........ ]

class Side:
    BUY = "buy"
    SELL = "sell"

def get_price():
    api_url = URL + "/price/EURGBP"
    res = requests.get(api_url)
    if res.status_code == 200:
        return json.loads(res.content.decode('utf-8'))["price"]
    return None

def get_inventory(trader_id):
    api_url = URL + "/positions/" + trader_id
    res = requests.get(api_url)
    if res.status_code == 200:
        return json.loads(res.content.decode('utf-8'))
    return None

def trade(trader_id, qty, side):
    api_url = URL + "/trade/EURGBP"
    data = {"trader_id": trader_id, "quantity": qty, "side": side}
    res = requests.post(api_url, json=data)
    if res.status_code == 200:
        resp_json = json.loads(res.content.decode('utf-8'))
        if resp_json["success"]:
            return resp_json["price"]
    return None

def calcInvValue(trader_id):
    tmp = get_inventory(trader_id)
    convert = get_price()

    print(f"Value : £{tmp["GBP"] + (tmp["EUR"] * convert)}")

#gets the window
def getWindow(data, size):
    if size >= len(data):
        return data
    
    return data[-size:]


if __name__ == '__main__':
    for i in range(0, 1):
        trade(TRADER_ID, 100000, Side.BUY)

        time.sleep(1)
        print("hello")
