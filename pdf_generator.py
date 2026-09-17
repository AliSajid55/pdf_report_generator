from datetime import datetime
from playwright.sync_api import sync_playwright
from database import get_report_data

REPORTS_DIR = "reports"


def build_html(data: dict) -> str:
    today = datetime.now().strftime("%Y-%m-%d")

    top_products_rows = ""
    for p in data["top_products"]:
        top_products_rows += f"""
        <tr>
            <td>{p['product']}</td>
            <td>${p['revenue']:,.2f}</td>
        </tr>"""

    all_orders_rows = ""
    for o in data["all_orders"]:
        all_orders_rows += f"""
        <tr>
            <td>{o['id']}</td>
            <td>{o['customer']}</td>
            <td>{o['product']}</td>
            <td>${o['amount']:,.2f}</td>
            <td>{o['created_at']}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
    h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
    .summary {{ display: flex; gap: 40px; margin: 20px 0; }}
    .summary-box {{ background: #f8f9fa; padding: 15px 25px; border-radius: 8px; border-left: 4px solid #3498db; }}
    .summary-box h3 {{ margin: 0; color: #7f8c8d; font-size: 14px; }}
    .summary-box p {{ margin: 5px 0 0; font-size: 24px; font-weight: bold; color: #2c3e50; }}
    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
    th {{ background: #3498db; color: white; padding: 10px; text-align: left; }}
    td {{ padding: 8px 10px; border-bottom: 1px solid #ecf0f1; }}
    tr:nth-child(even) {{ background: #f8f9fa; }}
    tr {{ break-inside: avoid; }}
    h2 {{ color: #2c3e50; margin-top: 30px; }}
</style>
</head>
<body>
    <h1>Sales Report — {today}</h1>

    <div class="summary">
        <div class="summary-box">
            <h3>Total Orders</h3>
            <p>{data['total_orders']}</p>
        </div>
        <div class="summary-box">
            <h3>Total Revenue</h3>
            <p>${data['total_revenue']:,.2f}</p>
        </div>
    </div>

    <h2>Top 5 Products by Revenue</h2>
    <table>
        <thead>
            <tr><th>Product</th><th>Revenue</th></tr>
        </thead>
        <tbody>
            {top_products_rows}
        </tbody>
    </table>

    <h2>All Orders</h2>
    <table>
        <thead>
            <tr><th>ID</th><th>Customer</th><th>Product</th><th>Amount</th><th>Date</th></tr>
        </thead>
        <tbody>
            {all_orders_rows}
        </tbody>
    </table>
</body>
</html>"""


def render_pdf(html: str, output_path: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        page.pdf(path=output_path, format="A4", print_background=True)
        browser.close()
    print(f"PDF saved to {output_path}")


if __name__ == "__main__":
    import os

    data = get_report_data()
    html = build_html(data)
    output_path = os.path.join(REPORTS_DIR, "test.pdf")
    render_pdf(html, output_path)
