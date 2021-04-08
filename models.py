from app import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#create our database models

# Strategy Assets - holds the amount of assets for each strategy
class Strat_Assets(db.Model):
    __tablename__= "strat_assets"
    id = db.Column(db.Integer, primary_key=True)
    strat_id = db.Column(db.String(20)) # the custom id you give to the trading view webhook
    symbol = db.Column(db.String(20)) # the ticker being traded
    usdt = db.Column(db.Float) # the amount in usdt currently available
    crypto = db.Column(db.Float) # the amount in crypto currently available
    total_asset_in_usdt = db.Column(db.Float) # total usdt when adding crypto and usdt

    def __init__(self, strat_id, symbol, usdt, crypto, total_asset_in_usdt):
        self.strat_id = strat_id
        self.symbol = symbol
        self.usdt = usdt
        self.crypto = crypto
        self.total_asset_in_usdt = total_asset_in_usdt


# Trade Table - holds all the trades from all of the strategies
class Trade_Table(db.Model):
    __tablename__= "trade_table"
    id = db.Column(db.Integer, primary_key=True)
    strat_id = db.Column(db.String(20)) # the custom id you give to the trading view webhook
    symbol = db.Column(db.String(20))
    amount = db.Column(db.Float)
    trade_type = db.Column(db.String(20))
    tradingview_price = db.Column(db.Float)
    price = db.Column(db.Float)
    tradingview_time = db.Column(db.String(120))
    real_time = db.Column(db.DateTime, default=datetime.now())
    total_usdt = db.Column(db.Float)

    def __init__(self, strat_id, symbol, amount, trade_type, tradingview_price, price, tradingview_time, real_time, total_usdt):
        self.strat_id = strat_id
        self.tradingview_time = tradingview_time
        self.real_time = real_time
        self.symbol = symbol
        self.amount = amount
        self.trade_type = trade_type
        self.tradingview_price = tradingview_price
        self.price = price
        self.total_usdt = total_usdt