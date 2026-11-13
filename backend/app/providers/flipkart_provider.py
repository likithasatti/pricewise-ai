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
    s = str(price_val).strip()
    match = re.search(r"[\d,]+(?:\.\d+)?", s)
    if match:
        try:
            return float(match.group(0).replace(",", ""))
        except ValueError:
            return None
    return None


class FlipkartPriceProvider(PriceProvider):

    def __init__(self):
        self.cache: Dict[str, Dict] = {}
        self.is_unavailable: bool = False
        self.last_error: Optional[str] = None

    def get_store_name(self) -> str:
        return "FLIPKART"

    def is_configured(self) -> bool:
        key = settings.REEFAPI_KEY or settings.FLIPKART_API_KEY
        return bool(key and key.strip())

    def get_store_status(self) -> str:
        if not self.is_configured():
            return "CONFIG_REQUIRED"
        if self.is_unavailable:
            return "UNAVAILABLE"
        return "LIVE"

    def get_description(self) -> str:
        return "Flipkart Real-Time Product & Price API via ReefAPI"

    def get_required_config(self) -> str:
        return "REEFAPI_KEY (ReefAPI Flipkart Data API)"

    def get_last_error(self) -> Optional[str]:
        return self.last_error

    async def search_products(self, query: str) -> List[ProviderProductDTO]:
        if not query or not query.strip():
            return []

        if not self.is_configured():
            logger.info(f"Flipkart provider not configured. Skipping live search for '{query}'.")
            return []

        safe_query = query.strip()
        cache_key = safe_query.lower()
        now = time.time()

        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if now - entry["timestamp"] < 300:
                logger.debug(f"Returning {len(entry['data'])} cached Flipkart results for '{safe_query}'")
                return entry["data"]

        key = (settings.REEFAPI_KEY or settings.FLIPKART_API_KEY).strip()
        url = settings.REEFAPI_FLIPKART_URL.strip()

        # Check if using ReefAPI or RapidAPI host
        is_rapidapi = "rapidapi.com" in settings.FLIPKART_API_HOST

        try:
            async with httpx.AsyncClient(timeout=settings.FLIPKART_TIMEOUT_SECONDS) as client:
                logger.info(f"Querying Flipkart API for '{safe_query}'")

                if is_rapidapi and not settings.REEFAPI_KEY:
                    headers = {
                        "x-rapidapi-key": key,
                        "x-rapidapi-host": settings.FLIPKART_API_HOST,
                        "Accept": "application/json"
                    }
                    rapid_url = f"https://{settings.FLIPKART_API_HOST}/search"
                    response = await client.get(rapid_url, headers=headers, params={"query": safe_query, "page": 1})
                else:
                    headers = {
                        "x-api-key": key,
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PriceWise-AI/1.0"
                    }
                    response = await client.post(url, headers=headers, json={"q": safe_query, "page": 1})

                if response.status_code != 200:
                    self.last_error = f"HTTP {response.status_code}: {response.text[:100]}"
                    logger.error(f"Flipkart API returned status {response.status_code}")
                    self.is_unavailable = True
                    return []

                data = response.json()
                results = self._parse_search_response(data)
                self.is_unavailable = False
                self.last_error = None

                if len(self.cache) > 100:
                    self.cache.clear()
                self.cache[cache_key] = {"data": results, "timestamp": now}

                logger.info(f"Found {len(results)} Flipkart products for '{safe_query}'")
                return results

        except httpx.TimeoutException:
            logger.warning(f"Flipkart search timed out for '{safe_query}'")
            self.last_error = "Request timed out"
            self.is_unavailable = True
            return []
        except Exception as e:
            logger.error(f"Error querying Flipkart API: {str(e)}")
            self.last_error = str(e)
            self.is_unavailable = True
            return []

    def _parse_search_response(self, data: dict) -> List[ProviderProductDTO]:
        items = []

        # Check various product list structures
        products = (
            data.get("products")
            or data.get("data", {}).get("products")
            or data.get("results")
            or data.get("data")
            or []
        )
        if isinstance(products, dict):
            products = products.get("products", [])

        if not isinstance(products, list):
            return []

        for item in products:
            if not isinstance(item, dict):
                continue

            pid = item.get("pid") or item.get("product_id") or item.get("id") or item.get("itemId")
            title = item.get("title") or item.get("product_title") or item.get("name")
            if not title:
                continue

            raw_price = (
                item.get("special_price")
                or item.get("selling_price")
                or item.get("price")
                or item.get("final_price")
            )
            price = clean_price(raw_price)

            image_url = (
                item.get("image")
                or item.get("product_photo")
                or item.get("thumbnail")
                or item.get("imageUrl")
            )
            product_url = item.get("url") or item.get("product_url")

            rating = clean_price(item.get("rating") or item.get("stars"))

            items.append(ProviderProductDTO(
                store="FLIPKART",
                storeProductId=str(pid or title[:20]),
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
