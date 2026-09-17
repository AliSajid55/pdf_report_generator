import sqlite3
from datetime import datetime, timedelta

DB_PATH = "report.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_report(path: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        "INSERT INTO reports (path, created_at) VALUES (?, ?)",
        (path, datetime.now().isoformat()),
    )
    report_id: int = cur.lastrowid or 0
    conn.commit()
    conn.close()
    return report_id


def get_today_report() -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    today = datetime.now().strftime("%Y-%m-%d")
    row = conn.execute(
        "SELECT * FROM reports WHERE created_at LIKE ? ORDER BY id DESC LIMIT 1",
        (f"{today}%",),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_report(report_id: int) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_report_data() -> dict:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    total_orders = conn.execute("SELECT COUNT(*) as cnt FROM orders").fetchone()["cnt"]

    total_revenue = conn.execute("SELECT SUM(amount) as total FROM orders").fetchone()["total"]

    top_products = [
        dict(row)
        for row in conn.execute(
            "SELECT product, SUM(amount) as revenue FROM orders GROUP BY product ORDER BY revenue DESC LIMIT 5"
        )
    ]

    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    orders_per_day = [
        dict(row)
        for row in conn.execute(
            "SELECT created_at as date, COUNT(*) as orders FROM orders WHERE created_at >= ? GROUP BY created_at ORDER BY created_at",
            (seven_days_ago,),
        )
    ]

    all_orders = [
        dict(row)
        for row in conn.execute("SELECT * FROM orders ORDER BY created_at DESC")
    ]

    conn.close()

    return {
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "top_products": top_products,
        "orders_per_day": orders_per_day,
        "all_orders": all_orders,
    }


if __name__ == "__main__":
    import json

    data = get_report_data()
    print(json.dumps(data, indent=2))
