# save this as app.py
import json, config, api_requests, os.path
from os import path
from datetime import datetime
from flask import Flask, escape, request, render_template, send_file
from binance.client import Client
from binance.enums import *
from flask_sqlalchemy import SQLAlchemy

ENV = 'dev'
app = Flask(__name__)

# handle heroku postgres bug (SQLAlchemy depreciated postgres for postgresql)
database_url = config.DATABASE_URL
if database_url.find('postgresql') != -1:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    database_url.replace('postgres', 'postgresql', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url

#debug if the environment is development
if ENV == 'dev':
    app.debug = True
else:
    app.debug = False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#must import after db to prevent circular import
from models import Trades, Settings
import trade_book

#starting capital
STARTING_CAPITAL = 100 

#set up the binance client
client = Client(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY, tld='us')

# init settings database if it is empty
if(Settings.query.first() is None):
    settings = Settings(usdt=STARTING_CAPITAL, crypto=0, total_asset_in_usdt=STARTING_CAPITAL)
    db.session.add(settings)
    db.session.commit()

# sends a real binance order
def order(side, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        #set buy / sell quantity
        if(side == 'BUY'):
            balance = client.get_asset_balance(asset='USDT')
            quantity = float(balance['free'] * 0.95) #trade with 95% of balance
        elif(side == 'SELL'):
            balance = client.get_asset_balance(asset=symbol)
            quantity = float(balance['free'] * 0.95) #trade with 95% of balance
        else:
            quantity = 0

        print(f"sending order {order_type} - {side} {quantity} {symbol}")
        #order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity, time=time)
        order = client.create_test_order(symbol="ETHUSDT", side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return order

# buys and sells a paper order with 95% of account
def paper_order(time, side, symbol, tradingview_price):

    #get bid/ask price
    book_ticker = api_requests.get_book_ticker(symbol)
    bid_price = book_ticker['bidPrice']
    ask_price = book_ticker['askPrice']
    actual_time = datetime.now().strftime("%H:%M:%S")
    if(side == 'BUY'):
        price = ask_price
    elif(side == 'SELL'):
        price = bid_price

    #set buy / sell quantity
    usdt = Settings.query.first().usdt
    crypto = Settings.query.first().crypto

    if(side == 'BUY'):
        balance = usdt
        quantity = balance * 0.95 #trade with 95% of balance
        usdt = balance - quantity
        quantity = quantity / float(ask_price)
        crypto = crypto + float(quantity)
        print(f"usdt:{usdt}")
        print(f"crypto:{crypto}; in usdt:{crypto * float(ask_price)}")
        
        total_usdt = usdt + crypto * float(ask_price)
        print(f"total usdt: {total_usdt}")

    elif(side == 'SELL'):
        balance = crypto
        quantity = balance * 0.95 #trade with 95% of balance
        crypto = balance - quantity
        usdt = usdt + float(quantity) * float(bid_price)
        print(f"usdt:{usdt}")
        print(f"crypto:{crypto}; in usdt:{crypto * float(bid_price)}")

        total_usdt = usdt + crypto * float(bid_price)
        print(f"total usdt: {total_usdt}")
    else:
        quantity = 0

    Settings.query.first().usdt = usdt
    Settings.query.first().crypto = crypto
    Settings.query.first().total_asset_in_usdt = total_usdt

    # add trade to database
    trade = Trades(tradingview_time=time, real_time=actual_time, symbol=symbol, amount=str(quantity), trade_type=side, tradingview_price=str(tradingview_price), price=str(ask_price), total_usdt=str(total_usdt))
    db.session.add(trade)
    db.session.commit()

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
    total_usdt = Settings.query.first().total_asset_in_usdt
    return render_template('index.html', total_usdt = total_usdt)

@app.route('/reset')
def reset():
    Trades.query.delete()
    Settings.query.delete()
    settings = Settings(usdt=STARTING_CAPITAL, crypto=0, total_asset_in_usdt=STARTING_CAPITAL)
    db.session.add(settings)
    db.session.commit()
    return "success"

@app.route('/profits')
def profits():
    response = trade_book.calculate_profit()
    response = "<xmp>{}</xmp>".format(response)
    return response

@app.route('/return_csv')
def return_csv():
    trade_book.export_csv()
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
    '''
    LIVE TRADING:   
    '''
    #order_response = order(time=time, side=side, symbol=symbol)

    '''
    PAPER TRADING:
    '''
    order_response = paper_order(time=time, side=side, symbol=symbol, tradingview_price=tradingview_price)

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
