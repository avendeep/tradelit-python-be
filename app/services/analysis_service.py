import logging
from datetime import datetime
from typing import Optional

from app.db.mongodb import MongoDB
from app.models.analysis import EODAnalysisModel, EODAnalysisConfigModel
from app.models.upstox import DayWiseCandlesModel
from app.services.upstox_service import upstox_service
from app.core.config import settings

logger = logging.getLogger(__name__)

class AnalysisService:
    """Service for performing trading analysis"""

    def __init__(self):
        self._analysis_collection = "eod_analysis"
        self._config_collection = "eod_analysis_config"
        self._candle_collection = "intraday_candles"

    async def save_analysis_config(
        self, 
        instrument_key: str,
        expiry_date: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        unit: str = "minute",
        interval: str = "15"
    ) -> bool:
        """
        Save or update the EOD analysis configuration.
        Only one configuration exists.
        """
        try:
            collection = MongoDB.get_collection(self._config_collection)
            
            config_model = EODAnalysisConfigModel(
                instrument_key=instrument_key,
                expiry_date=expiry_date,
                from_date=from_date,
                to_date=to_date,
                unit=unit,
                interval=interval,
                updated_at=settings.now_naive()
            )
            
            await collection.replace_one(
                {"_id": "eod_analysis_config"},
                config_model.model_dump(by_alias=True),
                upsert=True
            )
            
            logger.info(f"✅ Saved EOD analysis config: {instrument_key}, expiry: {expiry_date}, from: {from_date}, to: {to_date}, {interval}{unit}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving EOD analysis config: {str(e)}")
            return False

    async def get_analysis_config(self) -> Optional[dict]:
        """
        Get the current EOD analysis configuration.
        """
        try:
            collection = MongoDB.get_collection(self._config_collection)
            config = await collection.find_one({"_id": "eod_analysis_config"})
            return config
            
        except Exception as e:
            logger.error(f"❌ Error getting EOD analysis config: {str(e)}")
            return None

    async def calculate_daily_delta(
        self, 
        instrument_key: str, 
        from_date: str,
        to_date: str,
        unit: str = "minute",
        interval: str = "15"
    ) -> Optional[float]:
        """
        Calculate the daily cumulative delta for a given instrument and date range.
        Fetches historical candles from Upstox API.
        
        Formula:
        delta_bar_i = volume_i * ((close_i - open_i) / max(high_i - low_i, tiny))
        daily_cumulative_delta = Σ(delta_bar_i)
        """
        try:
            # 1. Construct interval string for UpstoxService
            if unit.endswith("s"):
                unit = unit[:-1]
                
            upstox_interval = f"{interval}{unit}"
            
            # 2. Fetch historical candles from Upstox API
            response = await upstox_service.get_historical_candles(instrument_key, upstox_interval, to_date, from_date)
            # print(response)
            if not response:
                logger.warning(f"No response from Upstox for {instrument_key}")
                return None
                
            if response.get("status") != "success":
                logger.warning(f"Upstox API returned non-success status for {instrument_key}: {response.get('status')}")
                return None
                
            if "data" not in response or "candles" not in response["data"]:
                logger.warning(f"Invalid response structure from Upstox for {instrument_key}")
                return None
                
            candles_data = response["data"]["candles"]
            
            if not candles_data:
                logger.warning(f"Empty candles list from Upstox for {instrument_key}")
                return None
            
            logger.info(f"✅ Received {len(candles_data)} candles from Upstox for {instrument_key}")
            
            # 3. Calculate delta for all candles
            daily_cumulative_delta = 0.0
            tiny = 0.1 # To avoid division by zero
            
            for candle in candles_data:
                # Candle format from Upstox: [timestamp, open, high, low, close, volume, oi]
                open_price = float(candle[1])
                high_price = float(candle[2])
                low_price = float(candle[3])
                close_price = float(candle[4])
                volume = int(candle[5])
                
                price_range = high_price - low_price
                denominator = max(price_range, tiny)
                
                delta_bar = volume * ((close_price - open_price) / denominator)
                daily_cumulative_delta += delta_bar

            # 4. Store the result
            analysis_collection = MongoDB.get_collection(self._analysis_collection)
            doc_id = f"{instrument_key}_{from_date}_{to_date}"
            
            analysis_model = EODAnalysisModel(
                _id=doc_id,
                instrument_key=instrument_key,
                date=f"{from_date} to {to_date}",
                daily_cumulative_delta=daily_cumulative_delta,
                updated_at=settings.now_naive()
            )
            
            await analysis_collection.replace_one(
                {"_id": doc_id},
                analysis_model.model_dump(by_alias=True),
                upsert=True
            )
            
            logger.info(f"✅ Calculated and saved EOD delta for {instrument_key} from {from_date} to {to_date}: {daily_cumulative_delta}")
            return daily_cumulative_delta

        except Exception as e:
            logger.error(f"❌ Error calculating daily delta for {instrument_key}: {str(e)}")
            return None

# Singleton instance
analysis_service = AnalysisService()
