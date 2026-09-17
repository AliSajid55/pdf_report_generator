import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from database import init_db, get_report_data, save_report, get_report, get_today_report, list_reports
from pdf_generator import build_html, render_pdf, make_filename, REPORTS_DIR

app = FastAPI()


class ReportRequest(BaseModel):
    days: int | None = None
    force: bool = False


@app.on_event("startup")
def startup():
    init_db()
    os.makedirs(REPORTS_DIR, exist_ok=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/reports")
def list_all_reports():
    reports = list_reports()
    return {"reports": [{"id": r["id"], "created_at": r["created_at"], "file": f"/reports/{r['id']}/file"} for r in reports]}


@app.post("/reports")
def create_report(body: ReportRequest = ReportRequest()):
    if not body.force:
        existing = get_today_report()
        if existing:
            return {"id": existing["id"], "file": f"/reports/{existing['id']}/file"}

    data = get_report_data(days=body.days)
    html = build_html(data, days=body.days)
    report_id = save_report("placeholder")
    filename = make_filename()
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
    filename = os.path.basename(report["path"])
    return FileResponse(report["path"], media_type="application/pdf", filename=filename)
