import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def analyze_market(market_data):
    if not GOOGLE_API_KEY:
        return {"error": "Google API Key not configured"}

    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""
    You are a professional 0DTE (Zero Days to Expiration) options trader.
    Analyze the following market data for {market_data.get('symbol')} and provide a trading suggestion.
    
    Current Price: {market_data.get('spot_price')}
    VIX Level: {market_data.get('vix_current')}
    VIX Trend (1hr): {market_data.get('vix_trend')}
    
    Data Summary:
    - Call Volume: {market_data.get('call_volume')}
    - Put Volume: {market_data.get('put_volume')}
    - Top Open Interest Strikes: {market_data.get('top_oi_strikes')}
    
    Technical Indicators (5min):
    - RSI (14): {market_data.get('rsi_5min')}
    - MACD: {market_data.get('macd_5min')}
    - Recent Trend: {market_data.get('recent_trend_5min')}
    
    Gamma & Delta Exposure:
    - Total GEX: {market_data.get('total_gex')}
    - Total DEX: {market_data.get('total_dex')}
    
    Please provide:
    1. Market Sentiment (Bullish/Bearish/Neutral)
    2. Predicted Closing Price Range
    3. Predicted Specific Closing Price Target (within 10 points)
    4. Suggested Strategy (e.g., Iron Condor, Long Call, etc.)
    5. Recommended Exit Criteria:
       - Profit Target (e.g., 20% or specific price)
       - Stop Loss (e.g., -10% or specific price)
       - Time Exit (e.g., "Close by 3:30 PM if target not met")
    6. Key Support/Resistance Levels
    
    Keep the response concise and suitable for a text-to-speech summary.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            return "Analysis unavailable: Rate limit exceeded. Please try again in a minute."
        return f"Error generating analysis: {error_msg}"
