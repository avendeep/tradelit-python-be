"""
Service for managing candle configuration and data storage
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.db.mongodb import MongoDB
from app.models.upstox import IntradayCandleModel, CandleConfigurationModel
from app.core.config import settings

logger = logging.getLogger(__name__)


class CandleService:
    """Service for managing candle data and configuration"""

    def __init__(self):
        self._config_collection = "candle_configuration"
        self._data_collection = "intraday_candles"

    async def get_interval(self) -> str:
        """
        Get the configured candle interval
        Returns default '10minute' if not configured
        """
        try:
            collection = MongoDB.get_collection(self._config_collection)
            config = await collection.find_one({"_id": "candle_config"})
            
            if config:
                return config.get("interval", "10minute")
            
            # Create default configuration if not exists
            default_config = CandleConfigurationModel(interval="10minute")
            await collection.insert_one(default_config.model_dump(by_alias=True))
            return "10minute"
            
        except Exception as e:
            logger.error(f"❌ Error getting candle interval: {str(e)}")
            return "10minute"  # Fallback default

    async def set_interval(self, interval: str) -> bool:
        """
        Set the candle interval configuration
        """
        try:
            collection = MongoDB.get_collection(self._config_collection)
            
            update_data = {
                "interval": interval,
                "updated_at": settings.now_naive()
            }
            
            await collection.update_one(
                {"_id": "candle_config"},
                {"$set": update_data},
                upsert=True
            )
            
            logger.info(f"✅ Updated candle interval to: {interval}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting candle interval: {str(e)}")
            return False

    async def save_candles(
        self, 
        instrument_key: str, 
        interval: str, 
        candles_data: List[List[Any]]
    ) -> int:
        """
        Save candle data to database, updating existing records
        
        Args:
            instrument_key: Instrument key
            interval: Candle interval
            candles_data: List of candles from Upstox API 
                          [timestamp, open, high, low, close, volume, oi]
        
        Returns:
            Number of candles saved/updated
        """
        if not candles_data:
            return 0

        try:
            collection = MongoDB.get_collection(self._data_collection)
            count = 0
            
            # Process each candle
            for candle in candles_data:
                # Upstox returns timestamp as string in ISO format
                timestamp_str = candle[0]
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                except ValueError:
                    # Handle potential format differences
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=None)

                candle_model = IntradayCandleModel(
                    instrument_key=instrument_key,
                    interval=interval,
                    timestamp=timestamp,
                    open=float(candle[1]),
                    high=float(candle[2]),
                    low=float(candle[3]),
                    close=float(candle[4]),
                    volume=int(candle[5]),
                    oi=int(candle[6]) if len(candle) > 6 else 0,
                    updated_at=settings.now_naive()
                )
                
                # Upsert based on instrument_key, interval, and timestamp
                filter_query = {
                    "instrument_key": instrument_key,
                    "interval": interval,
                    "timestamp": timestamp
                }
                
                await collection.replace_one(
                    filter_query,
                    candle_model.model_dump(by_alias=True),
                    upsert=True
                )
                count += 1
                
            return count

        except Exception as e:
            logger.error(f"❌ Error saving candles for {instrument_key}: {str(e)}")
            return 0


# Singleton instance
candle_service = CandleService()
