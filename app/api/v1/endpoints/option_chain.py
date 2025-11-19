"""
Option Chain API endpoints
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional

from app.schemas.option_chain import (
    OptionChainRequest,
    OptionChainResponse,
    OptionChainError,
)
from app.services.upstox_service import upstox_service


router = APIRouter(prefix="/option-chain", tags=["Option Chain"])


@router.get("", response_model=OptionChainResponse)
async def get_option_chain(
    instrument_key: str = Query(
        ...,
        description="Key of underlying symbol",
        examples=["NSE_INDEX|Nifty 50"],
    ),
    expiry_date: str = Query(
        ...,
        description="Expiry date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        examples=["2024-03-28"],
    ),
):
    """
    Get put/call option chain for an underlying symbol

    Retrieves complete option chain data including:
    - Strike prices
    - Call and Put options
    - Market data (LTP, Volume, OI)
    - Option Greeks (Delta, Gamma, Vega, Theta, IV)

    **Authentication Required**: Bearer token in Authorization header

    **Supported Exchanges**: NSE (Index and Equity), BSE

    **Example instrument_keys**:
    - `NSE_INDEX|Nifty 50`
    - `NSE_INDEX|Bank Nifty`
    - `NSE_EQ|RELIANCE`
    - `NSE_EQ|TCS`

    **Note**: MCX Exchange option chains are not currently available.
    """
    if not upstox_service.is_token_valid():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please login first.",
        )

    try:
        # Fetch option chain from Upstox API
        option_chain_data = await upstox_service.get_option_chain(
            instrument_key=instrument_key,
            expiry_date=expiry_date,
        )

        if not option_chain_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch option chain data",
            )

        return option_chain_data

    except Exception as e:
        error_message = str(e)

        # Handle specific error cases
        if "Not authenticated" in error_message:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_message,
            )
        elif "Invalid" in error_message or "not found" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid request: {error_message}",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch option chain: {error_message}",
            )


# @router.post("", response_model=OptionChainResponse)
# async def get_option_chain_post(request: OptionChainRequest):
#     """
#     Get put/call option chain (POST method)

#     Alternative endpoint using POST method for fetching option chain data.
#     Useful for programmatic access with request body validation.

#     **Authentication Required**: Bearer token in Authorization header
#     """
#     return await get_option_chain(
#         instrument_key=request.instrument_key,
#         expiry_date=request.expiry_date,
#     )


# @router.get("/instruments", response_model=dict)
# async def get_popular_instruments():
#     """
#     Get list of popular instruments for option chain

#     Returns commonly traded instruments with their keys.
#     Useful for UI dropdown menus and quick access.
#     """
#     return {
#         "status": "success",
#         "data": {
#             "indices": [
#                 {
#                     "name": "Nifty 50",
#                     "instrument_key": "NSE_INDEX|Nifty 50",
#                     "exchange": "NSE",
#                 },
#                 {
#                     "name": "Bank Nifty",
#                     "instrument_key": "NSE_INDEX|Bank Nifty",
#                     "exchange": "NSE",
#                 },
#                 {
#                     "name": "Fin Nifty",
#                     "instrument_key": "NSE_INDEX|Nifty Fin Service",
#                     "exchange": "NSE",
#                 },
#                 {
#                     "name": "Sensex",
#                     "instrument_key": "BSE_INDEX|Sensex",
#                     "exchange": "BSE",
#                 },
#             ],
#             "stocks": [
#                 {
#                     "name": "Reliance Industries",
#                     "instrument_key": "NSE_EQ|RELIANCE",
#                     "exchange": "NSE",
#                 },
#                 {
#                     "name": "TCS",
#                     "instrument_key": "NSE_EQ|TCS",
#                     "exchange": "NSE",
#                 },
#                 {
#                     "name": "HDFC Bank",
#                     "instrument_key": "NSE_EQ|HDFCBANK",
#                     "exchange": "NSE",
#                 },
#                 {
#                     "name": "Infosys",
#                     "instrument_key": "NSE_EQ|INFY",
#                     "exchange": "NSE",
#                 },
#             ],
#         },
#     }
