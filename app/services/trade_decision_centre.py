"""
Trade Decision Centre Service
Receives and logs trade analysis from trading bots.
"""

import logging
from typing import Any, Dict
from app.schemas.trading_bot import OIAnalysisResult

from app.services.signal_analysis import analyze_trade_signal

logger = logging.getLogger(__name__)

class TradeDecisionCentre:
    """
    Central service for receiving and processing trade analysis from bots.
    """
    
    def __init__(self):
        pass

    async def log_analysis(self, analysis: OIAnalysisResult) -> None:
        """
        Log the received trade analysis.
        
        Args:
            analysis: The analysis result from a trading bot.
        """
        try:
            # Calculate signal using the new service
            trade_signal = analyze_trade_signal(analysis)
            
            logger.info(f"\n{'='*80}")
            logger.info(f"🏢 TRADE DECISION CENTRE RECEIVED ANALYSIS")
            logger.info(f"{'='*80}")
            logger.info(f"Bot ID: {analysis.instrument_key}") # Using instrument key as proxy for bot source for now
            logger.info(f"Bot Signal: {analysis.signal}")
            logger.info(f"TDC Signal: {trade_signal}")
            logger.info(f"PCR: {analysis.pcr_oi}")
            logger.info(f"Call OI Change: {analysis.total_call_oi_change}")
            logger.info(f"Put OI Change: {analysis.total_put_oi_change}")
            
            logger.info(f"\n--- Strike Analysis ---")
            logger.info(f"{'Strike':<10} | {'Call OI Chg':<15} | {'Put OI Chg':<15}")
            logger.info("-" * 46)
            
            for strike in analysis.strikes_analyzed:
                logger.info(
                    f"{strike.strike_price:<10.2f} | "
                    f"{strike.call_oi_change:<15} | "
                    f"{strike.put_oi_change:<15}"
                )
            logger.info(f"{'='*80}\n")
            
        except Exception as e:
            logger.error(f"❌ Error logging analysis in Trade Decision Centre: {str(e)}")

# Singleton instance
trade_decision_centre = TradeDecisionCentre()
