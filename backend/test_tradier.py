import requests
import os
from dotenv import load_dotenv

load_dotenv()

TRADIER_TOKEN = os.getenv("TRADIER_API_KEY")
HEADERS = {
    "Authorization": f"Bearer {TRADIER_TOKEN}",
    "Accept": "application/json"
}

def test_candles(symbol, interval):
    url = "https://api.tradier.com/v1/markets/candles"
    params = {
        "symbol": symbol,
        "interval": interval,
        "session_filter": "all"
    }
    print(f"Testing {symbol} {interval}...")
    try:
        resp = requests.get(url, headers=HEADERS, params=params)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            candles = data.get("candles", {}).get("candle", [])
            print(f"Got {len(candles)} candles")
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print("-" * 20)

def test_quotes(symbol):
    url = "https://api.tradier.com/v1/markets/quotes"
    params = {"symbols": symbol}
    print(f"Testing Quotes {symbol}...")
    try:
        resp = requests.get(url, headers=HEADERS, params=params)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Quote: {resp.json()}")
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print("-" * 20)

def test_sandbox(symbol):
    url = "https://sandbox.tradier.com/v1/markets/quotes"
    params = {"symbols": symbol}
    print(f"Testing Sandbox Quotes {symbol}...")
    try:
        resp = requests.get(url, headers=HEADERS, params=params)
        print(f"Status: {resp.status_code}")
    except Exception as e:
        print(f"Exception: {e}")
    print("-" * 20)

def test_history(symbol, interval):
    url = "https://api.tradier.com/v1/markets/history"
    params = {
        "symbol": symbol,
        "interval": interval,
    }
    print(f"Testing History {symbol} {interval}...")
    try:
        resp = requests.get(url, headers=HEADERS, params=params)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            history = data.get("history", {}).get("day", [])
            print(f"Got {len(history)} candles")
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print("-" * 20)

def test_candles_plural(symbol, interval):
    url = "https://api.tradier.com/v1/markets/candles"
    params = {
        "symbols": symbol, # Try plural
        "interval": interval,
        "session_filter": "all"
    }
    print(f"Testing Candles Plural {symbol} {interval}...")
    try:
        resp = requests.get(url, headers=HEADERS, params=params)
        print(f"Status: {resp.status_code}")
    except Exception as e:
        print(f"Exception: {e}")
    print("-" * 20)

def test_history_daily(symbol):
    url = "https://api.tradier.com/v1/markets/history"
    params = {
        "symbol": symbol,
        "interval": "daily",
    }
    print(f"Testing History Daily {symbol}...")
    try:
        resp = requests.get(url, headers=HEADERS, params=params)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            history = data.get("history", {}).get("day", [])
            print(f"Got {len(history)} daily candles")
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print("-" * 20)

def test_timesales(symbol):
    url = "https://api.tradier.com/v1/markets/timesales"
    params = {
        "symbol": symbol,
        "interval": "5min", # timesales usually takes interval? No, it takes start/end.
        # But let's try basic params
    }
    print(f"Testing Timesales {symbol}...")
    try:
        resp = requests.get(url, headers=HEADERS, params=params)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            series = data.get("series", {}).get("data", [])
            print(f"Got {len(series)} timesales records")
            if series:
                for i in range(min(3, len(series))):
                    print(f"Record {i}: {series[i]}")
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")
    print("-" * 20)

if __name__ == "__main__":
    test_history_daily("SPY")
    test_timesales("SPY")
    test_candles("SPY", "15min")
