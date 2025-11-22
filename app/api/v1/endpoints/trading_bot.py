"""
Trading Bot API endpoints
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from app.schemas.trading_bot import (
    TradingBotActivateRequest,
    TradingBotResponse,
    TradingBotStatus,
    OIAnalysisResult,
)
from app.services.trading_bot import trading_bot_service

router = APIRouter(prefix="/trading-bot", tags=["Trading Bot"])


@router.post("/activate", response_model=TradingBotResponse)
async def activate_bot(request: TradingBotActivateRequest):
    """
    Activate a trading bot for OI analysis

    This will start analyzing Open Interest changes for the specified instrument.
    The bot will analyze 3 strikes above and below the ATM strike every minute.

    Args:
        request: Bot activation request with instrument details

    Returns:
        Bot activation confirmation and configuration
    """
    try:
        # Generate bot ID based on instrument and expiry
        bot_id = (
            f"oi_bot_{request.instrument_key.replace('|', '_')}_{request.expiry_date}"
        )

        bot_data = await trading_bot_service.activate_bot(
            bot_id=bot_id,
            instrument_key=request.instrument_key,
            expiry_date=request.expiry_date,
            lookback_minutes=request.lookback_minutes,
        )

        return TradingBotResponse(
            status="success",
            message=f"Trading bot activated successfully",
            data=bot_data,
        )

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
async def trigger_analysis(bot_id: str):
    """
    Manually trigger OI analysis for a bot

    This endpoint allows you to trigger an immediate analysis without waiting
    for the scheduled task.

    Args:
        bot_id: Unique identifier of the bot

    Returns:
        OI analysis result
    """
    try:
        result = await trading_bot_service.analyze_oi_changes(bot_id)

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
