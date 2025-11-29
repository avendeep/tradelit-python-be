"""
Upstox authentication data models for MongoDB
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UpstoxTokenModel(BaseModel):
    """Model for storing Upstox access tokens in MongoDB"""

    id: str = Field(
        default="upstox_token", alias="_id"
    )  # Single document with fixed ID
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "upstox_token",
                "access_token": "eyJ0eXAiOiJKV1QiLCJr...",
                "token_type": "Bearer",
                "expires_in": 86400,
                "expires_at": "2025-11-20T17:55:27.192142",
                "created_at": "2025-11-19T17:55:27.192142",
                "updated_at": "2025-11-19T17:55:27.192142",
            }
        }


class CandleData(BaseModel):
    """Model for individual candle data point"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    oi: Optional[int] = 0

class DayWiseCandlesModel(BaseModel):
    """Model for storing intraday candles grouped by day"""
    
    id: str = Field(alias="_id") # Format: {instrument_key}_{date}
    instrument_key: str
    date: str # YYYY-MM-DD
    interval: str
    candles: list[CandleData]
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "NSE_INDEX|Nifty 50_2025-11-20",
                "instrument_key": "NSE_INDEX|Nifty 50",
                "date": "2025-11-20",
                "interval": "10minute",
                "candles": [
                    {
                        "timestamp": "2025-11-20T10:15:00",
                        "open": 19800.5,
                        "high": 19850.0,
                        "low": 19780.0,
                        "close": 19820.0,
                        "volume": 0,
                        "oi": 0
                    }
                ],
                "updated_at": "2025-11-20T10:16:00",
            }
        }


class IntradayCandleModel(BaseModel):
    """
    Legacy Model for storing intraday candle data
    Kept for backward compatibility if needed, but new data uses DayWiseCandlesModel
    """

    instrument_key: str
    interval: str  # e.g., "1minute", "10minute"
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    oi: Optional[int] = 0
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "instrument_key": "NSE_INDEX|Nifty 50",
                "interval": "10minute",
                "timestamp": "2025-11-20T10:15:00",
                "open": 19800.5,
                "high": 19850.0,
                "low": 19780.0,
                "close": 19820.0,
                "volume": 0,
                "oi": 0,
                "updated_at": "2025-11-20T10:16:00",
            }
        }


class CandleConfigurationModel(BaseModel):
    """Model for storing candle configuration"""

    id: str = Field(default="candle_config", alias="_id")
    interval: str = "10minute"  # Default interval
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "candle_config",
                "interval": "10minute",
                "updated_at": "2025-11-20T10:00:00",
            }
        }
