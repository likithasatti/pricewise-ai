import logging
from datetime import datetime, timedelta
from app.database import (
    db_find_all_products,
    db_save_product,
    db_save_store_product,
    db_save_price_record,
    db_find_store_products
)

logger = logging.getLogger(__name__)

BENCHMARK_PRODUCTS = [
    {
        "id": 1,
        "canonical_name": "MacBook Air M2",
        "product_name": "Apple 2022 MacBook Air M2 - 8GB RAM, 256GB SSD",
        "brand": "Apple",
        "model": "MacBook Air M2 (2022)",
        "category": "Laptops",
        "description": "13.6-inch Liquid Retina Display, 8GB Unified Memory, 256GB SSD Storage, Backlit Magic Keyboard, 1080p FaceTime HD Camera.",
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80",
        "rating": 4.8,
        "amazon_price": 71499.0,
        "flipkart_price": 73990.0,
        "history": [74990.0, 73499.0, 72999.0, 71499.0]
    },
    {
        "id": 2,
        "canonical_name": "iPhone 15",
        "product_name": "Apple iPhone 15 (128 GB) - Black",
        "brand": "Apple",
        "model": "iPhone 15 (128 GB)",
        "category": "Smartphones",
        "description": "Dynamic Island, 48MP Main Camera with 2x Telephoto, USB-C Connectivity, All-day Battery Life, Precision-Engineered Color-Infused Glass.",
        "image_url": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?auto=format&fit=crop&w=600&q=80",
        "rating": 4.7,
        "amazon_price": 65999.0,
        "flipkart_price": 66499.0,
        "history": [69990.0, 68499.0, 66999.0, 65999.0]
    },
    {
        "id": 3,
        "canonical_name": "Samsung Galaxy S24",
        "product_name": "Samsung Galaxy S24 5G (Onyx Black, 8GB RAM, 128GB)",
        "brand": "Samsung",
        "model": "Galaxy S24 5G",
        "category": "Smartphones",
        "description": "Galaxy AI features: Circle to Search, Live Translate, Note Assist. Dynamic AMOLED 2X Display, Snapdragon 8 Gen 3 Processor.",
        "image_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?auto=format&fit=crop&w=600&q=80",
        "rating": 4.6,
        "amazon_price": 64999.0,
        "flipkart_price": 67999.0,
        "history": [67999.0, 66499.0, 65999.0, 64999.0]
    },
    {
        "id": 4,
        "canonical_name": "Sony WH-1000XM5 Wireless Headphones",
        "product_name": "Sony WH-1000XM5 Noise Cancelling Wireless Headphones - Silver",
        "brand": "Sony",
        "model": "WH-1000XM5",
        "category": "Audio",
        "description": "Industry Leading Wireless Noise Cancelling Headphones with 8 Microphones, Auto NC Optimizer, 30-Hour Battery Life, Ultra-comfortable fit.",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=600&q=80",
        "rating": 4.7,
        "amazon_price": 26990.0,
        "flipkart_price": 28490.0,
        "history": [29990.0, 28490.0, 27990.0, 26990.0]
    }
]


def seed_database_if_empty():
    existing = db_find_all_products()
    if existing and len(existing) > 0:
        logger.info(f"Database contains {len(existing)} existing products. Skipping initial seed.")
        return

    logger.info("Database is empty. Seeding verified benchmark products and price histories...")
    now = datetime.now()

    for item in BENCHMARK_PRODUCTS:
        # 1. Product
        pid = db_save_product({
            "id": item["id"],
            "canonical_name": item["canonical_name"],
            "product_name": item["product_name"],
            "brand": item["brand"],
            "model": item["model"],
            "category": item["category"],
            "description": item["description"],
            "image_url": item["image_url"],
            "rating": item["rating"],
            "amazon_price": item["amazon_price"],
            "flipkart_price": item["flipkart_price"]
        })

        # 2. Amazon Store Product
        amz_sp_id = db_save_store_product({
            "product_id": pid,
            "store": "AMAZON",
            "store_product_id": f"AMZ-{pid}",
            "title": f"{item['canonical_name']} on Amazon",
            "product_url": "https://www.amazon.in",
            "current_price": item["amazon_price"],
            "currency": "INR",
            "availability": "IN_STOCK",
            "status": "SAMPLE_DATA",
            "image_url": item["image_url"],
            "last_checked_at": now.isoformat()
        })

        # 3. Flipkart Store Product
        flp_sp_id = db_save_store_product({
            "product_id": pid,
            "store": "FLIPKART",
            "store_product_id": f"FLP-{pid}",
            "title": f"{item['canonical_name']} on Flipkart",
            "product_url": "https://www.flipkart.com",
            "current_price": item["flipkart_price"],
            "currency": "INR",
            "availability": "IN_STOCK",
            "status": "SAMPLE_DATA",
            "image_url": item["image_url"],
            "last_checked_at": now.isoformat()
        })

        # 4. Price History Points for Recharts
        history = item.get("history", [])
        days_back = len(history) * 3
        for i, price in enumerate(history):
            pt_date = now - timedelta(days=days_back - (i * 3))
            db_save_price_record({
                "store_product_id": amz_sp_id,
                "product_id": pid,
                "store": "AMAZON",
                "price": price,
                "currency": "INR",
                "availability": "IN_STOCK",
                "status": "SAMPLE_DATA",
                "source": "INITIAL_CATALOG",
                "checked_at": pt_date.isoformat()
            })

    logger.info("Successfully seeded database with benchmark catalog products!")
