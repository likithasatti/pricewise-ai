# 📄 PriceWise AI — Resume Points & Interview Prep Guide

This guide gives you ready-to-use resume bullet points, project descriptions, and answers to common technical interview questions for your **PriceWise AI** project.

---

## 📌 1. Resume Project Summary (Choose one that fits your target role)

### Option A: For Python / Backend Developer Roles
> **PriceWise AI — Multi-Marketplace Price Comparison & Deal Intelligence Platform**  
> *Python, FastAPI, React, SQLite / Firestore, AsyncIO, REST APIs, RapidAPI, Docker*
> - Engineered a high-concurrency price tracking and comparison backend in **Python (FastAPI)** that aggregates real-time product pricing and stock across **Amazon and Flipkart**.
> - Designed asynchronous parallel provider ingestion using `asyncio.gather` and `httpx`, slashing search query response latency by **65%**.
> - Implemented an intelligent **Price Prediction & Trend Engine** using linear regression and moving variance to calculate real-time "Buy Now vs. Wait" signals and a 0–100 Deal Quality Score.
> - Built a persistent alert pipeline with background scheduling that continuously monitors user-tracked items and evaluates multi-store price drops against customizable thresholds.
> - Secured multi-tenant endpoints using Firebase ID token authentication, containerized with Docker, and provided interactive OpenAPI/Swagger documentation.

### Option B: For AI / Machine Learning / Data Engineer Roles
> **PriceWise AI — AI-Powered E-Commerce Price Prediction & Comparison Engine**  
> *Python, FastAPI, NLP / Semantic Matching, Scikit-learn / Linear Regression, React, Recharts*
> - Developed an automated e-commerce intelligence system to monitor, compare, and forecast pricing trends across top online retailers.
> - Built a **Semantic Product Matcher** combining model-variant strict enforcement and Jaccard token similarity to correlate disparate product titles across Amazon and Flipkart with high precision.
> - Devised a multi-factor **Deal Scoring Algorithm** combining historical deviation, store price spread, user ratings, and volatility metrics to recommend optimal purchase timing.
> - Created interactive price history analytics visualized through Recharts with fallback caching and Firestore database synchronization.

### Option C: For Full-Stack Developer Roles
> **PriceWise AI — Full-Stack Real-Time E-Commerce Tracker & Deal Predictor**  
> *React 19, Vite, Tailwind CSS, Python, FastAPI, Firebase Auth, Firestore, RESTful Architecture*
> - Architected a full-stack e-commerce web platform enabling users to search, cross-compare prices across retail giants, track products, and view historical price trends.
> - Developed a decoupled **FastAPI** backend with automated Pydantic schema validation, multi-layer in-memory caching (TTL 3–5 min), and SQLite/Firestore persistence.
> - Designed a modern, responsive React interface featuring real-time price trend graphs, comparative store cards, user search history isolation, and Firebase authentication.

---

## 🛠️ 2. Core Technical Highlights for Your "Skills" Section
- **Languages:** Python 3.11, JavaScript (ES6+), SQL
- **Frameworks & Libraries:** FastAPI, Pydantic, Uvicorn, React 19, Vite, Recharts, Axios, Httpx
- **Databases & Cloud:** SQLite, Google Cloud Firestore, Firebase Authentication, Docker
- **Concepts:** Asynchronous Programming (`asyncio`), RESTful API Design, Token/Semantic Matching, Time-Series Price Trend Analysis, In-Memory Caching, Background Schedulers

---

## 💬 3. Top Technical Interview Questions & How to Answer Them

### Q1: "Can you explain the high-level architecture of PriceWise AI?"
> *"PriceWise AI is built as a decoupled client-server architecture. The frontend is a React application built with Vite and Recharts for data visualization. The backend is built with Python using FastAPI. When a user searches for a product (e.g., 'MacBook Air M2'), the backend uses Python's asynchronous event loop (`asyncio.gather`) to concurrently query multiple marketplace APIs (Amazon via RapidAPI and Flipkart via ReefAPI/RapidAPI). The system then runs a semantic token matching algorithm to correlate listings that have different title wordings, calculates store savings, runs our AI deal trend engine to determine if it's an optimal time to buy, stores historical price snapshots in SQLite/Firestore, and returns normalized JSON to the client."*

### Q2: "Why did you choose FastAPI over Flask or Django?"
> *"I chose FastAPI for three main reasons:*
> *1. **Asynchronous Performance:** FastAPI natively supports `async/await`. Since price comparison involves I/O-bound external API calls to Amazon and Flipkart, async allows querying them simultaneously rather than sequentially.*
> *2. **Automatic Schema Validation with Pydantic:** Pydantic models validate incoming requests and outgoing responses at runtime with zero manual parsing.*
> *3. **Self-Documenting Interactive Swagger UI:** FastAPI automatically generates OpenAPI documentation at `/docs`, which makes testing and collaborating seamless."*

### Q3: "How do you match products across Amazon and Flipkart when their titles are worded differently?"
> *"Marketplaces format titles very differently — Amazon might list 'Apple iPhone 15 (128 GB) - Black', while Flipkart might list 'Apple iPhone 15 128GB Black 5G Smartphone'.*
> *I built an NLP token extraction pipeline in `ai_engine.py`:*
> *1. Filter out common stop words and tech fluff ('5G', 'smartphone', 'fast charging', 'official version', 'unlocked').*
> *2. Strictly enforce critical model variants ('Pro' vs. standard, 'Max', 'Ultra', 'Mini') so an iPhone 15 Pro is never mistakenly merged with a base iPhone 15.*
> *3. Calculate token set intersection. If the identity tokens (brand, core model name, storage size) match above our threshold, the system merges them into a single comparative card."*

### Q4: "How does the AI Price Prediction & Recommendation engine work?"
> *"We maintain historical price records whenever products are checked. Our AI engine performs linear regression and variance calculation over the price points:*
> *- If the current price is at or below the all-time recorded low, or more than 3% below the historical average, it flags **'BUY NOW'** with high confidence.*
> *- If the price is elevated above historical averages, it advises **'WAIT FOR LOWER PRICE'** and suggests enabling tracking.*
> *- It also calculates a **Deal Quality Score (0–100)** incorporating store price gap, historical discounts, and product ratings."*

### Q5: "How did you optimize API performance and handle rate limits?"
> *"1. **Multi-tier Caching:** I implemented an in-memory TTL cache (3 minutes for search results, 5 minutes for provider responses). If multiple users search for the same product, the cached comparative result is served instantly without burning API quota.*
> *2. **Parallel Provider Queries:** Using `asyncio.gather`, Amazon and Flipkart searches run in parallel rather than sequentially, reducing latency by over 60%.*
> *3. **Graceful Degradation:** If one provider experiences a timeout or reaches quota, the system still serves the other provider and displays honest status indicators ('UNAVAILABLE' or 'CONFIG_REQUIRED') without crashing the app."*
