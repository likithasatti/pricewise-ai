import logging
from typing import Dict, List, Optional
from datetime import datetime
from app.models.schemas import PriceHistoryDTO, PricePointDTO
from app.database import (
    db_find_product_by_id,
    db_find_price_records,
    db_find_store_product_by_id
)
from app.services.ai_engine import ai_engine

logger = logging.getLogger(__name__)


class PriceHistoryService:

    def get_history(self, product_id: int) -> PriceHistoryDTO:
        product = db_find_product_by_id(product_id)
        if not product:
            raise ValueError(f"Product not found with ID: {product_id}")

        records = db_find_price_records(product_id)
        canonical_name = product.get("canonical_name") or product.get("product_name")

        dto = PriceHistoryDTO(
            productId=product_id,
            productName=canonical_name,
            totalRecords=len(records)
        )

        if not records:
            dto.priceTrend = "INSUFFICIENT_DATA"
            return dto

        lowest = float("inf")
        highest = float("-inf")
        total_sum = 0.0
        valid_count = 0
        points: List[PricePointDTO] = []
        store_series: Dict[str, List[PricePointDTO]] = {}
        last_checked_at: Optional[datetime] = None
        current_lowest: Optional[float] = None
        price_list: List[float] = []

        for pr in records:
            price = pr.get("price")
            if price is None or price <= 0:
                continue

            store = pr.get("store") or "MARKETPLACE"
            if price < lowest:
                lowest = price
            if price > highest:
                highest = price

            total_sum += price
            valid_count += 1
            current_lowest = price
            price_list.append(price)

            dt = None
            date_str = "Recent"
            if pr.get("checked_at"):
                try:
                    dt = datetime.fromisoformat(pr["checked_at"])
                    date_str = dt.strftime("%b %d")
                    if last_checked_at is None or dt > last_checked_at:
                        last_checked_at = dt
                except Exception:
                    pass

            pt = PricePointDTO(
                date=date_str,
                timestamp=dt,
                store=store,
                price=price,
                currency=pr.get("currency", "INR"),
                availability=pr.get("availability", "IN_STOCK"),
                source=pr.get("source"),
                status=pr.get("status", "SAMPLE_DATA")
            )

            points.append(pt)
            store_series.setdefault(store, []).append(pt)

        if valid_count == 0:
            dto.priceTrend = "INSUFFICIENT_DATA"
            return dto

        dto.lowestRecorded = lowest
        dto.highestRecorded = highest
        dto.averageRecorded = round(total_sum / valid_count, 2)
        dto.currentLowest = current_lowest
        dto.lastChecked = last_checked_at
        dto.totalRecords = valid_count
        dto.points = points
        dto.storeSeries = store_series

        # AI trend & volatility analysis
        ai_analysis = ai_engine.analyze_price_trends(price_list)
        dto.priceTrend = ai_analysis["trend"]
        dto.predictedTrend = f"{ai_analysis['trend']} (Next Est: ₹{ai_analysis['predicted_next']:,.0f})" if ai_analysis.get("predicted_next") else ai_analysis["trend"]
        dto.priceVolatilityScore = ai_analysis["volatility"]

        return dto


price_history_service = PriceHistoryService()
