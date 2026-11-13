# PriceWise AI — FastAPI Backend ⚡

> High-performance asynchronous Python (FastAPI) backend for real-time marketplace aggregation, NLP title correlation, price tracking, and AI deal prediction.

---

## 🔗 Live Service & Documentation

- **Live Service URL:** [https://pricewise-ai-backend-tz09.onrender.com/](https://pricewise-ai-backend-tz09.onrender.com/)
- **Interactive Swagger Docs:** [https://pricewise-ai-backend-tz09.onrender.com/docs](https://pricewise-ai-backend-tz09.onrender.com/docs)
- **ReDoc Documentation:** [https://pricewise-ai-backend-tz09.onrender.com/redoc](https://pricewise-ai-backend-tz09.onrender.com/redoc)

---

## 🛠️ Architecture & Components

- **FastAPI (Python 3.11+):** High-throughput async REST API framework.
- **AsyncIO & Httpx:** Concurrent non-blocking requests across Amazon and Flipkart marketplace providers via `asyncio.gather`.
- **NLP Product Matcher:** Token normalization, Jaccard similarity, and strict model-variant filtering to correlate disparate marketplace titles.
- **AI Deal Engine:** Time-series linear regression slope and volatility modeling calculating Buy Now vs. Wait signals and 0–100 Deal Quality Scores.
- **SQLite Database:** Local persistent relational storage (`pricewise.db`).
- **Scheduler:** Background async task continuously evaluating tracked items against price-drop alert thresholds.

---

## 🚀 Running Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start Uvicorn server
python run.py
```

The server starts at `http://localhost:8080`.
Open `http://localhost:8080/docs` to test endpoints via interactive Swagger UI.

---

## 🧪 Automated Tests

```bash
python -m pytest tests/test_api.py -v
```

11 automated tests verify health checks, provider statuses, search domain accuracy, product details, price histories, user tracking CRUD, and AI predictions.
