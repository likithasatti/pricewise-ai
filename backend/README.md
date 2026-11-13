# PriceWise AI - FastAPI Backend 🚀

This is the high-performance Python (FastAPI) backend for **PriceWise AI**. It provides RESTful endpoints for real-time price comparison, asynchronous marketplace scraping via RapidAPI, price tracking, search history, and AI deal prediction.

---

## 🛠️ Tech Stack & Architecture

- **Framework:** FastAPI (Python 3.11+)
- **Asynchronous HTTP Client:** `httpx`
- **Validation:** Pydantic v2
- **Database:** SQLite (local persistent storage) + Google Cloud Firestore compatible
- **Background Tasks:** `asyncio` scheduler for continuous price tracking
- **AI Engine:** Linear regression trendlines, volatility modeling, and NLP token matching

---

## 🚀 Running the Server

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python run.py
```

The server will start at:
- **API URL:** `http://localhost:8080`
- **Interactive Swagger Docs:** `http://localhost:8080/docs`
- **Alternative ReDoc:** `http://localhost:8080/redoc`

---

## 🧪 Testing

Run the automated test suite:

```bash
python -m pytest tests/test_api.py -v
```

All 10 test cases verify health checks, multi-provider statuses, search correlation, product details, price history graphs, user search history, tracking CRUD, and AI predictions.
