import re
import math
import logging
import httpx
from typing import List, Set, Dict, Any, Optional, Tuple
from app.config import settings

logger = logging.getLogger(__name__)

STOP_WORDS = {
    "5g", "4g", "3g", "lte", "smartphone", "phone", "mobile", "ram", "rom", "storage",
    "black", "white", "blue", "green", "gold", "silver", "gray", "grey", "titanium",
    "purple", "violet", "yellow", "amber", "red", "orange", "pink", "onyx", "marble",
    "with", "and", "for", "the", "edition", "series", "gb", "tb", "inch", "in",
    "ai", "camera", "display", "battery", "processor", "snapdragon", "bionic", "fast",
    "unlocked", "dual", "sim", "cellular", "wifi", "wi", "fi", "official", "global",
    "original", "genuine", "certified", "refurbished", "renewed", "new", "latest"
}

MODEL_VARIANTS = {"pro", "plus", "ultra", "mini", "max", "air", "fe", "lite", "neo"}


class AIEngine:

    @staticmethod
    def clean_product_title(title: Optional[str]) -> str:
        if not title:
            return ""
        s = title.strip()
        for delim in ["(", "[", "|", " - "]:
            idx = s.find(delim)
            if idx > 0:
                s = s[:idx]
        cleaned = re.sub(r"(?i)\b(5g|4g|lte|smartphone|mobile|phone)\b", "", s)
        return re.sub(r"\s+", " ", cleaned).strip()

    @staticmethod
    def extract_product_tokens(title: Optional[str]) -> Set[str]:
        if not title:
            return set()
        cleaned = re.sub(r"[^a-z0-9\s]", " ", title.lower())
        words = cleaned.split()
        tokens = set()
        for w in words:
            if len(w) >= 2 and w not in STOP_WORDS and not re.match(r"^\d+(gb|tb)$", w):
                tokens.add(w)
        return tokens

    @classmethod
    def is_token_match(cls, title_a: str, title_b: str) -> bool:
        tokens_a = cls.extract_product_tokens(title_a)
        tokens_b = cls.extract_product_tokens(title_b)

        if not tokens_a or not tokens_b:
            return False

        # Model variants must match exactly (e.g. Pro vs standard, Ultra vs standard)
        for variant in MODEL_VARIANTS:
            if (variant in tokens_a) != (variant in tokens_b):
                return False

        smaller = tokens_a if len(tokens_a) <= len(tokens_b) else tokens_b
        larger = tokens_b if len(tokens_a) <= len(tokens_b) else tokens_a

        match_count = sum(1 for t in smaller if t in larger)

        # Exact subset match
        if len(smaller) >= 2 and match_count >= len(smaller):
            return True
        if match_count >= 3 or (len(smaller) == 2 and match_count == 2):
            return True
        return match_count >= (len(smaller) * 0.6)

    @classmethod
    def analyze_price_trends(cls, prices: List[float]) -> Dict[str, Any]:
        """
        Calculates mathematical trend line, volatility, and predicted next direction.
        """
        valid_prices = [p for p in prices if p is not None and p > 0]
        if not valid_prices:
            return {
                "trend": "INSUFFICIENT_DATA",
                "volatility": 0.0,
                "confidence": 0.0,
                "predicted_next": None
            }

        n = len(valid_prices)
        avg = sum(valid_prices) / n

        if n < 2:
            return {
                "trend": "STABLE",
                "volatility": 0.0,
                "confidence": 50.0,
                "predicted_next": avg
            }

        # Volatility (standard deviation / mean)
        variance = sum((p - avg) ** 2 for p in valid_prices) / n
        std_dev = math.sqrt(variance)
        volatility = round((std_dev / avg) * 100, 2)

        # Linear regression slope (y = mx + b)
        x_mean = (n - 1) / 2.0
        numerator = sum((i - x_mean) * (valid_prices[i] - avg) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        slope = numerator / denominator if denominator != 0 else 0

        # Projected price for next period
        predicted_next = max(0.0, round(avg + slope * (n / 2.0), 2))

        # Classify trend
        slope_pct = (slope / avg) * 100
        if slope_pct < -1.0:
            trend = "FALLING"
            confidence = min(95.0, 70.0 + abs(slope_pct) * 5)
        elif slope_pct > 1.0:
            trend = "RISING"
            confidence = min(95.0, 70.0 + slope_pct * 5)
        else:
            trend = "STABLE"
            confidence = 80.0

        return {
            "trend": trend,
            "volatility": volatility,
            "confidence": round(confidence, 1),
            "predicted_next": predicted_next
        }

    @classmethod
    def calculate_deal_score(
        cls,
        current_price: Optional[float],
        historical_avg: Optional[float],
        savings_pct: Optional[float],
        rating: Optional[float],
        trend: str
    ) -> int:
        """
        Generates an AI Deal Score from 0 to 100.
        """
        if current_price is None or current_price <= 0:
            return 50

        score = 50.0

        # 1. Price relative to historical average (up to ±25 pts)
        if historical_avg and historical_avg > 0:
            diff_pct = ((historical_avg - current_price) / historical_avg) * 100
            score += max(-25.0, min(25.0, diff_pct * 2.0))

        # 2. Savings percentage across stores (up to +15 pts)
        if savings_pct and savings_pct > 0:
            score += min(15.0, savings_pct * 1.5)

        # 3. Product Rating (up to +10 pts)
        if rating and rating > 0:
            score += (rating - 3.0) * 5.0  # 4.8 rating gives ~9 pts

        # 4. Trend momentum (±10 pts)
        if trend == "FALLING":
            score += 8.0
        elif trend == "RISING":
            score -= 5.0

        return max(10, min(99, int(round(score))))

    @classmethod
    async def generate_smart_insight(
        cls,
        product_name: str,
        lowest_price: Optional[float],
        best_store: Optional[str],
        savings_amount: Optional[float],
        savings_pct: Optional[float],
        historical_prices: List[float]
    ) -> Tuple[str, str, int]:
        """
        Returns (trend_summary, recommendation, ai_deal_score).
        """
        if lowest_price is None or lowest_price <= 0:
            return (
                "No live pricing currently available across Amazon and Flipkart.",
                "INSUFFICIENT DATA",
                50
            )

        analysis = cls.analyze_price_trends(historical_prices)
        trend = analysis["trend"]
        confidence = analysis["confidence"]

        hist_avg = sum(historical_prices) / len(historical_prices) if historical_prices else lowest_price
        deal_score = cls.calculate_deal_score(lowest_price, hist_avg, savings_pct, 4.5, trend)

        # If LLM API key is present, attempt live AI summary
        llm_key = settings.GEMINI_API_KEY or settings.AI_API_KEY
        if llm_key and len(historical_prices) >= 2:
            try:
                ai_text = await cls._query_gemini_summary(
                    product_name, lowest_price, best_store, savings_amount, hist_avg, llm_key
                )
                if ai_text:
                    recommendation = "BUY NOW" if deal_score >= 70 else ("GOOD PRICE" if deal_score >= 50 else "WAIT FOR LOWER PRICE")
                    return (ai_text, recommendation, deal_score)
            except Exception as e:
                logger.debug(f"Gemini AI insight generation skipped: {e}")

        # Deterministic Intelligent Heuristics
        hist_min = min(historical_prices) if historical_prices else lowest_price
        diff_from_avg = round(((lowest_price - hist_avg) / hist_avg * 100), 1) if hist_avg > 0 else 0

        if lowest_price <= hist_min and len(historical_prices) >= 3:
            summary = (
                f"🔥 ALL-TIME LOW: Currently ₹{lowest_price:,.0f} at {best_store}, "
                f"which is {abs(diff_from_avg)}% below the historical average of ₹{hist_avg:,.0f}. "
                f"AI Confidence: {confidence}%."
            )
            recommendation = "BUY NOW"
        elif diff_from_avg < -3.0:
            summary = (
                f"Great deal: Current price is {abs(diff_from_avg)}% lower than average (₹{hist_avg:,.0f}). "
                f"Best deal at {best_store}."
            )
            recommendation = "BUY NOW"
        elif savings_amount and savings_amount > 0:
            summary = (
                f"{best_store} currently offers the lowest verified price at ₹{lowest_price:,.0f}. "
                f"You save ₹{savings_amount:,.0f} ({savings_pct:.1f}%) compared to highest store."
            )
            recommendation = "GOOD PRICE"
        elif diff_from_avg > 5.0 and len(historical_prices) >= 3:
            summary = (
                f"Price is elevated: Currently {diff_from_avg}% higher than historical average of ₹{hist_avg:,.0f}. "
                f"Consider setting a price drop alert."
            )
            recommendation = "WAIT FOR LOWER PRICE"
        else:
            summary = (
                f"Price is stable: Close to historical average of ₹{hist_avg:,.0f}. Best available at {best_store}."
            )
            recommendation = "GOOD PRICE"

        return (summary, recommendation, deal_score)

    @staticmethod
    async def _query_gemini_summary(
        product_name: str,
        price: float,
        best_store: Optional[str],
        savings: Optional[float],
        avg_price: float,
        api_key: str
    ) -> Optional[str]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        prompt = (
            f"Write a concise 2-sentence buying recommendation for '{product_name}'. "
            f"Current best price is ₹{price:,.0f} at {best_store}. "
            f"Historical average is ₹{avg_price:,.0f}. "
            f"Savings compared to other stores: ₹{savings or 0:,.0f}. "
            f"State clearly whether the user should buy now or wait."
        )
        body = {"contents": [{"parts": [{"text": prompt}]}]}

        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.post(url, json=body)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return text
        return None


ai_engine = AIEngine()
