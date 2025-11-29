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
        Save candle data to database, grouped by day
        
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
            
            # Group candles by date
            candles_by_date: Dict[str, List[Dict[str, Any]]] = {}
            
            for candle in candles_data:
                # Upstox returns timestamp as string in ISO format
                timestamp_str = candle[0]
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                except ValueError:
                    # Handle potential format differences
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=None)

                date_str = timestamp.strftime("%Y-%m-%d")
                
                candle_obj = {
                    "timestamp": timestamp,
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": int(candle[5]),
                    "oi": int(candle[6]) if len(candle) > 6 else 0
                }
                
                if date_str not in candles_by_date:
                    candles_by_date[date_str] = []
                
                candles_by_date[date_str].append(candle_obj)

            total_saved = 0
            
            # Save each day's candles as a single document
            for date_str, daily_candles in candles_by_date.items():
                doc_id = f"{instrument_key}_{date_str}"
                
                # Sort candles by timestamp to ensure order
                daily_candles.sort(key=lambda x: x["timestamp"])
                
                day_wise_model = {
                    "_id": doc_id,
                    "instrument_key": instrument_key,
                    "date": date_str,
                    "interval": interval,
                    "candles": daily_candles,
                    "updated_at": settings.now_naive()
                }
                
                await collection.replace_one(
                    {"_id": doc_id},
                    day_wise_model,
                    upsert=True
                )
                total_saved += len(daily_candles)
                
            return total_saved

        except Exception as e:
            logger.error(f"❌ Error saving candles for {instrument_key}: {str(e)}")
            return 0


# Singleton instance
candle_service = CandleService()
