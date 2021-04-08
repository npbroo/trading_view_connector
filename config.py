import os
from dotenv import load_dotenv
load_dotenv()

WEBHOOK_PASSPHRASE = os.getenv('WEBHOOK_PASSPHRASE')
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

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