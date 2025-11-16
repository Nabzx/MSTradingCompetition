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

    print(tmp)

    print(f"Value : £{tmp["GBP"] + (tmp["EUR"] / convert)}")

#gets the window
def getWindow(data, size):
    if size >= len(data):
        return data
    
    return data[-size:]

#code \/ \/
def proccess(i):
    #print(f"Expected to trade at: {str(get_price())}" )

    history.append({"time":time.time(), "EURGBP":get_price()})

    small = getWindow(history, 5)
    large = getWindow(history, 30)

    sg = np.polyfit([i["time"] for i in small], [i["EURGBP"] for i in small], 1)[0]
    lg = np.polyfit([i["time"] for i in large], [i["EURGBP"] for i in large], 1)[0]

    print(f"Grad s : {sg}")
    print(f"Grad l : {lg}")

    #print(f"Inv : {get_inventory(TRADER_ID)}")

    if lg > 0:
        trad = trade(TRADER_ID, lg*100000, Side.BUY)
    else:
        trad = trade(TRADER_ID, lg*-100000, Side.SELL)


    print(f"Effectively traded {lg*1000000} at: {trad}")

    calcInvValue(TRADER_ID)



if __name__ == '__main__':
    #for i in range(0, 3):
        #trade(TRADER_ID, 100000, Side.SELL)

        #time.sleep(1)

    #print(f"Expected to trade at: {str(get_price())}" )
    #print(f"Effectively traded at: {trade(TRADER_ID, 100, Side.BUY)}")

    for i in range(0, 100):
        proccess(i)

        time.sleep(1)
