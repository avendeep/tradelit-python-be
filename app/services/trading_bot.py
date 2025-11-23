"""
Trading Bot Service for OI Analysis
Analyzes Open Interest changes for strike prices around ATM
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple

from app.db.mongodb import MongoDB
from app.models.trading import TradingBotModel
from app.schemas.trading_bot import (
    OIAnalysisResult,
    StrikeOIAnalysis,
    TradingBotStatus,
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class TradingBotService:
    """Service for managing and running trading bots"""

    def __init__(self):
        self._bots_collection = "trading_bots"
        self._snapshots_collection = "option_chain_snapshots"

    async def activate_bot(
        self,
        bot_id: str,
        instrument_key: str,
        expiry_date: str,
        lookback_minutes: int = 10,
    ) -> Dict[str, Any]:
        """
        Activate a trading bot

        Args:
            bot_id: Unique identifier for the bot
            instrument_key: Instrument to analyze
            expiry_date: Expiry date
            lookback_minutes: Minutes to look back for analysis

        Returns:
            Bot configuration and status
        """
        try:
            collection = MongoDB.get_collection(self._bots_collection)

            # Check if bot already exists
            existing_bot = await collection.find_one({"bot_id": bot_id})

            bot_data = {
                "bot_id": bot_id,
                "is_active": True,
                "instrument_key": instrument_key,
                "expiry_date": expiry_date,
                "lookback_minutes": lookback_minutes,
                "activated_at": settings.now_naive(),
                "updated_at": settings.now_naive(),
            }

            if existing_bot:
                # Update existing bot
                await collection.update_one(
                    {"bot_id": bot_id},
                    {
                        "$set": {
                            **bot_data,
                            "created_at": existing_bot.get("created_at"),
                        }
                    },
                )
                logger.info(f"✅ Updated and activated bot: {bot_id}")
            else:
                # Create new bot
                bot_data["created_at"] = settings.now_naive()
                bot_data["total_analyses"] = 0
                await collection.insert_one(bot_data)
                logger.info(f"✅ Created and activated bot: {bot_id}")

            return {
                "bot_id": bot_id,
                "is_active": True,
                "instrument_key": instrument_key,
                "expiry_date": expiry_date,
                "lookback_minutes": lookback_minutes,
                "activated_at": bot_data["activated_at"].isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Error activating bot {bot_id}: {str(e)}")
            raise

    async def deactivate_bot(self, bot_id: str) -> bool:
        """
        Deactivate a trading bot

        Args:
            bot_id: Bot identifier

        Returns:
            True if deactivated successfully
        """
        try:
            collection = MongoDB.get_collection(self._bots_collection)

            result = await collection.update_one(
                {"bot_id": bot_id},
                {
                    "$set": {
                        "is_active": False,
                        "deactivated_at": settings.now_naive(),
                        "updated_at": settings.now_naive(),
                    }
                },
            )

            if result.modified_count > 0:
                logger.info(f"✅ Deactivated bot: {bot_id}")
                return True
            else:
                logger.warning(f"⚠️ Bot not found: {bot_id}")
                return False

        except Exception as e:
            logger.error(f"❌ Error deactivating bot {bot_id}: {str(e)}")
            raise

    async def get_bot_status(self, bot_id: str) -> Optional[TradingBotStatus]:
        """
        Get status of a trading bot

        Args:
            bot_id: Bot identifier

        Returns:
            Bot status or None if not found
        """
        try:
            collection = MongoDB.get_collection(self._bots_collection)
            bot = await collection.find_one({"bot_id": bot_id})

            if not bot:
                return None

            return TradingBotStatus(
                bot_id=bot["bot_id"],
                is_active=bot.get("is_active", False),
                instrument_key=bot["instrument_key"],
                expiry_date=bot["expiry_date"],
                lookback_minutes=bot.get("lookback_minutes", 10),
                activated_at=bot.get("activated_at"),
                last_analysis_at=bot.get("last_analysis_at"),
                total_analyses=bot.get("total_analyses", 0),
            )

        except Exception as e:
            logger.error(f"❌ Error getting bot status {bot_id}: {str(e)}")
            return None

    async def get_all_active_bots(self) -> List[Dict[str, Any]]:
        """
        Get all active trading bots

        Returns:
            List of active bot configurations
        """
        try:
            collection = MongoDB.get_collection(self._bots_collection)
            cursor = collection.find({"is_active": True})
            bots = await cursor.to_list(length=None)
            return bots

        except Exception as e:
            logger.error(f"❌ Error fetching active bots: {str(e)}")
            return []

    async def analyze_oi_changes(self, bot_id: str) -> Optional[OIAnalysisResult]:
        """
        Analyze OI changes for a specific bot

        Args:
            bot_id: Bot identifier

        Returns:
            OI analysis result or None if analysis failed
        """
        try:
            # Get bot configuration
            collection = MongoDB.get_collection(self._bots_collection)
            bot = await collection.find_one({"bot_id": bot_id})

            if not bot or not bot.get("is_active"):
                logger.warning(f"⚠️ Bot {bot_id} not found or not active")
                return None

            instrument_key = bot["instrument_key"]
            expiry_date = bot["expiry_date"]
            lookback_minutes = bot.get("lookback_minutes", 10)

            logger.info(f"🔍 Analyzing OI changes for {instrument_key} (Bot: {bot_id})")

            # Get current and historical option chain data
            current_data = await self._get_latest_snapshot(instrument_key, expiry_date)
            if not current_data:
                logger.warning(f"⚠️ No current data found for {instrument_key}")
                return None

            # Get snapshot from lookback_minutes ago
            historical_data = await self._get_historical_snapshot(
                instrument_key, expiry_date, lookback_minutes
            )
            if not historical_data:
                logger.warning(
                    f"⚠️ No historical data found for {instrument_key} ({lookback_minutes} min ago)"
                )
                return None

            # Identify ATM strike and analyze surrounding strikes
            atm_strike, spot_price = self._identify_atm_strike(current_data)
            if not atm_strike:
                logger.warning(f"⚠️ Could not identify ATM strike for {instrument_key}")
                return None

            logger.info(f"📊 ATM Strike: {atm_strike}, Spot Price: {spot_price}")

            # Get strikes to analyze (3 above and 3 below ATM)
            strikes_to_analyze = self._get_strikes_around_atm(
                current_data, atm_strike, num_strikes=3
            )

            # Analyze OI changes for each strike
            strike_analyses = []
            total_call_oi_change = 0
            total_put_oi_change = 0

            logger.info(f"\n{'='*80}")
            logger.info(f"📊 OI ANALYSIS DETAILS for {bot_id}")
            logger.info(f"{'='*80}")
            logger.info(f"Instrument: {instrument_key}")
            logger.info(f"Expiry: {expiry_date}")
            logger.info(f"ATM Strike: {atm_strike} | Spot Price: {spot_price}")
            logger.info(f"Lookback Period: {lookback_minutes} minutes")
            logger.info(f"Strikes Analyzed: {strikes_to_analyze}")
            logger.info(f"{'='*80}\n")

            for strike in strikes_to_analyze:
                analysis = self._analyze_strike_oi(
                    strike, current_data, historical_data
                )
                if analysis:
                    strike_analyses.append(analysis)
                    total_call_oi_change += analysis.call_oi_change or 0
                    total_put_oi_change += analysis.put_oi_change or 0

                    # Log detailed strike analysis
                    atm_marker = " ⭐ ATM" if strike == atm_strike else ""
                    logger.info(f"Strike {strike}{atm_marker}:")
                    logger.info(
                        f"  📞 CALL OI: {analysis.call_oi_previous:>10,} → {analysis.call_oi_current:>10,} | Change: {analysis.call_oi_change:>+10,} ({analysis.call_oi_change_percent:>+6.2f}%)"
                        if analysis.call_oi_change is not None
                        else f"  📞 CALL OI: {analysis.call_oi_current:>10,}"
                    )
                    logger.info(
                        f"  📗 PUT  OI: {analysis.put_oi_previous:>10,} → {analysis.put_oi_current:>10,} | Change: {analysis.put_oi_change:>+10,} ({analysis.put_oi_change_percent:>+6.2f}%)"
                        if analysis.put_oi_change is not None
                        else f"  📗 PUT  OI: {analysis.put_oi_current:>10,}"
                    )
                    logger.info("")

            # Calculate PCR (Put-Call Ratio)
            pcr_oi = None
            current_total_call_oi = sum(s.call_oi_current or 0 for s in strike_analyses)
            current_total_put_oi = sum(s.put_oi_current or 0 for s in strike_analyses)
            if current_total_call_oi > 0:
                pcr_oi = round(current_total_put_oi / current_total_call_oi, 4)

            logger.info(f"{'='*80}")
            logger.info(f"📊 SUMMARY")
            logger.info(f"{'='*80}")
            logger.info(f"Total Call OI Change: {total_call_oi_change:>+15,}")
            logger.info(f"Total Put  OI Change: {total_put_oi_change:>+15,}")
            logger.info(
                f"Net OI Change (Put - Call): {(total_put_oi_change - total_call_oi_change):>+15,}"
            )
            logger.info(f"Current Total Call OI: {current_total_call_oi:>15,}")
            logger.info(f"Current Total Put  OI: {current_total_put_oi:>15,}")
            logger.info(f"PCR (Put-Call Ratio): {pcr_oi if pcr_oi else 'N/A'}")

            # Generate trading signal
            signal = self._generate_signal(
                total_call_oi_change, total_put_oi_change, pcr_oi
            )

            logger.info(f"\n🎯 SIGNAL: {signal}")
            logger.info(f"{'='*80}\n")

            # Create analysis result
            result = OIAnalysisResult(
                timestamp=settings.now_naive(),
                instrument_key=instrument_key,
                expiry_date=expiry_date,
                atm_strike=atm_strike,
                spot_price=spot_price,
                strikes_analyzed=strike_analyses,
                analysis_period_minutes=lookback_minutes,
                total_call_oi_change=total_call_oi_change,
                total_put_oi_change=total_put_oi_change,
                pcr_oi=pcr_oi,
                signal=signal,
            )

            # Update bot last_analysis_at and increment total_analyses
            await collection.update_one(
                {"bot_id": bot_id},
                {
                    "$set": {
                        "last_analysis_at": settings.now_naive(),
                        "updated_at": settings.now_naive(),
                    },
                    "$inc": {"total_analyses": 1},
                },
            )

            logger.info(
                f"✅ OI Analysis complete for {bot_id} | Signal: {signal} | "
                f"Call OI Change: {total_call_oi_change:+,} | "
                f"Put OI Change: {total_put_oi_change:+,} | PCR: {pcr_oi}"
            )

            return result

        except Exception as e:
            logger.error(f"❌ Error analyzing OI changes for bot {bot_id}: {str(e)}")
            return None

    async def _get_latest_snapshot(
        self, instrument_key: str, expiry_date: str
    ) -> Optional[Dict[str, Any]]:
        """Get the most recent option chain snapshot"""
        try:
            collection = MongoDB.get_collection(self._snapshots_collection)
            snapshot = await collection.find_one(
                {"instrument_key": instrument_key, "expiry_date": expiry_date},
                sort=[("timestamp", -1)],
            )
            return snapshot.get("data") if snapshot else None

        except Exception as e:
            logger.error(f"❌ Error fetching latest snapshot: {str(e)}")
            return None

    async def _get_historical_snapshot(
        self, instrument_key: str, expiry_date: str, minutes_ago: int
    ) -> Optional[Dict[str, Any]]:
        """Get option chain snapshot from X minutes ago"""
        try:
            collection = MongoDB.get_collection(self._snapshots_collection)

            # Calculate target timestamp in IST (without seconds)
            target_time = settings.now_naive() - timedelta(minutes=minutes_ago)
            target_time = target_time.replace(second=0, microsecond=0)

            # Find snapshot closest to target time
            snapshot = await collection.find_one(
                {
                    "instrument_key": instrument_key,
                    "expiry_date": expiry_date,
                    "timestamp": {"$lte": target_time},
                },
                sort=[("timestamp", -1)],
            )
            return snapshot.get("data") if snapshot else None

        except Exception as e:
            logger.error(f"❌ Error fetching historical snapshot: {str(e)}")
            return None

    def _identify_atm_strike(
        self, option_chain_data: Dict[str, Any]
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Identify the ATM (At The Money) strike price

        Returns:
            Tuple of (atm_strike, spot_price)
        """
        try:
            data = option_chain_data.get("data", [])
            if not data:
                return None, None

            # Get spot price from first strike
            spot_price = None
            for strike_data in data:
                if strike_data.get("underlying_spot_price"):
                    spot_price = strike_data["underlying_spot_price"]
                    break

            if not spot_price:
                return None, None

            # Find strike closest to spot price
            atm_strike = None
            min_diff = float("inf")

            for strike_data in data:
                strike = strike_data.get("strike_price")
                if strike:
                    diff = abs(strike - spot_price)
                    if diff < min_diff:
                        min_diff = diff
                        atm_strike = strike

            return atm_strike, spot_price

        except Exception as e:
            logger.error(f"❌ Error identifying ATM strike: {str(e)}")
            return None, None

    def _get_strikes_around_atm(
        self, option_chain_data: Dict[str, Any], atm_strike: float, num_strikes: int = 3
    ) -> List[float]:
        """
        Get strike prices around ATM (num_strikes above and below)

        Args:
            option_chain_data: Option chain data
            atm_strike: ATM strike price
            num_strikes: Number of strikes above and below ATM

        Returns:
            List of strike prices
        """
        try:
            data = option_chain_data.get("data", [])
            all_strikes = sorted(
                [s.get("strike_price") for s in data if s.get("strike_price")]
            )

            if atm_strike not in all_strikes:
                return []

            atm_index = all_strikes.index(atm_strike)

            # Get strikes around ATM
            start_index = max(0, atm_index - num_strikes)
            end_index = min(len(all_strikes), atm_index + num_strikes + 1)

            return all_strikes[start_index:end_index]

        except Exception as e:
            logger.error(f"❌ Error getting strikes around ATM: {str(e)}")
            return []

    def _analyze_strike_oi(
        self,
        strike: float,
        current_data: Dict[str, Any],
        historical_data: Dict[str, Any],
    ) -> Optional[StrikeOIAnalysis]:
        """
        Analyze OI changes for a specific strike

        Args:
            strike: Strike price
            current_data: Current option chain data
            historical_data: Historical option chain data

        Returns:
            Strike OI analysis
        """
        try:
            # Find strike data in current and historical snapshots
            current_strike = self._find_strike_data(current_data, strike)
            historical_strike = self._find_strike_data(historical_data, strike)

            if not current_strike:
                return None

            # Extract OI values
            call_oi_current = self._get_oi(current_strike, "call_options")
            put_oi_current = self._get_oi(current_strike, "put_options")

            call_oi_previous = (
                self._get_oi(historical_strike, "call_options")
                if historical_strike
                else None
            )
            put_oi_previous = (
                self._get_oi(historical_strike, "put_options")
                if historical_strike
                else None
            )

            # Calculate changes
            call_oi_change = None
            call_oi_change_percent = None
            if call_oi_current is not None and call_oi_previous is not None:
                call_oi_change = call_oi_current - call_oi_previous
                if call_oi_previous > 0:
                    call_oi_change_percent = round(
                        (call_oi_change / call_oi_previous) * 100, 2
                    )

            put_oi_change = None
            put_oi_change_percent = None
            if put_oi_current is not None and put_oi_previous is not None:
                put_oi_change = put_oi_current - put_oi_previous
                if put_oi_previous > 0:
                    put_oi_change_percent = round(
                        (put_oi_change / put_oi_previous) * 100, 2
                    )

            return StrikeOIAnalysis(
                strike_price=strike,
                call_oi_current=call_oi_current,
                call_oi_previous=call_oi_previous,
                call_oi_change=call_oi_change,
                call_oi_change_percent=call_oi_change_percent,
                put_oi_current=put_oi_current,
                put_oi_previous=put_oi_previous,
                put_oi_change=put_oi_change,
                put_oi_change_percent=put_oi_change_percent,
            )

        except Exception as e:
            logger.error(f"❌ Error analyzing strike OI for {strike}: {str(e)}")
            return None

    def _find_strike_data(
        self, option_chain_data: Dict[str, Any], strike: float
    ) -> Optional[Dict[str, Any]]:
        """Find data for a specific strike in option chain"""
        data = option_chain_data.get("data", [])
        for strike_data in data:
            if strike_data.get("strike_price") == strike:
                return strike_data
        return None

    def _get_oi(
        self, strike_data: Optional[Dict[str, Any]], option_type: str
    ) -> Optional[int]:
        """Extract OI from strike data for call or put options"""
        if not strike_data:
            return None

        option_data = strike_data.get(option_type)
        if not option_data:
            return None

        market_data = option_data.get("market_data")
        if not market_data:
            return None

        return market_data.get("oi")

    def _generate_signal(
        self,
        call_oi_change: int,
        put_oi_change: int,
        pcr_oi: Optional[float],
    ) -> str:
        """
        Generate trading signal based on OI changes

        Simple logic:
        - If call OI increases significantly more than put OI -> BEARISH (writers selling calls)
        - If put OI increases significantly more than call OI -> BULLISH (writers selling puts)
        - Otherwise -> NEUTRAL

        Args:
            call_oi_change: Total call OI change
            put_oi_change: Total put OI change
            pcr_oi: Put-Call Ratio

        Returns:
            Trading signal: BULLISH, BEARISH, or NEUTRAL
        """
        try:
            # Calculate the difference in OI changes
            oi_change_diff = put_oi_change - call_oi_change

            # Define threshold (can be adjusted based on backtesting)
            threshold = 50000  # Example: 50,000 contracts difference

            if oi_change_diff > threshold:
                return "BULLISH"
            elif oi_change_diff < -threshold:
                return "BEARISH"
            else:
                return "NEUTRAL"

        except Exception as e:
            logger.error(f"❌ Error generating signal: {str(e)}")
            return "NEUTRAL"


# Singleton instance
trading_bot_service = TradingBotService()
