from fastapi import APIRouter
from app.api.v1.endpoints import (
    trades,
    strategies,
    portfolio,
    upstox,
    option_chain,
    trading_bot,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(trades.router, prefix="/trades", tags=["Trades"])
api_router.include_router(strategies.router, prefix="/strategies", tags=["Strategies"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])
api_router.include_router(upstox.router)  # Upstox auth endpoints
api_router.include_router(option_chain.router)  # Option chain endpoints
api_router.include_router(trading_bot.router)  # Trading bot endpoints
