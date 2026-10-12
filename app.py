import os
import re
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image
from werkzeug.security import check_password_hash, generate_password_hash


DB_PATH = Path(__file__).resolve().parent / "stylekart.db"
UPLOADS_DIR = Path(__file__).resolve().parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT,
            brand TEXT,
            description TEXT,
            price REAL NOT NULL,
            discount REAL DEFAULT 0,
            image_url TEXT,
            sizes TEXT,
            colors TEXT,
            stock INTEGER DEFAULT 0,
            popularity INTEGER DEFAULT 0,
            featured INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            is_admin INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS cart (
            cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            size TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            added_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            address TEXT,
            payment_method TEXT NOT NULL,
            subtotal REAL NOT NULL,
            shipping REAL NOT NULL,
            total REAL NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS order_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            size TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(order_id),
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        )
        """
    )
    conn.commit()
    conn.close()


def seed_default_accounts():
    conn = get_db_connection()
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if user_count == 0:
        conn.execute(
            "INSERT INTO users (full_name, email, password_hash, phone, address, is_admin) VALUES (?, ?, ?, ?, ?, ?)",
            (
                "StyleKart Admin",
                "admin@stylekart.com",
                generate_password_hash("admin123"),
                "+919999999999",
                "12 Fashion Avenue, Bengaluru",
                1,
            ),
        )
        conn.execute(
            "INSERT INTO users (full_name, email, password_hash, phone, address, is_admin) VALUES (?, ?, ?, ?, ?, ?)",
            (
                "Demo Customer",
                "customer@stylekart.com",
                generate_password_hash("customer123"),
                "+919876543210",
                "28 Market Road, Mumbai",
                0,
            ),
        )
        conn.commit()
    conn.close()


def seed_products():
    conn = get_db_connection()
    count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    if count > 0:
        conn.close()
        return

    product_rows = [
        (
            "AeroFlex Running Tee",
            "Men",
            "Tops",
            "Puma",
            "Lightweight everyday tee engineered for comfort and movement.",
            1499,
            15,
            "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=900&q=80",
            "S,M,L,XL",
            "Black,White,Blue",
            42,
            92,
            1,
        ),
        (
            "Urban Edge Denim",
            "Men",
            "Bottomwear",
            "Levi's",
            "Modern fit denim designed for all-day casual wear.",
            2299,
            20,
            "https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=900&q=80",
            "30,32,34,36",
            "Indigo,Black",
            20,
            88,
            1,
        ),
        (
            "Luna Satin Dress",
            "Women",
            "Dresses",
            "H&M",
            "Flowing satin dress with a flattering silhouette for day-to-night styling.",
            3199,
            25,
            "https://images.unsplash.com/photo-1496747611176-843222e1e57c?auto=format&fit=crop&w=900&q=80",
            "XS,S,M,L",
            "Rose,Black,Beige",
            18,
            95,
            1,
        ),
        (
            "Velvet Bloom Blazer",
            "Women",
            "Ethnic & Workwear",
            "Zara",
            "Tailored blazer for office-ready statement looks.",
            3999,
            30,
            "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=900&q=80",
            "S,M,L,XL",
            "Navy,Black,Stone",
            14,
            90,
            1,
        ),
        (
            "Sunbeam Kids Hoodie",
            "Kids",
            "Outerwear",
            "MiniM",
            "Cozy fleece hoodie made for active play and comfort.",
            1299,
            18,
            "https://images.unsplash.com/photo-1519345182560-3f2917c472ef?auto=format&fit=crop&w=900&q=80",
            "4Y,6Y,8Y,10Y",
            "Sky,Coral,Green",
            35,
            84,
            1,
        ),
        (
            "BrightStep Sneakers",
            "Footwear",
            "Sneakers",
            "Nike",
            "All-day cushioned sneakers with a sporty street-ready look.",
            3699,
            22,
            "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80",
            "6,7,8,9,10",
            "White,Black,Red",
            26,
            96,
            1,
        ),
        (
            "TrailPro Trek Shoes",
            "Footwear",
            "Boots",
            "Adidas",
            "Responsive outsole and breathable upper for outdoor comfort.",
            4499,
            28,
            "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?auto=format&fit=crop&w=900&q=80",
            "7,8,9,10,11",
            "Olive,Black,Gray",
            16,
            82,
            0,
        ),
        (
            "Royal Canvas Tote",
            "Accessories",
            "Bags",
            "Baggit",
            "Spacious everyday tote for work, travel, and errands.",
            1799,
            12,
            "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=900&q=80",
            "One Size",
            "Tan,Black,Mustard",
            45,
            72,
            0,
        ),
        (
            "Signature Travel Backpack",
            "Accessories",
            "Bags",
            "Wildcraft",
            "Water-resistant backpack with padded sections for daily use.",
            2599,
            18,
            "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=900&q=80",
            "One Size",
            "Black,Forest,Blue",
            24,
            78,
            1,
        ),
        (
            "Metro Glow Watch",
            "Accessories",
            "Watches",
            "Fossil",
            "Minimal luxury analog watch with polished finish.",
            4999,
            24,
            "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?auto=format&fit=crop&w=900&q=80",
            "One Size",
            "Silver,Gold,Black",
            12,
            70,
            0,
        ),
        (
            "CozyNest Pajama Set",
            "Women",
            "Sleepwear",
            "FabIndia",
            "Soft cotton sleepwear with an elevated lounge aesthetic.",
            1699,
            14,
            "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=900&q=80",
            "S,M,L",
            "Lavender,Pink,White",
            41,
            80,
            0,
        ),
        (
            "MileStone Polo",
            "Men",
            "Tops",
            "Tommy Hilfiger",
            "Crisp collar polo for casual meetings and everyday wear.",
            1999,
            16,
            "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=900&q=80",
            "M,L,XL",
            "Navy,White,Red",
            31,
            86,
            1,
        ),
    ]

    conn.executemany(
        """
        INSERT INTO products (
            name, category, subcategory, brand, description, price, discount, image_url,
            sizes, colors, stock, popularity, featured
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        product_rows,
    )
    conn.commit()
    conn.close()


def get_product_by_id(product_id):
    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE product_id = ?", (product_id,)).fetchone()
    conn.close()
    return dict(product) if product else None


def validate_email(value):
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value))


def validate_phone(value):
    digits = re.sub(r"\D", "", value)
    return len(digits) >= 10


def register_user(full_name, email, password, phone, address):
    if len(full_name.strip()) < 2:
        raise ValueError("Full name must be at least 2 characters long.")
    if not validate_email(email):
        raise ValueError("Please provide a valid email address.")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if not validate_phone(phone):
        raise ValueError("Please provide a valid phone number.")
    if not address.strip():
        raise ValueError("Address is required.")

    conn = get_db_connection()
    existing = conn.execute("SELECT user_id FROM users WHERE email = ?", (email.lower(),)).fetchone()
    if existing:
        conn.close()
        raise ValueError("An account already exists for this email.")

    hashed = generate_password_hash(password)
    cursor = conn.execute(
        "INSERT INTO users (full_name, email, password_hash, phone, address) VALUES (?, ?, ?, ?, ?)",
        (full_name.strip(), email.lower(), hashed, phone.strip(), address.strip()),
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id


def authenticate_user(email, password):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email.lower(),)).fetchone()
    if user and check_password_hash(user["password_hash"], password):
        user_data = dict(user)
        conn.close()
        return user_data
    conn.close()
    return None


def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None


def get_products(filters=None):
    conn = get_db_connection()
    query = "SELECT * FROM products WHERE 1 = 1"
    params = []

    if filters is None:
        filters = {}

    search = filters.get("search", "")
    category = filters.get("category")
    size = filters.get("size")
    color = filters.get("color")
    brand = filters.get("brand")
    max_price = filters.get("max_price")
    sort_by = filters.get("sort_by", "popularity")

    if search:
        query += " AND (name LIKE ? OR brand LIKE ? OR description LIKE ?)"
        like = f"%{search}%"
        params.extend([like, like, like])
    if category:
        query += " AND category = ?"
        params.append(category)
    if size:
        query += " AND sizes LIKE ?"
        params.append(f"%{size}%")
    if color:
        query += " AND colors LIKE ?"
        params.append(f"%{color}%")
    if brand:
        query += " AND brand = ?"
        params.append(brand)
    if max_price:
        query += " AND price <= ?"
        params.append(float(max_price))

    if sort_by == "price_low_high":
        query += " ORDER BY price ASC"
    elif sort_by == "price_high_low":
        query += " ORDER BY price DESC"
    elif sort_by == "popular":
        query += " ORDER BY popularity DESC"
    else:
        query += " ORDER BY popularity DESC"

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def parse_sizes(value):
    if not value:
        return []
    return [item.strip() for item in str(value).split(",") if item.strip()]


def parse_colors(value):
    if not value:
        return []
    return [item.strip() for item in str(value).split(",") if item.strip()]


def get_cart_items(user_id):
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT c.cart_id, c.product_id, c.size, c.quantity, p.name, p.brand, p.price, p.discount,
               p.image_url, p.stock
        FROM cart c
        JOIN products p ON p.product_id = c.product_id
        WHERE c.user_id = ?
        ORDER BY c.added_at DESC
        """,
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def cart_summary(user_id):
    items = get_cart_items(user_id)
    subtotal = 0
    item_count = 0
    for item in items:
        discounted_price = float(item["price"]) * (1 - float(item["discount"]) / 100)
        subtotal += discounted_price * int(item["quantity"])
        item_count += int(item["quantity"])

    shipping = 0 if subtotal == 0 else (40 if subtotal < 1500 else 0)
    total = subtotal + shipping
    return {
        "items": items,
        "subtotal": round(subtotal, 2),
        "shipping": round(shipping, 2),
        "total": round(total, 2),
        "item_count": item_count,
    }


def add_to_cart(user_id, product_id, size, quantity):
    if quantity <= 0:
        raise ValueError("Quantity must be greater than 0.")
    conn = get_db_connection()
    product = conn.execute("SELECT stock, name FROM products WHERE product_id = ?", (product_id,)).fetchone()
    if not product:
        conn.close()
        raise ValueError("Product not found.")
    existing = conn.execute(
        "SELECT cart_id, quantity FROM cart WHERE user_id = ? AND product_id = ? AND size = ?",
        (user_id, product_id, size),
    ).fetchone()
    current_qty = existing["quantity"] if existing else 0
    new_qty = current_qty + quantity
    if new_qty > int(product["stock"]):
        conn.close()
        raise ValueError(f"Only {product['stock']} units available for {product['name']}.")
    if existing:
        conn.execute(
            "UPDATE cart SET quantity = ?, added_at = CURRENT_TIMESTAMP WHERE cart_id = ?",
            (new_qty, existing["cart_id"]),
        )
    else:
        conn.execute(
            "INSERT INTO cart (user_id, product_id, size, quantity) VALUES (?, ?, ?, ?)",
            (user_id, product_id, size, quantity),
        )
    conn.commit()
    conn.close()


def update_cart_item(cart_id, quantity):
    if quantity <= 0:
        raise ValueError("Quantity must be at least 1.")
    conn = get_db_connection()
    cart_row = conn.execute(
        "SELECT c.product_id, c.size, p.stock FROM cart c JOIN products p ON p.product_id = c.product_id WHERE c.cart_id = ?",
        (cart_id,),
    ).fetchone()
    if not cart_row:
        conn.close()
        raise ValueError("Cart item not found.")
    if quantity > int(cart_row["stock"]):
        conn.close()
        raise ValueError(f"Only {cart_row['stock']} units available for this product.")
    conn.execute("UPDATE cart SET quantity = ? WHERE cart_id = ?", (quantity, cart_id))
    conn.commit()
    conn.close()


def remove_cart_item(cart_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM cart WHERE cart_id = ?", (cart_id,))
    conn.commit()
    conn.close()


def clear_cart(user_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def process_payment(payment_method, total_amount, customer_name, card_number=None):
    if payment_method == "Cash on Delivery":
        return {"status": "success", "mode": "cash_on_delivery"}

    stripe_key = os.getenv("STRIPE_SECRET_KEY")
    if stripe_key:
        return {"status": "success", "mode": "stripe"}

    if not card_number:
        return {"status": "demo", "mode": "demo"}

    return {"status": "success", "mode": "demo"}


def place_order(user_id, customer_name, phone, address, email, payment_method, card_number=None):
    items = get_cart_items(user_id)
    if not items:
        raise ValueError("Your cart is empty.")

    subtotal = 0
    order_items = []
    for item in items:
        unit_price = float(item["price"]) * (1 - float(item["discount"]) / 100)
        subtotal += unit_price * int(item["quantity"])
        order_items.append(
            {
                "product_id": item["product_id"],
                "name": item["name"],
                "size": item["size"],
                "quantity": item["quantity"],
                "price": round(unit_price, 2),
            }
        )

    shipping = 40 if subtotal < 1500 else 0
    total = round(subtotal + shipping, 2)
    payment_result = process_payment(payment_method, total, customer_name, card_number)
    if payment_result["status"] not in ["success", "demo"]:
        raise ValueError("Payment failed. Please try again.")

    conn = get_db_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO orders (user_id, customer_name, email, phone, address, payment_method, subtotal, shipping, total, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending')
            """,
            (user_id, customer_name.strip(), email.strip(), phone.strip(), address.strip(), payment_method, round(subtotal, 2), shipping, total),
        )
        order_id = cursor.lastrowid

        for item in order_items:
            conn.execute(
                "INSERT INTO order_items (order_id, product_id, name, size, quantity, price) VALUES (?, ?, ?, ?, ?, ?)",
                (order_id, item["product_id"], item["name"], item["size"], item["quantity"], item["price"]),
            )
            conn.execute(
                "UPDATE products SET stock = stock - ? WHERE product_id = ?",
                (item["quantity"], item["product_id"]),
            )

        conn.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return {"order_id": order_id, "total": total, "payment_mode": payment_result["mode"]}


def get_all_orders():
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT o.*, u.full_name AS customer
        FROM orders o
        LEFT JOIN users u ON u.user_id = o.user_id
        ORDER BY o.created_at DESC
        """
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_order_items(order_id):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM order_items WHERE order_id = ? ORDER BY item_id ASC",
        (order_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_user_orders(user_id):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_customers():
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT user_id, full_name, email, phone, address, is_admin, created_at FROM users ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_order_status(order_id, status):
    conn = get_db_connection()
    conn.execute("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))
    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
    conn.commit()
    conn.close()


def save_product(product_data, uploaded_file=None):
    image_url = product_data.get("image_url")
    if uploaded_file is not None and uploaded_file.getvalue():
        file_ext = Path(uploaded_file.name).suffix or ".png"
        unique_name = f"{uuid.uuid4().hex}{file_ext}"
        save_path = UPLOADS_DIR / unique_name
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        image_url = f"/uploads/{unique_name}"

    if not image_url:
        raise ValueError("Product image is required.")

    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO products (
            name, category, subcategory, brand, description, price, discount,
            image_url, sizes, colors, stock, popularity, featured
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            product_data["name"],
            product_data["category"],
            product_data.get("subcategory", ""),
            product_data["brand"],
            product_data["description"],
            float(product_data["price"]),
            float(product_data.get("discount", 0)),
            image_url,
            product_data["sizes"],
            product_data["colors"],
            int(product_data["stock"]),
            int(product_data.get("popularity", 0)),
            int(product_data.get("featured", 0)),
        ),
    )
    conn.commit()
    conn.close()


def update_product(product_id, product_data, uploaded_file=None):
    image_url = product_data.get("image_url")
    if uploaded_file is not None and uploaded_file.getvalue():
        file_ext = Path(uploaded_file.name).suffix or ".png"
        unique_name = f"{uuid.uuid4().hex}{file_ext}"
        save_path = UPLOADS_DIR / unique_name
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        image_url = f"/uploads/{unique_name}"

    if not image_url:
        raise ValueError("Product image is required.")

    conn = get_db_connection()
    conn.execute(
        """
        UPDATE products
        SET name = ?, category = ?, subcategory = ?, brand = ?, description = ?,
            price = ?, discount = ?, image_url = ?, sizes = ?, colors = ?,
            stock = ?, popularity = ?, featured = ?
        WHERE product_id = ?
        """,
        (
            product_data["name"],
            product_data["category"],
            product_data.get("subcategory", ""),
            product_data["brand"],
            product_data["description"],
            float(product_data["price"]),
            float(product_data.get("discount", 0)),
            image_url,
            product_data["sizes"],
            product_data["colors"],
            int(product_data["stock"]),
            int(product_data.get("popularity", 0)),
            int(product_data.get("featured", 0)),
            product_id,
        ),
    )
    conn.commit()
    conn.close()


def sales_report():
    conn = get_db_connection()
    stats = conn.execute(
        """
        SELECT
            COUNT(*) AS total_orders,
            COALESCE(SUM(total), 0) AS revenue,
            COALESCE(AVG(total), 0) AS avg_order_value
        FROM orders
        """
    ).fetchone()
    best_sellers = conn.execute(
        """
        SELECT oi.name, SUM(oi.quantity) AS sold_units, SUM(oi.quantity * oi.price) AS revenue
        FROM order_items oi
        GROUP BY oi.name
        ORDER BY sold_units DESC
        LIMIT 5
        """
    ).fetchall()
    low_stock = conn.execute(
        "SELECT product_id, name, stock FROM products WHERE stock <= 10 ORDER BY stock ASC LIMIT 10"
    ).fetchall()
    conn.close()
    return {
        "stats": dict(stats),
        "best_sellers": [dict(row) for row in best_sellers],
        "low_stock": [dict(row) for row in low_stock],
    }


def configure_page():
    st.set_page_config(page_title="StyleKart", page_icon="🛍️", layout="wide")
    st.markdown(
        """
        <style>
        :root {
            --bg: #f8f5f2;
            --card: #ffffff;
            --text: #1b1b1b;
            --muted: #5f6368;
            --primary: #ff3f6c;
            --primary-dark: #f31b52;
            --accent: #ffb3c3;
            --border: #f1e8e3;
            --success: #1bbf73;
            --shadow: 0 10px 25px rgba(0,0,0,0.06);
        }
        * { font-family: 'Segoe UI', Arial, sans-serif; }
        .stApp {
            background: linear-gradient(180deg, #fff 0%, #f6f3f0 100%);
        }
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
        }
        div[data-testid="stSidebar"] {
            background: #fff;
            border-right: 1px solid var(--border);
        }
        .brand-banner {
            background: linear-gradient(135deg, #fff2f6 0%, #ffe5ef 100%);
            padding: 1.4rem 1.2rem;
            border-radius: 18px;
            border: 1px solid var(--border);
            box-shadow: var(--shadow);
            margin-bottom: 1rem;
        }
        .stat-box {
            background: white;
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1rem;
            box-shadow: var(--shadow);
            height: 100%;
        }
        .product-card {
            background: white;
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 0.8rem;
            box-shadow: var(--shadow);
            height: 100%;
        }
        .price-tag {
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text);
        }
        .old-price {
            color: var(--muted);
            text-decoration: line-through;
            margin-left: 0.5rem;
        }
        .badge {
            display: inline-block;
            background: #ffe7ef;
            color: var(--primary-dark);
            border-radius: 999px;
            padding: 0.3rem 0.75rem;
            font-size: 0.72rem;
            font-weight: 700;
        }
        @media (max-width: 768px) {
            .main .block-container { padding: 0.5rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown(
        """
        <div class='brand-banner'>
            <h2 style='margin:0; font-size:2rem; color:#1b1b1b;'>StyleKart</h2>
            <p style='margin:0.5rem 0 0; color:#5f6368;'>Fashion for every mood, every season, every moment.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_login_register():
    st.subheader("My Account")
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            user = authenticate_user(email, password)
            if user:
                st.session_state.user = user
                st.session_state.logged_in = True
                st.success(f"Welcome back, {user['full_name']}!")
                st.rerun()
            else:
                st.error("Invalid email or password.")

    with tab_register:
        full_name = st.text_input("Full name")
        email = st.text_input("Email address", key="register_email")
        phone = st.text_input("Phone number")
        address = st.text_area("Delivery address")
        password = st.text_input("Password", type="password")
        if st.button("Create account"):
            try:
                user_id = register_user(full_name, email, password, phone, address)
                st.success("Account created successfully. Please login.")
                st.session_state.register_email = ""
            except ValueError as exc:
                st.error(str(exc))


def render_home_page():
    render_header()
    filters = st.sidebar.form("catalog_filters")
    search = filters.text_input("Search products")
    categories = ["Men", "Women", "Kids", "Footwear", "Accessories"]
    selected_category = filters.selectbox("Category", ["All"] + categories)
    selected_size = filters.selectbox("Size", ["All", "XS", "S", "M", "L", "XL", "6", "7", "8", "9", "10", "One Size", "4Y", "6Y", "8Y", "10Y"])
    selected_color = filters.selectbox("Color", ["All", "Black", "White", "Blue", "Indigo", "Rose", "Beige", "Navy", "Sky", "Coral", "Tan", "Olive", "Silver", "Gold", "Pink", "Lavender", "Green", "Mustard", "Gray"])
    selected_brand = filters.selectbox("Brand", ["All"] + sorted({row["brand"] for row in get_products({})}))
    max_price = filters.slider("Max price", 500, 10000, 10000, step=250)
    sort_by = filters.selectbox("Sort by", ["popular", "price_low_high", "price_high_low"], format_func=lambda x: {
        "popular": "Popularity",
        "price_low_high": "Price: Low to High",
        "price_high_low": "Price: High to Low",
    }[x])
    filters_submit = filters.form_submit_button("Apply filters")

    if not filters_submit and "catalog_filters" not in st.session_state:
        filters_submit = True

    active_filters = {
        "search": search,
        "category": None if selected_category == "All" else selected_category,
        "size": None if selected_size == "All" else selected_size,
        "color": None if selected_color == "All" else selected_color,
        "brand": None if selected_brand == "All" else selected_brand,
        "max_price": max_price,
        "sort_by": sort_by,
    }

    products = get_products(active_filters)

    if not products:
        st.info("No products match the selected filters.")
        return

    cols = st.columns(4)
    for idx, product in enumerate(products):
        with cols[idx % 4]:
            image = product["image_url"]
            st.image(image, use_container_width=True, caption="")
            if product["discount"]:
                st.markdown(f"<span class='badge'>{int(product['discount'])}% OFF</span>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-weight: 700; font-size: 1.1rem; margin: 0.4rem 0;'> {product['name']} </div>", unsafe_allow_html=True)
            st.caption(f"{product['brand']} · {product['category']}")
            discounted_price = float(product["price"]) * (1 - float(product["discount"]) / 100)
            st.markdown(
                f"<div class='price-tag'>₹{discounted_price:.0f}<span class='old-price'>₹{product['price']}</span></div>",
                unsafe_allow_html=True,
            )
            sizes = parse_sizes(product["sizes"])
            colors = parse_colors(product["colors"])
            st.caption(f"Sizes: {', '.join(sizes[:4])}")
            st.caption(f"Colors: {', '.join(colors[:4])}")
            stock_status = "In stock" if product["stock"] > 0 else "Out of stock"
            st.caption(f"Availability: {stock_status} ({product['stock']})")
            size_key = f"size_{product['product_id']}"
            qty_key = f"qty_{product['product_id']}"
            if size_key not in st.session_state:
                st.session_state[size_key] = sizes[0] if sizes else "One Size"
            if qty_key not in st.session_state:
                st.session_state[qty_key] = 1
            st.session_state[size_key] = st.selectbox("Size", sizes if sizes else ["One Size"], key=size_key, label_visibility="collapsed")
            st.session_state[qty_key] = st.number_input("Qty", min_value=1, max_value=max(1, product["stock"]), value=1, key=qty_key, label_visibility="collapsed")
            if st.button("Add to cart", key=f"add_{product['product_id']}"):
                if not st.session_state.get("logged_in"):
                    st.warning("Please login to add items to your cart.")
                else:
                    try:
                        add_to_cart(st.session_state.user["user_id"], product["product_id"], st.session_state[size_key], st.session_state[qty_key])
                        st.success(f"Added {product['name']} to cart.")
                    except ValueError as exc:
                        st.error(str(exc))
            if st.button("View details", key=f"detail_{product['product_id']}"):
                st.session_state.selected_product_id = product["product_id"]
                st.rerun()

    if "selected_product_id" in st.session_state:
        selected_product = get_product_by_id(st.session_state["selected_product_id"])
        if selected_product:
            st.subheader("Featured product details")
            detail_col1, detail_col2 = st.columns([1, 1.2])
            with detail_col1:
                st.image(selected_product["image_url"], use_container_width=True)
            with detail_col2:
                st.markdown(f"## {selected_product['name']}")
                st.caption(f"{selected_product['brand']} • {selected_product['category']} • {selected_product['subcategory']}")
                st.markdown(
                    f"<div class='price-tag'>₹{float(selected_product['price']) * (1 - float(selected_product['discount'])/100):.0f}<span class='old-price'>₹{selected_product['price']}</span></div>",
                    unsafe_allow_html=True,
                )
                st.write(selected_product["description"])
                st.caption(f"Sizes available: {selected_product['sizes']}")
                st.caption(f"Colors available: {selected_product['colors']}")
                st.caption(f"Stock: {selected_product['stock']}")
                if st.button("Add selected product to cart"):
                    if not st.session_state.get("logged_in"):
                        st.warning("Please login to add items to your cart.")
                    else:
                        size = parse_sizes(selected_product["sizes"])[0] if parse_sizes(selected_product["sizes"]) else "One Size"
                        try:
                            add_to_cart(st.session_state.user["user_id"], selected_product["product_id"], size, 1)
                            st.success(f"Added {selected_product['name']} to cart.")
                        except ValueError as exc:
                            st.error(str(exc))


def render_cart_page():
    if not st.session_state.get("logged_in"):
        st.warning("Please login to manage the cart.")
        return

    st.header("Shopping Bag")
    summary = cart_summary(st.session_state.user["user_id"])
    items = summary["items"]
    if not items:
        st.info("Your cart is empty. Add products to get started.")
        return

    for item in items:
        c1, c2, c3, c4 = st.columns([1.2, 2.2, 1.2, 1.2])
        with c1:
            st.image(item["image_url"], width=120)
        with c2:
            st.markdown(f"**{item['name']}**")
            st.caption(f"Brand: {item['brand']} | Size: {item['size']}")
            price = float(item["price"]) * (1 - float(item["discount"]) / 100)
            st.write(f"₹{price:.0f} each")
        with c3:
            qty = st.number_input("Qty", min_value=1, max_value=max(1, int(item["stock"])), value=int(item["quantity"]), key=f"cart_qty_{item['cart_id']}")
            if st.button("Update", key=f"update_{item['cart_id']}"):
                try:
                    update_cart_item(item["cart_id"], qty)
                    st.success("Cart updated.")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
        with c4:
            total = price * int(item["quantity"])
            st.write(f"₹{total:.0f}")
            if st.button("Remove", key=f"remove_{item['cart_id']}"):
                remove_cart_item(item["cart_id"])
                st.success("Item removed.")
                st.rerun()

    total_box = st.container()
    with total_box:
        st.markdown("---")
        subtotal_col, shipping_col, total_col = st.columns(3)
        with subtotal_col:
            st.metric("Subtotal", f"₹{summary['subtotal']:.0f}")
        with shipping_col:
            st.metric("Shipping", f"₹{summary['shipping']:.0f}")
        with total_col:
            st.metric("Total", f"₹{summary['total']:.0f}")

        if st.button("Proceed to Checkout"):
            st.session_state.page = "checkout"
            st.rerun()


def render_checkout_page():
    if not st.session_state.get("logged_in"):
        st.warning("Please login before checking out.")
        return

    user = st.session_state.user
    summary = cart_summary(user["user_id"])
    if not summary["items"]:
        st.info("Add some products to your cart before checkout.")
        return

    st.header("Checkout")
    order_col, summary_col = st.columns([1.5, 1])

    with order_col:
        st.subheader("Delivery details")
        name = st.text_input("Full name", value=user["full_name"])
        phone = st.text_input("Phone number", value=user["phone"] or "")
        email = st.text_input("Email", value=user["email"])
        address = st.text_area("Delivery address", value=user["address"] or "")
        payment_method = st.radio("Payment method", ["Card (Demo)", "Cash on Delivery"], index=0)
        card_number = None
        if payment_method == "Card (Demo)":
            card_number = st.text_input("Card number", type="password", placeholder="Demo only - not stored")
            st.caption("Demo mode: card data is never saved to the database.")

        if st.button("Place order"):
            try:
                result = place_order(user["user_id"], name, phone, address, email, payment_method, card_number)
                st.success(f"Order placed successfully! Order ID: #{result['order_id']}.")
                st.balloons()
                st.session_state.page = "home"
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

    with summary_col:
        st.subheader("Order summary")
        for item in summary["items"]:
            price = float(item["price"]) * (1 - float(item["discount"]) / 100)
            st.write(f"{item['name']} x {item['quantity']} — ₹{(price * item['quantity']):.0f}")
        st.markdown("---")
        st.write(f"Subtotal: ₹{summary['subtotal']:.0f}")
        st.write(f"Shipping: ₹{summary['shipping']:.0f}")
        st.write(f"Total: ₹{summary['total']:.0f}")


def render_profile_page():
    if not st.session_state.get("logged_in"):
        st.warning("Please login to view your profile.")
        return

    user = get_user_by_id(st.session_state.user["user_id"])
    st.header("My Profile")
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Account details")
        st.write(f"Name: {user['full_name']}")
        st.write(f"Email: {user['email']}")
        st.write(f"Phone: {user['phone'] or 'Not provided'}")
        st.write(f"Address: {user['address'] or 'Not provided'}")

    with col2:
        st.subheader("Update profile")
        new_name = st.text_input("Full name", value=user["full_name"])
        new_phone = st.text_input("Phone", value=user["phone"] or "")
        new_address = st.text_area("Address", value=user["address"] or "")
        if st.button("Save profile"):
            conn = get_db_connection()
            conn.execute(
                "UPDATE users SET full_name = ?, phone = ?, address = ? WHERE user_id = ?",
                (new_name.strip(), new_phone.strip(), new_address.strip(), user["user_id"]),
            )
            conn.commit()
            conn.close()
            st.success("Profile updated.")
            st.rerun()

    st.subheader("Order history")
    orders = get_user_orders(user["user_id"])
    if not orders:
        st.info("No orders yet. Start shopping to see your history here.")
        return

    for order in orders:
        st.markdown("---")
        st.write(f"Order #{order['order_id']} • {order['created_at']} • Status: {order['status']}")
        st.write(f"Total: ₹{order['total']:.2f} • Payment: {order['payment_method']}")
        items = get_order_items(order["order_id"])
        for item in items:
            st.write(f"- {item['name']} ({item['size']}) x {item['quantity']} �� ₹{item['price'] * item['quantity']:.2f}")


def render_admin_page():
    if not st.session_state.get("logged_in"):
        st.warning("Login required to access the admin dashboard.")
        return

    user = st.session_state.user
    if not user.get("is_admin"):
        st.warning("You do not have admin access.")
        return

    st.header("Admin Dashboard")
    tabs = st.tabs(["Products", "Orders", "Customers", "Reports"])

    with tabs[0]:
        st.subheader("Add product")
        with st.form("add_product_form"):
            name = st.text_input("Product name")
            category = st.selectbox("Category", ["Men", "Women", "Kids", "Footwear", "Accessories"])
            subcategory = st.text_input("Subcategory")
            brand = st.text_input("Brand")
            description = st.text_area("Description")
            price = st.number_input("Price", min_value=0.0, step=50.0)
            discount = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, step=1.0)
            sizes = st.text_input("Sizes (comma separated)", value="S,M,L,XL")
            colors = st.text_input("Colors (comma separated)", value="Black,White")
            stock = st.number_input("Stock", min_value=0, step=1)
            popularity = st.number_input("Popularity score", min_value=0, step=1)
            featured = st.checkbox("Feature on homepage")
            uploaded_file = st.file_uploader("Upload product image", type=["png", "jpg", "jpeg", "webp"])
            image_url = st.text_input("Or use remote image URL")
            submitted = st.form_submit_button("Save product")
        if submitted:
            try:
                data = {
                    "name": name,
                    "category": category,
                    "subcategory": subcategory,
                    "brand": brand,
                    "description": description,
                    "price": price,
                    "discount": discount,
                    "sizes": sizes,
                    "colors": colors,
                    "stock": stock,
                    "popularity": popularity,
                    "featured": int(featured),
                    "image_url": image_url,
                }
                save_product(data, uploaded_file)
                st.success("Product added successfully.")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

        st.subheader("Manage products")
        products = get_products({})
        for product in products:
            c1, c2, c3, c4 = st.columns([2, 1.4, 1, 0.8])
            with c1:
                st.write(f"{product['name']} ({product['brand']})")
            with c2:
                st.write(f"₹{product['price']} | {product['stock']} in stock")
            with c3:
                if st.button("Edit", key=f"edit_product_{product['product_id']}"):
                    st.session_state.edit_product_id = product["product_id"]
                    st.rerun()
            with c4:
                if st.button("Delete", key=f"delete_product_{product['product_id']}"):
                    delete_product(product["product_id"])
                    st.success("Product deleted.")
                    st.rerun()

        if "edit_product_id" in st.session_state:
            product = get_product_by_id(st.session_state.edit_product_id)
            if product:
                st.subheader(f"Editing: {product['name']}")
                with st.form(f"edit_form_{product['product_id']}"):
                    name = st.text_input("Name", value=product["name"])
                    category = st.selectbox("Category", ["Men", "Women", "Kids", "Footwear", "Accessories"], index=["Men", "Women", "Kids", "Footwear", "Accessories"].index(product["category"]))
                    subcategory = st.text_input("Subcategory", value=product["subcategory"]) 
                    brand = st.text_input("Brand", value=product["brand"])
                    description = st.text_area("Description", value=product["description"])
                    price = st.number_input("Price", min_value=0.0, value=float(product["price"]), step=50.0)
                    discount = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, value=float(product["discount"]), step=1.0)
                    sizes = st.text_input("Sizes", value=product["sizes"])
                    colors = st.text_input("Colors", value=product["colors"])
                    stock = st.number_input("Stock", min_value=0, value=int(product["stock"]), step=1)
                    popularity = st.number_input("Popularity", min_value=0, value=int(product["popularity"]), step=1)
                    featured = st.checkbox("Featured", value=bool(product["featured"]))
                    uploaded_file = st.file_uploader("Upload new image", type=["png", "jpg", "jpeg", "webp"])
                    image_url = st.text_input("Image URL", value=product["image_url"])
                    update_submit = st.form_submit_button("Update product")
                if update_submit:
                    try:
                        payload = {
                            "name": name,
                            "category": category,
                            "subcategory": subcategory,
                            "brand": brand,
                            "description": description,
                            "price": price,
                            "discount": discount,
                            "sizes": sizes,
                            "colors": colors,
                            "stock": stock,
                            "popularity": popularity,
                            "featured": int(featured),
                            "image_url": image_url,
                        }
                        update_product(product["product_id"], payload, uploaded_file)
                        st.success("Product updated successfully.")
                        del st.session_state.edit_product_id
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))

    with tabs[1]:
        st.subheader("Orders")
        orders = get_all_orders()
        if not orders:
            st.info("No orders yet.")
        else:
            for order in orders:
                with st.container():
                    st.write(f"Order #{order['order_id']} • {order['customer_name']} • {order['status']}")
                    st.write(f"Total: ₹{order['total']:.2f} • Payment: {order['payment_method']}")
                    new_status = st.selectbox("Status", ["Pending", "Packed", "Shipped", "Delivered", "Cancelled"], index=["Pending", "Packed", "Shipped", "Delivered", "Cancelled"].index(order["status"]), key=f"status_{order['order_id']}")
                    if st.button("Update status", key=f"update_status_{order['order_id']}"):
                        update_order_status(order["order_id"], new_status)
                        st.success("Order status updated.")
                        st.rerun()
                    items = get_order_items(order["order_id"])
                    for item in items:
                        st.write(f"- {item['name']} ({item['size']}) x {item['quantity']} — ₹{item['price'] * item['quantity']:.2f}")
                    st.markdown("---")

    with tabs[2]:
        st.subheader("Customers")
        customers = get_all_customers()
        if not customers:
            st.info("No customers registered yet.")
        else:
            df = pd.DataFrame(customers)
            st.dataframe(df, use_container_width=True)

    with tabs[3]:
        st.subheader("Reports")
        report = sales_report()
        stats = report["stats"]
        total_orders = int(stats.get("total_orders") or 0)
        revenue = float(stats.get("revenue") or 0)
        avg_order = float(stats.get("avg_order_value") or 0)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Orders", total_orders)
        with c2:
            st.metric("Revenue", f"₹{revenue:,.2f}")
        with c3:
            st.metric("Avg. Order Value", f"₹{avg_order:,.2f}")

        st.subheader("Best-selling products")
        best_sellers = report["best_sellers"]
        if best_sellers:
            st.dataframe(pd.DataFrame(best_sellers), use_container_width=True)
        else:
            st.info("No sales yet.")

        st.subheader("Low stock items")
        low_stock = report["low_stock"]
        if low_stock:
            st.dataframe(pd.DataFrame(low_stock), use_container_width=True)
        else:
            st.info("No low stock alerts.")


def main():
    init_db()
    seed_default_accounts()
    seed_products()
    configure_page()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "page" not in st.session_state:
        st.session_state.page = "home"

    with st.sidebar:
        st.image("https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=900&q=80", use_container_width=True)
        st.markdown("### StyleKart")
        pages = ["Home", "Cart", "Checkout", "Profile", "Admin"]
        selected_page = st.radio("Navigation", pages, index=0)
        st.session_state.page = selected_page.lower()

        if st.session_state.logged_in:
            st.write(f"Logged in as: {st.session_state.user['full_name']}")
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.user = None
                st.rerun()
        else:
            render_login_register()

    if st.session_state.page == "home":
        render_home_page()
    elif st.session_state.page == "cart":
        render_cart_page()
    elif st.session_state.page == "checkout":
        render_checkout_page()
    elif st.session_state.page == "profile":
        render_profile_page()
    elif st.session_state.page == "admin":
        render_admin_page()


if __name__ == "__main__":
    main()

