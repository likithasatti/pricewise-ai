# 🚀 PriceWise AI — Production Deployment Guide

This guide walks you through deploying **PriceWise AI** live to the web for free using **Render** (FastAPI Python Backend) and **Vercel** (React Frontend).

---

## 📋 Architecture Overview

- **Backend (Python 3.11 / FastAPI):** Hosted on [Render.com](https://render.com) (Free Web Service)
- **Frontend (React 19 / Vite):** Hosted on [Vercel.com](https://vercel.com) (Free Fast Global CDN)
- **Database:** SQLite initialized automatically on startup (`pricewise.db`)

---

## 1️⃣ Step 1: Push Project to Your GitHub

Both Render and Vercel automatically build and deploy directly from your GitHub repository.

1. Open [github.com/new](https://github.com/new) and create a new repository:
   - Repository Name: `pricewise-ai`
   - Set to **Public**
   - Leave "Add a README" **unchecked**

2. Run the following commands in your terminal:
   ```bash
   cd c:\Users\likit\Desktop\pricewise

   # Link to your new repository (replace YOUR_USERNAME with your GitHub username):
   git remote add origin https://github.com/YOUR_USERNAME/pricewise-ai.git
   git branch -M main
   git push -u origin main
   ```

---

## 2️⃣ Step 2: Deploy Backend to Render (Free)

1. Go to [dashboard.render.com](https://dashboard.render.com) and log in with your GitHub account.
2. Click **"New +"** in the top right and select **"Web Service"**.
3. Choose **"Build and deploy from a Git repository"** and select your `pricewise-ai` repository.
4. Configure the Web Service settings:
   - **Name:** `pricewise-ai-backend` (or your preferred name)
   - **Region:** Singapore or Frankfurt (closest to your location)
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** `Free`
5. In **"Environment Variables"**, add:
   - `PYTHON_VERSION` = `3.11.0`
6. Click **"Create Web Service"**.
7. Wait ~2 minutes for the build to finish. Once live, Render will give you a public URL like:
   `https://pricewise-ai-backend.onrender.com`
8. Verify it works by opening in your browser:
   `https://pricewise-ai-backend.onrender.com/api/health`

---

## 3️⃣ Step 3: Deploy Frontend to Vercel (Free)

1. Go to [vercel.com](https://vercel.com) and log in with your GitHub account.
2. Click **"Add New..."** → **"Project"**.
3. Import your `pricewise-ai` repository.
4. In the configuration screen:
   - **Framework Preset:** `Vite`
   - **Root Directory:** Click "Edit" and select `frontend`
5. Expand **"Environment Variables"** and add:
   - **Key:** `VITE_API_BASE_URL`
   - **Value:** `https://pricewise-ai-backend.onrender.com/api` *(use your actual Render backend URL from Step 2)*
   - *(Optional Firebase key if using authentication)*:
     - `VITE_FIREBASE_API_KEY` = `your_firebase_api_key_here`
6. Click **"Deploy"**.
7. In ~30 seconds, Vercel will give you your live production URL:
   `https://pricewise-ai.vercel.app`

---

## 4️⃣ Step 4: Verification Checklist

1. Open your live Vercel URL in your browser.
2. Search for `Kurtha Sets`, `MacBook Air`, or `Washing Machine`.
3. Check that prices, store comparison links (Amazon & Flipkart), and deal recommendations appear.
4. Click on a product card to view the historical price chart and details.
5. Put your new live URLs on your resume:
   - **Live Demo:** `https://pricewise-ai.vercel.app`
   - **API Docs (Swagger):** `https://pricewise-ai-backend.onrender.com/docs`
   - **GitHub Repo:** `https://github.com/YOUR_USERNAME/pricewise-ai`
