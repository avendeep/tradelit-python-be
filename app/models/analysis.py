from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from bson import ObjectId
from app.models.trading import PyObjectId

class EODAnalysisModel(BaseModel):
    """Model for storing End-of-Day (EOD) Order Flow Analysis"""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "_id": "NSE_INDEX|Nifty 50_2025-11-20",
                "instrument_key": "NSE_INDEX|Nifty 50",
                "date": "2025-11-20",
                "daily_cumulative_delta": 15000.5,
                "updated_at": "2025-11-20T16:00:00",
            }
        },
    )

    id: str = Field(alias="_id") # Format: {instrument_key}_{date}
    instrument_key: str = Field(..., description="Instrument key")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    daily_cumulative_delta: float = Field(..., description="Daily cumulative delta")
    updated_at: datetime = Field(default_factory=datetime.now)


class EODAnalysisConfigModel(BaseModel):
    """Model for storing EOD Analysis Configuration"""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "_id": "eod_analysis_config",
                "instrument_key": "NSE_INDEX|Nifty 50",
                "expiry_date": "2025-12-26",
                "from_date": "2025-11-20",
                "to_date": "2025-11-29",
                "unit": "minute",
                "interval": "15",
                "updated_at": "2025-11-20T16:00:00",
            }
        },
    )

    id: str = Field(default="eod_analysis_config", alias="_id")
    instrument_key: str = Field(..., description="Instrument key")
    expiry_date: Optional[str] = Field(None, description="Expiry date in YYYY-MM-DD format")
    from_date: Optional[str] = Field(None, description="From date in YYYY-MM-DD format")
    to_date: Optional[str] = Field(None, description="To date in YYYY-MM-DD format")
    unit: str = Field(default="minute", description="Candle unit (minute, day, etc.)")
    interval: str = Field(default="15", description="Candle interval value")
    updated_at: datetime = Field(default_factory=datetime.now)
