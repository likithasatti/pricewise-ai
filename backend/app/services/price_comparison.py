import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.models.schemas import PriceComparisonDTO, StorePriceDTO
from app.database import (
    db_find_store_products,
    db_find_price_records,
    db_save_store_product,
    db_save_price_record
)
from app.providers.manager import provider_manager
from app.services.ai_engine import ai_engine

logger = logging.getLogger(__name__)


class PriceComparisonService:

    async def compare_prices(self, product: Dict[str, Any]) -> PriceComparisonDTO:
        product_id = product.get("id")
        canonical_name = product.get("canonical_name") or product.get("product_name")

        # 1. Fetch persistent store listings
        raw_sps = db_find_store_products(product_id) if product_id else []
        store_products = [
            sp for sp in raw_sps
            if sp.get("store") in ("AMAZON", "FLIPKART")
        ]

        store_dtos: List[StorePriceDTO] = []
        min_price: Optional[float] = None
        max_price: Optional[float] = None
        total_sum = 0.0
        valid_store_count = 0
        best_store_name: Optional[str] = None

        for sp in store_products:
            price = sp.get("current_price")
            is_valid = price is not None and price > 0 and sp.get("availability") != "UNAVAILABLE"

            if is_valid:
                if min_price is None or price < min_price:
                    min_price = price
                    best_store_name = sp.get("store")
                if max_price is None or price > max_price:
                    max_price = price
                total_sum += price
                valid_store_count += 1

            last_checked = None
            if sp.get("last_checked_at"):
                try:
                    last_checked = datetime.fromisoformat(sp["last_checked_at"])
                except Exception:
                    pass

            store_dtos.append(StorePriceDTO(
                id=sp.get("id"),
                store=sp.get("store"),
                title=sp.get("title"),
                price=price,
                currency=sp.get("currency", "INR"),
                availability=sp.get("availability", "IN_STOCK"),
                productUrl=sp.get("product_url"),
                imageUrl=sp.get("image_url") or product.get("image_url"),
                status=sp.get("status", "LIVE"),
                lastCheckedAt=last_checked,
                isLowest=False
            ))

        # Check if Amazon or Flipkart are missing
        has_amazon = any(s.store == "AMAZON" and s.price and s.price > 0 for s in store_dtos)
        has_flipkart = any(s.store == "FLIPKART" and s.price and s.price > 0 for s in store_dtos)

        amz_provider = provider_manager.get_provider("AMAZON")
        flp_provider = provider_manager.get_provider("FLIPKART")

        # Live on-demand query if one store is missing and provider is configured
        search_target = ai_engine.clean_product_title(canonical_name)

        if not has_flipkart and flp_provider and flp_provider.is_configured() and product_id:
            try:
                flp_items = await flp_provider.search_products(search_target)
                match = next((item for item in flp_items if ai_engine.is_token_match(canonical_name, item.title) and item.price), None)
                if match:
                    new_sp_id = db_save_store_product({
                        "product_id": product_id,
                        "store": "FLIPKART",
                        "store_product_id": match.storeProductId,
                        "title": match.title,
                        "product_url": match.productUrl,
                        "current_price": match.price,
                        "currency": match.currency,
                        "availability": match.availability,
                        "status": match.status,
                        "image_url": match.imageUrl or product.get("image_url")
                    })
                    db_save_price_record({
                        "store_product_id": new_sp_id,
                        "product_id": product_id,
                        "store": "FLIPKART",
                        "price": match.price,
                        "currency": match.currency,
                        "availability": match.availability,
                        "status": match.status,
                        "source": "LIVE_FETCH"
                    })
                    has_flipkart = True
                    price = match.price
                    if min_price is None or price < min_price:
                        min_price = price
                        best_store_name = "FLIPKART"
                    if max_price is None or price > max_price:
                        max_price = price
                    total_sum += price
                    valid_store_count += 1

                    store_dtos.append(StorePriceDTO(
                        id=new_sp_id,
                        store="FLIPKART",
                        title=match.title,
                        price=match.price,
                        currency=match.currency,
                        availability=match.availability,
                        productUrl=match.productUrl,
                        imageUrl=match.imageUrl or product.get("image_url"),
                        status=match.status,
                        lastCheckedAt=datetime.now(),
                        isLowest=False
                    ))
            except Exception as e:
                logger.debug(f"On-demand Flipkart query failed: {e}")

        if not has_amazon and amz_provider and amz_provider.is_configured() and product_id:
            try:
                amz_items = await amz_provider.search_products(search_target)
                match = next((item for item in amz_items if ai_engine.is_token_match(canonical_name, item.title) and item.price), None)
                if match:
                    new_sp_id = db_save_store_product({
                        "product_id": product_id,
                        "store": "AMAZON",
                        "store_product_id": match.storeProductId,
                        "title": match.title,
                        "product_url": match.productUrl,
                        "current_price": match.price,
                        "currency": match.currency,
                        "availability": match.availability,
                        "status": match.status,
                        "image_url": match.imageUrl or product.get("image_url")
                    })
                    db_save_price_record({
                        "store_product_id": new_sp_id,
                        "product_id": product_id,
                        "store": "AMAZON",
                        "price": match.price,
                        "currency": match.currency,
                        "availability": match.availability,
                        "status": match.status,
                        "source": "LIVE_FETCH"
                    })
                    has_amazon = True
                    price = match.price
                    if min_price is None or price < min_price:
                        min_price = price
                        best_store_name = "AMAZON"
                    if max_price is None or price > max_price:
                        max_price = price
                    total_sum += price
                    valid_store_count += 1

                    store_dtos.append(StorePriceDTO(
                        id=new_sp_id,
                        store="AMAZON",
                        title=match.title,
                        price=match.price,
                        currency=match.currency,
                        availability=match.availability,
                        productUrl=match.productUrl,
                        imageUrl=match.imageUrl or product.get("image_url"),
                        status=match.status,
                        lastCheckedAt=datetime.now(),
                        isLowest=False
                    ))
            except Exception as e:
                logger.debug(f"On-demand Amazon query failed: {e}")

        # Add honest unavailable/config_required placeholders if not present
        if not has_amazon:
            cfg = amz_provider and amz_provider.is_configured()
            store_dtos.append(StorePriceDTO(
                store="AMAZON",
                title="Amazon (No matching offer)" if cfg else "Amazon (API Key Required)",
                price=None,
                currency="INR",
                availability="UNAVAILABLE",
                productUrl=None,
                imageUrl=product.get("image_url"),
                status="UNAVAILABLE" if cfg else "CONFIG_REQUIRED",
                isLowest=False
            ))

        if not has_flipkart:
            cfg = flp_provider and flp_provider.is_configured()
            store_dtos.append(StorePriceDTO(
                store="FLIPKART",
                title="Flipkart (No matching offer)" if cfg else "Flipkart (API Key Required)",
                price=None,
                currency="INR",
                availability="UNAVAILABLE",
                productUrl=None,
                imageUrl=product.get("image_url"),
                status="UNAVAILABLE" if cfg else "CONFIG_REQUIRED",
                isLowest=False
            ))

        # Mark lowest store listing
        if min_price is not None:
            for s in store_dtos:
                s.isLowest = (s.price is not None and abs(s.price - min_price) < 0.01)

        # Sort: lowest price first, unavailable at the end
        store_dtos.sort(key=lambda s: s.price if s.price is not None else float("inf"))

        # Calculate averages and savings
        savings_amount: Optional[float] = None
        savings_pct: Optional[float] = None
        avg_price: Optional[float] = None

        if valid_store_count > 0:
            avg_price = round(total_sum / valid_store_count, 2)
            if valid_store_count >= 2 and max_price and min_price and max_price > min_price:
                diff = round(max_price - min_price, 2)
                pct = round((diff / max_price) * 100, 1)
                savings_amount = diff
                savings_pct = pct

        # Historical prices for AI analysis
        price_records = db_find_price_records(product_id) if product_id else []
        hist_prices = [r["price"] for r in price_records if r.get("price")]

        trend_summary, recommendation, deal_score = await ai_engine.generate_smart_insight(
            canonical_name,
            min_price,
            best_store_name,
            savings_amount,
            savings_pct,
            hist_prices
        )

        return PriceComparisonDTO(
            productId=product_id,
            productName=canonical_name,
            brand=product.get("brand"),
            category=product.get("category"),
            description=product.get("description"),
            imageUrl=product.get("image_url"),
            rating=product.get("rating"),
            lowestPrice=min_price,
            highestPrice=max_price,
            averagePrice=avg_price,
            savingsAmount=savings_amount,
            savingsPercentage=savings_pct,
            bestStore=best_store_name,
            stores=store_dtos,
            trendSummary=trend_summary,
            recommendation=recommendation,
            aiDealScore=deal_score,
            aiInsights=trend_summary
        )


price_comparison_service = PriceComparisonService()
