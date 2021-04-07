import csv
from decimal import Decimal

def init_trade_book():
    with open('trade_history.csv','w',newline="") as File:
        writer = csv.writer(File)
        writer.writerow(['Tradingview Time', 'Real Time', 'Symbol', 'Amount', 'Trade Type', 'TradingView Price', 'Price', 'Total USDT'])

def write_trade(tradingview_date, date, symbol, amount, trade_type, tradingview_price, ticker_price, total_usdt):
    with open('trade_history.csv','a',newline="") as File:
        writer = csv.writer(File)
        writer.writerow([tradingview_date, date, symbol, amount, trade_type, tradingview_price, ticker_price, total_usdt])

def calculate_profit():
    with open('trade_history.csv', mode ='r') as File:
        text = "\n"
        print("\n")
        reader = csv.DictReader(File)
        total_profit = 0
        trade_profit = 0
        trades = []
        trade_num = 1
        trade_i = 0
        for line in reader:

            print(line['Amount'])
            print(line['Price'])
            
            if(line['Trade Type'] == 'BUY'):
                trade_profit -= Decimal(line['Total USDT'])
                #trade_profit -= Decimal(line['Price']) * Decimal(line['Amount'])
                print(trade_profit)
                trade_i += 1
            if(line['Trade Type'] == 'SELL'):
                trade_profit += Decimal(line['Total USDT'])
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
                
            '''
            if(line['Trade Type'] == 'BUY'):
                trade_profit -= Decimal(line['Price'])
            if(line['Trade Type'] == 'SELL'):
                trade_profit += Decimal(line['Price'])
                trades.append(trade_profit)
                print('Trade #{}: {}'.format(trade_num, trade_profit))
                total_profit += trade_profit
                trade_profit = 0
                trade_num += 1
            '''

        #print('Avg Trade: {}'.format(np.average(trades)))
        text += '\nTotal Profit: {}\n'.format(total_profit)
        print('Total Profit: {}\n'.format(total_profit))

        return text

def return_book():
    with open('trade_history.csv', mode ='r') as File:
        book = csv.DictReader(File)
        return list(book)
