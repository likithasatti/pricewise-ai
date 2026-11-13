import time
import logging
from typing import Dict, List, Set, Any, Optional
from datetime import datetime
from app.models.schemas import ProductSearchResultDTO, PriceComparisonDTO, ProviderProductDTO
from app.database import (
    db_find_all_products,
    db_find_product_by_id,
    db_find_product_by_name,
    db_search_products,
    db_save_product,
    db_find_store_products,
    db_find_store_product,
    db_save_store_product,
    db_find_latest_price_record,
    db_save_price_record,
    db_find_user_history,
    db_save_user_history
)
from app.providers.manager import provider_manager
from app.services.price_comparison import price_comparison_service
from app.services.ai_engine import ai_engine

logger = logging.getLogger(__name__)


class ProductSearchService:

    def __init__(self):
        self.search_cache: Dict[str, Dict] = {}

    def clear_cache(self):
        self.search_cache.clear()

    async def search(self, query: str = "", user_id: Optional[str] = None) -> ProductSearchResultDTO:
        safe_query = query.strip() if query else ""
        cache_key = safe_query.lower()
        now = time.time()

        # Cache check (3-minute TTL)
        if cache_key in self.search_cache:
            entry = self.search_cache[cache_key]
            if now - entry["timestamp"] < 180:
                logger.debug(f"Returning cached search results for '{safe_query}'")
                return entry["data"]

        logger.info(f"Executing unified search for: '{safe_query}'")

        # 1. Fetch live results from active providers (Amazon & Flipkart)
        provider_results: List[ProviderProductDTO] = []
        if safe_query:
            provider_results = await provider_manager.search_all(safe_query)

        # 2. Correlate / ingest provider results into persistent database
        matched_product_ids: Set[int] = set()

        for item in provider_results:
            product = self._find_or_create_product(item)
            pid = product["id"]
            store_product = self._find_or_create_store_product(pid, item)

            # Record price change
            self._record_price_if_changed(store_product["id"], pid, item)
            matched_product_ids.add(pid)

        # 3. Also include existing database products matching query
        candidate_products = db_search_products(safe_query) if safe_query else db_find_all_products()
        for p in candidate_products:
            pid = p["id"]
            sps = db_find_store_products(pid)
            has_real_store = any(
                sp.get("store") in ("AMAZON", "FLIPKART") and sp.get("current_price") and sp.get("current_price") > 0
                for sp in sps
            )
            if has_real_store:
                matched_product_ids.add(pid)

        # 4. Build comparative DTOs
        comparisons: List[PriceComparisonDTO] = []
        for pid in matched_product_ids:
            prod = db_find_product_by_id(pid)
            if prod:
                comp = await price_comparison_service.compare_prices(prod)
                if comp and comp.lowestPrice is not None:
                    comparisons.append(comp)

        # Sort comparisons: highest AI deal score first, then lowest price
        comparisons.sort(key=lambda c: (-(c.aiDealScore or 50), c.lowestPrice or float("inf")))

        result_dto = ProductSearchResultDTO(
            query=safe_query,
            totalFound=len(comparisons),
            providers=provider_manager.get_provider_statuses(),
            results=comparisons
        )

        # Cache results if comparisons found
        if comparisons:
            if len(self.search_cache) > 200:
                self.search_cache.clear()
            self.search_cache[cache_key] = {"data": result_dto, "timestamp": now}

        # 5. Record search history if authenticated user searched a non-empty query
        if safe_query and user_id:
            try:
                self._record_user_history(user_id, safe_query, comparisons)
            except Exception as e:
                logger.debug(f"History recording failed (non-blocking): {e}")

        return result_dto

    def _find_or_create_product(self, item: ProviderProductDTO) -> Dict[str, Any]:
        canonical = item.canonicalName or item.title
        clean_name = ai_engine.clean_product_title(canonical)

        # 1. Exact canonical name match
        existing = db_find_product_by_name(clean_name) or db_find_product_by_name(canonical)
        if existing:
            return existing

        # 2. Token similarity matching
        all_prods = db_find_all_products()
        for p in all_prods:
            p_name = p.get("canonical_name") or p.get("product_name") or ""
            if ai_engine.is_token_match(clean_name, p_name):
                return p

        # 3. Create new product
        new_id = db_save_product({
            "canonical_name": clean_name if clean_name else canonical,
            "product_name": canonical,
            "brand": item.brand or "Electronics",
            "model": item.model or "",
            "category": item.category or "Electronics",
            "description": item.description or f"Verified {item.store} product listing",
            "image_url": item.imageUrl,
            "rating": item.rating or 4.5,
            "amazon_price": item.price if item.store == "AMAZON" else None,
            "flipkart_price": item.price if item.store == "FLIPKART" else None
        })

        return db_find_product_by_id(new_id)

    def _find_or_create_store_product(self, product_id: int, item: ProviderProductDTO) -> Dict[str, Any]:
        existing = db_find_store_product(product_id, item.store)
        now_str = datetime.now().isoformat()

        if existing:
            sp_id = db_save_store_product({
                "id": existing["id"],
                "product_id": product_id,
                "store": item.store,
                "store_product_id": item.storeProductId,
                "title": item.title,
                "product_url": item.productUrl or existing.get("product_url"),
                "current_price": item.price,
                "currency": item.currency,
                "availability": item.availability,
                "status": item.status,
                "image_url": item.imageUrl or existing.get("image_url"),
                "last_checked_at": now_str
            })
            return db_find_store_product(product_id, item.store)
        else:
            new_id = db_save_store_product({
                "product_id": product_id,
                "store": item.store,
                "store_product_id": item.storeProductId,
                "title": item.title,
                "product_url": item.productUrl,
                "current_price": item.price,
                "currency": item.currency,
                "availability": item.availability,
                "status": item.status,
                "image_url": item.imageUrl,
                "last_checked_at": now_str
            })
            return db_find_store_product(product_id, item.store)

    def _record_price_if_changed(self, store_product_id: int, product_id: int, item: ProviderProductDTO):
        if item.price is None or item.price <= 0:
            return

        latest = db_find_latest_price_record(store_product_id)
        if not latest or abs(latest["price"] - item.price) > 0.01:
            db_save_price_record({
                "store_product_id": store_product_id,
                "product_id": product_id,
                "store": item.store,
                "price": item.price,
                "currency": item.currency,
                "availability": item.availability,
                "status": item.status,
                "source": "LIVE_PROVIDER"
            })
            logger.info(f"Recorded price change for [{item.title[:30]}] on {item.store}: ₹{item.price}")

    def _record_user_history(self, user_id: str, query: str, results: List[PriceComparisonDTO]):
        # Prevent rapid duplicates (within 5 seconds)
        recent = db_find_user_history(user_id)
        if recent:
            latest = recent[0]
            if latest.get("query", "").lower() == query.lower():
                try:
                    dt = datetime.fromisoformat(latest.get("created_at", ""))
                    if (datetime.now() - dt).total_seconds() < 5:
                        return  # Skip duplicate
                except Exception:
                    pass

        top_prod = results[0] if results else None
        db_save_user_history({
            "user_id": user_id,
            "query": query,
            "result_count": len(results),
            "top_product_name": top_prod.productName if top_prod else None,
            "top_product_price": top_prod.lowestPrice if top_prod else None,
            "top_product_store": top_prod.bestStore if top_prod else None,
            "top_product_image": top_prod.imageUrl if top_prod else None,
            "top_product_id": top_prod.productId if top_prod else None
        })


product_search_service = ProductSearchService()
