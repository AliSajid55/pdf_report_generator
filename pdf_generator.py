from datetime import datetime
from playwright.sync_api import sync_playwright
from database import get_report_data

REPORTS_DIR = "reports"

BRAND_COLOR = "#6C63FF"
BRAND_DARK = "#2D2B55"


def build_html(data: dict, days: int | None = None) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    period = f"Last {days} days" if days else "All time"

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
    @page {{
        margin: 60px 40px 80px 40px;
        @bottom-center {{
            content: "Page " counter(page) " of " counter(pages);
            font-size: 10px;
            color: #999;
        }}
        @bottom-left {{
            content: "Sales Report — FlyRank";
            font-size: 10px;
            color: #999;
        }}
    }}
    body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 40px; color: #333; background: white; }}
    .header {{ display: flex; align-items: center; justify-content: space-between; border-bottom: 3px solid {BRAND_COLOR}; padding-bottom: 20px; margin-bottom: 30px; }}
    .logo {{ display: flex; align-items: center; gap: 12px; }}
    .logo-icon {{ width: 48px; height: 48px; background: {BRAND_COLOR}; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-size: 24px; font-weight: bold; }}
    .logo-text {{ font-size: 24px; font-weight: bold; color: {BRAND_DARK}; }}
    .logo-sub {{ font-size: 12px; color: #999; margin-top: 2px; }}
    .meta {{ text-align: right; color: #666; font-size: 13px; }}
    .meta strong {{ color: {BRAND_DARK}; }}
    .summary {{ display: flex; gap: 24px; margin: 24px 0; }}
    .summary-box {{ flex: 1; background: linear-gradient(135deg, {BRAND_COLOR}15, {BRAND_COLOR}08); padding: 20px; border-radius: 12px; border-left: 4px solid {BRAND_COLOR}; }}
    .summary-box h3 {{ margin: 0; color: #999; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }}
    .summary-box p {{ margin: 8px 0 0; font-size: 28px; font-weight: bold; color: {BRAND_DARK}; }}
    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
    th {{ background: {BRAND_COLOR}; color: white; padding: 12px; text-align: left; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; }}
    td {{ padding: 10px 12px; border-bottom: 1px solid #eee; font-size: 13px; }}
    tr:nth-child(even) {{ background: #f8f9ff; }}
    tr {{ break-inside: avoid; }}
    thead {{ display: table-header-group; }}
    tr {{ page-break-inside: avoid; }}
    h2 {{ color: {BRAND_DARK}; margin-top: 32px; font-size: 18px; }}
    .footer {{ position: fixed; bottom: 0; left: 0; right: 0; padding: 15px 40px; border-top: 1px solid #eee; font-size: 10px; color: #999; display: flex; justify-content: space-between; }}
</style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <div class="logo-icon">FR</div>
            <div>
                <div class="logo-text">FlyRank</div>
                <div class="logo-sub">Analytics Platform</div>
            </div>
        </div>
        <div class="meta">
            <strong>Sales Report</strong><br>
            Generated: {today}<br>
            Period: {period}
        </div>
    </div>

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

    <div class="footer">
        <span>Sales Report — FlyRank</span>
        <span>Confidential</span>
    </div>
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


def make_filename(prefix: str = "sales-report") -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    return f"{prefix}-{today}.pdf"


if __name__ == "__main__":
    import os

    data = get_report_data()
    html = build_html(data)
    output_path = os.path.join(REPORTS_DIR, make_filename())
    render_pdf(html, output_path)
