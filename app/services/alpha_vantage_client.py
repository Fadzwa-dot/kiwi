import os
import requests
from flask import current_app
from pydantic import BaseModel
from typing import Optional

class SecurityQuote(BaseModel):
    ticker: str
    date: str
    price: float
    issuer: str

class AlphaVantageClient:
    BASE_URL = "https://www.alphavantage.co/query"

    @staticmethod
    def _get_api_key() -> str:
        return current_app.config.get("ALPHA_VANTAGE_API_KEY") or os.environ.get("ALPHA_VANTAGE_API_KEY")

    @staticmethod
    def get_company_name(ticker: str) -> Optional[str]:
        cache = current_app.cache
        cache_key = f"company_name:{ticker}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        api_key = AlphaVantageClient._get_api_key()
        params = {
            "function": "OVERVIEW",
            "symbol": ticker,
            "apikey": api_key
        }
        resp = requests.get(AlphaVantageClient.BASE_URL, params=params)
        if resp.status_code == 200:
            data = resp.json()
            name = data.get("Name")
            if name:
                cache.set(cache_key, name)
            return name
        return None

    @staticmethod
    def get_price_data(ticker: str) -> Optional[dict]:
        cache = current_app.cache
        cache_key = f"price_data:{ticker}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        api_key = AlphaVantageClient._get_api_key()
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker,
            "apikey": api_key
        }
        resp = requests.get(AlphaVantageClient.BASE_URL, params=params)
        if resp.status_code == 200:
            data = resp.json()
            time_series = data.get("Time Series (Daily)")
            if time_series:
                latest_date = sorted(time_series.keys())[-1]
                latest_data = time_series[latest_date]
                result = {
                    "date": latest_date,
                    "open": float(latest_data["1. open"]),
                    "high": float(latest_data["2. high"]),
                    "low": float(latest_data["3. low"]),
                    "close": float(latest_data["4. close"]),
                    "volume": int(latest_data["5. volume"])
                }
                cache.set(cache_key, result)
                return result
        return None

    @staticmethod
    def get_quote(ticker: str) -> Optional[SecurityQuote]:
        issuer = AlphaVantageClient.get_company_name(ticker)
        price_data = AlphaVantageClient.get_price_data(ticker)
        if issuer and price_data:
            return SecurityQuote(
                ticker=ticker,
                date=price_data["date"],
                price=price_data["close"],
                issuer=issuer
            )
        return None
