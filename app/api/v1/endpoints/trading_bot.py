"""
Trading Bot API endpoints
"""

from fastapi import APIRouter, HTTPException, status, Query, BackgroundTasks
from typing import Dict, Any

from app.schemas.trading_bot import (
    TradingBotResponse,
    TradingBotStatus,
    OIAnalysisResult,
)
from app.services.trading_bot import trading_bot_service
from app.db.mongodb import MongoDB

router = APIRouter(prefix="/trading-bot", tags=["Trading Bot"])


@router.post("/activate", response_model=TradingBotResponse)
async def activate_bot(
    lookback_minutes: int = Query(
        default=10,
        description="Number of minutes to look back for OI analysis",
        ge=1,
        le=60,
    )
):
    """
    Activate a trading bot for OI analysis

    This will start analyzing Open Interest changes for the instrument stored in the watchlist.
    The bot will analyze 3 strikes above and below the ATM strike every minute.

    **Note**: An instrument must be saved to the watchlist before activating the bot.
    Use the `/api/v1/option-chain/watchlist` endpoint to save an instrument.

    Args:
        lookback_minutes: Number of minutes to look back for OI analysis (default: 10)

    Returns:
        Bot activation confirmation and configuration
    """
    try:
        # Get instrument from watchlist
        collection = MongoDB.get_collection("instrument_watchlist")
        watchlist_entry = await collection.find_one({"is_active": True})

        if not watchlist_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active instrument found in watchlist. Please add an instrument to the watchlist first using /api/v1/option-chain/watchlist endpoint.",
            )

        instrument_key = watchlist_entry["instrument_key"]
        expiry_date = watchlist_entry["expiry_date"]

        # Generate bot ID based on instrument and expiry
        bot_id = f"oi_bot_{instrument_key.replace('|', '_')}_{expiry_date}"

        bot_data = await trading_bot_service.activate_bot(
            bot_id=bot_id,
            instrument_key=instrument_key,
            expiry_date=expiry_date,
            lookback_minutes=lookback_minutes,
        )

        return TradingBotResponse(
            status="success",
            message=f"Trading bot activated successfully for {instrument_key}",
            data=bot_data,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate bot: {str(e)}",
        )


@router.post("/deactivate/{bot_id}", response_model=TradingBotResponse)
async def deactivate_bot(bot_id: str):
    """
    Deactivate a trading bot

    This will stop the bot from analyzing OI changes.

    Args:
        bot_id: Unique identifier of the bot to deactivate

    Returns:
        Deactivation confirmation
    """
    try:
        result = await trading_bot_service.deactivate_bot(bot_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bot not found: {bot_id}",
            )

        return TradingBotResponse(
            status="success",
            message=f"Trading bot deactivated successfully",
            data={"bot_id": bot_id, "is_active": False},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate bot: {str(e)}",
        )


@router.get("/status/{bot_id}", response_model=TradingBotStatus)
async def get_bot_status(bot_id: str):
    """
    Get status of a trading bot

    Args:
        bot_id: Unique identifier of the bot

    Returns:
        Bot status including configuration and activity
    """
    try:
        bot_status = await trading_bot_service.get_bot_status(bot_id)

        if not bot_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bot not found: {bot_id}",
            )

        return bot_status

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get bot status: {str(e)}",
        )


@router.get("/list", response_model=TradingBotResponse)
async def list_active_bots():
    """
    List all active trading bots

    Returns:
        List of all active bots with their configurations
    """
    try:
        active_bots = await trading_bot_service.get_all_active_bots()

        return TradingBotResponse(
            status="success",
            message=f"Found {len(active_bots)} active bots",
            data={"active_bots": active_bots, "count": len(active_bots)},
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list active bots: {str(e)}",
        )


@router.post("/analyze/{bot_id}", response_model=OIAnalysisResult)
async def trigger_analysis(bot_id: str, background_tasks: BackgroundTasks):
    """
    Manually trigger OI analysis for a bot

    This endpoint allows you to trigger an immediate analysis without waiting
    for the scheduled task.

    Args:
        bot_id: Unique identifier of the bot
        background_tasks: FastAPI BackgroundTasks object

    Returns:
        OI analysis result
    """
    try:
        result = await trading_bot_service.analyze_oi_changes(bot_id, background_tasks=background_tasks)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bot not found or analysis failed: {bot_id}",
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze OI: {str(e)}",
        )
