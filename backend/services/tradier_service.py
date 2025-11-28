import requests
import os
from dotenv import load_dotenv

load_dotenv()

TRADIER_TOKEN = os.getenv("TRADIER_API_KEY")
HEADERS = {
    "Authorization": f"Bearer {TRADIER_TOKEN}",
    "Accept": "application/json"
}

def get_spot_price(symbol: str) -> float:
    url = "https://api.tradier.com/v1/markets/quotes"
    resp = requests.get(url, headers=HEADERS, params={"symbols": symbol})
    resp.raise_for_status()
    data = resp.json()

    quote = data.get("quotes", {}).get("quote")
    if not quote:
        raise ValueError("No quote data returned")

    if isinstance(quote, list):
        quote = quote[0]

    last = quote.get("last")
    if last is not None:
        return float(last)
    
    raise ValueError("Could not determine price")

def get_quote(symbol: str):
    url = "https://api.tradier.com/v1/markets/quotes"
    resp = requests.get(url, headers=HEADERS, params={"symbols": symbol})
    resp.raise_for_status()
    data = resp.json()
    quote = data.get("quotes", {}).get("quote")
    if isinstance(quote, list):
        return quote[0]
    return quote

def fetch_option_chain(symbol: str, expiration: str):
    url = "https://api.tradier.com/v1/markets/options/chains"
    params = {"symbol": symbol, "expiration": expiration, "greeks": "true"}
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    data = resp.json()
    
    options = data.get("options")
    if not options:
        return []
        
    option_list = options.get("option")
    if not option_list:
        return []
        
    return option_list

def get_historical_candles(symbol: str, interval: str = "1min", start_date: str = None):
    url = "https://api.tradier.com/v1/markets/candles"
    params = {
        "symbol": symbol, 
        "interval": interval,
        "session_filter": "all"
    }
    if start_date:
        params["start"] = start_date
        
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    data = resp.json()
    
    # Tradier structure: {'history': {'day': [...]}} or {'candles': ...} depending on endpoint
    # markets/candles returns {'candles': {'candle': [...]}}
    
    candles = data.get("candles", {}).get("candle", [])
    if not candles:
        return []
    if isinstance(candles, dict): # Single candle case
        return [candles]
        
    return candles
