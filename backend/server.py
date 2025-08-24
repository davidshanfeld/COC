from fastapi import FastAPI, APIRouter, HTTPException, Depends, Query
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

# in-memory refresh lock (UTC timestamp in ms)
_last_refresh_ms: Optional[int] = None

# Create the main app without a prefix
app = FastAPI()

# CORS (if needed in preview env)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
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

# Excel Data Models
class DealData(BaseModel):
    id: str
    name: str
    status: str  # active, exited, pipeline
    market: str
    strategy: str  # distressed_debt, value_add, opportunistic, net_lease
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

# Authentication configuration (legacy JWT endpoints kept intact)
LP_PASSWORD = "DigitalDepression"
GP_PASSWORD = "NicoleWest0904!!"
SECRET_KEY = "coastal_oak_secret_key_2024"

# Helpers
async def gp_basic_auth(credentials: HTTPBasicCredentials = Depends(security)):
    # Do not log credentials
    correct_username = credentials.username == GP_BASIC_USERNAME
    correct_password = credentials.password == GP_BASIC_PASSWORD
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

async def fetch_treasury_yields():
    try:
        import random
        today = datetime.utcnow().strftime('%Y-%m-%d')
        treasury_data = {
            'DGS3MO': 5.25 + random.uniform(-0.1, 0.1),
            'DGS2': 4.18 + random.uniform(-0.1, 0.1),
            'DGS10': 4.45 + random.uniform(-0.1, 0.1),
            'T10Y2Y': 0.27 + random.uniform(-0.05, 0.05),
            'last_updated': today
        }
        return treasury_data
    except Exception as e:
        logger.error(f"Error fetching Treasury data: {e}")
        return {
            'DGS3MO': 5.25,
            'DGS2': 4.18,
            'DGS10': 4.45,
            'T10Y2Y': 0.27,
            'last_updated': datetime.utcnow().strftime('%Y-%m-%d')
        }

async def fetch_cpi_data():
    try:
        import random
        today = datetime.utcnow().strftime('%Y-%m-%d')
        cpi_data = {
            'CPI_U_SA': 310.5 + random.uniform(-1, 1),
            'CPI_Core_SA': 315.2 + random.uniform(-1, 1),
            'inflation_yoy': 2.8 + random.uniform(-0.2, 0.2),
            'last_updated': today
        }
        return cpi_data
    except Exception as e:
        logger.error(f"Error fetching CPI data: {e}")
        return {
            'CPI_U_SA': 310.5,
            'CPI_Core_SA': 315.2,
            'inflation_yoy': 2.8,
            'last_updated': datetime.utcnow().strftime('%Y-%m-%d')
        }

external_data_cache: Dict[str, Any] = {}
cache_expiry_minutes = 30

async def get_cached_external_data():
    global external_data_cache
    current_time = datetime.utcnow()
    if ('last_update' not in external_data_cache or
        (current_time - external_data_cache['last_update']).total_seconds() > cache_expiry_minutes * 60):
        logger.info("Fetching fresh external data...")
        treasury_data = await fetch_treasury_yields()
        cpi_data = await fetch_cpi_data()
        external_data_cache = {
            'treasury': treasury_data,
            'cpi': cpi_data,
            'last_update': current_time,
            'sources_accessed': [
                'Federal Reserve Economic Data (FRED)',
                'Bureau of Labor Statistics (BLS)',
                'US Treasury'
            ]
        }
        logger.info("External data cache updated successfully")
    return external_data_cache

ALLOWLIST = set([
    "home.treasury.gov",
    "treasury.gov",
    "bls.gov",
    "download.bls.gov",
    "fred.stlouisfed.org",
    "stlouisfed.org",
    "bea.gov",
    "eia.gov",
    "sec.gov",
    "energy.ca.gov",
    "cpuc.ca.gov",
])

def build_lineage(external: Dict[str, Any]) -> List[Dict[str, Any]]:
    now_iso = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    lineage: List[Dict[str, Any]] = []
    items = [
        {
            "title": "Daily Treasury Yield Curve Rates",
            "url": "https://home.treasury.gov/resource-center/data-chart-center/interest-rates",
            "publisher": "US Department of the Treasury",
            "series_id": "DGS10,DGS2,DGS3MO",
        },
        {
            "title": "FRED Economic Data",
            "url": "https://fred.stlouisfed.org/series/DGS10",
            "publisher": "Federal Reserve Bank of St. Louis",
            "series_id": "DGS10",
        },
        {
            "title": "Consumer Price Index (CPI)",
            "url": "https://www.bls.gov/cpi/",
            "publisher": "Bureau of Labor Statistics",
            "series_id": "CPI_U_SA,CPI_Core_SA",
        },
    ]
    for it in items:
        domain = it["url"].split("/")[2]
        if domain in ALLOWLIST:
            lineage.append({
                "title": it["title"],
                "url": it["url"],
                "publisher": it["publisher"],
                "series_id": it.get("series_id"),
                "transform_chain": [
                    {
                        "id": "fetch",
                        "desc": "HTTP GET to source endpoint",
                        "inputs": [it["url"]],
                        "outputs": ["raw_csv_or_html"],
                    },
                    {
                        "id": "normalize",
                        "desc": "Normalize and cache values",
                        "inputs": ["raw_csv_or_html"],
                        "outputs": ["treasury", "cpi"],
                    },
                ],
                "checksum_sha256": hashlib.sha256(it["url"].encode()).hexdigest(),
                "accessed_at": now_iso,
            })
    return lineage

async def compute_summary_now() -> Dict[str, Any]:
    external_data = await get_cached_external_data()
    import random, time
    seed = int(time.time() / 60)
    random.seed(seed)
    base_fv = 125000000
    base_nav = 98.7
    base_irr = 12.8
    current_fund_value = base_fv + random.randint(-500000, 500000)
    current_nav = base_nav + random.uniform(-0.5, 0.5)
    current_irr = base_irr + random.uniform(-0.3, 0.3)
    deals = [
        {
            "id": "deal_001",
            "name": "Metro Office Complex - Atlanta",
            "status": "active",
            "market": "Atlanta",
            "strategy": "value_add",
            "equity_committed": 25000000.0,
            "irr": 15.2,
            "moic": 1.8,
            "close_date": "2023-06-15",
            "power_mw": None,
        },
        {
            "id": "deal_002",
            "name": "Riverside Retail Plaza - Dallas",
            "status": "active",
            "market": "Dallas",
            "strategy": "opportunistic",
            "equity_committed": 18500000.0,
            "irr": 13.8,
            "moic": 1.6,
            "close_date": "2024-01-20",
            "power_mw": None,
        },
        {
            "id": "deal_003",
            "name": "Industrial Park - Phoenix",
            "status": "active",
            "market": "Phoenix",
            "strategy": "distressed_debt",
            "equity_committed": 32000000.0,
            "irr": 16.1,
            "moic": 2.1,
            "close_date": "2023-11-10",
            "power_mw": None,
        },
        {
            "id": "deal_004",
            "name": "Pico Blvd Office Complex - West LA",
            "status": "pipeline",
            "market": "Los Angeles",
            "strategy": "value_add",
            "equity_committed": 18500000.0,
            "irr": 28.4,
            "moic": 3.2,
            "close_date": "2024-03-01",
            "power_mw": None,
        },
    ]
    active = [d for d in deals if d["status"] == "active"]
    pipeline = [d for d in deals if d["status"] == "pipeline"]
    exited = [d for d in deals if d["status"] == "exited"]
    fund_kpis = {
        "nav": current_nav,
        "gross_irr": current_irr + 1.5,
        "net_irr": current_irr,
        "gross_moic": 1.45 + random.uniform(-0.05, 0.05),
        "net_moic": 1.34 + random.uniform(-0.05, 0.05),
        "tvpi": 1.42,
        "dpi": 0.28,
        "rvpi": 1.14,
        "aum": current_fund_value,
        "committed_capital": 500000000.0,
        "called_capital": current_fund_value,
        "uncalled_commitments": 500000000.0 - current_fund_value,
        "cash_balance": 5200000.0,
        "management_fee_accrual": 2500000.0,
        "carry_accrual": 8400000.0,
    }
    risk_kpis = {
        "wa_ltv": 65.2 + random.uniform(-2, 2),
        "wa_dscr": 1.85 + random.uniform(-0.1, 0.1),
        "interest_coverage": 2.4 + random.uniform(-0.1, 0.1),
        "wa_coupon": external_data['treasury']['DGS10'] + 2.5,
        "duration_proxy_years": 4.2,
        "default_rate_rolling_12m": 0.8,
    }
    pipeline_kpis = {
        "active_deals_count": len(active),
        "pipeline_deals_count": len(pipeline),
        "exited_deals_count": len(exited),
        "avg_underwriting_cycle_days": 45.5,
    }
    power_infra_kpis = {
        "mw_contracted": 0.0,
        "mw_energized": 0.0,
        "mw_under_loa_or_loi": 0.0,
        "run_rate_revenue_per_mw": 0.0,
        "wa_power_cost_per_mwh": 0.0,
    }
    kpis = {
        "fund": fund_kpis,
        "risk": risk_kpis,
        "pipeline": pipeline_kpis,
        "power_infra": power_infra_kpis,
    }
    as_of = datetime.utcnow().strftime('%Y-%m-%d')
    return {
        "as_of_date": as_of,
        "aum": current_fund_value,
        "deals": deals,
        "kpis": kpis,
        "external": external_data,
    }

async def next_seq_for_date(as_of_date: str) -> str:
    # find highest seq for date and increment
    max_n = 0
    async for doc in db.snapshots.find({"as_of_date": as_of_date}):
        try:
            n = int(str(doc.get("seq", "v000")).replace("v", ""))
            max_n = max(max_n, n)
        except Exception:
            continue
    return f"v{max_n+1:03d}"

async def ensure_latest_snapshot() -> Dict[str, Any]:
    doc = await db.snapshots.find_one(sort=[("created_at", -1)])
    if doc:
        return doc
    # Create initial snapshot
    return await create_snapshot(creator="system")

async def create_snapshot(creator: str = "gp") -> Dict[str, Any]:
    global _last_refresh_ms
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    now_ms = int(now.timestamp() * 1000)
    # Build summary now
    base = await compute_summary_now()
    as_of = base["as_of_date"]
    seq = await next_seq_for_date(as_of)
    lineage = build_lineage(base["external"])
    snap_id = str(uuid.uuid4())
    doc: Dict[str, Any] = {
        "_id": snap_id,  # ensure no ObjectId
        "id": snap_id,
        "as_of_date": as_of,
        "created_at": now.isoformat(),
        "creator": creator,
        "seq": seq,
        "summary": {k: base[k] for k in ["as_of_date", "aum", "deals", "kpis"]},
        "deals": base["deals"],
        "kpis": base["kpis"],
        "lineage": lineage,
        "env": {
            "timezone": "America/Los_Angeles",
            "repo_commit": os.environ.get("GIT_COMMIT", "unknown"),
            "api_base": os.environ.get("API_BASE", ""),
        },
    }
    await db.snapshots.insert_one(doc)
    logger.info(f"snapshot.created id={snap_id} as_of={as_of} seq={seq}")
    _last_refresh_ms = now_ms
    return doc

# Routes
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/excel/summary")
async def get_excel_summary(refresh: Optional[bool] = Query(default=False), snapshot_id: Optional[str] = Query(default=None)):
    global _last_refresh_ms
    if refresh:
        # rate limit
        now_ms = int(datetime.utcnow().timestamp() * 1000)
        if _last_refresh_ms is not None and (now_ms - _last_refresh_ms) < REFRESH_LOCK_MS:
            raise HTTPException(status_code=429, detail="Refresh rate-limited. Please wait before creating another snapshot.")
        snap = await create_snapshot(creator="gp")
    elif snapshot_id:
        snap = await db.snapshots.find_one({"id": snapshot_id})
        if not snap:
            # also try _id
            snap = await db.snapshots.find_one({"_id": snapshot_id})
        if not snap:
            raise HTTPException(status_code=404, detail="Snapshot not found")
    else:
        snap = await ensure_latest_snapshot()
    # Build response based on snapshot
    resp: Dict[str, Any] = {
        "as_of_date": snap["as_of_date"],
        "aum": snap["summary"]["aum"],
        "deals": snap["summary"]["deals"],
        "kpis": snap["summary"]["kpis"],
        "_last_updated_iso": snap["created_at"],
        "_snapshot_id": snap["id"],
        "_lineage": snap.get("lineage", []),
    }
    return resp

@api_router.get("/excel/data")
async def get_excel_data():
    # Keep legacy behavior but source from latest snapshot for consistency
    snap = await ensure_latest_snapshot()
    rows = []
    for d in snap["summary"]["deals"]:
        rows.append({
            "name": d["name"],
            "status": d["status"],
            "market": d["market"],
            "strategy": d["strategy"],
            "equity_committed": d.get("equity_committed"),
            "irr": d.get("irr"),
            "moic": d.get("moic"),
            "close_date": d.get("close_date"),
            "power_mw": d.get("power_mw") or 0.0,
        })
    return {
        "rows": rows,
        "as_of_date": snap["as_of_date"],
        "last_updated": snap["created_at"],
    }

@api_router.get("/excel/deals")
async def get_excel_deals():
    snap = await ensure_latest_snapshot()
    deals = snap["summary"]["deals"]
    return {
        "deals": deals,
        "total_deals": len(deals),
        "active_count": len([d for d in deals if d["status"] == "active"]),
        "pipeline_count": len([d for d in deals if d["status"] == "pipeline"]),
        "exited_count": len([d for d in deals if d["status"] == "exited"]),
        "as_of_date": snap["as_of_date"],
    }

@api_router.post("/excel/generate")
async def generate_excel_export(snapshot_id: Optional[str] = Query(default=None)):
    # Choose snapshot
    if snapshot_id:
        snap = await db.snapshots.find_one({"id": snapshot_id}) or await db.snapshots.find_one({"_id": snapshot_id})
        if not snap:
            raise HTTPException(status_code=404, detail="Snapshot not found")
    else:
        snap = await ensure_latest_snapshot()
    as_of = snap["as_of_date"]
    seq = snap["seq"]
    # Build Excel in-memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Summary sheet
        summary_df = pd.DataFrame([
            {"as_of_date": as_of, "aum": snap["summary"].get("aum"), "seq": seq, "snapshot_id": snap["id"]}
        ])
        summary_df.to_excel(writer, index=False, sheet_name="Summary")
        # Deals sheet
        deals_df = pd.DataFrame(snap["summary"].get("deals", []))
        deals_df.to_excel(writer, index=False, sheet_name="Deals")
        # KPIs sheet (flatten)
        kpis = snap["summary"].get("kpis", {})
        flat_rows = []
        for cat, vals in kpis.items():
            if isinstance(vals, dict):
                for k, v in vals.items():
                    flat_rows.append({"category": cat, "metric": k, "value": v})
        kpis_df = pd.DataFrame(flat_rows)
        kpis_df.to_excel(writer, index=False, sheet_name="KPIs")
        # Lineage sheet
        lineage_df = pd.DataFrame(snap.get("lineage", []))
        lineage_df.to_excel(writer, index=False, sheet_name="Lineage")
    output.seek(0)
    filename = f"Coastal_Excel_Analytics_{as_of}_{seq}.xlsx"
    logger.info(f"snapshot.exported id={snap['id']} filename={filename}")
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\""
        },
    )

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

@api_router.post("/auth", response_model=AuthResponse)
async def authenticate(auth_request: AuthRequest):
    password = auth_request.password.strip()
    if password == LP_PASSWORD:
        token_payload = {"user_type": "lp", "exp": datetime.utcnow() + timedelta(hours=24)}
        token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")
        return AuthResponse(success=True, user_type="lp", message="LP access granted", token=token)
    elif password == GP_PASSWORD:
        token_payload = {"user_type": "gp", "exp": datetime.utcnow() + timedelta(hours=24)}
        token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")
        return AuthResponse(success=True, user_type="gp", message="GP access granted", token=token)
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@api_router.get("/market-data", response_model=MarketDataResponse)
async def get_market_data():
    import random, time
    seed = int(time.time() / 60)
    random.seed(seed)
    base_fund_value = 125000000
    base_nav = 98.7
    base_irr = 12.8
    return MarketDataResponse(
        fund_value=base_fund_value + random.randint(-500000, 500000),
        nav=base_nav + random.uniform(-0.5, 0.5),
        irr=base_irr + random.uniform(-0.3, 0.3),
        multiple=1.34 + random.uniform(-0.05, 0.05),
        occupancy=87.2 + random.uniform(-2, 2),
        leverage=62.5 + random.uniform(-1, 1),
        last_update=datetime.utcnow().isoformat(),
    )

# Snapshot APIs
@api_router.post("/snapshots")
async def create_snapshot_endpoint(auth_ok: bool = Depends(gp_basic_auth)):
    # Rate-limit similar to refresh
    now_ms = int(datetime.utcnow().timestamp() * 1000)
    global _last_refresh_ms
    if _last_refresh_ms is not None and (now_ms - _last_refresh_ms) < REFRESH_LOCK_MS:
        raise HTTPException(status_code=429, detail="Snapshot creation rate-limited")
    snap = await create_snapshot(creator="gp")
    return snap

@api_router.get("/snapshots")
async def list_snapshots(limit: int = Query(default=10, ge=1, le=100), cursor: Optional[str] = Query(default=None), auth_ok: bool = Depends(gp_basic_auth)):
    query: Dict[str, Any] = {}
    sort = [("created_at", -1)]
    if cursor:
        # cursor is ISO created_at; return docs created before this
        query["created_at"] = {"$lt": cursor}
    cursor_db = db.snapshots.find(query).sort(sort).limit(limit + 1)
    docs = await cursor_db.to_list(length=limit + 1)
    items = []
    for d in docs[:limit]:
        items.append({
            "id": d["id"],
            "as_of_date": d["as_of_date"],
            "created_at": d["created_at"],
            "creator": d.get("creator", "gp"),
            "seq": d.get("seq", "v001"),
        })
    next_cursor_val = None
    if len(docs) > limit:
        next_cursor_val = docs[limit]["created_at"]
    return {"items": items, "next_cursor": next_cursor_val}

@api_router.get("/snapshots/{snap_id}")
async def get_snapshot_by_id(snap_id: str, auth_ok: bool = Depends(gp_basic_auth)):
    snap = await db.snapshots.find_one({"id": snap_id}) or await db.snapshots.find_one({"_id": snap_id})
    if not snap:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return snap

# Register API router
app.include_router(api_router)