import csv
from decimal import Decimal
from models import Trade_Table

def export_all_csv():
    with open('trade_history.csv','w',newline="") as File:
        writer = csv.writer(File)
        writer.writerow(['Strategy', 'Tradingview Time', 'Real Time', 'Symbol', 'Amount', 'Trade Type', 'TradingView Price', 'Price', 'Total USDT'])
        query = Trade_Table.query.all()
        for trade in query:
            writer.writerow([trade.strat_id, trade.tradingview_time, trade.real_time, trade.symbol, trade.amount, trade.trade_type, trade.tradingview_price, trade.price, trade.total_usdt])

def export_csv(strat_id):
    with open('trade_history.csv','w',newline="") as File:
        writer = csv.writer(File)
        writer.writerow(['Tradingview Time', 'Real Time', 'Symbol', 'Amount', 'Trade Type', 'TradingView Price', 'Price', 'Total USDT'])
        query = Trade_Table.query.filter_by(strat_id=strat_id).all()
        for trade in query:
            writer.writerow([trade.tradingview_time, trade.real_time, trade.symbol, trade.amount, trade.trade_type, trade.tradingview_price, trade.price, trade.total_usdt])

def calculate_profit(strat_id):
    
    text = "\n"
    total_profit = 0
    trade_profit = 0
    trades = []
    trade_num = 1
    trade_i = 0

    query = Trade_Table.query.filter_by(strat_id=strat_id).all()
    symbol = query[0].symbol
    starting_capital = 0
    text += f"TRANSACTION HISTORY ({strat_id}) ({symbol})"
    for trade in query:

        if(trade_i == 0):
            if(trade_num == 1):
                starting_capital = trade.total_usdt
            text += '\n\nTrade #{}:'.format(trade_num)

        print(trade.amount)
        print(trade.price)
        real_time = trade.real_time
        
        if(trade.trade_type == 'BUY'):
            trade_profit -= Decimal(trade.total_usdt)
            text += '\n\tBUY @ {} | PRICE: {}'.format(real_time.strftime('%x - %X'), str(trade.price))
            trade_i += 1
        if(trade.trade_type == 'SELL'):
            trade_profit += Decimal(trade.total_usdt)
            text += '\n\tSELL@ {} | PRICE: {}'.format(real_time.strftime('%x - %X'), str(trade.price))
            trade_i += 1
        if(trade_i == 2):
            trade_i = 0
            trades.append(trade_profit)
            text += '\n\tTRADE PROFIT: {}'.format(trade_profit)
            text += '\n\tTOTAL ASSET: ${}'.format(trade.total_usdt)
            total_profit += trade_profit
            trade_profit = 0
            trade_num += 1

    #print('Avg Trade: {}'.format(np.average(trades)))
    text += '\n\nSTARTING ASSET: ${}'.format(float(starting_capital))
    text += '\nENDING ASSET: ${}'.format(float(starting_capital) + float(total_profit))
    text += '\nTOTAL PROFIT: ${}'.format(float(total_profit))
    return text
