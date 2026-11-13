# PriceWise AI — Frontend Client 🌐

> Modern, responsive React 19 web application for real-time multi-marketplace price comparison, deal forecasting, and price tracking.

---

## 🔗 Live Application

- **Live URL:** [https://pricewise-ai-delta.vercel.app/](https://pricewise-ai-delta.vercel.app/)
- **Backend API:** [https://pricewise-ai-backend-tz09.onrender.com/api](https://pricewise-ai-backend-tz09.onrender.com/api)

---

## 🛠️ Tech Stack

- **Framework:** React 19
- **Build Tool:** Vite 6
- **Routing:** React Router v7 (SPA with Vercel client-side rewrite)
- **Charts:** Recharts (Interactive price history time-series)
- **HTTP Client:** Axios (with automatic JWT header injection and timeout fallback)
- **Styling:** Tailwind CSS & modular CSS
- **Authentication:** Firebase Auth

---

## 🚀 Running Locally

```bash
# 1. Install dependencies
npm install

# 2. Start Vite dev server
npm run dev
```

Visit **http://localhost:5173** in your browser.

---

## 📦 Building for Production

```bash
npm run build
```

Production artifacts are bundled into `dist/`.
Client-side routing rules are defined in `vercel.json` to ensure deep links and refreshes on subroutes like `/results?q=MacBook` work seamlessly.
