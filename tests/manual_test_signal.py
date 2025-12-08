import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.schemas.trading_bot import OIAnalysisResult, StrikeOIAnalysis
from app.services.signal_analysis import analyze_trade_signal

def create_mock_analysis(strikes_data, pcr, atm_strike=1000.0):
    strikes_analyzed = []
    for s_price, call_chg, put_chg in strikes_data:
        strikes_analyzed.append(StrikeOIAnalysis(
            strike_price=s_price,
            call_oi_current=1000,
            call_oi_previous=1000,
            call_oi_change=call_chg,
            call_oi_change_percent=0.0,
            put_oi_current=1000,
            put_oi_previous=1000,
            put_oi_change=put_chg,
            put_oi_change_percent=0.0
        ))
        
    return OIAnalysisResult(
        timestamp=datetime.now(),
        instrument_key="TEST",
        expiry_date="2023-01-01",
        atm_strike=atm_strike,
        spot_price=atm_strike,
        strikes_analyzed=strikes_analyzed,
        analysis_period_minutes=10,
        total_call_oi_change=0,
        total_put_oi_change=0,
        pcr_oi=pcr,
        signal="NEUTRAL"
    )

def test_signal():
    # Strikes: 980, 990, 1000(ATM), 1010, 1020
    
    # Case 1: Bullish Push (All 5 Bullish: Put Chg > 0, Call Chg < 0)
    # Bullish Push: Put > 0, Call < 0 (NEW LOGIC)
    bullish_push_data = [
        (980, -100, 100),
        (990, -100, 100),
        (1000, -100, 100),
        (1010, -100, 100),
        (1020, -100, 100)
    ]
    result = analyze_trade_signal(create_mock_analysis(bullish_push_data, pcr=1.5))
    print(f"Case 1 (Bullish Push, PCR>1): {result} - {'PASS' if result == 'BULLISH PUSH' else 'FAIL'}")

    # Case 2: Bearish Push (All 5 Bearish: Put Chg < 0, Call Chg > 0)
    # Bearish Push: Put < 0, Call > 0 (NEW LOGIC)
    bearish_push_data = [
        (980, 100, -100),
        (990, 100, -100),
        (1000, 100, -100),
        (1010, 100, -100),
        (1020, 100, -100)
    ]
    result = analyze_trade_signal(create_mock_analysis(bearish_push_data, pcr=0.5))
    print(f"Case 2 (Bearish Push, PCR<1): {result} - {'PASS' if result == 'BEARISH PUSH' else 'FAIL'}")

    # Case 3: Bullish Accumulation (ATM & 2 Below Bullish)
    # 980, 990, 1000 are Bullish (Put > 0, Call < 0).
    bullish_accum_data = [
        (980, -100, 100),  # Bullish
        (990, -100, 100),  # Bullish
        (1000, -100, 100), # Bullish
        (1010, 0, 0),      # No Signal
        (1020, 0, 0)       # No Signal
    ]
    result = analyze_trade_signal(create_mock_analysis(bullish_accum_data, pcr=1.5))
    print(f"Case 3 (Bullish Accum, PCR>1): {result} - {'PASS' if result == 'BULLISH ACCUMULATION' else 'FAIL'}")

    # Case 4: Bearish Accumulation (ATM & 2 Above Bearish)
    # 1000, 1010, 1020 are Bearish (Put < 0, Call > 0).
    bearish_accum_data = [
        (980, 0, 0),       # No Signal
        (990, 0, 0),       # No Signal
        (1000, 100, -100), # Bearish
        (1010, 100, -100), # Bearish
        (1020, 100, -100)  # Bearish
    ]
    result = analyze_trade_signal(create_mock_analysis(bearish_accum_data, pcr=0.5))
    print(f"Case 4 (Bearish Accum, PCR<1): {result} - {'PASS' if result == 'BEARISH ACCUMULATION' else 'FAIL'}")

    # Case 5: PCR Filter - PCR = 1
    result = analyze_trade_signal(create_mock_analysis(bullish_push_data, pcr=1.0))
    print(f"Case 5 (PCR=1): {result} - {'PASS' if result == 'NO TRADE/NEUTRAL MARKET' else 'FAIL'}")

    # Case 6: PCR Filter - PCR < 1 but Bullish Signal
    result = analyze_trade_signal(create_mock_analysis(bullish_push_data, pcr=0.5))
    print(f"Case 6 (PCR<1, Bullish Signal): {result} - {'PASS' if 'NO SIGNAL' in result else 'FAIL'}")

    # Case 7: PCR Filter - PCR > 1 but Bearish Signal
    result = analyze_trade_signal(create_mock_analysis(bearish_push_data, pcr=1.5))
    print(f"Case 7 (PCR>1, Bearish Signal): {result} - {'PASS' if 'NO SIGNAL' in result else 'FAIL'}")

if __name__ == "__main__":
    # Redirect stdout to a file
    with open("test_results_utf8.txt", "w", encoding="utf-8") as f:
        sys.stdout = f
        test_signal()
        sys.stdout = sys.__stdout__
