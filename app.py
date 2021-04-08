# save this as app.py
import json, config, trade_book, api_requests, os.path
from os import path
from datetime import datetime
from flask import Flask, escape, request, render_template, send_file
from binance.client import Client
from binance.enums import *
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABSE_URI'] = config.SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

#starting capital
STARTING_CAPITAL = 100 

#set up the binance client
client = Client(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY, tld='us')

#init the tradebook if it doesnt exist
if(not path.exists('trade_history.csv')):
    trade_book.init_trade_book()

#init settings if it doenst exist
if(not path.exists('settings.csv')):
    config.update_settings(0, STARTING_CAPITAL)


#create our database models
class Trades(db.Model):
    __tablename__= "trades"
    id = db.Column(db.Integer, primary_key=True)
    tradingview_time = db.Column(db.String(120))
    real_time = db.Column(db.String(120))
    symbol = db.Column(db.String(20))
    amount = db.Column(db.Float)
    trade_type = db.Column(db.String(20))
    tradingview_price = db.Column(db.Float)
    price = db.Column(db.Float)
    total_usdt = db.Column(db.Float)

    def __init__(self, tradingview_time, real_time, symbol, amount, trade_type, tradingview_price, price, total_usdt):
        self.tradingview_time = tradingview_time
        self.real_time = real_time
        self.symbol = symbol
        self.amount = amount
        self.trade_type = trade_type
        self.tradingview_price = tradingview_price
        self.price = price
        self.total_usdt = total_usdt

class Settings(db.Model):
    __tablename__= "settings"
    id = db.Column(db.Integer, primary_key=True)
    usdt = db.Column(db.Float)
    crypto = db.Column(db.Float)



#set up the trade book for paper trading
#trade_book.init_trade_book()

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

# buys and sells with 95% of account
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
    usdt = config.get_usdt()
    crypto = config.get_crypto()

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

    config.update_settings(crypto, usdt)
    trade_book.write_trade(tradingview_date=time, date=actual_time, symbol=symbol, amount=str(quantity), trade_type=side, tradingview_price=str(tradingview_price), ticker_price=str(ask_price), total_usdt=str(total_usdt))


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
    global STARTING_CAPITAL
    usdt = STARTING_CAPITAL
    crypto = 0
    config.update_settings(crypto, usdt)
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
    #order_response = order(time=time, side=side, symbol=symbol)

    #paper trading
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
