from pydantic import BaseModel, Field, ConfigDict, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic v2 models"""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.union_schema(
            [
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema(
                    [
                        core_schema.str_schema(),
                        core_schema.no_info_plain_validator_function(cls.validate),
                    ]
                ),
            ],
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {"type": "string"}


class TradeModel(BaseModel):
    """Database model for trades"""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "symbol": "AAPL",
                "side": "BUY",
                "quantity": 100,
                "price": 150.50,
                "strategy_id": "momentum_strategy_1",
                "status": "EXECUTED",
            }
        },
    )

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    symbol: str = Field(..., description="Trading symbol (e.g., AAPL, BTCUSD)")
    side: str = Field(..., description="Trade side: BUY or SELL")
    quantity: float = Field(..., description="Quantity traded")
    price: float = Field(..., description="Execution price")
    strategy_id: Optional[str] = Field(
        None, description="Strategy that generated this trade"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(
        default="PENDING", description="Trade status: PENDING, EXECUTED, FAILED"
    )


class StrategyModel(BaseModel):
    """Database model for trading strategies"""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "name": "Moving Average Crossover",
                "description": "Simple moving average crossover strategy",
                "parameters": {"short_period": 10, "long_period": 50},
                "is_active": True,
            }
        },
    )

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str = Field(..., description="Strategy name")
    description: Optional[str] = Field(None, description="Strategy description")
    parameters: dict = Field(default_factory=dict, description="Strategy parameters")
    is_active: bool = Field(default=True, description="Whether strategy is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PortfolioModel(BaseModel):
    """Database model for portfolio"""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "user_id": "user_123",
                "positions": {"AAPL": 100, "GOOGL": 50},
                "cash_balance": 50000.00,
                "total_value": 75000.00,
            }
        },
    )

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str = Field(..., description="User identifier")
    positions: dict = Field(
        default_factory=dict, description="Current positions {symbol: quantity}"
    )
    cash_balance: float = Field(default=0.0, description="Available cash balance")
    total_value: float = Field(default=0.0, description="Total portfolio value")
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class InstrumentWatchlistModel(BaseModel):
    """Database model for instrument watchlist"""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "instrument_key": "NSE_INDEX|Nifty 50",
                "expiry_date": "2024-03-28",
                "is_active": True,
            }
        },
    )

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    instrument_key: str = Field(
        ..., description="Key of underlying symbol (e.g., NSE_INDEX|Nifty 50)"
    )
    expiry_date: str = Field(..., description="Expiry date in YYYY-MM-DD format")
    is_active: bool = Field(
        default=True, description="Whether this watchlist entry is active"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class OptionChainSnapshotModel(BaseModel):
    """Database model for storing option chain snapshots"""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "instrument_key": "NSE_INDEX|Nifty 50",
                "expiry_date": "2024-03-28",
                "timestamp": "2024-03-20T10:15:00",
                "data": {},
            }
        },
    )

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    instrument_key: str = Field(
        ..., description="Key of underlying symbol (e.g., NSE_INDEX|Nifty 50)"
    )
    expiry_date: str = Field(..., description="Expiry date in YYYY-MM-DD format")
    timestamp: datetime = Field(
        ..., description="Timestamp of snapshot (without seconds, only hour and minute)"
    )
    data: dict = Field(..., description="Complete option chain data snapshot")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TradingBotModel(BaseModel):
    """Database model for trading bot configuration and state"""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "bot_id": "oi_analyzer_nifty",
                "is_active": True,
                "instrument_key": "NSE_INDEX|Nifty 50",
                "expiry_date": "2024-03-28",
                "lookback_minutes": 10,
            }
        },
    )

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    bot_id: str = Field(..., description="Unique identifier for the bot")
    is_active: bool = Field(default=False, description="Whether bot is active")
    instrument_key: str = Field(
        ..., description="Key of underlying symbol (e.g., NSE_INDEX|Nifty 50)"
    )
    expiry_date: str = Field(..., description="Expiry date in YYYY-MM-DD format")
    lookback_minutes: int = Field(
        default=10, description="Number of minutes to look back for OI analysis"
    )
    strikes_range: int = Field(
        default=3, description="Number of strikes above and below ATM to analyze"
    )
    activated_at: Optional[datetime] = Field(
        None, description="Timestamp when bot was activated"
    )
    deactivated_at: Optional[datetime] = Field(
        None, description="Timestamp when bot was deactivated"
    )
    last_analysis_at: Optional[datetime] = Field(
        None, description="Timestamp of last analysis"
    )
    total_analyses: int = Field(default=0, description="Total number of analyses run")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class OIAnalysisLogModel(BaseModel):
    """Database model for storing OI analysis results"""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "bot_id": "oi_analyzer_nifty",
                "instrument_key": "NSE_INDEX|Nifty 50",
                "expiry_date": "2024-03-28",
                "analysis_result": {},
            }
        },
    )

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    bot_id: str = Field(..., description="Bot that performed this analysis")
    instrument_key: str = Field(
        ..., description="Key of underlying symbol (e.g., NSE_INDEX|Nifty 50)"
    )
    expiry_date: str = Field(..., description="Expiry date in YYYY-MM-DD format")
    timestamp: datetime = Field(..., description="Timestamp of analysis")
    atm_strike: float = Field(..., description="ATM strike price at time of analysis")
    spot_price: Optional[float] = Field(
        None, description="Spot price at time of analysis"
    )
    analysis_result: dict = Field(..., description="Complete analysis result")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DailySignalCountModel(BaseModel):
    """Database model for storing daily signal counts"""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "date": "2024-03-20",
                "instrument_key": "NSE_INDEX|Nifty 50",
                "bullish_push_count": 5,
                "bullish_accumulation_count": 2,
                "bearish_push_count": 3,
                "bearish_accumulation_count": 1,
            }
        },
    )

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    date: str = Field(..., description="Date of the count (YYYY-MM-DD)")
    instrument_key: str = Field(..., description="Instrument Key")
    bullish_push_count: int = Field(default=0, description="Count of Bullish Push signals")
    bullish_accumulation_count: int = Field(default=0, description="Count of Bullish Accumulation signals")
    bearish_push_count: int = Field(default=0, description="Count of Bearish Push signals")
    bearish_accumulation_count: int = Field(default=0, description="Count of Bearish Accumulation signals")
    last_updated_at: datetime = Field(default_factory=datetime.utcnow)
