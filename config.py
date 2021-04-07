WEBHOOK_PASSPHRASE = 'abcdefgh'
BINANCE_API_KEY = 'XUn3FtmKQ4o794YNb1ketTD1XlQl8onZa6MnyQlTxZTwycOCiBzLBp8bZ2DsJopn'
BINANCE_SECRET_KEY = 'WYCZG6E38wPHavKofr982IInnzmJoOueOJIMFx9YlnG8QBzXmy8pSA6gI8adMuN0'

# API CONNECTION (rest server requests)
API_BASE = 'https://api.binance.com'


import csv
def update_settings(crypto, usdt):
    with open('settings.csv','w',newline="") as File:
        writer = csv.writer(File)
        writer.writerow(['crypto', 'usdt'])
        writer.writerow([crypto, usdt])

def get_crypto():
    with open('settings.csv', mode ='r') as File:
        settings = csv.DictReader(File)
        return float(list(settings)[0]['crypto'])

def get_usdt():
    with open('settings.csv', mode ='r') as File:
        settings = csv.DictReader(File)
        return float(list(settings)[0]['usdt'])