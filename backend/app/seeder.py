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
    # Laptops
    {
        "id": 1,
        "canonical_name": "MacBook Air M2",
        "product_name": "Apple 2022 MacBook Air M2 - 8GB RAM, 256GB SSD (Space Grey)",
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
        "id": 5,
        "canonical_name": "Dell XPS 13 Laptop",
        "product_name": "Dell XPS 13 9315 Laptop - Intel Core i7 12th Gen, 16GB RAM, 512GB SSD",
        "brand": "Dell",
        "model": "XPS 13",
        "category": "Laptops",
        "description": "13.4-inch FHD+ InfinityEdge Display, Intel Iris Xe Graphics, Backlit Keyboard with Fingerprint Reader, Windows 11.",
        "image_url": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=600&q=80",
        "rating": 4.6,
        "amazon_price": 114990.0,
        "flipkart_price": 119990.0,
        "history": [124990.0, 121990.0, 118990.0, 114990.0]
    },
    {
        "id": 6,
        "canonical_name": "HP Pavilion 15 Gaming Laptop",
        "product_name": "HP Pavilion 15 - AMD Ryzen 5 5600H, 16GB RAM, 512GB SSD, RTX 3050",
        "brand": "HP",
        "model": "Pavilion 15",
        "category": "Laptops",
        "description": "15.6-inch FHD 144Hz Micro-Edge Anti-Glare Display, NVIDIA GeForce RTX 3050 4GB Graphics, B&O Audio.",
        "image_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=600&q=80",
        "rating": 4.5,
        "amazon_price": 54990.0,
        "flipkart_price": 57990.0,
        "history": [59990.0, 58490.0, 56990.0, 54990.0]
    },
    {
        "id": 7,
        "canonical_name": "ASUS TUF Gaming F15 Laptop",
        "product_name": "ASUS TUF Gaming F15 - Intel Core i5 11th Gen, 16GB RAM, 512GB SSD, RTX 2050",
        "brand": "ASUS",
        "model": "TUF F15",
        "category": "Laptops",
        "description": "15.6-inch 144Hz Refresh Rate Display, Military-Grade Durability, RGB Backlit Keyboard, 48Wh Battery.",
        "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=600&q=80",
        "rating": 4.4,
        "amazon_price": 52990.0,
        "flipkart_price": 54990.0,
        "history": [56990.0, 55490.0, 53990.0, 52990.0]
    },
    {
        "id": 8,
        "canonical_name": "Lenovo IdeaPad Slim 3 Laptop",
        "product_name": "Lenovo IdeaPad Slim 3 - Intel Core i3 12th Gen, 8GB RAM, 512GB SSD",
        "brand": "Lenovo",
        "model": "IdeaPad Slim 3",
        "category": "Laptops",
        "description": "15.6-inch FHD Thin & Light Laptop, Rapid Charge, Dolby Audio, Windows 11 Home + MS Office.",
        "image_url": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=600&q=80",
        "rating": 4.3,
        "amazon_price": 36990.0,
        "flipkart_price": 38490.0,
        "history": [39990.0, 38990.0, 37490.0, 36990.0]
    },

    # Smartphones
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
        "id": 9,
        "canonical_name": "Apple iPhone 15 Pro Max",
        "product_name": "Apple iPhone 15 Pro Max (256 GB) - Natural Titanium",
        "brand": "Apple",
        "model": "iPhone 15 Pro Max",
        "category": "Smartphones",
        "description": "Forged in Titanium, A17 Pro Chip, Action Button, 48MP Main Camera with 5x Telephoto, Super Retina XDR with ProMotion.",
        "image_url": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&w=600&q=80",
        "rating": 4.8,
        "amazon_price": 134900.0,
        "flipkart_price": 139900.0,
        "history": [144900.0, 139900.0, 137500.0, 134900.0]
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
        "id": 10,
        "canonical_name": "OnePlus 12 5G",
        "product_name": "OnePlus 12 5G (Silky Black, 12GB RAM, 256GB Storage)",
        "brand": "OnePlus",
        "model": "OnePlus 12",
        "category": "Smartphones",
        "description": "Snapdragon 8 Gen 3, 4th Gen Hasselblad Camera for Mobile, 5400mAh Battery with 100W SUPERVOOC charging.",
        "image_url": "https://images.unsplash.com/photo-1565849904461-04a58ad377e0?auto=format&fit=crop&w=600&q=80",
        "rating": 4.6,
        "amazon_price": 64999.0,
        "flipkart_price": 66999.0,
        "history": [69999.0, 67999.0, 66499.0, 64999.0]
    },
    {
        "id": 11,
        "canonical_name": "Google Pixel 8",
        "product_name": "Google Pixel 8 5G (Hazel, 128 GB) - 8GB RAM",
        "brand": "Google",
        "model": "Pixel 8",
        "category": "Smartphones",
        "description": "Google Tensor G3 chip, Best Take, Audio Magic Eraser, Macro Focus, 24+ hour battery, 7 years of OS updates.",
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=600&q=80",
        "rating": 4.5,
        "amazon_price": 49999.0,
        "flipkart_price": 52499.0,
        "history": [55999.0, 53499.0, 51999.0, 49999.0]
    },

    # Audio & Headphones
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
    },
    {
        "id": 12,
        "canonical_name": "Apple AirPods Pro (2nd Generation)",
        "product_name": "Apple AirPods Pro (2nd Gen) with MagSafe Case (USB-C)",
        "brand": "Apple",
        "model": "AirPods Pro 2",
        "category": "Audio",
        "description": "Up to 2x more Active Noise Cancellation, Transparency mode, Adaptive Audio, Personalized Spatial Audio with dynamic head tracking.",
        "image_url": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?auto=format&fit=crop&w=600&q=80",
        "rating": 4.8,
        "amazon_price": 20990.0,
        "flipkart_price": 22490.0,
        "history": [24990.0, 22990.0, 21990.0, 20990.0]
    },
    {
        "id": 13,
        "canonical_name": "boAt Rockerz 450 Bluetooth Headphones",
        "product_name": "boAt Rockerz 450 Bluetooth On-Ear Headphones with Mic - Luscious Black",
        "brand": "boAt",
        "model": "Rockerz 450",
        "category": "Audio",
        "description": "15 Hours Playback, 40mm Dynamic Drivers, Padded Ear Cushions, Integrated Controls, Dual Modes (Bluetooth + AUX).",
        "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=600&q=80",
        "rating": 4.3,
        "amazon_price": 1499.0,
        "flipkart_price": 1699.0,
        "history": [1999.0, 1799.0, 1649.0, 1499.0]
    },

    # Smartwatches & Tablets
    {
        "id": 14,
        "canonical_name": "Apple Watch Series 9",
        "product_name": "Apple Watch Series 9 (GPS 41mm) - Midnight Aluminium Case with Sport Band",
        "brand": "Apple",
        "model": "Series 9",
        "category": "Smartwatches",
        "description": "S9 SiP chip with Double Tap gesture, brighter Always-On display, ECG and Blood Oxygen apps, Advanced workout metrics.",
        "image_url": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=600&q=80",
        "rating": 4.7,
        "amazon_price": 37900.0,
        "flipkart_price": 39900.0,
        "history": [41900.0, 39900.0, 38500.0, 37900.0]
    },
    {
        "id": 15,
        "canonical_name": "Samsung Galaxy Watch 6",
        "product_name": "Samsung Galaxy Watch 6 Bluetooth (40mm, Graphite)",
        "brand": "Samsung",
        "model": "Galaxy Watch 6",
        "category": "Smartwatches",
        "description": "Advanced sleep coaching, ECG monitoring, Sapphire Crystal glass, Body Composition analysis, Wear OS with One UI Watch.",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=600&q=80",
        "rating": 4.5,
        "amazon_price": 19999.0,
        "flipkart_price": 21999.0,
        "history": [24999.0, 22999.0, 20999.0, 19999.0]
    },
    {
        "id": 16,
        "canonical_name": "Apple iPad Air M2",
        "product_name": "Apple 11-inch iPad Air M2 chip (Wi-Fi, 128GB) - Space Grey",
        "brand": "Apple",
        "model": "iPad Air M2",
        "category": "Tablets",
        "description": "Liquid Retina display, M2 chip, 12MP landscape front camera with Center Stage, 12MP back camera, Touch ID, Wi-Fi 6E.",
        "image_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=600&q=80",
        "rating": 4.8,
        "amazon_price": 54900.0,
        "flipkart_price": 57900.0,
        "history": [59900.0, 57900.0, 56000.0, 54900.0]
    }
]


def seed_database_if_empty(force: bool = False):
    existing = db_find_all_products()
    existing_ids = {p["id"] for p in existing}
    now = datetime.now()

    for item in BENCHMARK_PRODUCTS:
        pid = item["id"]
        if pid in existing_ids and not force:
            continue

        # 1. Product
        db_save_product({
            "id": pid,
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
        amz_url = f"https://www.amazon.in/s?k={item['canonical_name'].replace(' ', '+')}"
        amz_sp_id = db_save_store_product({
            "product_id": pid,
            "store": "AMAZON",
            "store_product_id": f"AMZ-{pid}",
            "title": f"{item['canonical_name']} on Amazon",
            "product_url": amz_url,
            "current_price": item["amazon_price"],
            "currency": "INR",
            "availability": "IN_STOCK",
            "status": "LIVE",
            "image_url": item["image_url"],
            "last_checked_at": now.isoformat()
        })

        # 3. Flipkart Store Product
        flp_url = f"https://www.flipkart.com/search?q={item['canonical_name'].replace(' ', '+')}"
        flp_sp_id = db_save_store_product({
            "product_id": pid,
            "store": "FLIPKART",
            "store_product_id": f"FLP-{pid}",
            "title": f"{item['canonical_name']} on Flipkart",
            "product_url": flp_url,
            "current_price": item["flipkart_price"],
            "currency": "INR",
            "availability": "IN_STOCK",
            "status": "LIVE",
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
                "status": "LIVE",
                "source": "INITIAL_CATALOG",
                "checked_at": pt_date.isoformat()
            })

    logger.info("Benchmark catalog seeded with verified products and price histories.")
