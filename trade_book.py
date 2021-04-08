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
    print("\n")
    total_profit = 0
    trade_profit = 0
    trades = []
    trade_num = 1
    trade_i = 0

    query = Trades.query.all()
    for trade in query:

        print(trade.amount)
        print(trade.price)
        
        if(trade.trade_type == 'BUY'):
            trade_profit -= Decimal(trade.total_usdt)
            #trade_profit -= Decimal(line['Price']) * Decimal(line['Amount'])
            print(trade_profit)
            trade_i += 1
        if(trade.trade_type == 'SELL'):
            trade_profit += Decimal(trade.total_usdt)
            #trade_profit += Decimal(line['Price']) * Decimal(line['Amount'])
            trade_i += 1
        
        if(trade_i == 2):
            trade_i = 0
            trades.append(trade_profit)
            text += '\nTrade #{}: {}'.format(trade_num, trade_profit)
            print('Trade #{}: {}'.format(trade_num, trade_profit))
            total_profit += trade_profit
            trade_profit = 0
            trade_num += 1

    #print('Avg Trade: {}'.format(np.average(trades)))
    text += '\nTotal Profit: {}\n'.format(total_profit)
    print('Total Profit: {}\n'.format(total_profit))

    return text
