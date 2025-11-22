"""
Pydantic schemas for Trading Bot
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime


class TradingBotConfig(BaseModel):
    """Configuration for trading bot"""

    instrument_key: str = Field(
        ...,
        description="Key of underlying symbol (e.g., 'NSE_INDEX|Nifty 50')",
        examples=["NSE_INDEX|Nifty 50", "NSE_INDEX|Bank Nifty"],
    )
    expiry_date: str = Field(
        ...,
        description="Expiry date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        examples=["2024-03-28", "2024-04-25"],
    )
    lookback_minutes: int = Field(
        default=10,
        description="Number of minutes to look back for OI analysis",
        ge=1,
        le=60,
    )
    analysis_interval_seconds: int = Field(
        default=60,
        description="Interval in seconds to analyze OI changes",
        ge=30,
        le=300,
    )


class TradingBotActivateRequest(BaseModel):
    """Request to activate trading bot"""

    instrument_key: str = Field(
        ...,
        description="Key of underlying symbol (e.g., 'NSE_INDEX|Nifty 50')",
    )
    expiry_date: str = Field(
        ...,
        description="Expiry date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    lookback_minutes: int = Field(
        default=10,
        description="Number of minutes to look back for OI analysis",
        ge=1,
        le=60,
    )


class StrikeOIAnalysis(BaseModel):
    """OI analysis for a single strike price"""

    strike_price: float
    call_oi_current: Optional[int] = None
    call_oi_previous: Optional[int] = None
    call_oi_change: Optional[int] = None
    call_oi_change_percent: Optional[float] = None
    put_oi_current: Optional[int] = None
    put_oi_previous: Optional[int] = None
    put_oi_change: Optional[int] = None
    put_oi_change_percent: Optional[float] = None


class OIAnalysisResult(BaseModel):
    """Result of OI analysis"""

    timestamp: datetime
    instrument_key: str
    expiry_date: str
    atm_strike: float
    spot_price: Optional[float] = None
    strikes_analyzed: List[StrikeOIAnalysis]
    analysis_period_minutes: int
    total_call_oi_change: int = 0
    total_put_oi_change: int = 0
    pcr_oi: Optional[float] = Field(None, description="Put-Call Ratio based on OI")
    signal: Optional[str] = Field(
        None,
        description="Trading signal: BULLISH, BEARISH, NEUTRAL",
    )


class TradingBotStatus(BaseModel):
    """Status of trading bot"""

    bot_id: str
    is_active: bool
    instrument_key: str
    expiry_date: str
    lookback_minutes: int
    activated_at: Optional[datetime] = None
    last_analysis_at: Optional[datetime] = None
    total_analyses: int = 0


class TradingBotResponse(BaseModel):
    """Response for trading bot operations"""

    status: str = "success"
    message: str
    data: Optional[Dict[str, Any]] = None
