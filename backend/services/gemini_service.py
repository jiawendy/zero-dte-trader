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

    model = genai.GenerativeModel('gemini-flash-latest')
    
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
    
    Please provide:
    1. Market Sentiment (Bullish/Bearish/Neutral)
    2. Predicted Closing Price Range
    3. Suggested Strategy (e.g., Iron Condor, Long Call, etc.)
    4. Key Support/Resistance Levels
    
    Keep the response concise and suitable for a text-to-speech summary.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating analysis: {str(e)}"
