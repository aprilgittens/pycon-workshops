"""
setup/seed_db.py — Creates the database schema and seeds it with fake data.

Run once (before the lab):
    python setup/seed_db.py

Requires the following environment variables (or a .env file in the project root):
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
"""

from __future__ import annotations

import asyncio
import os
import sys
from datetime import date, timedelta
from pathlib import Path

# Allow running from any working directory
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncpg
from dotenv import load_dotenv

load_dotenv(override=False)

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

DDL = """
CREATE TABLE IF NOT EXISTS customers (
    customer_id  VARCHAR(10)  PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    email        VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS orders (
    order_id          VARCHAR(20)    PRIMARY KEY,
    customer_id       VARCHAR(10)    NOT NULL REFERENCES customers(customer_id),
    product_name      VARCHAR(150)   NOT NULL,
    product_category  VARCHAR(50)    NOT NULL,
    order_date        DATE           NOT NULL,
    delivery_date     DATE,
    status            VARCHAR(20)    NOT NULL DEFAULT 'Delivered',
    total_amount      NUMERIC(10, 2) NOT NULL
);
"""

# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

# Delivery dates expressed as "N days ago from today"
TODAY = date.today()


def ago(days: int) -> date:
    return TODAY - timedelta(days=days)


CUSTOMERS = [
    ("CUST-001", "Alice Johnson",   "alice@example.com"),
    ("CUST-002", "Bob Martinez",    "bob@example.com"),
    ("CUST-003", "Carol Williams",  "carol@example.com"),
    ("CUST-004", "David Kim",       "david@example.com"),
    ("CUST-005", "Emma Thompson",   "emma@example.com"),
]

# (order_id, customer_id, product_name, product_category,
#  order_date, delivery_date, status, total_amount)
ORDERS = [
    (
        "ORD-001", "CUST-001",
        "Sony WH-1000XM5 Wireless Noise-Cancelling Headphones",
        "Electronics",
        ago(52), ago(45), "Delivered", 349.99,
    ),
    (
        "ORD-002", "CUST-002",
        "Python Crash Course, 3rd Edition",
        "Books",
        ago(14), ago(10), "Delivered", 29.99,
    ),
    (
        "ORD-003", "CUST-003",
        "Samsung 65-inch QLED 4K Smart TV",
        "Electronics",
        ago(25), ago(20), "Delivered", 1_199.99,
    ),
    (
        "ORD-004", "CUST-001",
        "Nike Men's Therma-FIT Running Jacket",
        "Clothing",
        ago(9), ago(5), "Delivered", 89.95,
    ),
    (
        "ORD-005", "CUST-004",
        "Instant Pot Duo 7-in-1 Electric Pressure Cooker",
        "Home & Kitchen",
        ago(6), ago(3), "Delivered", 99.95,
    ),
    (
        "ORD-006", "CUST-002",
        "Apple AirPods Pro (2nd Generation)",
        "Electronics",
        ago(12), ago(8), "Delivered", 249.00,
    ),
    (
        "ORD-007", "CUST-005",
        "Dell XPS 15 Laptop (Intel Core i7, 16GB RAM, 512GB SSD)",
        "Electronics",
        ago(20), ago(15), "Delivered", 1_549.00,
    ),
    (
        "ORD-008", "CUST-003",
        "The Pragmatic Programmer: 20th Anniversary Edition",
        "Books",
        ago(68), ago(60), "Delivered", 49.99,
    ),
    (
        "ORD-009", "CUST-004",
        "Levi's 501 Original Fit Jeans",
        "Clothing",
        ago(40), ago(35), "Delivered", 59.50,
    ),
    (
        "ORD-010", "CUST-005",
        "Logitech MX Master 3S Wireless Mouse",
        "Electronics",
        ago(5), ago(2), "Delivered", 99.99,
    ),
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main() -> None:
    print("Connecting to PostgreSQL …")
    conn = await asyncpg.connect(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        database=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        ssl="require",
    )

    print("Creating schema …")
    await conn.execute(DDL)

    print("Seeding customers …")
    await conn.executemany(
        "INSERT INTO customers (customer_id, name, email) VALUES ($1, $2, $3) "
        "ON CONFLICT (customer_id) DO NOTHING",
        CUSTOMERS,
    )

    print("Seeding orders …")
    await conn.executemany(
        """
        INSERT INTO orders
            (order_id, customer_id, product_name, product_category,
             order_date, delivery_date, status, total_amount)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (order_id) DO NOTHING
        """,
        ORDERS,
    )

    # Quick verification
    count = await conn.fetchval("SELECT COUNT(*) FROM orders")
    print(f"\nDone!  {count} order(s) in the database.")

    print("\nSample rows:")
    rows = await conn.fetch(
        "SELECT order_id, product_name, product_category, delivery_date, status "
        "FROM orders ORDER BY order_id"
    )
    for r in rows:
        print(
            f"  {r['order_id']}  {r['delivery_date']}  "
            f"{r['product_category']:<16}  {r['product_name'][:50]}"
        )

    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
