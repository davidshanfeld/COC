from fastapi import FastAPI, APIRouter, HTTPException, Depends, Query, Body
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timedelta, timezone
import jwt
import hashlib
import requests
import asyncio
import pandas as pd
from io import BytesIO

# For exports
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from pptx import Presentation
from pptx.util import Inches, Pt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("coastal_oak_backend")

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security - Basic GP-only for snapshots and refresh/export
security = HTTPBasic()
GP_BASIC_USERNAME = os.environ.get('GP_BASIC_USERNAME', 'gp')
GP_BASIC_PASSWORD = os.environ.get('GP_BASIC_PASSWORD', 'Contrarians')
REFRESH_LOCK_MS = int(os.environ.get('REFRESH_LOCK_MS', '60000'))

_last_refresh_ms: Optional[int] = None

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api_router = APIRouter(prefix="/api")

class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class AuthRequest(BaseModel):
    password: str

class AuthResponse(BaseModel):
    success: bool
    user_type: str
    message: str
    token: str = None

class MarketDataResponse(BaseModel):
    fund_value: float
    nav: float
    irr: float
    multiple: float
    occupancy: float
    leverage: float
    last_update: str

class DealData(BaseModel):
    id: str
    name: str
    status: str
    market: str
    strategy: str
    equity_committed: Optional[float] = None
    irr: Optional[float] = None
    moic: Optional[float] = None
    close_date: Optional[str] = None
    power_mw: Optional[float] = None

class FundKPIs(BaseModel):
    nav: float
    gross_irr: float
    net_irr: float
    gross_moic: float
    net_moic: float
    tvpi: float
    dpi: float
    rvpi: float
    aum: Optional[float] = None
    committed_capital: Optional[float] = None
    called_capital: Optional[float] = None
    uncalled_commitments: Optional[float] = None
    cash_balance: Optional[float] = None
    management_fee_accrual: Optional[float] = None
    carry_accrual: Optional[float] = None

class RiskKPIs(BaseModel):
    wa_ltv: float
    wa_dscr: float
    interest_coverage: float
    wa_coupon: Optional[float] = None
    duration_proxy_years: Optional[float] = None
    default_rate_rolling_12m: Optional[float] = None

class PipelineKPIs(BaseModel):
    active_deals_count: int
    pipeline_deals_count: int
    exited_deals_count: int
    avg_underwriting_cycle_days: Optional[float] = None

class PowerInfraKPIs(BaseModel):
    mw_contracted: Optional[float] = None
    mw_energized: Optional[float] = None
    mw_under_loa_or_loi: Optional[float] = None
    run_rate_revenue_per_mw: Optional[float] = None
    wa_power_cost_per_mwh: Optional[float] = None

class ExcelKPIs(BaseModel):
    fund: FundKPIs
    risk: RiskKPIs
    pipeline: PipelineKPIs
    power_infra: Optional[PowerInfraKPIs] = None

class ExcelSummaryResponse(BaseModel):
    as_of_date: str
    aum: float
    deals: List[DealData]
    kpis: ExcelKPIs

class ExcelSummaryWithMeta(ExcelSummaryResponse):
    _last_updated_iso: Optional[str] = None
    _snapshot_id: Optional[str] = None
    _lineage: Optional[List[Dict[str, Any]]] = None

LP_PASSWORD = "DigitalDepression"
GP_PASSWORD = "NicoleWest0904!!"
SECRET_KEY = "coastal_oak_secret_key_2024"

async def gp_basic_auth(credentials: HTTPBasicCredentials = Depends(security)):
    if not (credentials.username == GP_BASIC_USERNAME and credentials.password == GP_BASIC_PASSWORD):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

# External data and summary functions (unchanged)…
# [omitted here for brevity in this diff; the rest of the file remains as previously implemented]

# -- Existing snapshot and excel routes here --

# Export Endpoints (GP-only)
class ExecSummaryRequest(BaseModel):
    as_of_date: Optional[str] = None
    scenario: Optional[str] = "Base"
    sections: Optional[List[str]] = ["What", "Why", "How", "Proof", "Risks", "Next"]
    brand_mode: Optional[str] = "light"

@api_router.post("/export/executive-summary")
async def export_executive_summary(req: ExecSummaryRequest = Body(...), auth_ok: bool = Depends(gp_basic_auth)):
    # Use latest snapshot
    snap = await ensure_latest_snapshot()
    as_of = req.as_of_date or snap["as_of_date"]
    # Build simple PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    textobject = c.beginText(72, 720)
    textobject.setFont("Helvetica-Bold", 16)
    textobject.textLine("Coastal Oak Capital — Executive Summary")
    textobject.setFont("Helvetica", 10)
    textobject.textLine("")
    textobject.textLine(f"As of {as_of}. Scenario: {req.scenario}.")
    textobject.textLine("")
    textobject.textLine("Fund KPIs:")
    kf = snap["summary"]["kpis"]["fund"]
    textobject.textLine(f"AUM: ${kf.get('aum', 0):,.0f} | NAV: {kf.get('nav', 0):.2f}")
    textobject.textLine(f"Net IRR: {kf.get('net_irr', 0):.2f}% | Net MOIC: {kf.get('net_moic', 0):.2f}x")
    textobject.textLine(f"TVPI: {kf.get('tvpi', 0):.2f}x | DPI: {kf.get('dpi', 0):.2f} | RVPI: {kf.get('rvpi', 0):.2f}")
    textobject.textLine("")
    textobject.textLine("Sources & Methods:")
    for it in snap.get("lineage", [])[:5]:
        title = it.get('title', 'Source')
        url = it.get('url', '')
        textobject.textLine(f"- {title} — {url}")
    textobject.textLine("")
    textobject.textLine("For institutional use only. Not investment advice.")
    c.drawText(textobject)
    c.showPage()
    c.save()
    buffer.seek(0)
    filename = f"Executive_Summary_{as_of}.pdf"
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=\"{filename}\""})

class PitchDeckRequest(BaseModel):
    as_of_date: Optional[str] = None
    format: Optional[str] = "pptx"
    slideset: Optional[str] = "default_v1"
    include_notes: Optional[bool] = True

@api_router.post("/export/pitch-deck")
async def export_pitch_deck(req: PitchDeckRequest = Body(...), auth_ok: bool = Depends(gp_basic_auth)):
    snap = await ensure_latest_snapshot()
    as_of = req.as_of_date or snap["as_of_date"]
    prs = Presentation()
    # Title slide
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    slide.shapes.title.text = "Coastal Oak Capital"
    slide.placeholders[1].text = f"Turning structured credit into equity control — As of {as_of}"
    # KPI slide
    layout = prs.slide_layouts[1]
    s2 = prs.slides.add_slide(layout)
    s2.shapes.title.text = "Fund KPIs"
    tf = s2.placeholders[1].text_frame
    kf = snap["summary"]["kpis"]["fund"]
    tf.text = f"NAV: {kf.get('nav', 0):.2f}\nNet IRR: {kf.get('net_irr', 0):.2f}%\nNet MOIC: {kf.get('net_moic', 0):.2f}x\nTVPI: {kf.get('tvpi', 0):.2f}x"
    # Sources slide
    s3 = prs.slides.add_slide(layout)
    s3.shapes.title.text = "Sources & Methods"
    tf2 = s3.placeholders[1].text_frame
    for it in snap.get("lineage", [])[:5]:
        tf2.add_paragraph().text = f"{it.get('title', '')} — {it.get('url', '')}"
    out = BytesIO()
    prs.save(out)
    out.seek(0)
    filename = f"Coastal_Oak_Pitch_{as_of}.pptx"
    return StreamingResponse(out, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", headers={"Content-Disposition": f"attachment; filename=\"{filename}\""})

@api_router.get("/export/excel")
async def export_excel(snapshot_id: Optional[str] = Query(default=None), auth_ok: bool = Depends(gp_basic_auth)):
    # Reuse generate logic
    if snapshot_id:
        snap = await db.snapshots.find_one({"id": snapshot_id}) or await db.snapshots.find_one({"_id": snapshot_id})
        if not snap:
            raise HTTPException(status_code=404, detail="Snapshot not found")
    else:
        snap = await ensure_latest_snapshot()
    as_of = snap["as_of_date"]
    seq = snap.get("seq", "v001")
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary_df = pd.DataFrame([{ "as_of_date": as_of, "aum": snap["summary"].get("aum"), "seq": seq, "snapshot_id": snap["id"] }])
        summary_df.to_excel(writer, index=False, sheet_name="Summary")
        deals_df = pd.DataFrame(snap["summary"].get("deals", []))
        deals_df.to_excel(writer, index=False, sheet_name="Deals")
        kpis = snap["summary"].get("kpis", {})
        flat_rows = []
        for cat, vals in kpis.items():
            if isinstance(vals, dict):
                for k, v in vals.items():
                    flat_rows.append({"category": cat, "metric": k, "value": v})
        kpis_df = pd.DataFrame(flat_rows)
        kpis_df.to_excel(writer, index=False, sheet_name="KPIs")
        lineage_df = pd.DataFrame(snap.get("lineage", []))
        lineage_df.to_excel(writer, index=False, sheet_name="Lineage")
    output.seek(0)
    filename = f"Coastal_Excel_Analytics_{as_of}_{seq}.xlsx"
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment; filename=\"{filename}\""})

app.include_router(api_router)