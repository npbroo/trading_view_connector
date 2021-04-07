# save this as app.py
import json, config, trade_book, api_requests
from datetime import datetime
from flask import Flask, escape, request, render_template, send_file
from binance.client import Client
from binance.enums import *

app = Flask(__name__)

#set up the binance client
client = Client(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY, tld='us')

#set up the trade book for paper trading
trade_book.init_trade_book()

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

def paper_order(time, side, quantity, symbol, tradingview_price):
    book_ticker = api_requests.get_book_ticker(symbol)
    bid_price = book_ticker['bidPrice']
    ask_price = book_ticker['askPrice']
    actual_time = datetime.now().strftime("%H:%M:%S")
    if(side == 'BUY'):
        price = ask_price
    elif(side == 'SELL'):
        price = bid_price

    trade_book.write_trade(tradingview_date=time, date=actual_time, symbol=symbol, amount=str(quantity), trade_type=side, tradingview_price=str(tradingview_price), ticker_price=str(ask_price))

    return {
        "code": "success",
        "message": "executed paper trade",
        "details": {
            "tradingview_time": time,
            "actual_time": actual_time,
            "symbol": symbol,
            "quantity": quantity,
            "side": side,
            "price": price,
            "tradingview_price": tradingview_price,
        }
    }

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/reset')
def reset():
    trade_book.init_trade_book()
    return "success"

@app.route('/profits')
def profits():
    response = trade_book.calculate_profit()
    response = "<xmp>{}</xmp>".format(response)
    return response

@app.route('/return_csv')
def return_csv():
    return send_file('trade_history.csv', as_attachment=True, cache_timeout=0)

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
    symbol = data['ticker']
    time = data['time']
    tradingview_price = data['strategy']['order_price']
    #live trading    
    #order_response = order(time=time, side=side, quantity=quantity, symbol=symbol)

    #paper trading
    order_response = paper_order(time=time, side=side, quantity=quantity, symbol=symbol, tradingview_price=tradingview_price)

    if order_response:
        return order_response
        response = {
            "code": "success",
            "message": "order executed"
        }
    else:
        print("order failed")
        return {
            "code": "error",
            "message": "order failed"
        }
