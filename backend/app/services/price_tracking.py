import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status
from app.models.schemas import TrackedProductDTO, TrackingRequestDTO
from app.database import (
    db_find_store_product_by_id,
    db_find_tracked_products,
    db_find_tracked_product_by_id,
    db_find_active_tracked,
    db_save_tracked_product,
    db_stop_tracking,
    db_find_product_by_id
)

logger = logging.getLogger(__name__)


class PriceTrackingService:

    def track_product(self, req: TrackingRequestDTO, user_id: str) -> TrackedProductDTO:
        if not user_id or not user_id.strip():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authenticated user ID is required")

        safe_uid = user_id.strip()
        sp = db_find_store_product_by_id(req.storeProductId)
        if not sp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Store product not found: {req.storeProductId}")

        current_price = sp.get("current_price")
        target_price = req.targetPrice
        if target_price is None and current_price:
            target_price = round(current_price * 0.95, 2)  # 5% drop default

        existing = db_find_active_tracked(req.storeProductId, safe_uid)
        if existing:
            tid = db_save_tracked_product({
                "id": existing["id"],
                "target_price": target_price,
                "target_drop_percentage": req.targetDropPercentage or 5.0,
                "user_email": req.userEmail or existing.get("user_email"),
                "active": True
            })
            tracked = db_find_tracked_product_by_id(tid)
        else:
            tid = db_save_tracked_product({
                "store_product_id": sp["id"],
                "product_id": sp.get("product_id"),
                "user_id": safe_uid,
                "user_email": req.userEmail,
                "initial_price": current_price,
                "target_price": target_price,
                "target_drop_percentage": req.targetDropPercentage or 5.0,
                "active": True
            })
            tracked = db_find_tracked_product_by_id(tid)

        logger.info(f"User [{safe_uid}] tracking store product [{sp.get('title')}] (Target: ₹{target_price})")
        return self._to_dto(tracked)

    def get_tracked_products(self, user_id: str) -> List[TrackedProductDTO]:
        if not user_id or not user_id.strip():
            return []
        rows = db_find_tracked_products(user_id.strip())
        return [self._to_dto(r) for r in rows]

    def get_tracked_product(self, tracked_id: int, user_id: str) -> TrackedProductDTO:
        row = db_find_tracked_product_by_id(tracked_id)
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracked product not found")
        if user_id and row.get("user_id") != user_id.strip():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracked product not found")
        return self._to_dto(row)

    def stop_tracking(self, tracked_id: int, user_id: str):
        row = db_find_tracked_product_by_id(tracked_id)
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracked product not found")
        if user_id and row.get("user_id") != user_id.strip():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracked product not found")
        db_stop_tracking(tracked_id)
        logger.info(f"User [{user_id}] stopped tracking item ID: {tracked_id}")

    def check_price_now(self, tracked_id: int, user_id: str) -> TrackedProductDTO:
        row = db_find_tracked_product_by_id(tracked_id)
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracked product not found")
        if user_id and row.get("user_id") != user_id.strip():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracked product not found")

        # Update last_checked_at
        db_save_tracked_product({
            "id": tracked_id,
            "last_checked_at": datetime.now().isoformat(),
            "target_price": row.get("target_price"),
            "target_drop_percentage": row.get("target_drop_percentage"),
            "user_email": row.get("user_email"),
            "active": True
        })
        updated = db_find_tracked_product_by_id(tracked_id)
        return self._to_dto(updated)

    def _to_dto(self, row: Dict[str, Any]) -> TrackedProductDTO:
        initial_price = row.get("initial_price")
        current_price = row.get("current_price")

        price_drop = None
        drop_percentage = None
        if initial_price and current_price:
            diff = initial_price - current_price
            price_drop = round(diff, 2)
            if initial_price > 0:
                drop_percentage = round((diff / initial_price) * 100, 1)

        last_checked = None
        if row.get("last_checked_at"):
            try:
                last_checked = datetime.fromisoformat(row["last_checked_at"])
            except Exception:
                pass

        created_at = None
        if row.get("created_at"):
            try:
                created_at = datetime.fromisoformat(row["created_at"])
            except Exception:
                pass

        return TrackedProductDTO(
            id=row.get("id"),
            storeProductId=row.get("store_product_id"),
            productId=row.get("p_id") or row.get("product_id"),
            productName=row.get("canonical_name") or row.get("sp_title") or "Tracked Product",
            store=row.get("store"),
            imageUrl=row.get("sp_image") or row.get("p_image"),
            productUrl=row.get("product_url"),
            currentPrice=current_price,
            initialPrice=initial_price,
            targetPrice=row.get("target_price"),
            targetDropPercentage=row.get("target_drop_percentage"),
            lastNotifiedPrice=row.get("last_notified_price"),
            priceDrop=price_drop,
            dropPercentage=drop_percentage,
            lastCheckedAt=last_checked,
            createdAt=created_at,
            active=bool(row.get("active", 1)),
            userEmail=row.get("user_email")
        )


price_tracking_service = PriceTrackingService()
