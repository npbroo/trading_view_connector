import csv
from decimal import Decimal
from models import Trade_Table, Strat_Assets
from app import db

def export_all_csv():
    with open('trade_history.csv','w',newline="") as File:
        writer = csv.writer(File)
        writer.writerow(['Strategy', 'Tradingview Time', 'Real Time', 'Symbol', 'Amount', 'Trade Type', 'TradingView Price', 'Price', 'Total USDT'])
        query = Trade_Table.query.order_by(Trade_Table.real_time).all()
        for trade in query:
            writer.writerow([trade.strat_id, trade.tradingview_time, trade.real_time, trade.symbol, trade.amount, trade.trade_type, trade.tradingview_price, trade.price, trade.total_usdt])

def export_csv(strat_id):
    with open('trade_history.csv','w',newline="") as File:
        writer = csv.writer(File)
        writer.writerow(['Tradingview Time', 'Real Time', 'Symbol', 'Amount', 'Trade Type', 'TradingView Price', 'Price', 'Total USDT'])
        query = Trade_Table.query.filter_by(strat_id=strat_id).order_by(Trade_Table.real_time).all()
        for trade in query:
            writer.writerow([trade.tradingview_time, trade.real_time, trade.symbol, trade.amount, trade.trade_type, trade.tradingview_price, trade.price, trade.total_usdt])


starting_capital = 100
trade_percent = .95
fee = .001
def calculate_profit(strat_id):

    text = "\n"
    total_profit = 0
    
    trade_num = 1
    trade_i = 0

    query = Trade_Table.query.filter_by(strat_id=strat_id).order_by(Trade_Table.real_time).all()
    symbol = query[0].symbol
    text += f"TRANSACTION HISTORY ({strat_id}) ({symbol})"

    amt_passed_usdt = starting_capital * trade_percent
    usdt=starting_capital - amt_passed_usdt
    amt_passed_crypto = amt_passed_usdt/query[0].price
    crypto=amt_passed_crypto

    last_trade_type = 'BUY'
    total_usdt = (crypto*query[0].price)+usdt


    for trade in query:

        
        if(trade_i == 0):
            text += '\n\nTrade #{}:'.format(trade_num)
            if(trade_num == 1):
                if(trade.trade_type == 'BUY'):
                    text += '\n\tBUY @ {} | PRICE: {}'.format(trade.real_time.strftime('%x - %X'), str(trade.price))
                    #text += f'\n\tUSDT{usdt}   amt_passed{amt_passed_usdt}    amt_passed_crypto{amt_passed_crypto}    crypto{crypto}'
                else:
                    text+= f"\n\tERROR, trade doesn't open with a buy [ID:{trade.id}]"
                    break
                trade_i += 1
                continue

        if(last_trade_type == trade.trade_type):
            text+= f"\n\tERROR, repeat order type [ID:{trade.id}]"
            break

        real_time = trade.real_time
        
        if(trade.trade_type == 'BUY'):
            amt_passed_usdt = (usdt*trade_percent) - (usdt*trade_percent*fee)
            usdt = usdt - amt_passed_usdt
            amt_passed_crypto = amt_passed_usdt/trade.price
            crypto = crypto + amt_passed_crypto

            last_trade_type = 'BUY'
            text += '\n\tBUY @ {} | PRICE: {}'.format(real_time.strftime('%x - %X'), str(trade.price))
            #text += f'\n\tUSDT{usdt}   amt_passed{amt_passed_usdt}    amt_passed_crypto{amt_passed_crypto}    crypto{crypto}'
            trade_i += 1
        elif(trade.trade_type == 'SELL'):
            amt_passed_crypto = (crypto * trade_percent) - (crypto * trade_percent * fee)
            crypto = crypto-amt_passed_crypto
            amt_passed_usdt = amt_passed_crypto*trade.price
            usdt = usdt+amt_passed_usdt

            last_trade_type = 'SELL'
            text += '\n\tSELL@ {} | PRICE: {}'.format(real_time.strftime('%x - %X'), str(trade.price))
            #text += f'\n\tUSDT{usdt}   amt_passed{amt_passed_usdt}    amt_passed_crypto{amt_passed_crypto}    crypto{crypto}'
            trade_i += 1
        
        if(trade_i == 2):
            if(trade.trade_type == 'BUY'):
                text+= f"\n\tERROR, unparallel order types [ID:{trade.id}]"
                break

            trade_i = 0

            new_total_usdt = (crypto*trade.price)+usdt
            trade_profit = new_total_usdt - total_usdt
            total_usdt = new_total_usdt

            text += '\n\tTRADE PROFIT: {}'.format(trade_profit)
            text += '\n\tTOTAL ASSET: ${}'.format(total_usdt)
            total_profit += trade_profit
            trade_num += 1

    #text+=f'total usdt: {usdt} | total crypto: {crypto} | total asset: {(crypto*trade.price)+usdt}'

    # update the strategy assets to reflect the transaction
    Strat_Assets.query.filter_by(strat_id=strat_id).first().usdt = usdt
    Strat_Assets.query.filter_by(strat_id=strat_id).first().crypto = crypto
    Strat_Assets.query.filter_by(strat_id=strat_id).first().total_asset_in_usdt = (crypto*trade.price)+usdt
    db.session.commit()

    text += '\n\nSTARTING ASSET: ${}'.format(float(starting_capital))
    text += '\nENDING ASSET: ${}'.format(float(starting_capital) + float(total_profit))
    text += '\nTOTAL PROFIT: ${}'.format(float(total_profit))
    return text
