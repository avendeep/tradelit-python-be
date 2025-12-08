"""
Signal Analysis Service
Analyzes OI changes to generate trade signals based on specific criteria.
"""

import logging
from typing import List, Optional
from app.schemas.trading_bot import OIAnalysisResult, StrikeOIAnalysis

logger = logging.getLogger(__name__)

def analyze_strike_signal(strike: StrikeOIAnalysis) -> str:
    """
    Determine the signal for a single strike based on OI changes.
    
    Logic:
    - Positive PUT OI change and negative CALL OI change -> BEARISH PUSH
    - Negative PUT OI change and positive CALL OI change -> BULLISH PUSH
    - Both Positive or Both Negative -> NO SIGNAL
    """
    call_change = strike.call_oi_change or 0
    put_change = strike.put_oi_change or 0
    
    if put_change > 0 and call_change < 0:
        return "BULLISH PUSH"
    elif put_change < 0 and call_change > 0:
        return "BEARISH PUSH"
    else:
        return "NO SIGNAL"

def get_signal_for_strikes(strikes: List[StrikeOIAnalysis], atm_strike: float) -> str:
    """
    Analyze 5 strikes (ATM, 2 Above, 2 Below) to generate an aggregate signal.
    """
    # Sort strikes by price just in case
    sorted_strikes = sorted(strikes, key=lambda x: x.strike_price)
    
    # Find ATM index
    atm_index = -1
    for i, s in enumerate(sorted_strikes):
        if s.strike_price == atm_strike:
            atm_index = i
            break
            
    if atm_index == -1:
        logger.warning(f"ATM strike {atm_strike} not found in analyzed strikes")
        return "NO SIGNAL"
        
    # We need 2 below and 2 above. 
    # Check if we have enough data. 
    # The user said "consider 5 strike prices ( 1 ATM, 2 Below ATM, 2 Above ATM)"
    # Indices: ATM-2, ATM-1, ATM, ATM+1, ATM+2
    
    start_idx = atm_index - 2
    end_idx = atm_index + 3 # Exclusive
    
    if start_idx < 0 or end_idx > len(sorted_strikes):
        logger.warning("Not enough strikes around ATM to perform full 5-strike analysis")
        # Fallback or partial analysis? For now, let's return NO SIGNAL if data is insufficient
        return "NO SIGNAL"
        
    target_strikes = sorted_strikes[start_idx:end_idx]
    
    # Map signals
    signals = [analyze_strike_signal(s) for s in target_strikes]
    
    # target_strikes[0] = ATM-2
    # target_strikes[1] = ATM-1
    # target_strikes[2] = ATM
    # target_strikes[3] = ATM+1
    # target_strikes[4] = ATM+2
    
    # Logic 1: If all 5 strike prices has bullish push signal then log BULLISH push signal.
    if all(s == "BULLISH PUSH" for s in signals):
        return "BULLISH PUSH"
        
    # Logic 2: If all 5 strike prices have bearish push signal then log BEARISH push signal.
    if all(s == "BEARISH PUSH" for s in signals):
        return "BEARISH PUSH"
        
    # Logic 3: If the ATM strike price and 2 strike prices above ATM strike or just 2 strike prices above the ATM has bearish push then log BEARISH Accumulation.
    # "ATM and 2 strike prices above" -> indices 2, 3, 4
    # "just 2 strike prices above" -> indices 3, 4
    # The user said "OR", so if indices 3 and 4 are Bearish Push, it satisfies the condition.
    # Actually, "ATM and 2 strike prices above" implies 3 strikes. "Just 2 strike prices above" implies 2 strikes.
    # If the 2 above are bearish, the condition is met regardless of ATM.
    # So checking indices 3 and 4 is sufficient?
    # Let's interpret strictly: (Signal[ATM] == Bearish AND Signal[ATM+1] == Bearish AND Signal[ATM+2] == Bearish) OR (Signal[ATM+1] == Bearish AND Signal[ATM+2] == Bearish)
    # This simplifies to: Signal[ATM+1] == Bearish AND Signal[ATM+2] == Bearish
    
    if signals[3] == "BEARISH PUSH" and signals[4] == "BEARISH PUSH":
         # Check if ATM is also bearish for the first part of OR, but the second part covers it.
         return "BEARISH ACCUMULATION"

    # Logic 4: If the ATM strike price and 2 strike prices below ATM strike or just 2 strike prices below the ATM has bullish push then log BULLISH Accumulation.
    # Indices 0, 1 (Below) and 2 (ATM).
    # "ATM and 2 strike prices below" -> indices 0, 1, 2
    # "just 2 strike prices below" -> indices 0, 1
    # Simplifies to: Signal[ATM-2] == Bullish AND Signal[ATM-1] == Bullish
    
    if signals[0] == "BULLISH PUSH" and signals[1] == "BULLISH PUSH":
        return "BULLISH ACCUMULATION"
        
    return "NO SIGNAL"

def analyze_trade_signal(analysis: OIAnalysisResult) -> str:
    """
    Main function to generate the final trade signal.
    """
    raw_signal = get_signal_for_strikes(analysis.strikes_analyzed, analysis.atm_strike)
    pcr = analysis.pcr_oi
    
    if pcr is None:
        return "NO SIGNAL (PCR N/A)"
        
    # PCR Filter Logic
    # - If the PCR is =1 then send 'NO TRADE/NEUTRAL MARKET' Signals
    if pcr == 1:
        return "NO TRADE/NEUTRAL MARKET"
        
    # - if the PCR is <1 then send 'BEARISH' Signals
    if pcr < 1:
        if "BEARISH" in raw_signal:
            return raw_signal
        else:
            return "NO SIGNAL (PCR < 1 but Signal not Bearish)"
            
    # - if the PCR is >1 then send 'BULLISH' Signals
    if pcr > 1:
        if "BULLISH" in raw_signal:
            return raw_signal
        else:
            return "NO SIGNAL (PCR > 1 but Signal not Bullish)"
            
    return "NO SIGNAL"
