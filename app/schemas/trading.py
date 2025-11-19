from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class TradeCreate(BaseModel):
    """Schema for creating a new trade"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "AAPL",
                "side": "BUY",
                "quantity": 100,
                "price": 150.50,
                "strategy_id": "momentum_strategy_1",
            }
        }
    )

    symbol: str = Field(..., description="Trading symbol")
    side: str = Field(..., description="BUY or SELL")
    quantity: float = Field(..., gt=0, description="Quantity to trade")
    price: float = Field(..., gt=0, description="Execution price")
    strategy_id: Optional[str] = Field(None, description="Strategy ID")


class TradeResponse(BaseModel):
    """Schema for trade response"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "symbol": "AAPL",
                "side": "BUY",
                "quantity": 100,
                "price": 150.50,
                "strategy_id": "momentum_strategy_1",
                "timestamp": "2025-11-10T10:30:00",
                "status": "EXECUTED",
            }
        }
    )

    id: str = Field(..., description="Trade ID")
    symbol: str
    side: str
    quantity: float
    price: float
    strategy_id: Optional[str]
    timestamp: datetime
    status: str


class StrategyCreate(BaseModel):
    """Schema for creating a new strategy"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Moving Average Crossover",
                "description": "SMA crossover strategy",
                "parameters": {"short_period": 10, "long_period": 50},
                "is_active": True,
            }
        }
    )

    name: str = Field(..., description="Strategy name")
    description: Optional[str] = Field(None, description="Strategy description")
    parameters: dict = Field(default_factory=dict, description="Strategy parameters")
    is_active: bool = Field(default=True, description="Strategy status")


class StrategyResponse(BaseModel):
    """Schema for strategy response"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "Moving Average Crossover",
                "description": "SMA crossover strategy",
                "parameters": {"short_period": 10, "long_period": 50},
                "is_active": True,
                "created_at": "2025-11-10T10:00:00",
                "updated_at": "2025-11-10T10:00:00",
            }
        }
    )

    id: str = Field(..., description="Strategy ID")
    name: str
    description: Optional[str]
    parameters: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PortfolioResponse(BaseModel):
    """Schema for portfolio response"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "user_id": "user_123",
                "positions": {"AAPL": 100, "GOOGL": 50},
                "cash_balance": 50000.00,
                "total_value": 75000.00,
                "updated_at": "2025-11-10T10:30:00",
            }
        }
    )

    id: str = Field(..., description="Portfolio ID")
    user_id: str
    positions: dict
    cash_balance: float
    total_value: float
    updated_at: datetime
