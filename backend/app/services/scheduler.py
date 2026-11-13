import asyncio
import logging
from datetime import datetime
from app.config import settings
from app.database import db_find_all_active_tracked, db_save_tracked_product, db_find_store_product_by_id

logger = logging.getLogger(__name__)


async def background_tracking_loop():
    if not settings.TRACKING_ENABLED:
        logger.info("Price tracking scheduler is disabled in settings.")
        return

    interval_sec = max(10, settings.TRACKING_INTERVAL_MS // 1000)
    logger.info(f"Price tracking scheduler started (running every {interval_sec} seconds).")

    while True:
        try:
            await asyncio.sleep(interval_sec)
            active_items = db_find_all_active_tracked()
            if active_items:
                logger.info(f"Tracking scheduler checking {len(active_items)} active tracked items...")
                for item in active_items:
                    sp = db_find_store_product_by_id(item["store_product_id"])
                    if sp and sp.get("current_price"):
                        curr = sp["current_price"]
                        target = item.get("target_price")
                        if target and curr <= target:
                            logger.info(f"Price drop detected for tracked item #{item['id']}! Price: ₹{curr} <= Target: ₹{target}")
                            # Record notification timestamp
                            db_save_tracked_product({
                                "id": item["id"],
                                "last_checked_at": datetime.now().isoformat(),
                                "last_notified_price": curr,
                                "target_price": item.get("target_price"),
                                "target_drop_percentage": item.get("target_drop_percentage"),
                                "user_email": item.get("user_email"),
                                "active": True
                            })
        except asyncio.CancelledError:
            logger.info("Price tracking background loop stopped.")
            break
        except Exception as e:
            logger.error(f"Error in price tracking loop: {str(e)}")
