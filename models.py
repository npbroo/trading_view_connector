from app import db
from flask_sqlalchemy import SQLAlchemy

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
    total_asset_in_usdt = db.Column(db.Float)

    def __init__(self, usdt, crypto, total_asset_in_usdt):
        self.usdt = usdt
        self.crypto = crypto
        self.total_asset_in_usdt = total_asset_in_usdt