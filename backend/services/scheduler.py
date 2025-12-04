from apscheduler.schedulers.background import BackgroundScheduler
from .tradier_service import get_spot_price, fetch_option_chain, get_historical_candles, get_quote
from .gemini_service import analyze_market
from .indicators import calculate_rsi, calculate_macd, calculate_gex_dex
import datetime
import pandas as pd

latest_analysis = {
    "timestamp": None,
    "text": "Waiting for initial analysis...",
    "data": {}
}

is_paused = False

def job_analyze_market():
    global latest_analysis, last_analysis_time, is_paused
    
    if is_paused:
        print(f"[{datetime.datetime.now()}] Analysis skipped: Scheduler is PAUSED.")
        return

    now = datetime.datetime.now()
    if last_analysis_time and (now - last_analysis_time).total_seconds() < 60:
        print(f"[{now}] Skipping analysis: Cooldown active (wait 60s)")
        return

    print(f"[{now}] Running scheduled analysis...")
    last_analysis_time = now
    try:
        symbol = "SPX" # Default to SPX for 0DTE
        today = datetime.date.today().strftime("%Y-%m-%d")
        
        spot = get_spot_price(symbol)
        chain = fetch_option_chain(symbol, today)
        
        # 1. Basic Volume Aggregation
        call_vol = sum(opt['volume'] for opt in chain if opt['option_type'] == 'call')
        put_vol = sum(opt['volume'] for opt in chain if opt['option_type'] == 'put')
        
        # 2. Top OI
        sorted_oi = sorted(chain, key=lambda x: x['open_interest'], reverse=True)[:5]
        top_oi_strikes = [f"{opt['strike']} ({opt['option_type']})" for opt in sorted_oi]

        # 3. Gamma & Delta Exposure
        total_gex, total_dex = calculate_gex_dex(chain, spot)

        # 4. Technical Analysis (5min candles)
        candles = get_historical_candles(symbol, interval="5min")
        rsi_val = "N/A"
        macd_val = "N/A"
        recent_trend = "N/A"
        
        if candles and len(candles) > 20:
            df = pd.DataFrame(candles)
            if 'close' in df.columns:
                df['close'] = df['close'].astype(float)
                
                # Calculate Indicators
                rsi_val = round(calculate_rsi(df['close']), 2)
                macd_data = calculate_macd(df['close'])
                macd_val = f"MACD: {macd_data['macd']:.2f}, Signal: {macd_data['signal']:.2f}, Hist: {macd_data['histogram']:.2f}"
                
                # Simple Trend (Last 5 candles)
                last_5 = df['close'].tail(5).tolist()
                start_p = last_5[0]
                end_p = last_5[-1]
                if end_p > start_p:
                    recent_trend = "Up"
                elif end_p < start_p:
                    recent_trend = "Down"
                else:
                    recent_trend = "Flat"

        # 5. Fetch VIX Data
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
            "vix_trend": vix_trend,
            "total_gex": f"${total_gex:,.0f}",
            "total_dex": f"${total_dex:,.0f}",
            "rsi_5min": rsi_val,
            "macd_5min": macd_val,
            "recent_trend_5min": recent_trend
        }
        
        analysis_text = analyze_market(market_data)
        
        latest_analysis = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "text": analysis_text,
            "data": market_data
        }
        
        # Auto-save to disk
        from .storage_service import save_analysis_to_disk
        path, err = save_analysis_to_disk(latest_analysis)
        if path:
            print(f"Auto-saved analysis to {path}")
        else:
            print(f"Failed to auto-save: {err}")
            
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

def pause_analysis():
    global is_paused
    is_paused = True
    print("Scheduler PAUSED.")

def resume_analysis():
    global is_paused
    is_paused = False
    print("Scheduler RESUMED.")
    # Optionally trigger one immediately
    job_analyze_market()

def get_scheduler_status():
    return {"paused": is_paused}
