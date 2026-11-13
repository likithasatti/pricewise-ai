from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class StorePriceDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[int] = None
    store: str
    title: Optional[str] = None
    price: Optional[float] = None
    currency: str = "INR"
    availability: str = "IN_STOCK"
    productUrl: Optional[str] = None
    imageUrl: Optional[str] = None
    status: str = "LIVE"  # LIVE, LAST_KNOWN, CONFIG_REQUIRED, UNAVAILABLE, SAMPLE_DATA
    lastCheckedAt: Optional[datetime] = None
    isLowest: bool = False


class PriceComparisonDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    productId: Optional[int] = None
    productName: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    imageUrl: Optional[str] = None
    rating: Optional[float] = None
    lowestPrice: Optional[float] = None
    highestPrice: Optional[float] = None
    averagePrice: Optional[float] = None
    savingsAmount: Optional[float] = None
    savingsPercentage: Optional[float] = None
    bestStore: Optional[str] = None
    stores: List[StorePriceDTO] = Field(default_factory=list)
    trendSummary: Optional[str] = None
    recommendation: Optional[str] = "INSUFFICIENT DATA"  # BUY NOW, GOOD PRICE, WAIT FOR LOWER PRICE, INSUFFICIENT DATA
    # AI enhanced intelligence
    aiDealScore: Optional[int] = None  # 0-100 deal rating
    aiInsights: Optional[str] = None


class ProviderStatusDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    store: str
    configured: bool
    status: str  # LIVE, SAMPLE_DATA, CONFIG_REQUIRED, UNAVAILABLE
    description: Optional[str] = None
    requiredConfig: Optional[str] = None
    error: Optional[str] = None


class ProductSearchResultDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    query: str = ""
    totalFound: int = 0
    providers: List[ProviderStatusDTO] = Field(default_factory=list)
    results: List[PriceComparisonDTO] = Field(default_factory=list)


class PricePointDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    date: Optional[str] = None
    timestamp: Optional[datetime] = None
    store: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = "INR"
    availability: Optional[str] = "IN_STOCK"
    source: Optional[str] = None
    status: Optional[str] = None


class PriceHistoryDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    productId: Optional[int] = None
    productName: Optional[str] = None
    currentLowest: Optional[float] = None
    lowestRecorded: Optional[float] = None
    highestRecorded: Optional[float] = None
    averageRecorded: Optional[float] = None
    priceTrend: str = "INSUFFICIENT_DATA"  # FALLING, RISING, STABLE, INSUFFICIENT_DATA
    lastChecked: Optional[datetime] = None
    totalRecords: int = 0
    points: List[PricePointDTO] = Field(default_factory=list)
    storeSeries: Dict[str, List[PricePointDTO]] = Field(default_factory=dict)
    # AI price trend prediction
    predictedTrend: Optional[str] = None
    priceVolatilityScore: Optional[float] = None


class TrackedProductDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[int] = None
    storeProductId: Optional[int] = None
    productId: Optional[int] = None
    productName: Optional[str] = None
    store: Optional[str] = None
    imageUrl: Optional[str] = None
    productUrl: Optional[str] = None
    currentPrice: Optional[float] = None
    initialPrice: Optional[float] = None
    targetPrice: Optional[float] = None
    targetDropPercentage: Optional[float] = None
    lastNotifiedPrice: Optional[float] = None
    priceDrop: Optional[float] = None
    dropPercentage: Optional[float] = None
    lastCheckedAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None
    active: bool = True
    userEmail: Optional[str] = None


class TrackingRequestDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    storeProductId: int
    userEmail: Optional[str] = None
    targetPrice: Optional[float] = None
    targetDropPercentage: Optional[float] = None
    userId: Optional[str] = "local-user"


class UserSearchHistoryDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = None
    userId: Optional[str] = None
    query: str
    resultCount: Optional[int] = 0
    topProductName: Optional[str] = None
    topProductPrice: Optional[float] = None
    topProductStore: Optional[str] = None
    topProductImage: Optional[str] = None
    topProductId: Optional[int] = None
    createdAt: Optional[datetime] = None


class ProviderProductDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    store: str
    storeProductId: str
    title: str
    canonicalName: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: str = "INR"
    availability: str = "IN_STOCK"
    productUrl: Optional[str] = None
    imageUrl: Optional[str] = None
    rating: Optional[float] = None
    status: str = "LIVE"
