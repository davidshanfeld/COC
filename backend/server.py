# ================================
# FILE: /app/backend/server.py
# Framework: FastAPI (keeps CORS + Mongo optional)
# ================================

import os
import json
import time
import random
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

try:
    # optional, runs in-memory if missing
    from pymongo import MongoClient
except Exception:  # pragma: no cover
    MongoClient = None  # type: ignore

try:
    # Optional PDF engine
    import weasyprint
    PDF_ENGINE = "weasyprint"
except ImportError:
    try:
        from playwright.sync_api import sync_playwright
        PDF_ENGINE = "playwright"
    except ImportError:
        PDF_ENGINE = None

import httpx
import xml.etree.ElementTree as ET
from math import isfinite

APP_VERSION = "coastal-oak-mvp-1.2.0"
PORT = int(os.getenv("PORT", "5050"))
MONGO_URL = os.getenv("MONGO_URL", "")
FRED_API_KEY = os.getenv("FRED_API_KEY", "")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

app = FastAPI(title="Coastal Oak — Living Pitch Deck")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ORIGINS] if CORS_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# Optional Mongo setup
# ------------------------------
_db = None
if MONGO_URL and MongoClient is not None:
    try:
        _db = MongoClient(MONGO_URL).get_default_database()
    except Exception:
        _db = None

# Fallback in-memory stores
FOOTNOTES: Dict[str, Dict[str, Any]] = {}
ACCESS_LOG: List[Dict[str, Any]] = []
TOKENS: Dict[str, Dict[str, Any]] = {}

# Simple caches
CACHE: Dict[str, Dict[str, Any]] = {
    "fred_dff": {"data": None, "exp": 0, "ttl": 15 * 60},
    "treasury_curve": {"data": None, "exp": 0, "ttl": 15 * 60},
}

# ------------------------------
# Helpers
# ------------------------------

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _hash(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:12]

async def fetch_fred_dff_live() -> Dict[str, Any]:
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {"series_id": "DFF", "api_key": FRED_API_KEY, "file_type": "json", "sort_order": "desc", "limit": 1}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        obs = data.get("observations", [])
        if not obs:
            raise ValueError("no observations")
        latest = obs[0]
        v = latest.get("value")
        v_num = float(v) if v not in (None, ".") else None
        return {"value": v_num, "date": latest.get("date"), "source": "live"}

async def fetch_fred_dff() -> Dict[str, Any]:
    """Fetch latest DFF from FRED with cache. Falls back to mock if no key or error."""
    now = time.time()
    if CACHE["fred_dff"]["data"] and CACHE["fred_dff"]["exp"] > now:
        return CACHE["fred_dff"]["data"]
    try:
        if not FRED_API_KEY:
            raise RuntimeError("no key")
        data = await fetch_fred_dff_live()
    except Exception:
        data = {"value": 5.33, "date": "2025-06-01", "source": "fallback" if FRED_API_KEY else "mock"}
    CACHE["fred_dff"]["data"] = data
    CACHE["fred_dff"]["exp"] = now + CACHE["fred_dff"]["ttl"]
    return data

async def fetch_treasury_curve_live() -> Dict[str, Any]:
    year = datetime.now().year
    base = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml"
    params_year = {"data": "daily_treasury_yield_curve", "field_tdr_date_value": str(year)}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(base, params=params_year)
        r.raise_for_status()
        root = ET.fromstring(r.text)
        records = root.findall(".//record")
        if not records:
            raise ValueError("no records for year")
        last = records[-1]
        def _get(tag: str) -> Optional[float]:
            el = last.find(tag)
            if el is None or el.text in (None, ""):
                return None
            try:
                return float(el.text)
            except Exception:
                return None
        t5 = _get("bc_5year")
        t10 = _get("bc_10year")
        t30 = _get("bc_30year")
        d = last.findtext("new_date") or last.findtext("record_date")
        return {"t5": t5, "t10": t10, "t30": t30, "date": d, "source": "live"}

async def fetch_treasury_curve() -> Dict[str, Any]:
    now = time.time()
    if CACHE["treasury_curve"]["data"] and CACHE["treasury_curve"]["exp"] > now:
        return CACHE["treasury_curve"]["data"]
    try:
        data = await fetch_treasury_curve_live()
    except Exception:
        data = {"t5": 4.50, "t10": 4.49, "t30": 4.66, "date": "2025-06-01", "source": "fallback"}
    CACHE["treasury_curve"]["data"] = data
    CACHE["treasury_curve"]["exp"] = now + CACHE["treasury_curve"]["ttl"]
    return data

# ------------------------------
# Footnote registry (Mongo-backed if available)
# ------------------------------

def upsert_footnote(_id: str, label: str, source: str, refresh: str, transform: str) -> None:
    rec = {
        "id": _id,
        "label": label,
        "source": source,
        "retrievedAt": now_iso(),
        "refresh": refresh,
        "transform": transform,
    }
    FOOTNOTES[_id] = rec
    if _db is not None:
        try:
            col = _db["footnotes"]
            # Add a simple version and hash for integrity
            rec["version"] = int(time.time())
            rec["hash"] = _hash(json.dumps({k: rec[k] for k in sorted(rec)}))
            col.update_one({"id": _id}, {"$set": rec}, upsert=True)
        except Exception:
            pass

# Seed static notes (updated at runtime on requests)
upsert_footnote("T1", "Treasury yield curve (5y/10y/30y)", "Treasury XML", "Daily", "latest close")
upsert_footnote("F1", "Effective Federal Funds Rate (DFF)", "FRED API", "Daily", "latest observation")
upsert_footnote("M1", "CRE maturities by asset type (placeholder)", "Vendor feed pending (Trepp/MSCI)", "Quarterly", "rolling sum")
upsert_footnote("B1", "Bank exposure metrics (placeholder)", "FDIC Call Reports", "Quarterly", "latest available")

# ------------------------------
# Audit helper
# ------------------------------

def log_event(action: str, meta: Optional[Dict[str, Any]] = None) -> None:
    entry = {"action": action, "ts": now_iso(), **(meta or {})}
    ACCESS_LOG.append(entry)
    if _db is not None:
        try:
            _db["access_log"].insert_one(entry)
        except Exception:
            pass

# ------------------------------
# PDF Generation Helpers
# ------------------------------

def render_executive_summary_html(data: Dict[str, Any]) -> str:
    """Render executive summary HTML with data substitution."""
    template_path = Path(__file__).parent / "pdf" / "templates" / "executive_summary.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Simple template substitution
        html_content = html_content.replace("{{ asOf }}", str(data.get("asOf", "—")))
        html_content = html_content.replace("{{ ffr }}", f"{data.get('ffr', 5.33):.2f}")
        html_content = html_content.replace("{{ t5 }}", f"{data.get('t5', 4.50):.2f}")
        html_content = html_content.replace("{{ t10 }}", f"{data.get('t10', 4.49):.2f}")
        html_content = html_content.replace("{{ t30 }}", f"{data.get('t30', 4.66):.2f}")
        html_content = html_content.replace("{{ watermark }}", data.get("watermark", "Confidential"))
        
        return html_content
        
    except FileNotFoundError:
        # Fallback if template not found
        return f"""
        <html><head><title>Executive Summary</title></head>
        <body style="font-family: Arial, sans-serif; margin: 2em;">
        <h1>Coastal Oak Capital - Executive Summary</h1>
        <p><strong>Watermark:</strong> {data.get('watermark', 'Confidential')}</p>
        <p><strong>As of:</strong> {data.get('asOf', '—')}</p>
        <h2>Current Rates</h2>
        <ul>
        <li>Fed Funds: {data.get('ffr', 5.33):.2f}%</li>
        <li>5-Year Treasury: {data.get('t5', 4.50):.2f}%</li>
        <li>10-Year Treasury: {data.get('t10', 4.49):.2f}%</li>
        <li>30-Year Treasury: {data.get('t30', 4.66):.2f}%</li>
        </ul>
        <p><em>This is a fallback template. Full template not found.</em></p>
        </body></html>
        """

def generate_pdf_from_html(html_content: str) -> bytes:
    """Generate PDF from HTML using available engine."""
    if PDF_ENGINE == "weasyprint":
        try:
            pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
            return pdf_bytes
        except Exception as e:
            raise RuntimeError(f"WeasyPrint PDF generation failed: {e}")
    
    elif PDF_ENGINE == "playwright":
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.set_content(html_content)
                pdf_bytes = page.pdf(
                    format="A4",
                    margin={"top": "1in", "right": "1in", "bottom": "1in", "left": "1in"},
                    print_background=True
                )
                browser.close()
                return pdf_bytes
        except Exception as e:
            raise RuntimeError(f"Playwright PDF generation failed: {e}")
    
    else:
        raise RuntimeError("No PDF engine available")

# ------------------------------
# API
# ------------------------------

@app.middleware("http")
async def add_version_header(request: Request, call_next):
    resp = await call_next(request)
    resp.headers["X-Coastal-Version"] = APP_VERSION
    return resp

# Serve CSS for executive summary
@app.get("/api/execsum/styles.css")
async def serve_executive_css():
    css_path = Path(__file__).parent / "pdf" / "styles" / "executive.css"
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        return Response(content=css_content, media_type="text/css")
    except FileNotFoundError:
        # Fallback minimal CSS
        return Response(content="body{font-family:Arial,sans-serif;margin:2em;}", media_type="text/css")

@app.get("/api/health")
async def health():
    return {"ok": True, "version": APP_VERSION, "time": now_iso()}

@app.get("/api/healthz/deps")
async def health_deps():
    deps = {"mongo": False, "fred": False, "treasury": False, "pdf": PDF_ENGINE}
    # Mongo
    if _db is not None:
        try:
            _db.list_collection_names()
            deps["mongo"] = True
        except Exception:
            deps["mongo"] = False
    # FRED
    if FRED_API_KEY:
        try:
            await fetch_fred_dff_live()
            deps["fred"] = True
        except Exception:
            deps["fred"] = False
    # Treasury
    try:
        await fetch_treasury_curve_live()
        deps["treasury"] = True
    except Exception:
        deps["treasury"] = False
    return {"ok": all(deps.values()) or True, "deps": deps, "time": now_iso()}

@app.get("/api/rates")
async def api_rates(audience: str = Query("LP", regex="^(LP|GP|Internal)$")):
    fred = await fetch_fred_dff()
    tsy = await fetch_treasury_curve()

    upsert_footnote("F1", "Effective Federal Funds Rate (DFF)", "FRED API", "Daily", "latest observation")
    upsert_footnote("T1", "Treasury yield curve (5y/10y/30y)", "Treasury XML", "Daily", "latest close")

    payload = {
        "ffr": fred["value"],
        "ffr_date": fred["date"],
        "t5": tsy["t5"],
        "t10": tsy["t10"],
        "t30": tsy["t30"],
        "asOf": tsy["date"] or fred["date"],
        "sources": {"F1": fred["source"], "T1": tsy["source"]},
        "audience": audience,
    }
    # Audience gating placeholder (extend as sensitive fields appear)
    if audience == "LP":
        payload.pop("internalNotes", None)
    return payload

@app.get("/api/maturities")
async def api_maturities(audience: str = Query("LP", regex="^(LP|GP|Internal)$")):
    # Placeholder rows compatible with Trepp/MSCI swap later
    rows = [
        {"year": 2025, "mf": 38, "off": 29, "ind": 14, "other": 19},
        {"year": 2026, "mf": 32, "off": 31, "ind": 18, "other": 19},
        {"year": 2027, "mf": 28, "off": 26, "ind": 22, "other": 24},
    ]
    upsert_footnote("M1", "CRE maturities by asset type (placeholder)", "Vendor feed pending (Trepp/MSCI)", "Quarterly", "rolling sum")
    return {"rows": rows, "asOf": now_iso(), "source": "mock", "audience": audience}

@app.get("/api/footnotes")
async def api_footnotes():
    """Return footnotes as array for frontend compatibility."""
    footnotes_list = []
    
    # Try MongoDB first
    if _db is not None:
        try:
            for doc in _db["footnotes"].find({}, {"_id": 0}):
                footnotes_list.append(doc)
        except Exception:
            pass
    
    # Fallback to in-memory
    if not footnotes_list:
        footnotes_list = list(FOOTNOTES.values())
    
    return footnotes_list

# --- Banks (FDIC placeholder, structure-compatible) ---
BANKS = [
    {"id": "bk1", "name": "Regional Alpha", "type": "regional", "region": "West", "creShare": 31.2, "exposure": {"mf": 22, "off": 38, "ind": 24, "other": 16}},
    {"id": "bk2", "name": "Community Beta", "type": "community", "region": "South", "creShare": 44.5, "exposure": {"mf": 28, "off": 34, "ind": 18, "other": 20}},
    {"id": "bk3", "name": "Regional Gamma", "type": "regional", "region": "Midwest", "creShare": 27.9, "exposure": {"mf": 20, "off": 30, "ind": 30, "other": 20}},
]

@app.get("/api/banks")
async def api_banks(region: Optional[str] = None, btype: Optional[str] = None):
    data = BANKS
    if region:
        data = [b for b in data if b["region"].lower() == region.lower()]
    if btype:
        data = [b for b in data if b["type"].lower() == btype.lower()]
    upsert_footnote("B1", "Bank exposure metrics (placeholder)", "FDIC Call Reports", "Quarterly", "latest available")
    return {"rows": [{"id": b["id"], "name": b["name"], "type": b["type"], "region": b["region"], "creShare": b["creShare"]} for b in data]}

@app.get("/api/banks/{bank_id}")
async def api_bank_detail(bank_id: str):
    for b in BANKS:
        if b["id"] == bank_id:
            return {"id": b["id"], "name": b["name"], "exposure": b["exposure"], "creShare": b["creShare"], "asOf": now_iso(), "source": "mock"}
    raise HTTPException(status_code=404, detail="bank not found")

# --- Waterfall (simplified) ---

def irr(cashflows: List[float], guess: float = 0.1, max_iter: int = 100, tol: float = 1e-6) -> Optional[float]:
    """Simple IRR for equal-period cashflows; returns None if fails."""
    if not cashflows or all(c == 0 for c in cashflows):
        return None
    r = guess
    for _ in range(max_iter):
        npv = 0.0
        dnpv = 0.0
        for t, c in enumerate(cashflows):
            denom = (1 + r) ** t
            npv += c / denom
            if denom != 0:
                dnpv -= t * c / denom / (1 + r)
        if abs(dnpv) < 1e-12:
            break
        step = npv / dnpv
        r -= step
        if abs(step) < tol and isfinite(r):
            return r
    return None

@app.post("/api/waterfall/calc")
async def api_waterfall_calc(payload: Dict[str, Any]):
    terms = payload.get("terms", {})
    cf = payload.get("cashflows") or []  # e.g., [-1_000_000, 100_000, 120_000, ...]
    mgmt = float(terms.get("mgmtFee", 0.02))
    pref = float(terms.get("pref", 0.08))
    lp_split = float(terms.get("splitLP", 0.6))
    gp_split = float(terms.get("splitGP", 0.4))
    gross_irr = float(terms.get("grossIRR", 0.18))

    computed_irr = irr(cf) if cf else gross_irr
    if computed_irr is None:
        computed_irr = gross_irr

    fee_drag = mgmt
    over_pref = max(0.0, computed_irr - pref)
    lp_net = pref + over_pref * lp_split - fee_drag
    gp_carry = over_pref * gp_split

    out = {
        "inputs": {"mgmtFee": mgmt, "pref": pref, "splitLP": lp_split, "splitGP": gp_split, "grossIRR": gross_irr, "cashflows": cf},
        "outputs": {"lpNetIRR": round(lp_net, 4), "gpCarry": round(gp_carry, 4), "feeDrag": round(fee_drag, 4), "overPref": round(over_pref, 4), "computedIRR": round(computed_irr, 4)},
        "note": "Simplified waterfall; replace with time-phased engine for production.",
    }
    return out

# ------------------------------
# Security: token issuance + single-use download
# ------------------------------

@app.post("/api/deck/request")
async def api_deck_request(payload: Dict[str, Any], request: Request):
    email = (payload or {}).get("email") or "guest@unknown"
    token = f"tok_{int(time.time())}_{random.randint(1000,9999)}"
    meta = {"user": email, "token": token, "issuedAt": now_iso(), "used": False, "ip": request.client.host}
    TOKENS[token] = meta
    log_event("issue-token", meta)
    return {"token": token, "message": "Single-use token issued (demo)", "watermark": f"{email} | {now_iso()}"}

@app.get("/api/deck/download")
async def api_deck_download(token: str = Query(...), request: Request = None):
    rec = TOKENS.get(token)
    if not rec:
        log_event("download-deny", {"reason": "invalid-token", "ip": getattr(request.client, 'host', None) if request else None})
        raise HTTPException(status_code=403, detail="invalid token")
    if rec.get("used"):
        log_event("download-deny", {"reason": "reused-token", "token": token, "ip": getattr(request.client, 'host', None) if request else None})
        raise HTTPException(status_code=403, detail="token already used")
    # Bind on first use
    rec["used"] = True
    rec["firstUseAt"] = now_iso()
    rec["firstUseIp"] = getattr(request.client, 'host', None) if request else None
    TOKENS[token] = rec
    log_event("download-allow", {"token": token, "ip": rec.get("firstUseIp")})
    # For MVP, return JSON. Replace with file response later.
    return {"ok": True, "watermark": f"{rec['user']} | {now_iso()}", "note": "This would stream a watermarked PDF in production."}

@app.get("/api/audit")
async def api_audit(limit: int = 50):
    return {"rows": ACCESS_LOG[-limit:]}

# ------------------------------
# Executive Summary PDF Generation
# ------------------------------

@app.get("/api/execsum/html", response_class=HTMLResponse)
async def api_execsum_html(email: str = Query("viewer@example.com")):
    """Render executive summary as HTML (always works, zero deps)."""
    # Gather data
    fred = await fetch_fred_dff()
    tsy = await fetch_treasury_curve()
    
    data = {
        "asOf": tsy.get("date") or fred.get("date", now_iso()[:10]),
        "ffr": fred.get("value", 5.33),
        "t5": tsy.get("t5", 4.50),
        "t10": tsy.get("t10", 4.49),
        "t30": tsy.get("t30", 4.66),
        "watermark": f"{email} | {now_iso()[:19]}"
    }
    
    html_content = render_executive_summary_html(data)
    log_event("execsum-html", {"email": email, "asOf": data["asOf"]})
    
    return HTMLResponse(content=html_content)

@app.get("/api/execsum.pdf")
async def api_execsum_pdf(email: str = Query("viewer@example.com")):
    """Generate executive summary PDF or return HTML fallback."""
    # Gather data
    fred = await fetch_fred_dff()
    tsy = await fetch_treasury_curve()
    
    data = {
        "asOf": tsy.get("date") or fred.get("date", now_iso()[:10]),
        "ffr": fred.get("value", 5.33),
        "t5": tsy.get("t5", 4.50),
        "t10": tsy.get("t10", 4.49),
        "t30": tsy.get("t30", 4.66),
        "watermark": f"{email} | {now_iso()[:19]}"
    }
    
    html_content = render_executive_summary_html(data)
    
    # Try PDF generation
    if PDF_ENGINE:
        try:
            pdf_bytes = generate_pdf_from_html(html_content)
            log_event("execsum-pdf", {"email": email, "asOf": data["asOf"], "engine": PDF_ENGINE})
            
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=CoastalOak_ExecSummary_{data['asOf']}.pdf",
                    "X-PDF-Engine": PDF_ENGINE
                }
            )
        except Exception as e:
            log_event("execsum-pdf-fallback", {"email": email, "error": str(e)})
    
    # Fallback to HTML with special header
    log_event("execsum-html-fallback", {"email": email, "asOf": data["asOf"]})
    return HTMLResponse(
        content=html_content,
        headers={"X-PDF-Mode": "fallback"}
    )

# Minimal agent orchestrator stub
@app.post("/api/agents/execute")
async def api_agents_execute(payload: Dict[str, Any]):
    objective = payload.get("objective", "")
    tags = payload.get("tags", [])
    packets: List[Dict[str, Any]] = []

    if "data" in tags:
        r = await api_rates()
        m = await api_maturities()
        packets.append({
            "name": "Data Packet",
            "executive_takeaway": "Rates and maturities refreshed.",
            "findings": {"rates": r, "maturities": m},
            "footnotes": ["F1", "T1", "M1", "B1"],
        })

    summary = f"Completed {len(packets)} packets for '{objective}'."
    # Flatten footnotes from Mongo if available
    registry: Dict[str, Dict[str, Any]] = {}
    if _db is not None:
        try:
            for doc in _db["footnotes"].find({}, {"_id": 0}):
                registry[doc["id"]] = doc
        except Exception:
            registry = {}
    if not registry:
        registry = FOOTNOTES

    footnote_register = {k: f"{v['label']} | {v['source']} | {v.get('retrievedAt','')} | {v.get('refresh','')} | {v.get('transform','')}" for k, v in registry.items()}
    return {"summary": summary, "packets": packets, "footnoteRegister": footnote_register}

if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(app, host="0.0.0.0", port=PORT)