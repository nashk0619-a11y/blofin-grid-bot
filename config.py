import os
from dotenv import load_dotenv

load_dotenv()

MODE = os.getenv("BLOFIN_MODE", "demo")

if MODE == "live":
    API_KEY = os.getenv("BLOFIN_API_KEY")
    API_SECRET = os.getenv("BLOFIN_API_SECRET")
    API_PASSPHRASE = os.getenv("BLOFIN_API_PASSPHRASE")
    BASE_URL = "https://openapi.blofin.com"
else:
    API_KEY = os.getenv("BLOFIN_DEMO_API_KEY")
    API_SECRET = os.getenv("BLOFIN_DEMO_API_SECRET")
    API_PASSPHRASE = os.getenv("BLOFIN_DEMO_API_PASSPHRASE")
    BASE_URL = "https://demo-trading-openapi.blofin.com"

SYMBOL = os.getenv("SYMBOL", "BTC-USDT")
TOTAL_CAPITAL = float(os.getenv("TOTAL_CAPITAL", 800))
LEVERAGE = int(os.getenv("LEVERAGE", 3))
GRID_LEVELS = int(os.getenv("GRID_LEVELS", 25))
GRID_RANGE_PCT = float(os.getenv("GRID_RANGE_PCT", 15))
STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", 20))
MAKER_FEE = 0.0002
TAKER_FEE = 0.0006
