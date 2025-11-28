from apscheduler.schedulers.background import BackgroundScheduler
from .tradier_service import get_spot_price, fetch_option_chain, get_historical_candles, get_quote
from .gemini_service import analyze_market
import datetime

latest_analysis = {
    "timestamp": None,
    "text": "Waiting for initial analysis...",
    "data": {}
}

def job_analyze_market():
    global latest_analysis
    print(f"[{datetime.datetime.now()}] Running scheduled analysis...")
    try:
        symbol = "SPX" # Default to SPX for 0DTE
        # Logic to determine expiration (today)
        today = datetime.date.today().strftime("%Y-%m-%d")
        
        spot = get_spot_price(symbol)
        chain = fetch_option_chain(symbol, today)
        
        # Basic aggregation for the prompt
        call_vol = sum(opt['volume'] for opt in chain if opt['option_type'] == 'call')
        put_vol = sum(opt['volume'] for opt in chain if opt['option_type'] == 'put')
        
        # Top OI
        sorted_oi = sorted(chain, key=lambda x: x['open_interest'], reverse=True)[:5]
        top_oi_strikes = [f"{opt['strike']} ({opt['option_type']})" for opt in sorted_oi]

        # Fetch VIX Data
        vix_current = "N/A"
        vix_trend = "N/A"
        try:
            vix_quote = get_quote("VIX")
            if vix_quote:
                vix_current = vix_quote.get("last")
                change = vix_quote.get("change", 0)
                if change > 0:
                    vix_trend = f"Up {change}"
                elif change < 0:
                    vix_trend = f"Down {change}"
                else:
                    vix_trend = "Flat"
        except Exception as e:
            print(f"Error fetching VIX: {e}")

        market_data = {
            "symbol": symbol,
            "spot_price": spot,
            "call_volume": call_vol,
            "put_volume": put_vol,
            "top_oi_strikes": top_oi_strikes,
            "vix_current": vix_current,
            "vix_trend": vix_trend
        }
        
        analysis_text = analyze_market(market_data)
        
        latest_analysis = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "text": analysis_text,
            "data": market_data
        }
        print("Analysis complete.")
        
    except Exception as e:
        print(f"Error in analysis job: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(job_analyze_market, 'interval', minutes=10)

def get_latest_analysis_data():
    return latest_analysis

def start_scheduler():
    scheduler.start()
    # Run once immediately for testing
    scheduler.add_job(job_analyze_market, 'date', run_date=datetime.datetime.now() + datetime.timedelta(seconds=5))
