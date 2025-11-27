"""
Scheduled task to fetch intraday candle data from Upstox
Runs every minute and stores data in MongoDB
"""

import logging
from typing import List, Dict, Any

from app.db.mongodb import MongoDB
from app.services.upstox_service import upstox_service
from app.services.candle_service import candle_service

logger = logging.getLogger(__name__)


async def fetch_intraday_candles_task():
    """
    Fetch intraday candle data for all active instruments in watchlist
    """
    try:
        logger.info("🔄 Starting intraday candle fetch task...")

        # Check if Upstox token is valid
        if not upstox_service.is_token_valid():
            logger.warning("⚠️ Upstox token is not valid. Skipping candle fetch.")
            return

        # Get all active watchlist entries
        watchlist_entries = await get_active_watchlist_entries()

        if not watchlist_entries:
            logger.info("ℹ️ No active watchlist entries found. Skipping fetch.")
            return

        # Get configured interval
        interval = await candle_service.get_interval()
        logger.info(f"⏱️ Using candle interval: {interval}")

        success_count = 0
        error_count = 0

        for entry in watchlist_entries:
            try:
                instrument_key = entry.get("instrument_key")
                
                # Fetch candles from Upstox
                # Response format: 
                # {
                #   "status": "success",
                #   "data": {
                #     "candles": [
                #       ["2023-11-20T10:00:00+05:30", 19800, 19810, 19790, 19805, 1000, 0],
                #       ...
                #     ]
                #   }
                # }
                # Fetch candles from Upstox
                logger.debug(f"Fetching candles for {instrument_key} with interval: {interval}")
                
                response = await upstox_service.get_intraday_candles(
                    instrument_key=instrument_key,
                    interval=interval
                )

                if response and response.get("status") == "success":
                    candles_data = response.get("data", {}).get("candles", [])
                    
                    if candles_data:
                        # Save candles
                        saved_count = await candle_service.save_candles(
                            instrument_key=instrument_key,
                            interval=interval,
                            candles_data=candles_data
                        )
                        success_count += 1
                        logger.debug(f"✅ Saved {saved_count} candles for {instrument_key}")
                    else:
                        logger.debug(f"ℹ️ No candles returned for {instrument_key}")
                else:
                    logger.warning(f"⚠️ Failed to fetch candles for {instrument_key}")
                    error_count += 1

            except Exception as e:
                logger.error(
                    f"❌ Error fetching candles for {entry.get('instrument_key')}: {str(e)}"
                )
                error_count += 1

        logger.info(
            f"✅ Intraday candle fetch task completed. Success: {success_count}, Errors: {error_count}"
        )

    except Exception as e:
        logger.error(f"❌ Error in fetch_intraday_candles_task: {str(e)}")


async def get_active_watchlist_entries() -> List[Dict[str, Any]]:
    """
    Get all active watchlist entries from database
    """
    try:
        collection = MongoDB.get_collection("instrument_watchlist")
        cursor = collection.find({"is_active": True})
        entries = await cursor.to_list(length=None)
        return entries
    except Exception as e:
        logger.error(f"❌ Error fetching watchlist entries: {str(e)}")
        return []
