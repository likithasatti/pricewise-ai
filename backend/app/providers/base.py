from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.schemas import ProviderProductDTO


class PriceProvider(ABC):

    @abstractmethod
    def get_store_name(self) -> str:
        """Returns the store identifier, e.g. AMAZON or FLIPKART"""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Returns whether required API credentials are present"""
        pass

    @abstractmethod
    def get_store_status(self) -> str:
        """Returns LIVE, SAMPLE_DATA, CONFIG_REQUIRED, or UNAVAILABLE"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

    @abstractmethod
    def get_required_config(self) -> str:
        pass

    def get_last_error(self) -> Optional[str]:
        return None

    @abstractmethod
    async def search_products(self, query: str) -> List[ProviderProductDTO]:
        """Asynchronously searches products from this provider"""
        pass
