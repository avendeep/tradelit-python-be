"""
Scheduled task to fetch option chain data from Upstox
Runs every minute and stores data in MongoDB
"""

import logging
from datetime import datetime
from typing import List, Dict, Any

from app.db.mongodb import MongoDB
from app.services.upstox_service import upstox_service
from app.models.trading import OptionChainSnapshotModel
from app.core.config import settings

logger = logging.getLogger(__name__)


async def fetch_option_chain_task():
    """
    Fetch option chain data for all active instruments in watchlist
    and store in database with timestamp (hour and minute only)
    """
    try:
        logger.info("🔄 Starting option chain fetch task...")

        # Check if Upstox token is valid
        if not upstox_service.is_token_valid():
            logger.warning("⚠️ Upstox token is not valid. Skipping option chain fetch.")
            return

        # Get all active watchlist entries
        watchlist_entries = await get_active_watchlist_entries()

        if not watchlist_entries:
            logger.info("ℹ️ No active watchlist entries found. Skipping fetch.")
            return

        logger.info(f"📋 Found {len(watchlist_entries)} active watchlist entries")

        # Get current timestamp without seconds
        current_timestamp = get_timestamp_without_seconds()

        # Fetch and store option chain data for each watchlist entry
        success_count = 0
        error_count = 0

        for entry in watchlist_entries:
            try:
                instrument_key = entry.get("instrument_key")
                expiry_date = entry.get("expiry_date")

                logger.info(
                    f"📊 Fetching option chain for {instrument_key} (Expiry: {expiry_date})"
                )

                # Fetch option chain data from Upstox
                option_chain_data = await upstox_service.get_option_chain(
                    instrument_key=instrument_key,
                    expiry_date=expiry_date,
                )

                if option_chain_data:
                    # Store snapshot in database
                    await save_option_chain_snapshot(
                        instrument_key=instrument_key,
                        expiry_date=expiry_date,
                        timestamp=current_timestamp,
                        data=option_chain_data,
                    )
                    success_count += 1
                    logger.info(f"✅ Saved option chain snapshot for {instrument_key}")
                else:
                    logger.warning(f"⚠️ No data returned for {instrument_key}")
                    error_count += 1

            except Exception as e:
                logger.error(
                    f"❌ Error fetching option chain for {entry.get('instrument_key')}: {str(e)}"
                )
                error_count += 1

        logger.info(
            f"✅ Option chain fetch task completed. Success: {success_count}, Errors: {error_count}"
        )

    except Exception as e:
        logger.error(f"❌ Error in fetch_option_chain_task: {str(e)}")


async def get_active_watchlist_entries() -> List[Dict[str, Any]]:
    """
    Get all active watchlist entries from database

    Returns:
        List of active watchlist entries
    """
    try:
        collection = MongoDB.get_collection("instrument_watchlist")
        cursor = collection.find({"is_active": True})
        entries = await cursor.to_list(length=None)
        return entries
    except Exception as e:
        logger.error(f"❌ Error fetching watchlist entries: {str(e)}")
        return []


def get_timestamp_without_seconds() -> datetime:
    """
    Get current timestamp in IST with seconds set to 0

    Returns:
        Datetime object in IST with seconds set to 0
    """
    now = settings.now_naive()  # Get current time in IST
    return now.replace(second=0, microsecond=0)


async def save_option_chain_snapshot(
    instrument_key: str,
    expiry_date: str,
    timestamp: datetime,
    data: Dict[str, Any],
) -> bool:
    """
    Save option chain snapshot to database

    Args:
        instrument_key: Instrument key (e.g., 'NSE_INDEX|Nifty 50')
        expiry_date: Expiry date in YYYY-MM-DD format
        timestamp: Timestamp of snapshot (without seconds)
        data: Complete option chain data

    Returns:
        True if saved successfully, False otherwise
    """
    try:
        collection = MongoDB.get_collection("option_chain_snapshots")

        # Create snapshot model
        snapshot = OptionChainSnapshotModel(
            instrument_key=instrument_key,
            expiry_date=expiry_date,
            timestamp=timestamp,
            data=data,
        )

        # Insert into database
        snapshot_dict = snapshot.model_dump(by_alias=True, exclude={"id"})
        result = await collection.insert_one(snapshot_dict)

        logger.debug(f"Inserted snapshot with ID: {result.inserted_id} at {timestamp}")
        return True

    except Exception as e:
        logger.error(f"❌ Error saving option chain snapshot: {str(e)}")
        return False
