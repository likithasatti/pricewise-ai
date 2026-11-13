# PriceWise AI 🛒🤖

> **Full-Stack Multi-Marketplace Price Comparison & AI Deal Prediction Platform**  
> Compare real-time prices across **Amazon and Flipkart**, forecast price trends, track price drops, and get AI-powered buying recommendations.

---

## 🏗️ Architecture

```text
                           PriceWise AI
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
          React Frontend                FastAPI Backend
          (Vite + Recharts)            (Python 3.11+ Async)
                 │                             │
                 │              ┌──────────────┴──────────────┐
                 │              │                             │
                 │         Amazon Provider            Flipkart Provider
                 │        (RapidAPI Real-Time)        (ReefAPI / RapidAPI)
                 │              │                             │
                 └──────────────┼─────────────────────────────┘
                                │
                      SQLite / Firestore Cache
                                │
                      AI Deal Prediction Engine
```

---

## ✨ Key Features

### 🔍 Unified Multi-Marketplace Search
- Concurrent asynchronous searches across **Amazon and Flipkart** using `asyncio.gather`.
- **NLP Semantic Matching:** Correlates disparate titles (e.g. Amazon's *"Apple iPhone 15 (128 GB) - Blue"* vs. Flipkart's *"Apple iPhone 15 128GB Blue 5G"*) using strict model-variant filtering and Jaccard token similarity.
- Displays savings, best price, ratings, stock availability, and verified store links.

### 🤖 AI Price Prediction & Deal Scoring
- **"Buy Now vs. Wait" Signals:** Evaluates time-series price records with linear regression trendlines and volatility metrics.
- **AI Deal Score (0–100):** Weighted algorithmic scoring incorporating price deviation from historical average, cross-store savings spread, user reviews, and price momentum.
- **Generative AI Advice:** Optional Google Gemini integration providing natural-language buying verdicts.

### 📈 Price Tracking & Drop Alerts
- Users can track products and specify target prices or percentage drops (e.g., alert if price drops by 5%).
- Background asynchronous scheduler continuously evaluates tracked items and logs/sends price drop notifications.

### 📊 Historical Analytics Visualization
- Interactive price trend charts powered by **Recharts**.
- Compares historical price trajectories across different stores.

### 🔐 User Isolation & Search History
- Firebase Auth ID token verification with user-specific data isolation.
- Automatic search history recording with duplicate suppression.

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** & npm

---

### 1. Backend Setup (FastAPI / Python)

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run backend (starts on http://localhost:8080)
python run.py
```

- 📖 **Interactive Swagger Docs:** http://localhost:8080/docs  
- 🩺 **Health Check:** http://localhost:8080/api/health

---

### 2. Frontend Setup (React / Vite)

```bash
cd frontend

# Install dependencies
npm install

# Run frontend (starts on http://localhost:5173)
npm run dev
```

Visit **http://localhost:5173** in your browser!

---

## 🧪 Running Backend Tests

The Python backend includes a full test suite covering all API endpoints, auth verification, tracking CRUD, and AI prediction:

```bash
cd backend
python -m pytest tests/test_api.py -v
```

---

## 📦 Tech Stack

- **Backend:** Python 3.11, FastAPI, Pydantic v2, Uvicorn, Httpx (Async HTTP), SQLite / Google Cloud Firestore
- **Frontend:** React 19, Vite, Recharts, Tailwind CSS / Custom CSS, Axios, Firebase Auth
- **AI / Data:** Scikit-learn / Linear Regression heuristics, NLP Token Matching, Google Gemini Flash API
- **APIs:** Real-Time Amazon Data API (RapidAPI), ReefAPI / Flipkart API
- **Deployment:** Docker, Render, Firebase Hosting
