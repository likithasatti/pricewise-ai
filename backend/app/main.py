import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.seeder import seed_database_if_empty
from app.routers import products, tracking, history, ai_insights
from app.services.scheduler import background_tracking_loop

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("pricewise")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup:
    logger.info("Initializing PriceWise AI database...")
    init_db()
    seed_database_if_empty()

    # Launch background tracking task
    tracking_task = asyncio.create_task(background_tracking_loop())
    logger.info("PriceWise AI backend initialized successfully!")

    yield

    # Shutdown:
    tracking_task.cancel()
    try:
        await tracking_task
    except asyncio.CancelledError:
        pass
    logger.info("PriceWise AI backend shut down cleanly.")


app = FastAPI(
    title="PriceWise AI API",
    description="Real-time multi-marketplace price comparison & AI deal prediction platform for Amazon & Flipkart.",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware (supports React frontend on Vite port 5173 / Vercel / Render)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(products.router)
app.include_router(tracking.router)
app.include_router(history.router)
app.include_router(ai_insights.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ONLINE",
        "service": "PriceWise AI Backend (Python / FastAPI)",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "search": "/api/products/search?query=macbook",
            "providers": "/api/products/providers",
            "tracking": "/api/tracking",
            "history": "/api/history",
            "ai_insights": "/api/ai/top-deals"
        }
    }


@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "UP",
        "app": "PriceWise AI",
        "framework": "FastAPI",
        "python": "3.11+"
    }
