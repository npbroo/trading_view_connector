import os
from dotenv import load_dotenv
load_dotenv()

WEBHOOK_PASSPHRASE = os.getenv('WEBHOOK_PASSPHRASE')
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

# API CONNECTION (rest server requests)
API_BASE = 'https://api.binance.com'