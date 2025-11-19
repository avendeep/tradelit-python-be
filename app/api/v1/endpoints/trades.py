from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.schemas.trading import TradeCreate, TradeResponse
from app.services.trading import TradeService

router = APIRouter()


@router.post("/", response_model=TradeResponse, status_code=201)
async def create_trade(trade: TradeCreate):
    """Create a new trade"""
    try:
        trade_data = trade.dict()
        new_trade = await TradeService.create_trade(trade_data)
        return TradeResponse(
            id=str(new_trade.id),
            symbol=new_trade.symbol,
            side=new_trade.side,
            quantity=new_trade.quantity,
            price=new_trade.price,
            strategy_id=new_trade.strategy_id,
            timestamp=new_trade.timestamp,
            status=new_trade.status,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create trade: {str(e)}")


@router.get("/", response_model=List[TradeResponse])
async def get_trades(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
):
    """Get all trades with pagination"""
    try:
        trades = await TradeService.get_all_trades(skip=skip, limit=limit)
        return [
            TradeResponse(
                id=str(trade.id),
                symbol=trade.symbol,
                side=trade.side,
                quantity=trade.quantity,
                price=trade.price,
                strategy_id=trade.strategy_id,
                timestamp=trade.timestamp,
                status=trade.status,
            )
            for trade in trades
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trades: {str(e)}")


@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(trade_id: str):
    """Get a specific trade by ID"""
    try:
        trade = await TradeService.get_trade(trade_id)
        if not trade:
            raise HTTPException(status_code=404, detail="Trade not found")

        return TradeResponse(
            id=str(trade.id),
            symbol=trade.symbol,
            side=trade.side,
            quantity=trade.quantity,
            price=trade.price,
            strategy_id=trade.strategy_id,
            timestamp=trade.timestamp,
            status=trade.status,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trade: {str(e)}")


@router.patch("/{trade_id}/status")
async def update_trade_status(trade_id: str, status: str):
    """Update trade status"""
    try:
        valid_statuses = ["PENDING", "EXECUTED", "FAILED", "CANCELLED"]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
            )

        updated_trade = await TradeService.update_trade_status(trade_id, status)
        if not updated_trade:
            raise HTTPException(status_code=404, detail="Trade not found")

        return {
            "message": "Trade status updated successfully",
            "trade_id": trade_id,
            "status": status,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update trade status: {str(e)}"
        )
