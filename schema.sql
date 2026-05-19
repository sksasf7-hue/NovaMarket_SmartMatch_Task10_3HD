-- SIT774 Task 10.3HD - NovaMarket SmartMatch SQLite schema
-- This schema is also created automatically by app.py.

DROP TABLE IF EXISTS recommendation_event;
DROP TABLE IF EXISTS wishlist_event;
DROP TABLE IF EXISTS contact_message;
DROP TABLE IF EXISTS product;

CREATE TABLE product (
  product_id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_name TEXT NOT NULL CHECK(length(product_name) <= 100),
  category TEXT NOT NULL CHECK(category IN ('Electronics','Workspace','Lifestyle','Home','Travel','Wellbeing')),
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
);

CREATE TABLE contact_message (
  message_id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_name TEXT NOT NULL CHECK(length(customer_name) <= 80),
  email TEXT NOT NULL CHECK(length(email) <= 120),
  subject TEXT NOT NULL CHECK(length(subject) <= 120),
  message TEXT NOT NULL CHECK(length(message) <= 600),
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE recommendation_event (
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
);

CREATE TABLE wishlist_event (
  wishlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_token TEXT NOT NULL,
  product_id INTEGER NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (product_id) REFERENCES product(product_id)
);
