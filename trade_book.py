import csv
from decimal import Decimal
from models import Trades

def export_csv():
    with open('trade_history.csv','w',newline="") as File:
        writer = csv.writer(File)
        writer.writerow(['Tradingview Time', 'Real Time', 'Symbol', 'Amount', 'Trade Type', 'TradingView Price', 'Price', 'Total USDT'])
        query = Trades.query.all()
        print(query)
        for trade in query:
            writer.writerow([trade.tradingview_time, trade.real_time, trade.symbol, trade.amount, trade.trade_type, trade.tradingview_price, trade.price, trade.total_usdt])

def calculate_profit():
    
    text = "\n"
    total_profit = 0
    trade_profit = 0
    trades = []
    trade_num = 1
    trade_i = 0

    query = Trades.query.all()
    starting_capital = 0
    text += "TRANSACTION HISTORY"
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
            text += '\n\tBUY @ {} | PRICE: {}'.format(real_time, str(trade.price))
            trade_i += 1
        if(trade.trade_type == 'SELL'):
            trade_profit += Decimal(trade.total_usdt)
            text += '\n\tSELL@ {} | PRICE: {}'.format(real_time, str(trade.price))
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
