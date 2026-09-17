import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "report.db"

PRODUCTS = ["Laptop", "Phone", "Tablet", "Headphones", "Keyboard", "Mouse"]
END_DATE = datetime.now()
START_DATE = END_DATE - timedelta(days=30)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS orders")
cur.execute("""
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer TEXT NOT NULL,
        product TEXT NOT NULL,
        amount REAL NOT NULL,
        created_at TEXT NOT NULL
    )
""")

rows = []
for _ in range(200):
    product = random.choice(PRODUCTS)
    amount = round(random.uniform(5, 200), 2)
    days_ago = random.randint(0, 30)
    created_at = (END_DATE - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    customer = f"Customer_{random.randint(1, 50)}"
    rows.append((customer, product, amount, created_at))

cur.executemany("INSERT INTO orders (customer, product, amount, created_at) VALUES (?, ?, ?, ?)", rows)
conn.commit()

count = cur.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
print(f"Seeded {count} orders into {DB_PATH}")

conn.close()
