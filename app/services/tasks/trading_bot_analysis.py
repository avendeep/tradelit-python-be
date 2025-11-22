"""
Scheduled task to run trading bot OI analysis
Runs every minute for all active bots
"""

import logging
from app.services.trading_bot import trading_bot_service

logger = logging.getLogger(__name__)


async def trading_bot_analysis_task():
    """
    Run OI analysis for all active trading bots
    Executed every minute by the scheduler
    """
    try:
        logger.info("🤖 Starting trading bot analysis task...")

        # Get all active bots
        active_bots = await trading_bot_service.get_all_active_bots()

        if not active_bots:
            logger.info("ℹ️ No active trading bots found. Skipping analysis.")
            return

        logger.info(f"📋 Found {len(active_bots)} active trading bot(s)")

        # Analyze OI changes for each active bot
        success_count = 0
        error_count = 0

        for bot in active_bots:
            try:
                bot_id = bot.get("bot_id")
                instrument_key = bot.get("instrument_key")

                logger.info(f"🔍 Analyzing bot: {bot_id} ({instrument_key})")

                # Run OI analysis
                result = await trading_bot_service.analyze_oi_changes(bot_id)

                if result:
                    success_count += 1
                    logger.info(
                        f"✅ Analysis complete for {bot_id} | "
                        f"Signal: {result.signal} | "
                        f"ATM: {result.atm_strike} | "
                        f"Call OI Δ: {result.total_call_oi_change:+,} | "
                        f"Put OI Δ: {result.total_put_oi_change:+,}"
                    )
                else:
                    logger.warning(f"⚠️ No analysis result for bot: {bot_id}")
                    error_count += 1

            except Exception as e:
                logger.error(f"❌ Error analyzing bot {bot.get('bot_id')}: {str(e)}")
                error_count += 1

        logger.info(
            f"✅ Trading bot analysis task completed. "
            f"Success: {success_count}, Errors: {error_count}"
        )

    except Exception as e:
        logger.error(f"❌ Error in trading_bot_analysis_task: {str(e)}")
