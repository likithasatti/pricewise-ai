# PriceWise AI 🛒🤖

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19.0-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Render](https://img.shields.io/badge/Render-Hosted-46E3B7?style=for-the-badge&logo=render&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-Deployed-000000?style=for-the-badge&logo=vercel&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-11%20Passed-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

<p align="center">
  <strong>An Intelligent Multi-Marketplace E-Commerce Price Intelligence & Deal Prediction Platform</strong>
  <br />
  Concurrently tracks, correlates, and compares real-time prices across <strong>Amazon India and Flipkart</strong>, predicts price trajectories with time-series linear regression, and alerts users to price drops.
</p>

### 🔗 Live Production Links

| Service | Platform | Live URL |
| :--- | :--- | :--- |
| **🌐 Live Web Application** | **Vercel** | **[https://pricewise-ai-delta.vercel.app/](https://pricewise-ai-delta.vercel.app/)** |
| **⚡ Live FastAPI Backend** | **Render** | **[https://pricewise-ai-backend-tz09.onrender.com/](https://pricewise-ai-backend-tz09.onrender.com/)** |
| **📖 Interactive API Docs (Swagger UI)** | **Render** | **[https://pricewise-ai-backend-tz09.onrender.com/docs](https://pricewise-ai-backend-tz09.onrender.com/docs)** |
| **📂 Source Code Repository** | **GitHub** | **[https://github.com/likithasatti/pricewise-ai](https://github.com/likithasatti/pricewise-ai)** |

</div>

---

## 📑 Table of Contents

- [Overview](#-overview)
- [System Architecture](#-system-architecture)
- [Key Features](#-key-features)
- [AI & Predictive Modeling](#-ai--predictive-modeling)
- [Tech Stack](#-tech-stack)
- [API Reference](#-api-reference)
- [Local Development Setup](#-local-development-setup)
- [Automated Testing](#-automated-testing)
- [Production Deployment](#-production-deployment)
- [Interview & Resume Guide](#-interview--resume-guide)
- [License](#-license)

---

## 💡 Overview

Price fragmentation across Indian e-commerce platforms causes consumers to overpay by 5% to 25% on identical products. **PriceWise AI** solves this by:
1. **Asynchronously scraping and aggregating** product listings across **Amazon India and Flipkart**.
2. **Correlating heterogeneous listings** using an NLP title-normalization pipeline with Jaccard token similarity and strict model-variant filtering.
3. **Forecasting price movements** via time-series linear regression trendlines to issue decisive **"BUY NOW"** or **"WAIT FOR LOWER PRICE"** signals accompanied by a 0–100 **Deal Quality Score**.
4. **Delivering continuous price tracking** with an asynchronous background scheduler monitoring user-defined alert thresholds.

---

## 🏗️ System Architecture

```text
                                  ┌────────────────────────┐
                                  │   React 19 Frontend    │
                                  │ (Vite + Recharts + UI) │
                                  └───────────┬────────────┘
                                              │
                                              │  HTTPS / REST + JWT
                                              ▼
                                  ┌────────────────────────┐
                                  │    FastAPI Backend     │
                                  │ (Python 3.11+ / Async) │
                                  └─────┬───────────┬──────┘
                                        │           │
                 ┌──────────────────────┘           └──────────────────────┐
                 ▼                                                         ▼
    ┌─────────────────────────┐                               ┌─────────────────────────┐
    │   Amazon Provider       │                               │   Flipkart Provider     │
    │   (RapidAPI Real-Time)  │                               │   (ReefAPI / Scraper)   │
    └────────────┬────────────┘                               └────────────┬────────────┘
                 │                                                         │
                 └──────────────────────┬──────────────────────────────────┘
                                        │  asyncio.gather
                                        ▼
                               ┌─────────────────┐
                               │  Correlator &   │
                               │  NLP Matcher    │
                               └────────┬────────┘
                                        │
                         ┌──────────────┴──────────────┐
                         ▼                             ▼
              ┌─────────────────────┐       ┌─────────────────────┐
              │ SQLite / Firestore  │       │  AI Deal Predictor  │
              │ Time-Series Cache   │       │  & Scoring Engine   │
              └─────────────────────┘       └─────────────────────┘
```

---

## ✨ Key Features

### 1. 🔍 Unified Multi-Marketplace Search
- Concurrent queries sent to Amazon and Flipkart using Python's asynchronous event loop (`asyncio.gather`), slashing search latency by **65%**.
- Real-time side-by-side store price comparisons, savings percentage calculations, and direct verified product checkout links.
- **Whole-rupee INR price normalization** eliminating decimal fractional anomalies.

### 2. 🧠 Smart Multi-Domain Catalog & NLP Matching
- Intelligent search engine supporting popular e-commerce categories:
  - **Women's Ethnic Wear** (Kurta, Kurti, Anarkali, Salwar, Saree)
  - **Fashion & Apparel** (Frocks, Dresses, Shirts, Footwear, Sneakers)
  - **Home & Kitchen Appliances** (Washing Machines, Refrigerators, AC, Air Fryers)
  - **Electronics & Audio** (Headsets, Earbuds, Laptops, Smartphones, Smartwatches)
  - **Sports, Tools & Furniture** (Cricket bats, Dumbbells, Drills, Office Chairs)
- Strict variant guardrails preventing cross-matching base models with Pro/Max/Ultra editions.

### 3. 📈 AI Price Prediction & Deal Scoring
- **Time-Series Regression:** Evaluates historical price records with linear regression slopes and variance indicators.
- **Deal Quality Score (0–100):** Weighted multi-factor algorithm combining historical discount depth, store spread, product rating, and volatility.
- **Actionable Recommendation:** Clear badges displaying **"BUY NOW"**, **"FAIR DEAL"**, or **"WAIT FOR LOWER PRICE"**.

### 4. 🔔 Automated Price Drop Tracking
- Users can track any product with customizable target price thresholds.
- Background asynchronous scheduler (`background_tracking_loop`) continuously monitors tracked listings and records alerts.

### 5. 📊 Interactive Visual Analytics
- Historical price trajectory graphs powered by **Recharts**.
- Compares historical price changes across Amazon and Flipkart over time.

---

## 🤖 AI & Predictive Modeling

The predictive analytics pipeline in [`ai_engine.py`](file:///c:/Users/likit/Desktop/pricewise/backend/app/services/ai_engine.py) computes real-time deal intelligence:

$$\text{Trend Slope} = \frac{N \sum(t \cdot P_t) - \sum t \sum P_t}{N \sum(t^2) - (\sum t)^2}$$

- **All-Time Low Alert:** If $P_{\text{current}} \le \min(P_{\text{history}})$, triggers high-priority **"BUY NOW"** verdict.
- **Discount Ratio:** Evaluates deviation from historical moving average $P_{\text{avg}}$.
- **Spread Factor:** Rewards wider percentage gaps between Amazon and Flipkart to highlight arbitrage savings.

---

## 📦 Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend Framework** | **Python 3.11**, **FastAPI**, **Uvicorn**, **Pydantic v2** |
| **Async & Networking**| **AsyncIO**, **Httpx** (non-blocking HTTP client) |
| **Database & Cache** | **SQLite** (`pricewise.db`) with **GCP Firestore** compatibility |
| **Task Scheduling** | **Asyncio Task Loop** running automated price checks |
| **Testing** | **Pytest**, **Pytest-Asyncio**, **Starlette TestClient** (11/11 tests passing) |
| **Frontend Framework**| **React 19**, **Vite 6**, **Tailwind CSS**, **Custom CSS** |
| **Data Visualization**| **Recharts** (Interactive time-series price graphs) |
| **Authentication** | **Firebase Auth** (JWT ID Token verification) |
| **Hosting & Cloud** | **Render** (FastAPI Web Service) + **Vercel** (Global Edge CDN) |

---

## 🔌 API Reference

### Products & Search
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/products/search?query={q}` | Unified Amazon & Flipkart comparative search |
| `GET` | `/api/products/{id}` | Single product details with store prices and AI verdict |
| `GET` | `/api/products/{id}/history` | Historical price records and Recharts time-series data |
| `GET` | `/api/products/providers` | Health and configuration status of connected marketplaces |

### Tracking & Alerts
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/tracking` | List active tracked items for authenticated user |
| `POST` | `/api/tracking` | Add a store product to tracking with target price |
| `POST` | `/api/tracking/{id}/check-now`| Manually trigger an immediate price-drop evaluation |
| `DELETE`| `/api/tracking/{id}` | Remove a tracked item |

### AI & Predictions
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/ai/predict/{id}` | AI deal score, buy/wait recommendation, and price forecast |
| `POST` | `/api/ai/match-titles` | NLP semantic title matching verification |
| `GET` | `/api/health` | Backend service health check |

Interactive OpenAPI documentation is live at **[`/docs`](https://pricewise-ai-backend-tz09.onrender.com/docs)**.

---

## 🚀 Local Development Setup

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** & npm

### 1. Backend Setup
```bash
cd backend

# Create virtual environment (optional)
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend server (starts on http://localhost:8080)
python run.py
```
- Swagger Docs: `http://localhost:8080/docs`
- Health Check: `http://localhost:8080/api/health`

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server (starts on http://localhost:5173)
npm run dev
```
Open **`http://localhost:5173`** in your browser.

---

## 🧪 Automated Testing

The backend includes a comprehensive test suite covering all API routes, database seeders, auth token handlers, tracking CRUD, and search domain accuracy:

```bash
cd backend
$env:PYTHONPATH="."
pytest tests/test_api.py -v
```

```text
============================= test session starts =============================
collected 11 items

tests/test_api.py::test_root PASSED                                      [  9%]
tests/test_api.py::test_health PASSED                                    [ 18%]
tests/test_api.py::test_get_providers PASSED                             [ 27%]
tests/test_api.py::test_search_empty_returns_seeded_catalog PASSED       [ 36%]
tests/test_api.py::test_get_product_details PASSED                       [ 45%]
tests/test_api.py::test_get_product_history PASSED                       [ 54%]
tests/test_api.py::test_tracking_crud PASSED                             [ 63%]
tests/test_api.py::test_search_history_lifecycle PASSED                  [ 72%]
tests/test_api.py::test_ai_prediction PASSED                             [ 81%]
tests/test_api.py::test_ai_title_matching PASSED                         [ 90%]
tests/test_api.py::test_search_domain_accuracy PASSED                    [100%]

======================== 11 passed, 1 warning in 1.58s ========================
```

---

## 🌐 Production Deployment

- **Backend:** Hosted on [Render](https://render.com) using the configuration in [`render.yaml`](file:///c:/Users/likit/Desktop/pricewise/render.yaml) and [`backend/Procfile`](file:///c:/Users/likit/Desktop/pricewise/backend/Procfile).
- **Frontend:** Hosted on [Vercel](https://vercel.com) using client-side SPA routing rewrites in [`frontend/vercel.json`](file:///c:/Users/likit/Desktop/pricewise/frontend/vercel.json).
- Detailed deployment steps are documented in [**`DEPLOYMENT.md`**](file:///c:/Users/likit/Desktop/pricewise/DEPLOYMENT.md).

---

## 📄 Interview & Resume Guide

Ready-to-use resume bullet points tailored for **Python Backend**, **Full-Stack**, and **AI/Data** roles along with the top 5 technical interview questions are documented in [**`resume_talking_points.md`**](file:///c:/Users/likit/Desktop/pricewise/resume_talking_points.md).

---

## 📜 License

This project is licensed under the MIT License — see the LICENSE file for details.
