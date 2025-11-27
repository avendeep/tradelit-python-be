"""
API endpoints for candle configuration
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel

from app.services.candle_service import candle_service

router = APIRouter()


class IntervalUpdate(BaseModel):
    interval: str


@router.get("/interval", response_model=dict)
async def get_candle_interval():
    """
    Get the current candle interval configuration
    """
    interval = await candle_service.get_interval()
    return {"interval": interval}


@router.post("/interval", response_model=dict)
async def set_candle_interval(update: IntervalUpdate):
    """
    Set the candle interval configuration
    """
    # Validate interval (basic validation, can be expanded based on Upstox supported intervals)
    valid_intervals = ["1minute", "3minute", "5minute", "10minute", "15minute", "30minute", "60minute", "day", "week", "month"]
    if update.interval not in valid_intervals:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid interval. Must be one of: {', '.join(valid_intervals)}"
        )

    success = await candle_service.set_interval(update.interval)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update interval")
        
    return {"status": "success", "interval": update.interval}
