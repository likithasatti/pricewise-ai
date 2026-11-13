import re
import time
import logging
import httpx
from typing import List, Dict, Optional, Any
from app.config import settings
from app.models.schemas import ProviderProductDTO
from app.providers.base import PriceProvider

logger = logging.getLogger(__name__)


def clean_price(price_val: Any) -> Optional[float]:
    if price_val is None:
        return None
    if isinstance(price_val, (int, float)):
        return float(price_val)
    # String cleanup: remove ₹, $, commas, spaces
    s = str(price_val).strip()
    match = re.search(r"[\d,]+(?:\.\d+)?", s)
    if match:
        try:
            return float(match.group(0).replace(",", ""))
        except ValueError:
            return None
    return None


class AmazonPriceProvider(PriceProvider):

    def __init__(self):
        self.cache: Dict[str, Dict] = {}
        self.is_unavailable: bool = False
        self.last_error: Optional[str] = None

    def get_store_name(self) -> str:
        return "AMAZON"

    def is_configured(self) -> bool:
        return bool(settings.RAPIDAPI_KEY and settings.RAPIDAPI_KEY.strip())

    def get_store_status(self) -> str:
        if not self.is_configured():
            return "CONFIG_REQUIRED"
        if self.is_unavailable:
            return "UNAVAILABLE"
        return "LIVE"

    def get_description(self) -> str:
        return "Amazon Real-Time Product & Price API via RapidAPI"

    def get_required_config(self) -> str:
        return f"RAPIDAPI_KEY (Host: {settings.RAPIDAPI_HOST})"

    def get_last_error(self) -> Optional[str]:
        return self.last_error

    async def search_products(self, query: str) -> List[ProviderProductDTO]:
        if not query or not query.strip():
            return []

        if not self.is_configured():
            logger.info(f"Amazon RapidAPI provider not configured. Skipping live search for '{query}'.")
            return []

        safe_query = query.strip()
        cache_key = f"{safe_query.lower()}:{settings.AMAZON_COUNTRY}"
        now = time.time()

        # In-memory cache check (5 min TTL)
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if now - entry["timestamp"] < 300:
                logger.debug(f"Returning {len(entry['data'])} cached Amazon results for '{safe_query}'")
                return entry["data"]

        headers = {
            "x-rapidapi-key": settings.RAPIDAPI_KEY.strip(),
            "x-rapidapi-host": settings.RAPIDAPI_HOST.strip(),
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PriceWise-AI/1.0"
        }

        params = {
            "query": safe_query,
            "page": "1",
            "country": settings.AMAZON_COUNTRY
        }

        url = f"https://{settings.RAPIDAPI_HOST.strip()}/search"

        try:
            async with httpx.AsyncClient(timeout=settings.AMAZON_TIMEOUT_SECONDS) as client:
                logger.info(f"Querying Real-Time Amazon API for '{safe_query}'")
                response = await client.get(url, headers=headers, params=params)

                if response.status_code != 200:
                    self.last_error = f"HTTP {response.status_code}: {response.text[:100]}"
                    logger.error(f"Amazon API returned status {response.status_code}")
                    self.is_unavailable = True
                    return []

                data = response.json()
                results = self._parse_search_response(data)
                self.is_unavailable = False
                self.last_error = None

                # Keep cache bounded
                if len(self.cache) > 100:
                    self.cache.clear()
                self.cache[cache_key] = {"data": results, "timestamp": now}

                logger.info(f"Found {len(results)} Amazon products for '{safe_query}'")
                return results

        except httpx.TimeoutException:
            logger.warning(f"Amazon RapidAPI search timed out for '{safe_query}'")
            self.last_error = "Request timed out"
            self.is_unavailable = True
            return []
        except Exception as e:
            logger.error(f"Error querying Amazon RapidAPI: {str(e)}")
            self.last_error = str(e)
            self.is_unavailable = True
            return []

    def _parse_search_response(self, data: dict) -> List[ProviderProductDTO]:
        items = []
        products = data.get("data", {}).get("products", [])
        if not products and isinstance(data.get("products"), list):
            products = data["products"]

        for item in products:
            if not isinstance(item, dict):
                continue

            asin = item.get("asin")
            title = item.get("product_title") or item.get("title")
            if not title:
                continue

            raw_price = (
                item.get("product_price")
                or item.get("product_minimum_offer_price")
                or item.get("product_original_price")
                or item.get("price")
            )
            price = clean_price(raw_price)

            image_url = item.get("product_photo") or item.get("product_main_image_url") or item.get("thumbnail")
            product_url = item.get("product_url") or (f"https://www.amazon.in/dp/{asin}" if asin else None)

            rating = clean_price(item.get("product_star_rating") or item.get("rating"))

            items.append(ProviderProductDTO(
                store="AMAZON",
                storeProductId=str(asin or title[:20]),
                title=title.strip(),
                canonicalName=title.strip(),
                price=price,
                currency="INR",
                availability="IN_STOCK" if price else "UNAVAILABLE",
                productUrl=product_url,
                imageUrl=image_url,
                rating=rating,
                status="LIVE" if price else "UNAVAILABLE"
            ))

        return items
