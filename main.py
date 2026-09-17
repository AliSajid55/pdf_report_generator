import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from database import init_db, get_report_data, save_report, get_report
from pdf_generator import build_html, render_pdf, REPORTS_DIR

app = FastAPI()


@app.on_event("startup")
def startup():
    init_db()
    os.makedirs(REPORTS_DIR, exist_ok=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/reports", status_code=201)
def create_report():
    data = get_report_data()
    html = build_html(data)
    report_id = save_report("placeholder")
    filename = f"{report_id}.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)
    render_pdf(html, filepath)

    conn = __import__("sqlite3").connect("report.db")
    conn.execute("UPDATE reports SET path = ? WHERE id = ?", (filepath, report_id))
    conn.commit()
    conn.close()

    return {"id": report_id, "file": f"/reports/{report_id}/file"}


@app.get("/reports/{report_id}")
def get_report_info(report_id: int):
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"id": report["id"], "path": report["path"], "created_at": report["created_at"]}


@app.get("/reports/{report_id}/file")
def get_report_file(report_id: int):
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if not os.path.exists(report["path"]):
        raise HTTPException(status_code=404, detail="PDF file not found")
    return FileResponse(report["path"], media_type="application/pdf", filename=f"report_{report_id}.pdf")
