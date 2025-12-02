import pandas as pd
import numpy as np

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_macd(prices, fast=12, slow=26, signal=9):
    exp1 = prices.ewm(span=fast, adjust=False).mean()
    exp2 = prices.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    
    return {
        "macd": macd.iloc[-1],
        "signal": signal_line.iloc[-1],
        "histogram": macd.iloc[-1] - signal_line.iloc[-1]
    }

def calculate_gex_dex(chain, spot_price):
    total_gex = 0
    total_dex = 0
    
    for opt in chain:
        try:
            # Basic checks
            if 'greeks' not in opt or not opt['greeks']:
                continue
                
            gamma = opt['greeks'].get('gamma', 0)
            delta = opt['greeks'].get('delta', 0)
            oi = opt.get('open_interest', 0)
            
            if gamma is None or delta is None or oi is None:
                continue
                
            # Standard GEX formula: Gamma * OI * 100 * Spot
            # Call Gamma is positive, Put Gamma is usually treated as positive for the option but negative for the dealer (short gamma).
            # Common dealer positioning assumption: Dealers are long calls (positive gamma) and short puts (negative gamma)? 
            # Actually, standard GEX assumption: Dealers are short calls (negative gamma) and long puts (positive gamma)?
            # Let's use the SpotGamma / SqueezeMetrics convention:
            # Call GEX = Gamma * OI * 100 * Spot (Positive)
            # Put GEX = Gamma * OI * 100 * Spot * -1 (Negative)
            
            gex_contribution = gamma * oi * 100 * spot_price
            if opt['option_type'] == 'put':
                gex_contribution *= -1
                
            total_gex += gex_contribution
            
            # DEX (Delta Exposure)
            # Call DEX = Delta * OI * 100 * Spot
            # Put DEX = Delta * OI * 100 * Spot (Delta is already negative for puts)
            dex_contribution = delta * oi * 100 * spot_price
            total_dex += dex_contribution
            
        except Exception:
            continue
            
    return total_gex, total_dex
