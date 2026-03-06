import hmac
import hashlib
import base64
import time
import json
import requests
from config import API_KEY, API_SECRET, API_PASSPHRASE, BASE_URL


class BlofinClient:
    def __init__(self):
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.passphrase = API_PASSPHRASE
        self.base_url = BASE_URL
        self.session = requests.Session()

    def _sign(self, timestamp: str, method: str, path: str, body: str = "") -> str:
        message = f"{timestamp}{method.upper()}{path}{body}"
        mac = hmac.new(
            self.api_secret.encode("utf-8"),
            message.encode("utf-8"),
            digestmod=hashlib.sha256,
        )
        return base64.b64encode(mac.digest()).decode()

    def _headers(self, method: str, path: str, body: str = "") -> dict:
        timestamp = str(int(time.time() * 1000))
        sign = self._sign(timestamp, method, path, body)
        return {
            "ACCESS-KEY": self.api_key,
            "ACCESS-SIGN": sign,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json",
        }

    def get(self, path: str, params: dict = None) -> dict:
        query = ""
        if params:
            query = "?" + "&".join(f"{k}={v}" for k, v in params.items())
        headers = self._headers("GET", path + query)
        resp = self.session.get(self.base_url + path + query, headers=headers)
        resp.raise_for_status()
        return resp.json()

    def post(self, path: str, payload: dict) -> dict:
        body = json.dumps(payload)
        headers = self._headers("POST", path, body)
        resp = self.session.post(self.base_url + path, headers=headers, data=body)
        resp.raise_for_status()
        return resp.json()

    def get_ticker(self, symbol: str) -> float:
        data = self.get("/api/v1/market/tickers", {"instId": symbol})
        return float(data["data"][0]["last"])

    def get_balance(self) -> float:
        data = self.get("/api/v1/asset/balances")
        for asset in data.get("data", []):
            if asset["currency"] == "USDT":
                return float(asset["available"])
        return 0.0

    def place_order(self, symbol: str, side: str, price: float, size: float) -> dict:
        payload = {
            "instId": symbol,
            "marginMode": "cross",
            "positionSide": "net",
            "side": side,
            "orderType": "limit",
            "price": str(round(price, 1)),
            "size": str(round(size, 4)),
        }
        return self.post("/api/v1/trade/order", payload)

    def cancel_all_orders(self, symbol: str) -> dict:
        return self.post("/api/v1/trade/cancel-batch-orders", [{"instId": symbol}])

    def get_open_orders(self, symbol: str) -> list:
        data = self.get("/api/v1/trade/orders-pending", {"instId": symbol})
        return data.get("data", [])

    def set_leverage(self, symbol: str, leverage: int) -> dict:
        return self.post("/api/v1/account/set-leverage", {
            "instId": symbol,
            "leverage": str(leverage),
            "marginMode": "cross",
        })
