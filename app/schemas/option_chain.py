"""
Pydantic schemas for Upstox Option Chain data
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date


class OptionChainRequest(BaseModel):
    """Request schema for option chain"""

    instrument_key: str = Field(
        ...,
        description="Key of underlying symbol (e.g., 'NSE_INDEX|Nifty 50')",
        examples=["NSE_INDEX|Nifty 50", "NSE_INDEX|Bank Nifty", "NSE_EQ|RELIANCE"],
    )
    expiry_date: str = Field(
        ...,
        description="Expiry date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        examples=["2024-03-28", "2024-04-25"],
    )


class OptionGreeks(BaseModel):
    """Option Greeks data"""

    vega: Optional[float] = None
    theta: Optional[float] = None
    gamma: Optional[float] = None
    delta: Optional[float] = None
    iv: Optional[float] = Field(None, description="Implied Volatility")


class MarketData(BaseModel):
    """Market data for option"""

    ltp: Optional[float] = Field(None, description="Last Traded Price")
    close_price: Optional[float] = None
    volume: Optional[int] = None
    oi: Optional[int] = Field(None, description="Open Interest")
    bid_price: Optional[float] = None
    bid_qty: Optional[int] = None
    ask_price: Optional[float] = None
    ask_qty: Optional[int] = None
    prev_oi: Optional[int] = Field(None, description="Previous Open Interest")


class OptionData(BaseModel):
    """Individual option data"""

    instrument_key: Optional[str] = None
    market_data: Optional[MarketData] = None
    option_greeks: Optional[OptionGreeks] = None
    strike_price: Optional[float] = None
    expiry: Optional[str] = None
    underlying_spot_price: Optional[float] = None
    underlying_key: Optional[str] = None
    call_options: Optional[Dict[str, Any]] = Field(
        None, description="Call option details"
    )
    put_options: Optional[Dict[str, Any]] = Field(
        None, description="Put option details"
    )


class OptionChainData(BaseModel):
    """Option chain strike data"""

    strike_price: float
    expiry: str
    underlying_spot_price: Optional[float] = None
    underlying_key: Optional[str] = None
    call_options: Optional[OptionData] = None
    put_options: Optional[OptionData] = None


class OptionChainResponse(BaseModel):
    """Response schema for option chain"""

    status: str = "success"
    data: List[OptionChainData] = Field(default_factory=list)


class OptionChainError(BaseModel):
    """Error response for option chain"""

    status: str = "error"
    message: str
    errors: Optional[List[Dict[str, Any]]] = None
