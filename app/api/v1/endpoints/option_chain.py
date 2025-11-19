"""
Option Chain API endpoints
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional, List
from datetime import datetime

from app.schemas.option_chain import (
    OptionChainRequest,
    OptionChainResponse,
    OptionChainError,
)
from app.schemas.trading import InstrumentWatchlistCreate, InstrumentWatchlistResponse
from app.models.trading import InstrumentWatchlistModel
from app.services.upstox_service import upstox_service
from app.db.mongodb import MongoDB


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


@router.post(
    "/watchlist",
    response_model=InstrumentWatchlistResponse,
    status_code=status.HTTP_201_CREATED,
)
async def save_instrument_watchlist(request: InstrumentWatchlistCreate):
    """
    Save instrument key and expiry date to watchlist

    Stores instrument information in the database for quick access.
    Use this to maintain a list of frequently monitored instruments.

    **Example Request Body**:
    ```json
    {
        "instrument_key": "NSE_INDEX|Nifty 50",
        "expiry_date": "2024-03-28"
    }
    ```

    **Returns**: Created watchlist entry with ID and timestamps
    """
    try:
        # Create watchlist model instance
        watchlist_entry = InstrumentWatchlistModel(
            instrument_key=request.instrument_key,
            expiry_date=request.expiry_date,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Get database collection
        collection = MongoDB.get_collection("instrument_watchlist")

        # Insert into database
        result = await collection.insert_one(
            watchlist_entry.model_dump(by_alias=True, exclude={"id"})
        )

        # Fetch the created document
        created_entry = await collection.find_one({"_id": result.inserted_id})

        if not created_entry:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created watchlist entry",
            )

        # Convert ObjectId to string for response
        created_entry["id"] = str(created_entry["_id"])
        del created_entry["_id"]

        return InstrumentWatchlistResponse(**created_entry)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save watchlist entry: {str(e)}",
        )


@router.get("/watchlist", response_model=List[InstrumentWatchlistResponse])
async def get_instrument_watchlist(
    is_active: Optional[bool] = Query(None, description="Filter by active status")
):
    """
    Get all saved instrument watchlist entries

    Retrieves all instruments that have been saved to the watchlist.
    Optionally filter by active status.

    **Query Parameters**:
    - `is_active`: Filter by active status (true/false). If not provided, returns all entries.

    **Returns**: List of watchlist entries
    """
    try:
        # Get database collection
        collection = MongoDB.get_collection("instrument_watchlist")

        # Build query filter
        query_filter = {}
        if is_active is not None:
            query_filter["is_active"] = is_active

        # Fetch watchlist entries
        cursor = collection.find(query_filter).sort("created_at", -1)
        entries = await cursor.to_list(length=None)

        # Convert ObjectId to string for each entry
        result = []
        for entry in entries:
            entry["id"] = str(entry["_id"])
            del entry["_id"]
            result.append(InstrumentWatchlistResponse(**entry))

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch watchlist entries: {str(e)}",
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
