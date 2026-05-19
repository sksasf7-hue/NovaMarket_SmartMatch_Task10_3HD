#!/usr/bin/env python3
"""
SIT774 Task 10.3HD - NovaMarket SmartMatch
Professional website prototype with an innovative website feature:
Adaptive Smart Product Match & Compare Assistant.

How to run:
    python app.py
    python app.py --reset
Then open:
    http://127.0.0.1:8765

This project intentionally uses only Python standard-library modules plus SQLite.
It is easy to run locally and simple for assessors to inspect.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs
import html
import json
import mimetypes
import sqlite3
import sys
import time
import uuid

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "novamarket.db"
HOST = "127.0.0.1"
PORT = 8765

ALLOWED_CATEGORIES = [
    "Electronics",
    "Workspace",
    "Lifestyle",
    "Home",
    "Travel",
    "Wellbeing",
]

# Starter products give the SmartMatch algorithm useful data to compare.
SEED_PRODUCTS = [
    {
        "name": "AuraBook Pro 14",
        "category": "Electronics",
        "price": 1299.00,
        "stock": 12,
        "rating": 4.8,
        "eco": 74,
        "accessibility": 88,
        "performance": 96,
        "badge": "Power Pick",
        "icon": "💻",
        "description": "A fast, lightweight laptop for study, design work, and hybrid productivity.",
        "features": ["Long battery life", "High-contrast display", "Quiet keyboard", "USB-C fast charging"],
    },
    {
        "name": "Pulse Wireless Mouse",
        "category": "Workspace",
        "price": 39.95,
        "stock": 42,
        "rating": 4.5,
        "eco": 68,
        "accessibility": 84,
        "performance": 74,
        "badge": "Best Value",
        "icon": "🖱️",
        "description": "Comfortable wireless mouse with silent clicks and multi-device pairing.",
        "features": ["Ergonomic shape", "Silent buttons", "Adjustable DPI", "Recycled packaging"],
    },
    {
        "name": "FocusFlow Desk Lamp",
        "category": "Home",
        "price": 89.00,
        "stock": 18,
        "rating": 4.7,
        "eco": 82,
        "accessibility": 91,
        "performance": 78,
        "badge": "Accessible",
        "icon": "💡",
        "description": "Adaptive desk lamp with glare reduction and a screen-friendly focus mode.",
        "features": ["Glare control", "Large tactile dial", "Warm/cool modes", "Auto dimming"],
    },
    {
        "name": "EcoSip Smart Bottle",
        "category": "Lifestyle",
        "price": 59.50,
        "stock": 33,
        "rating": 4.4,
        "eco": 95,
        "accessibility": 72,
        "performance": 70,
        "badge": "Eco Hero",
        "icon": "🥤",
        "description": "Reusable smart bottle with hydration reminders and durable stainless construction.",
        "features": ["Hydration reminders", "BPA-free", "Stainless body", "Replaceable lid"],
    },
    {
        "name": "Nomad Charge Hub",
        "category": "Travel",
        "price": 119.00,
        "stock": 7,
        "rating": 4.6,
        "eco": 62,
        "accessibility": 76,
        "performance": 90,
        "badge": "Travel Ready",
        "icon": "🔌",
        "description": "Compact travel hub with international plug support and multi-device charging.",
        "features": ["4-port charging", "International adapters", "Surge protection", "Compact case"],
    },
    {
        "name": "CalmPods Lite",
        "category": "Wellbeing",
        "price": 149.00,
        "stock": 21,
        "rating": 4.3,
        "eco": 66,
        "accessibility": 89,
        "performance": 86,
        "badge": "Focus Audio",
        "icon": "🎧",
        "description": "Noise-reducing earbuds designed for focus sessions, commuting, and calls.",
        "features": ["Noise reduction", "Transparency mode", "Large touch controls", "Find-my-case alert"],
    },
    {
        "name": "GreenBoard Keyboard",
        "category": "Workspace",
        "price": 99.00,
        "stock": 0,
        "rating": 4.9,
        "eco": 98,
        "accessibility": 93,
        "performance": 82,
        "badge": "Waitlist",
        "icon": "⌨️",
        "description": "Premium keyboard built from recycled aluminium and repairable modular keys.",
        "features": ["Repairable keys", "High contrast caps", "Recycled aluminium", "Low-profile switches"],
    },
    {
        "name": "HomeSense Mini",
        "category": "Home",
        "price": 179.00,
        "stock": 14,
        "rating": 4.2,
        "eco": 71,
        "accessibility": 80,
        "performance": 88,
        "badge": "Smart Home",
        "icon": "🏠",
        "description": "Privacy-focused home sensor that tracks room comfort without cameras.",
        "features": ["No camera", "Air-quality alerts", "Local controls", "Voice assistant ready"],
    },
]


def get_connection():
    """Open a short-lived SQLite connection and return rows as sqlite3.Row objects."""
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db(reset=False):
    """Create all database tables and seed starter products for the prototype."""
    con = get_connection()
    cur = con.cursor()

    if reset:
        cur.execute("DROP TABLE IF EXISTS recommendation_event")
        cur.execute("DROP TABLE IF EXISTS wishlist_event")
        cur.execute("DROP TABLE IF EXISTS contact_message")
        cur.execute("DROP TABLE IF EXISTS product")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS product (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL CHECK(length(product_name) <= 100),
            category TEXT NOT NULL CHECK(category IN
                ('Electronics','Workspace','Lifestyle','Home','Travel','Wellbeing')),
            unit_price REAL NOT NULL CHECK(unit_price >= 0),
            stock_qty INTEGER NOT NULL CHECK(stock_qty >= 0),
            is_active INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0,1)),
            rating REAL NOT NULL CHECK(rating BETWEEN 0 AND 5),
            eco_score INTEGER NOT NULL CHECK(eco_score BETWEEN 0 AND 100),
            accessibility_score INTEGER NOT NULL CHECK(accessibility_score BETWEEN 0 AND 100),
            performance_score INTEGER NOT NULL CHECK(performance_score BETWEEN 0 AND 100),
            badge TEXT NOT NULL CHECK(length(badge) <= 40),
            icon TEXT NOT NULL CHECK(length(icon) <= 10),
            description TEXT NOT NULL CHECK(length(description) <= 220),
            features TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS contact_message (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL CHECK(length(customer_name) <= 80),
            email TEXT NOT NULL CHECK(length(email) <= 120),
            subject TEXT NOT NULL CHECK(length(subject) <= 120),
            message TEXT NOT NULL CHECK(length(message) <= 600),
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS recommendation_event (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_token TEXT NOT NULL,
            selected_category TEXT NOT NULL,
            budget REAL,
            priority TEXT NOT NULL,
            usage_profile TEXT NOT NULL,
            top_product_id INTEGER,
            top_score REAL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (top_product_id) REFERENCES product(product_id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS wishlist_event (
            wishlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_token TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (product_id) REFERENCES product(product_id)
        )
        """
    )

    cur.execute("SELECT COUNT(*) AS total FROM product")
    if cur.fetchone()["total"] == 0:
        for product in SEED_PRODUCTS:
            cur.execute(
                """
                INSERT INTO product (
                    product_name, category, unit_price, stock_qty, is_active, rating,
                    eco_score, accessibility_score, performance_score, badge, icon,
                    description, features
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product["name"],
                    product["category"],
                    product["price"],
                    product["stock"],
                    1,
                    product["rating"],
                    product["eco"],
                    product["accessibility"],
                    product["performance"],
                    product["badge"],
                    product["icon"],
                    product["description"],
                    json.dumps(product["features"]),
                ),
            )

    con.commit()
    con.close()


def row_to_product(row):
    """Convert a SQLite product row into a JSON-safe dictionary for the front end."""
    return {
        "product_id": row["product_id"],
        "product_name": row["product_name"],
        "category": row["category"],
        "unit_price": float(row["unit_price"]),
        "stock_qty": int(row["stock_qty"]),
        "is_active": bool(row["is_active"]),
        "rating": float(row["rating"]),
        "eco_score": int(row["eco_score"]),
        "accessibility_score": int(row["accessibility_score"]),
        "performance_score": int(row["performance_score"]),
        "badge": row["badge"],
        "icon": row["icon"],
        "description": row["description"],
        "features": json.loads(row["features"]),
        "created_at": row["created_at"],
    }


def get_products(include_inactive=False):
    """Read product records from SQLite for catalog and recommendation features."""
    con = get_connection()
    cur = con.cursor()
    query = "SELECT * FROM product"
    if not include_inactive:
        query += " WHERE is_active = 1"
    query += " ORDER BY product_id"
    rows = [row_to_product(row) for row in cur.execute(query).fetchall()]
    con.close()
    return rows


def clamp(value, low=0, high=100):
    return max(low, min(high, value))


def calculate_recommendation_score(product, prefs):
    """
    Awesome feature implementation: explainable product matching.

    The score is not a black box. It combines category fit, budget fit, stock,
    user priority, and usage profile, then returns a breakdown that the interface
    displays as transparent progress bars. This supports user trust and usability.
    """
    budget = prefs.get("budget")
    selected_category = prefs.get("category", "All")
    priority = prefs.get("priority", "balanced")
    usage = prefs.get("usage", "study")
    include_unavailable = prefs.get("include_unavailable", False)

    score = 0.0
    breakdown = []
    reasons = []

    # Category fit: exact matches get more points, while All still keeps discovery wide.
    if selected_category == "All":
        category_points = 10
        reasons.append("available across your selected discovery range")
    elif product["category"] == selected_category:
        category_points = 18
        reasons.append(f"matches the {selected_category} category")
    else:
        category_points = -10
    score += category_points
    breakdown.append({"label": "Category fit", "value": clamp(category_points + 10, 0, 28), "max": 28})

    # Budget fit: strongly rewards items inside budget but still allows near-matches.
    if budget is not None and budget > 0:
        price = product["unit_price"]
        if price <= budget:
            budget_points = 30 - min(10, (price / budget) * 8)
            reasons.append("fits within your budget")
        else:
            over_ratio = (price - budget) / budget
            budget_points = max(-18, 12 - over_ratio * 40)
            reasons.append("is above budget but may still be worth comparing")
        score += budget_points
        breakdown.append({"label": "Budget fit", "value": clamp(budget_points + 18, 0, 48), "max": 48})
    else:
        score += 12
        breakdown.append({"label": "Budget fit", "value": 18, "max": 48})

    # Availability: in-stock products are prioritised for performance and user satisfaction.
    if product["stock_qty"] > 0:
        stock_points = min(12, 5 + product["stock_qty"] / 6)
        reasons.append("is currently in stock")
    elif include_unavailable:
        stock_points = -3
        reasons.append("is out of stock but still visible because you allowed waitlist items")
    else:
        stock_points = -40
    score += stock_points
    breakdown.append({"label": "Availability", "value": clamp(stock_points + 5, 0, 20), "max": 20})

    # Priority weighting changes depending on the user's goal.
    priority_map = {
        "balanced": (
            product["rating"] * 5
            + product["eco_score"] * 0.16
            + product["accessibility_score"] * 0.16
            + product["performance_score"] * 0.18
        ),
        "value": (
            product["rating"] * 5
            + (100 - min(product["unit_price"] / 15, 100)) * 0.22
            + product["stock_qty"] * 0.12
        ),
        "sustainability": product["eco_score"] * 0.42 + product["rating"] * 4,
        "performance": product["performance_score"] * 0.44 + product["rating"] * 4,
        "accessibility": product["accessibility_score"] * 0.45 + product["rating"] * 4,
    }
    priority_points = priority_map.get(priority, priority_map["balanced"])
    score += priority_points
    breakdown.append({"label": "Priority match", "value": clamp(priority_points, 0, 55), "max": 55})

    if priority == "sustainability":
        reasons.append("has a strong sustainability score")
    elif priority == "accessibility":
        reasons.append("supports accessibility-focused buying decisions")
    elif priority == "performance":
        reasons.append("has strong performance attributes")
    elif priority == "value":
        reasons.append("balances price, rating, and availability")
    else:
        reasons.append("balances quality, access, sustainability, and performance")

    # Usage profile adds contextual nuance so the feature feels personalised.
    usage_points = 0
    if usage == "study" and product["category"] in ("Electronics", "Workspace"):
        usage_points = 12
        reasons.append("suits study and productivity workflows")
    elif usage == "home-office" and product["category"] in ("Workspace", "Home", "Electronics"):
        usage_points = 14
        reasons.append("supports a home-office setup")
    elif usage == "eco" and product["eco_score"] >= 80:
        usage_points = 15
        reasons.append("aligns with eco-conscious shopping")
    elif usage == "gift" and product["rating"] >= 4.5 and product["stock_qty"] > 0:
        usage_points = 12
        reasons.append("is a reliable gift option with strong reviews")
    else:
        usage_points = 5
    score += usage_points
    breakdown.append({"label": "Use-case fit", "value": clamp(usage_points, 0, 18), "max": 18})

    final_score = clamp(round(score, 1), 0, 100)
    return final_score, breakdown, reasons[:4]


def build_recommendations(prefs, session_token):
    """Rank products, store a lightweight recommendation event, and return results."""
    products = get_products()
    include_unavailable = prefs.get("include_unavailable", False)
    ranked = []

    for product in products:
        if product["stock_qty"] <= 0 and not include_unavailable:
            continue
        score, breakdown, reasons = calculate_recommendation_score(product, prefs)
        item = dict(product)
        item["match_score"] = score
        item["score_breakdown"] = breakdown
        item["match_reasons"] = reasons
        ranked.append(item)

    ranked.sort(key=lambda p: p["match_score"], reverse=True)
    top = ranked[0] if ranked else None

    con = get_connection()
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO recommendation_event (
            session_token, selected_category, budget, priority, usage_profile,
            top_product_id, top_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session_token,
            prefs.get("category", "All"),
            prefs.get("budget"),
            prefs.get("priority", "balanced"),
            prefs.get("usage", "study"),
            top["product_id"] if top else None,
            top["match_score"] if top else None,
        ),
    )
    con.commit()
    con.close()
    return ranked


def validate_contact(payload):
    """Validate contact messages before writing to SQLite."""
    errors = []
    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip()
    subject = str(payload.get("subject", "")).strip()
    message = str(payload.get("message", "")).strip()

    if not name:
        errors.append("Name is required.")
    elif len(name) > 80:
        errors.append("Name must be 80 characters or less.")

    if not email:
        errors.append("Email is required.")
    elif "@" not in email or "." not in email:
        errors.append("Email must look like a valid email address.")
    elif len(email) > 120:
        errors.append("Email must be 120 characters or less.")

    if not subject:
        errors.append("Subject is required.")
    elif len(subject) > 120:
        errors.append("Subject must be 120 characters or less.")

    if not message:
        errors.append("Message is required.")
    elif len(message) > 600:
        errors.append("Message must be 600 characters or less.")

    return errors, name, email, subject, message


def validate_new_product(payload):
    """Validate admin demo product input before INSERT."""
    errors = []
    name = str(payload.get("product_name", "")).strip()
    category = str(payload.get("category", "")).strip()
    badge = str(payload.get("badge", "New")).strip() or "New"
    description = str(payload.get("description", "")).strip()
    icon = str(payload.get("icon", "✨")).strip() or "✨"

    def number(field, label, min_value, max_value=None, integer=False):
        raw = payload.get(field, "")
        try:
            value = int(raw) if integer else float(raw)
        except (ValueError, TypeError):
            errors.append(f"{label} must be a valid number.")
            return None
        if value < min_value:
            errors.append(f"{label} must be at least {min_value}.")
        if max_value is not None and value > max_value:
            errors.append(f"{label} must be {max_value} or less.")
        return value

    price = number("unit_price", "Unit price", 0)
    stock = number("stock_qty", "Stock quantity", 0, integer=True)
    rating = number("rating", "Rating", 0, 5)
    eco = number("eco_score", "Eco score", 0, 100, integer=True)
    accessibility = number("accessibility_score", "Accessibility score", 0, 100, integer=True)
    performance = number("performance_score", "Performance score", 0, 100, integer=True)

    if not name:
        errors.append("Product name is required.")
    elif len(name) > 100:
        errors.append("Product name must be 100 characters or less.")
    if category not in ALLOWED_CATEGORIES:
        errors.append("Please select a valid category.")
    if len(badge) > 40:
        errors.append("Badge must be 40 characters or less.")
    if not description:
        errors.append("Description is required.")
    elif len(description) > 220:
        errors.append("Description must be 220 characters or less.")

    features = [f.strip() for f in str(payload.get("features", "")).split(",") if f.strip()]
    if not features:
        features = ["New product", "Smart catalog ready"]
    features = features[:5]

    values = {
        "product_name": name,
        "category": category,
        "unit_price": price,
        "stock_qty": stock,
        "rating": rating,
        "eco_score": eco,
        "accessibility_score": accessibility,
        "performance_score": performance,
        "badge": badge,
        "icon": icon[:4],
        "description": description,
        "features": features,
    }
    return errors, values


def insert_contact(name, email, subject, message):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO contact_message (customer_name, email, subject, message)
        VALUES (?, ?, ?, ?)
        """,
        (name, email, subject, message),
    )
    con.commit()
    con.close()


def insert_new_product(values):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO product (
            product_name, category, unit_price, stock_qty, is_active, rating,
            eco_score, accessibility_score, performance_score, badge, icon,
            description, features
        ) VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            values["product_name"],
            values["category"],
            values["unit_price"],
            values["stock_qty"],
            values["rating"],
            values["eco_score"],
            values["accessibility_score"],
            values["performance_score"],
            values["badge"],
            values["icon"],
            values["description"],
            json.dumps(values["features"]),
        ),
    )
    con.commit()
    con.close()


def add_wishlist_event(session_token, product_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO wishlist_event (session_token, product_id) VALUES (?, ?)",
        (session_token, int(product_id)),
    )
    con.commit()
    con.close()


def get_stats():
    con = get_connection()
    cur = con.cursor()
    product_count = cur.execute("SELECT COUNT(*) AS count FROM product WHERE is_active = 1").fetchone()["count"]
    wishlist_count = cur.execute("SELECT COUNT(*) AS count FROM wishlist_event").fetchone()["count"]
    recommendation_count = cur.execute("SELECT COUNT(*) AS count FROM recommendation_event").fetchone()["count"]
    average_rating = cur.execute("SELECT AVG(rating) AS avg_rating FROM product WHERE is_active = 1").fetchone()["avg_rating"] or 0
    message_count = cur.execute("SELECT COUNT(*) AS count FROM contact_message").fetchone()["count"]
    con.close()
    return {
        "product_count": product_count,
        "wishlist_count": wishlist_count,
        "recommendation_count": recommendation_count,
        "average_rating": round(float(average_rating), 2),
        "message_count": message_count,
    }


def parse_json_body(handler):
    length = int(handler.headers.get("Content-Length", "0"))
    raw = handler.rfile.read(length).decode("utf-8") if length else "{}"
    return json.loads(raw or "{}")


def safe_path(relative_path):
    """Resolve a requested static path while preventing directory traversal."""
    requested = (BASE_DIR / relative_path.lstrip("/")).resolve()
    if BASE_DIR not in requested.parents and requested != BASE_DIR:
        return None
    return requested


class Handler(BaseHTTPRequestHandler):
    """Tiny HTTP handler that serves the website and JSON API endpoints."""

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path):
        mime, _ = mimetypes.guess_type(path.name)
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        if path.suffix in {".css", ".js", ".svg"}:
            self.send_header("Cache-Control", "public, max-age=120")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_file(BASE_DIR / "index.html")
            return
        if self.path == "/api/products":
            self.send_json({"products": get_products(), "stats": get_stats(), "categories": ALLOWED_CATEGORIES})
            return
        if self.path == "/api/stats":
            self.send_json(get_stats())
            return
        if self.path.startswith("/static/"):
            file_path = safe_path(self.path)
            if file_path and file_path.exists() and file_path.is_file():
                self.send_file(file_path)
                return
        self.send_error(404, "Not Found")

    def do_POST(self):
        try:
            payload = parse_json_body(self)
        except json.JSONDecodeError:
            self.send_json({"ok": False, "errors": ["Invalid JSON request."]}, status=400)
            return

        session_token = payload.get("session_token") or str(uuid.uuid4())

        if self.path == "/api/recommend":
            category = str(payload.get("category", "All")).strip() or "All"
            if category != "All" and category not in ALLOWED_CATEGORIES:
                self.send_json({"ok": False, "errors": ["Invalid category."]}, status=400)
                return
            budget_value = payload.get("budget")
            try:
                budget = float(budget_value) if str(budget_value).strip() != "" else None
                if budget is not None and budget < 0:
                    raise ValueError
            except (ValueError, TypeError):
                self.send_json({"ok": False, "errors": ["Budget must be a positive number."]}, status=400)
                return
            prefs = {
                "category": category,
                "budget": budget,
                "priority": str(payload.get("priority", "balanced")),
                "usage": str(payload.get("usage", "study")),
                "include_unavailable": bool(payload.get("include_unavailable", False)),
            }
            started = time.perf_counter()
            ranked = build_recommendations(prefs, session_token)
            elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            self.send_json(
                {
                    "ok": True,
                    "session_token": session_token,
                    "preferences": prefs,
                    "elapsed_ms": elapsed_ms,
                    "results": ranked[:5],
                    "stats": get_stats(),
                }
            )
            return

        if self.path == "/api/contact":
            errors, name, email, subject, message = validate_contact(payload)
            if errors:
                self.send_json({"ok": False, "errors": errors}, status=400)
                return
            insert_contact(name, email, subject, message)
            self.send_json({"ok": True, "message": "Message saved successfully in SQLite.", "stats": get_stats()})
            return

        if self.path == "/api/wishlist":
            product_id = payload.get("product_id")
            try:
                add_wishlist_event(session_token, int(product_id))
            except (ValueError, TypeError, sqlite3.Error):
                self.send_json({"ok": False, "errors": ["Invalid product selected."]}, status=400)
                return
            self.send_json({"ok": True, "message": "Saved to wishlist events.", "stats": get_stats()})
            return

        if self.path == "/api/add-product":
            errors, values = validate_new_product(payload)
            if errors:
                self.send_json({"ok": False, "errors": errors}, status=400)
                return
            insert_new_product(values)
            self.send_json({"ok": True, "message": "Product inserted successfully.", "products": get_products(), "stats": get_stats()})
            return

        self.send_error(404, "Not Found")

    def log_message(self, fmt, *args):
        # Keep the terminal clean for demonstration recordings.
        return


def main():
    reset = "--reset" in sys.argv
    init_db(reset=reset)
    server = HTTPServer((HOST, PORT), Handler)
    print(f"NovaMarket SmartMatch is running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop the server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
