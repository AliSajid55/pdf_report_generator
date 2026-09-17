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


def list_reports() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM reports ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_report_data(days: int | None = None) -> dict:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    if days:
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        where_clause = "WHERE created_at >= ?"
        params = (cutoff,)
    else:
        where_clause = ""
        params = ()

    total_orders = conn.execute(
        f"SELECT COUNT(*) as cnt FROM orders {where_clause}", params
    ).fetchone()["cnt"]

    total_revenue = conn.execute(
        f"SELECT SUM(amount) as total FROM orders {where_clause}", params
    ).fetchone()["total"] or 0

    top_products = [
        dict(row)
        for row in conn.execute(
            f"SELECT product, SUM(amount) as revenue FROM orders {where_clause} GROUP BY product ORDER BY revenue DESC LIMIT 5",
            params,
        )
    ]

    orders_per_day = [
        dict(row)
        for row in conn.execute(
            f"SELECT created_at as date, COUNT(*) as orders FROM orders {where_clause} GROUP BY created_at ORDER BY created_at",
            params,
        )
    ]

    all_orders = [
        dict(row)
        for row in conn.execute(
            f"SELECT * FROM orders {where_clause} ORDER BY created_at DESC", params
        )
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
