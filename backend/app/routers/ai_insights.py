from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.database import db_find_product_by_id, db_find_price_records, db_find_all_products
from app.services.ai_engine import ai_engine
from app.services.price_comparison import price_comparison_service

router = APIRouter(prefix="/api/ai", tags=["AI & Machine Learning"])


class TitleMatchRequest(BaseModel):
    title_a: str
    title_b: str


@router.get("/predict/{product_id}")
async def get_ai_price_prediction(product_id: int):
    """
    Analyzes historical price trajectories and provides predictive buying intelligence.
    """
    prod = db_find_product_by_id(product_id)
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product not found: {product_id}")

    records = db_find_price_records(product_id)
    prices = [r["price"] for r in records if r.get("price")]
    comp = await price_comparison_service.compare_prices(prod)

    analysis = ai_engine.analyze_price_trends(prices)
    deal_score = comp.aiDealScore or 50

    return {
        "productId": product_id,
        "productName": comp.productName,
        "currentLowestPrice": comp.lowestPrice,
        "bestStore": comp.bestStore,
        "aiDealScore": deal_score,
        "recommendation": comp.recommendation,
        "trend": analysis["trend"],
        "confidence": analysis["confidence"],
        "predictedNextPrice": analysis.get("predicted_next"),
        "priceVolatility": f"{analysis['volatility']}%",
        "insightSummary": comp.trendSummary
    }


@router.post("/match-titles")
def match_product_titles(req: TitleMatchRequest):
    """
    Tests semantic title matching across marketplace listings.
    """
    tokens_a = list(ai_engine.extract_product_tokens(req.title_a))
    tokens_b = list(ai_engine.extract_product_tokens(req.title_b))
    is_match = ai_engine.is_token_match(req.title_a, req.title_b)

    shared = list(set(tokens_a).intersection(set(tokens_b)))
    score = round((len(shared) / max(1, len(tokens_a))) * 100, 1)

    return {
        "isMatch": is_match,
        "similarityScore": f"{score}%",
        "tokensA": tokens_a,
        "tokensB": tokens_b,
        "sharedTokens": shared,
        "verdict": "Identical product listing across stores" if is_match else "Distinct product variant or model"
    }


@router.get("/top-deals")
async def get_top_ai_deals():
    """
    Scans catalog products and returns the highest AI deal scores.
    """
    prods = db_find_all_products()
    deals = []

    for p in prods:
        comp = await price_comparison_service.compare_prices(p)
        if comp and comp.lowestPrice:
            deals.append({
                "productId": comp.productId,
                "productName": comp.productName,
                "lowestPrice": comp.lowestPrice,
                "bestStore": comp.bestStore,
                "savingsAmount": comp.savingsAmount,
                "savingsPercentage": comp.savingsPercentage,
                "aiDealScore": comp.aiDealScore,
                "recommendation": comp.recommendation,
                "imageUrl": comp.imageUrl
            })

    deals.sort(key=lambda d: -(d.get("aiDealScore") or 0))
    return deals[:5]
