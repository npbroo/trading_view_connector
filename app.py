# save this as app.py
import json, config
from flask import Flask, escape, request, render_template
from binance.client import Client
from binance.enums import *

app = Flask(__name__)

client = Client(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY, tld='us')

def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print(f"sending order {order_type} - {side} {quantity} {symbol}")
        #order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity, time=time)
        order = client.create_test_order(symbol="ETHUSDT", side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return order

@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/webhook', methods=['POST'])
def webhook():
    data = json.loads(request.data)

    passphrase = data['passphrase']
    if( config.WEBHOOK_PASSPHRASE != passphrase):
        return {
            "code": "error",
            "message": "invalid credentials"
        }

    print(data['ticker'])
    print(data['bar'])

    side = data['strategy']['order_action'].upper()
    quantity = data['strategy']['order_contracts']
    order_response = order(side=side, quantity=quantity, symbol="ETHUSDT")

    if order_response:
        return {
            "code": "success",
            "message": "order executed"
        }
    else:
        print("order failed")
        return {
            "code": "error",
            "message": "order failed"
        }
