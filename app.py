# save this as app.py
import json, config, api_requests, os.path, random
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
    database_url = database_url.replace('postgres', 'postgresql', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url

#debug if the environment is development
if ENV == 'dev':
    app.debug = True
else:
    app.debug = False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#must import after db to prevent circular import
#from models import Trades, Settings, Strat_Assets, Trade_Table
from models import Strat_Assets, Trade_Table
import trade_book

#starting capital
STARTING_CAPITAL = 100 
TRADE_PERCENT = 0.95
FEE = 0.01

#set up the binance client
client = Client(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY, tld='us')

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

# Webhook for buying and selling multiple different strategies and storage in the same database
def paper_order(strat_id, side, symbol, tradingview_price, tradingview_time):
    #get bid/ask price
    book_ticker = api_requests.get_book_ticker(symbol)
    bid_price = book_ticker['bidPrice']
    ask_price = book_ticker['askPrice']
    #actual_time = datetime.now().strftime("%x - %X")
    if(side == 'BUY'):
        price = ask_price
    elif(side == 'SELL'):
        price = bid_price

    #check if database entry exists for this strat (if not create a new entry)
    if(Strat_Assets.query.filter_by(strat_id=strat_id).first() is None):
        #dont execute order if the first order is a sell order
        if(side == 'SELL'):
            return
        strat_asset = Strat_Assets(strat_id=strat_id, symbol=symbol, usdt=STARTING_CAPITAL, crypto=0, total_asset_in_usdt=STARTING_CAPITAL)
        db.session.add(strat_asset)
        db.session.commit()


    #check if it's a duplicate order type
    query = Trade_Table.query.filter_by(strat_id=strat_id).order_by(Trade_Table.real_time.desc()).first()
    if( not query is None):
        if(side == query.trade_type):
            return

    #get the amount of usdt and crypto for the strategies assets
    usdt = Strat_Assets.query.filter_by(strat_id=strat_id).first().usdt
    crypto = Strat_Assets.query.filter_by(strat_id=strat_id).first().crypto
    quantity = 0

    if(side == 'BUY'):
        quantity = usdt * TRADE_PERCENT #trade with 95% of balance

        amt_passed_usdt = (usdt*TRADE_PERCENT) - (usdt*TRADE_PERCENT*FEE)
        usdt = usdt - amt_passed_usdt
        amt_passed_crypto = amt_passed_usdt/float(ask_price)
        crypto = crypto + amt_passed_crypto

        print(f"usdt:{usdt}")
        print(f"crypto:{crypto}; in usdt:{crypto * float(ask_price)}")

        #calculate the total assets in usdt
        total_usdt = usdt + crypto * float(ask_price)
        print(f"total usdt: {total_usdt}")

    elif(side == 'SELL'):
        quantity = crypto * TRADE_PERCENT #trade with 95% of balance

        amt_passed_crypto = (crypto * TRADE_PERCENT) - (crypto * TRADE_PERCENT * FEE)
        crypto = crypto - amt_passed_crypto
        amt_passed_usdt = amt_passed_crypto * float(bid_price)
        usdt = usdt + amt_passed_usdt

        print(f"usdt:{usdt}")
        print(f"crypto:{crypto}; in usdt:{crypto * float(bid_price)}")

        #calculate the total assets in usdt
        total_usdt = usdt + crypto * float(bid_price)
        print(f"total usdt: {total_usdt}")

    # update the strategy assets to reflect the transaction
    Strat_Assets.query.filter_by(strat_id=strat_id).first().usdt = usdt
    Strat_Assets.query.filter_by(strat_id=strat_id).first().crypto = crypto
    Strat_Assets.query.filter_by(strat_id=strat_id).first().total_asset_in_usdt = total_usdt

    # add trade to database
    real_time = datetime.now()
    trade = Trade_Table(strat_id=strat_id, symbol=symbol, amount=str(quantity), trade_type=side, tradingview_price=str(tradingview_price), price=str(ask_price), tradingview_time=tradingview_time, real_time=real_time, total_usdt=str(total_usdt))
    db.session.add(trade)
    db.session.commit()

    #return success
    return {
        "code": "success",
        "message": "executed paper trade",
        "details": {
            "tradingview_time": tradingview_time,
            "actual_time": real_time,
            "symbol": symbol,
            "quantity": quantity,
            "side": side,
            "price": price,
            "tradingview_price": tradingview_price,
        }
    }

# The homepage
@app.route('/')
def home():
    query = Strat_Assets.query.order_by(Strat_Assets.total_asset_in_usdt.desc()).all()
    strats = {}
    for strat in query:
        strats[strat.strat_id] =  strat.total_asset_in_usdt
    rand = random.randint(1, 3)
    return render_template('index.html', random=rand, strats=strats)

# Reset all strategies or just some strategies
@app.route('/reset/<strat_id>')
def reset(strat_id):
    if(strat_id == 'ALL'):
        print('Deleting ALL table entries')
        Trade_Table.query.delete()
        Strat_Assets.query.delete()
    else:
        print(f'Deleting all table entries for {strat_id}')
        Trade_Table.query.filter_by(strat_id=strat_id).delete()
        Strat_Assets.query.filter_by(strat_id=strat_id).delete()
    db.session.commit()
    return "SUCCESS"

# Print profit report to the screen
@app.route('/profits')
@app.route('/profits/<strat_id>')
def profits(strat_id='all'):
    if(strat_id == 'all'):
        return "Pass the strategy you would like to view as a parameter."
    else:
        response = trade_book.calculate_profit(strat_id)
        response = "<xmp>{}</xmp>".format(response)
        return response

# Export a csv containing all trades or pass the parameter for a certain strategy
@app.route('/export')
@app.route('/export/<strat_id>')
def export(strat_id='all'):
    if(strat_id == 'all'):
        trade_book.export_all_csv()
    else:
        trade_book.export_csv(strat_id)
    return send_file('trade_history.csv', as_attachment=True, cache_timeout=0)

# Route for tradingview webhooks
@app.route('/webhook', methods=['POST'])
def webhook():
    data = json.loads(request.data)

    if( not 'passphrase' in data or config.WEBHOOK_PASSPHRASE != data['passphrase']):
        return {
            "code": "error",
            "message": "invalid credentials"
        }

    if not 'strat_id' in data:
        print("strat_id invalid")
        return {
            "code": "error",
            "message": "strat_id invalid"
        }
    
    strat_id = data['strat_id']
    side = data['strategy']['order_action'].upper()
    quantity = data['strategy']['order_contracts']
    symbol = data['ticker']
    tradingview_time = data['time']
    tradingview_price = data['strategy']['order_price']

    #PAPER TRADING
    order_response = paper_order(strat_id=strat_id, side=side, symbol=symbol, tradingview_price=tradingview_price, tradingview_time=tradingview_time)

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
