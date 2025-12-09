"""
Trade Decision Centre Service
Receives and logs trade analysis from trading bots.
"""

import logging
from typing import Any, Dict
from datetime import datetime

from app.schemas.trading_bot import OIAnalysisResult
from app.db.mongodb import MongoDB
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
            
            # --- Store Signal Count ---
            await self._update_signal_count(analysis.instrument_key, trade_signal)
            
        except Exception as e:
            logger.error(f"❌ Error logging analysis in Trade Decision Centre: {str(e)}")

    async def _update_signal_count(self, instrument_key: str, signal: str) -> None:
        """
        Update the daily signal count in the database.
        """
        try:
            today_str = datetime.now().strftime("%Y-%m-%d")
            collection = MongoDB.get_collection("daily_signal_counts")
            
            update_field = None
            if "BULLISH PUSH" in signal:
                update_field = "bullish_push_count"
            elif "BULLISH ACCUMULATION" in signal:
                update_field = "bullish_accumulation_count"
            elif "BEARISH PUSH" in signal:
                update_field = "bearish_push_count"
            elif "BEARISH ACCUMULATION" in signal:
                update_field = "bearish_accumulation_count"
                
            if update_field:
                await collection.update_one(
                    {"date": today_str, "instrument_key": instrument_key},
                    {
                        "$inc": {update_field: 1},
                        "$set": {"last_updated_at": datetime.utcnow()}
                    },
                    upsert=True
                )
                
                # Fetch updated counts for logging
                doc = await collection.find_one({"date": today_str, "instrument_key": instrument_key})
                if doc:
                    logger.info(f"📊 Daily Signal Count ({today_str}):")
                    logger.info(f"   Bullish Push: {doc.get('bullish_push_count', 0)}")
                    logger.info(f"   Bullish Accum: {doc.get('bullish_accumulation_count', 0)}")
                    logger.info(f"   Bearish Push: {doc.get('bearish_push_count', 0)}")
                    logger.info(f"   Bearish Accum: {doc.get('bearish_accumulation_count', 0)}")

        except Exception as e:
            logger.error(f"❌ Error updating signal count: {str(e)}")

# Singleton instance
trade_decision_centre = TradeDecisionCentre()
