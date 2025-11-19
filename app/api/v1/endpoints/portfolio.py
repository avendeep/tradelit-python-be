from fastapi import APIRouter, HTTPException
from app.schemas.trading import PortfolioResponse
from app.services.trading import PortfolioService

router = APIRouter()


@router.get("/{user_id}", response_model=PortfolioResponse)
async def get_portfolio(user_id: str):
    """Get portfolio for a specific user"""
    try:
        portfolio = await PortfolioService.get_portfolio(user_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        return PortfolioResponse(
            id=str(portfolio.id),
            user_id=portfolio.user_id,
            positions=portfolio.positions,
            cash_balance=portfolio.cash_balance,
            total_value=portfolio.total_value,
            updated_at=portfolio.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch portfolio: {str(e)}"
        )


@router.post("/{user_id}")
async def update_portfolio(user_id: str, portfolio_data: dict):
    """Create or update portfolio for a user"""
    try:
        portfolio = await PortfolioService.create_or_update_portfolio(
            user_id, portfolio_data
        )
        return PortfolioResponse(
            id=str(portfolio.id),
            user_id=portfolio.user_id,
            positions=portfolio.positions,
            cash_balance=portfolio.cash_balance,
            total_value=portfolio.total_value,
            updated_at=portfolio.updated_at,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update portfolio: {str(e)}"
        )
