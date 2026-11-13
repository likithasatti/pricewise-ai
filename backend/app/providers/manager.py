import asyncio
import logging
from typing import List, Dict, Optional
from app.models.schemas import ProviderProductDTO, ProviderStatusDTO
from app.providers.base import PriceProvider
from app.providers.amazon_provider import AmazonPriceProvider
from app.providers.flipkart_provider import FlipkartPriceProvider

logger = logging.getLogger(__name__)


class ProviderManager:

    def __init__(self):
        self.providers: Dict[str, PriceProvider] = {
            "AMAZON": AmazonPriceProvider(),
            "FLIPKART": FlipkartPriceProvider()
        }

    def get_provider(self, store: str) -> Optional[PriceProvider]:
        return self.providers.get(store.upper())

    def get_provider_statuses(self) -> List[ProviderStatusDTO]:
        statuses = []
        for name, provider in self.providers.items():
            statuses.append(ProviderStatusDTO(
                store=name,
                configured=provider.is_configured(),
                status=provider.get_store_status(),
                description=provider.get_description(),
                requiredConfig=provider.get_required_config(),
                error=provider.get_last_error()
            ))
        return statuses

    async def search_all(self, query: str) -> List[ProviderProductDTO]:
        if not query or not query.strip():
            return []

        tasks = [
            provider.search_products(query)
            for provider in self.providers.values()
        ]

        # Execute parallel searches with asyncio.gather
        results_nested = await asyncio.gather(*tasks, return_exceptions=True)

        combined: List[ProviderProductDTO] = []
        for res in results_nested:
            if isinstance(res, list):
                combined.extend(res)
            elif isinstance(res, Exception):
                logger.error(f"Provider search raised exception: {str(res)}")

        logger.info(f"Aggregated {len(combined)} live items across all providers for '{query}'")
        return combined


provider_manager = ProviderManager()
