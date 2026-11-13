import sqlite3
import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.config import settings

DB_FILE = settings.DATABASE_PATH


def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        canonical_name TEXT,
        product_name TEXT,
        brand TEXT,
        model TEXT,
        category TEXT,
        description TEXT,
        image_url TEXT,
        rating REAL,
        flipkart_price REAL,
        amazon_price REAL,
        croma_price REAL,
        created_at TEXT,
        updated_at TEXT
    )
    """)

    # Store Products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS store_products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        store TEXT NOT NULL,
        store_product_id TEXT,
        title TEXT,
        product_url TEXT,
        current_price REAL,
        currency TEXT DEFAULT 'INR',
        availability TEXT DEFAULT 'IN_STOCK',
        status TEXT DEFAULT 'LIVE',
        image_url TEXT,
        last_checked_at TEXT,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
    )
    """)

    # Price Records table (history points)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS price_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        store_product_id INTEGER,
        product_id INTEGER,
        store TEXT,
        price REAL NOT NULL,
        currency TEXT DEFAULT 'INR',
        availability TEXT DEFAULT 'IN_STOCK',
        status TEXT DEFAULT 'LIVE',
        source TEXT,
        checked_at TEXT,
        FOREIGN KEY (store_product_id) REFERENCES store_products(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
    )
    """)

    # Tracked Products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tracked_products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        store_product_id INTEGER NOT NULL,
        product_id INTEGER,
        user_id TEXT NOT NULL,
        user_email TEXT,
        initial_price REAL,
        target_price REAL,
        target_drop_percentage REAL,
        last_notified_price REAL,
        active INTEGER DEFAULT 1,
        last_checked_at TEXT,
        created_at TEXT,
        FOREIGN KEY (store_product_id) REFERENCES store_products(id) ON DELETE CASCADE
    )
    """)

    # User Search History table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_search_history (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        query TEXT NOT NULL,
        result_count INTEGER DEFAULT 0,
        top_product_name TEXT,
        top_product_price REAL,
        top_product_store TEXT,
        top_product_image TEXT,
        top_product_id INTEGER,
        created_at TEXT
    )
    """)

    # Notifications table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notification_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracked_product_id INTEGER,
        recipient TEXT,
        channel TEXT DEFAULT 'EMAIL',
        status TEXT DEFAULT 'SENT',
        message TEXT,
        sent_at TEXT
    )
    """)

    conn.commit()
    conn.close()


# Database helper functions

def db_find_all_products() -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY id ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def db_find_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def db_find_product_by_name(name: str) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM products WHERE LOWER(canonical_name) = LOWER(?) OR LOWER(product_name) = LOWER(?) LIMIT 1",
        (name.strip(), name.strip())
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def db_search_products(query: str) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    pattern = f"%{query.strip().lower()}%"
    cursor.execute(
        """
        SELECT * FROM products
        WHERE LOWER(canonical_name) LIKE ?
           OR LOWER(product_name) LIKE ?
           OR LOWER(brand) LIKE ?
           OR LOWER(description) LIKE ?
        ORDER BY id ASC
        """,
        (pattern, pattern, pattern, pattern)
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def db_save_product(data: Dict[str, Any]) -> int:
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()

    pid = data.get("id")
    existing_row = None
    if pid:
        cursor.execute("SELECT id FROM products WHERE id = ?", (pid,))
        existing_row = cursor.fetchone()

    if existing_row:
        cursor.execute("""
            UPDATE products SET
                canonical_name = ?, product_name = ?, brand = ?, model = ?, category = ?,
                description = ?, image_url = ?, rating = ?, flipkart_price = ?,
                amazon_price = ?, croma_price = ?, updated_at = ?
            WHERE id = ?
        """, (
            data.get("canonical_name"), data.get("product_name"), data.get("brand"),
            data.get("model"), data.get("category"), data.get("description"),
            data.get("image_url"), data.get("rating"), data.get("flipkart_price"),
            data.get("amazon_price"), data.get("croma_price"), now, pid
        ))
        conn.commit()
        conn.close()
        return pid
    else:
        if pid:
            cursor.execute("""
                INSERT INTO products (
                    id, canonical_name, product_name, brand, model, category,
                    description, image_url, rating, flipkart_price,
                    amazon_price, croma_price, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pid, data.get("canonical_name"), data.get("product_name"), data.get("brand"),
                data.get("model"), data.get("category"), data.get("description"),
                data.get("image_url"), data.get("rating"), data.get("flipkart_price"),
                data.get("amazon_price"), data.get("croma_price"), now, now
            ))
            new_id = pid
        else:
            cursor.execute("""
                INSERT INTO products (
                    canonical_name, product_name, brand, model, category,
                    description, image_url, rating, flipkart_price,
                    amazon_price, croma_price, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("canonical_name"), data.get("product_name"), data.get("brand"),
                data.get("model"), data.get("category"), data.get("description"),
                data.get("image_url"), data.get("rating"), data.get("flipkart_price"),
                data.get("amazon_price"), data.get("croma_price"), now, now
            ))
            new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return new_id


def db_find_store_products(product_id: int) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM store_products WHERE product_id = ?", (product_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def db_find_store_product_by_id(store_product_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM store_products WHERE id = ?", (store_product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def db_find_store_product(product_id: int, store: str) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM store_products WHERE product_id = ? AND UPPER(store) = UPPER(?) LIMIT 1",
        (product_id, store.strip())
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def db_save_store_product(data: Dict[str, Any]) -> int:
    conn = get_db()
    cursor = conn.cursor()
    sp_id = data.get("id")
    existing_row = None
    if sp_id:
        cursor.execute("SELECT id FROM store_products WHERE id = ?", (sp_id,))
        existing_row = cursor.fetchone()

    if existing_row:
        cursor.execute("""
            UPDATE store_products SET
                product_id = ?, store = ?, store_product_id = ?, title = ?,
                product_url = ?, current_price = ?, currency = ?, availability = ?,
                status = ?, image_url = ?, last_checked_at = ?
            WHERE id = ?
        """, (
            data.get("product_id"), data.get("store"), data.get("store_product_id"),
            data.get("title"), data.get("product_url"), data.get("current_price"),
            data.get("currency", "INR"), data.get("availability", "IN_STOCK"),
            data.get("status", "LIVE"), data.get("image_url"),
            data.get("last_checked_at", datetime.now().isoformat()), sp_id
        ))
        conn.commit()
        conn.close()
        return sp_id
    else:
        if sp_id:
            cursor.execute("""
                INSERT INTO store_products (
                    id, product_id, store, store_product_id, title, product_url,
                    current_price, currency, availability, status, image_url, last_checked_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sp_id, data.get("product_id"), data.get("store"), data.get("store_product_id"),
                data.get("title"), data.get("product_url"), data.get("current_price"),
                data.get("currency", "INR"), data.get("availability", "IN_STOCK"),
                data.get("status", "LIVE"), data.get("image_url"),
                data.get("last_checked_at", datetime.now().isoformat())
            ))
            new_id = sp_id
        else:
            cursor.execute("""
                INSERT INTO store_products (
                    product_id, store, store_product_id, title, product_url,
                    current_price, currency, availability, status, image_url, last_checked_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("product_id"), data.get("store"), data.get("store_product_id"),
                data.get("title"), data.get("product_url"), data.get("current_price"),
                data.get("currency", "INR"), data.get("availability", "IN_STOCK"),
                data.get("status", "LIVE"), data.get("image_url"),
                data.get("last_checked_at", datetime.now().isoformat())
            ))
            new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return new_id


def db_find_price_records(product_id: int) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM price_records WHERE product_id = ? ORDER BY checked_at ASC",
        (product_id,)
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def db_find_latest_price_record(store_product_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM price_records WHERE store_product_id = ? ORDER BY checked_at DESC LIMIT 1",
        (store_product_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def db_save_price_record(data: Dict[str, Any]) -> int:
    conn = get_db()
    cursor = conn.cursor()
    checked_at = data.get("checked_at") or datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO price_records (
            store_product_id, product_id, store, price, currency,
            availability, status, source, checked_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("store_product_id"), data.get("product_id"), data.get("store"),
        data.get("price"), data.get("currency", "INR"), data.get("availability", "IN_STOCK"),
        data.get("status", "LIVE"), data.get("source"), checked_at
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


# Tracking
def db_find_tracked_products(user_id: str) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tp.*, sp.store, sp.product_url, sp.current_price, sp.title as sp_title,
               sp.image_url as sp_image, p.canonical_name, p.image_url as p_image, p.id as p_id
        FROM tracked_products tp
        LEFT JOIN store_products sp ON tp.store_product_id = sp.id
        LEFT JOIN products p ON sp.product_id = p.id
        WHERE tp.user_id = ? AND tp.active = 1
        ORDER BY tp.created_at DESC
    """, (user_id.strip(),))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def db_find_tracked_product_by_id(tracked_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tp.*, sp.store, sp.product_url, sp.current_price, sp.title as sp_title,
               sp.image_url as sp_image, p.canonical_name, p.image_url as p_image, p.id as p_id
        FROM tracked_products tp
        LEFT JOIN store_products sp ON tp.store_product_id = sp.id
        LEFT JOIN products p ON sp.product_id = p.id
        WHERE tp.id = ?
    """, (tracked_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def db_find_active_tracked(store_product_id: int, user_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM tracked_products
        WHERE store_product_id = ? AND user_id = ? AND active = 1
        LIMIT 1
    """, (store_product_id, user_id.strip()))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def db_find_all_active_tracked() -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tracked_products WHERE active = 1")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def db_save_tracked_product(data: Dict[str, Any]) -> int:
    conn = get_db()
    cursor = conn.cursor()
    tid = data.get("id")
    now = datetime.now().isoformat()

    if tid:
        cursor.execute("""
            UPDATE tracked_products SET
                target_price = ?, target_drop_percentage = ?, user_email = ?,
                last_notified_price = ?, active = ?, last_checked_at = ?
            WHERE id = ?
        """, (
            data.get("target_price"), data.get("target_drop_percentage"),
            data.get("user_email"), data.get("last_notified_price"),
            1 if data.get("active", True) else 0,
            data.get("last_checked_at", now), tid
        ))
        conn.commit()
        conn.close()
        return tid
    else:
        cursor.execute("""
            INSERT INTO tracked_products (
                store_product_id, product_id, user_id, user_email, initial_price,
                target_price, target_drop_percentage, last_notified_price,
                active, last_checked_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("store_product_id"), data.get("product_id"), data.get("user_id"),
            data.get("user_email"), data.get("initial_price"), data.get("target_price"),
            data.get("target_drop_percentage", 5.0), data.get("last_notified_price"),
            1, now, now
        ))
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return new_id


def db_stop_tracking(tracked_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tracked_products SET active = 0 WHERE id = ?", (tracked_id,))
    conn.commit()
    conn.close()


# Search History
def db_find_user_history(user_id: str) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM user_search_history WHERE user_id = ? ORDER BY created_at DESC",
        (user_id.strip(),)
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def db_save_user_history(data: Dict[str, Any]) -> str:
    conn = get_db()
    cursor = conn.cursor()
    history_id = data.get("id") or str(uuid.uuid4())
    now = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO user_search_history (
            id, user_id, query, result_count, top_product_name,
            top_product_price, top_product_store, top_product_image,
            top_product_id, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        history_id, data.get("user_id"), data.get("query"),
        data.get("result_count", 0), data.get("top_product_name"),
        data.get("top_product_price"), data.get("top_product_store"),
        data.get("top_product_image"), data.get("top_product_id"),
        data.get("created_at") or now
    ))
    conn.commit()
    conn.close()
    return history_id


def db_delete_user_history(user_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_search_history WHERE user_id = ?", (user_id.strip(),))
    conn.commit()
    conn.close()


# Auto-initialize tables
init_db()
