import sqlite3
from datetime import datetime, timedelta

DB_PATH = "report.db"


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

    conn.close()

    return {
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "top_products": top_products,
        "orders_per_day": orders_per_day,
    }


if __name__ == "__main__":
    import json

    data = get_report_data()
    print(json.dumps(data, indent=2))
