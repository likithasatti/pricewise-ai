import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Header, HTTPException, Query, status
from app.models.schemas import (
    ProductSearchResultDTO,
    PriceComparisonDTO,
    PriceHistoryDTO,
    ProviderStatusDTO
)
from app.database import db_find_all_products, db_find_product_by_id
from app.services.product_search import product_search_service
from app.services.price_comparison import price_comparison_service
from app.services.price_history import price_history_service
from app.services.auth_service import extract_uid_or_null
from app.providers.manager import provider_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("", response_model=List[Dict[str, Any]])
def get_all_products():
    """Legacy endpoint for backward compatibility."""
    return db_find_all_products()


@router.get("/search", response_model=ProductSearchResultDTO)
async def search_products(
    query: Optional[str] = Query(None, description="Product name or keyword"),
    q: Optional[str] = Query(None, description="Product name or keyword alias"),
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """
    Unified multi-store search across Amazon and Flipkart.
    Returns correlated comparative results, savings calculations, and provider statuses.
    """
    search_term = (query or q or "").strip()
    user_id = extract_uid_or_null(authorization)
    result = await product_search_service.search(query=search_term, user_id=user_id)
    return result


@router.get("/providers", response_model=List[ProviderStatusDTO])
def get_provider_statuses():
    """Inspects connection status of registered marketplace price providers."""
    return provider_manager.get_provider_statuses()


@router.get("/{product_id}", response_model=PriceComparisonDTO)
async def get_product_details(product_id: int):
    """Single product details with comparative store listings and AI buy recommendation."""
    prod = db_find_product_by_id(product_id)
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product not found: {product_id}")
    comp = await price_comparison_service.compare_prices(prod)
    return comp


@router.get("/{product_id}/prices", response_model=PriceComparisonDTO)
async def get_product_prices(product_id: int):
    """Alias for product details with comparative store prices."""
    return await get_product_details(product_id)


@router.get("/{product_id}/history", response_model=PriceHistoryDTO)
def get_product_history(product_id: int):
    """Historical price points and trend analytics formatted for Recharts graph visualization."""
    try:
        return price_history_service.get_history(product_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/diagnose-flipkart")
async def diagnose_flipkart(
    query: str = Query("Samsung Galaxy S24", description="Diagnostic test query")
):
    """Diagnostic endpoint to inspect live Flipkart provider status."""
    flp = provider_manager.get_provider("FLIPKART")
    if not flp:
        return {"error": "Flipkart provider not registered"}
    return {
        "store": "FLIPKART",
        "configured": flp.is_configured(),
        "status": flp.get_store_status(),
        "lastError": flp.get_last_error(),
        "description": flp.get_description()
    }
