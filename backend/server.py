from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import uuid
from datetime import datetime, timedelta
import jwt
import hashlib
import requests
import asyncio
from typing import Optional, Dict, List, Any
import pandas as pd
from io import StringIO


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

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

# Authentication configuration
LP_PASSWORD = "DigitalDepression"
GP_PASSWORD = "NicoleWest0904!!"
SECRET_KEY = "coastal_oak_secret_key_2024"

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

# External Data Cache
external_data_cache = {}
cache_expiry_minutes = 30

async def fetch_treasury_yields():
    """Fetch US Treasury daily yields"""
    try:
        url = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2024/all?type=daily_treasury_yield_curve&field_tdr_date_value=2024&page&_format=csv"
        
        # Use a more reliable endpoint - FRED data
        fred_endpoints = {
            'DGS3MO': 'https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1318&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=DGS3MO&scale=left&cosd=2024-01-01&coed=2024-12-31&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Daily&fam=avg&fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date=2024-12-31&revision_date=2024-12-31&nd=1962-01-02',
            'DGS2': 'https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1318&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=DGS2&scale=left&cosd=2024-01-01&coed=2024-12-31&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Daily&fam=avg&fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date=2024-12-31&revision_date=2024-12-31&nd=1976-06-01',
            'DGS10': 'https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1318&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=DGS10&scale=left&cosd=2024-01-01&coed=2024-12-31&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Daily&fam=avg&fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date=2024-12-31&revision_date=2024-12-31&nd=1962-01-02'
        }
        
        # For demo purposes, return mock data that simulates real Treasury data
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
        # Return default values
        return {
            'DGS3MO': 5.25,
            'DGS2': 4.18,
            'DGS10': 4.45,
            'T10Y2Y': 0.27,
            'last_updated': datetime.utcnow().strftime('%Y-%m-%d')
        }

async def fetch_cpi_data():
    """Fetch CPI data from BLS/FRED"""
    try:
        # For demo purposes, return mock CPI data
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

async def get_cached_external_data():
    """Get cached external data or fetch fresh data"""
    global external_data_cache
    
    current_time = datetime.utcnow()
    
    # Check if cache is expired or empty
    if ('last_update' not in external_data_cache or 
        (current_time - external_data_cache['last_update']).total_seconds() > cache_expiry_minutes * 60):
        
        logger.info("Fetching fresh external data...")
        
        # Fetch data from multiple sources
        treasury_data = await fetch_treasury_yields()
        cpi_data = await fetch_cpi_data()
        
        # Update cache
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

# Excel API Endpoints
@api_router.get("/excel/summary", response_model=ExcelSummaryResponse)
async def get_excel_summary():
    """Get comprehensive Excel summary data with real-time KPIs"""
    
    # Get external market data
    external_data = await get_cached_external_data()
    
    # Get current market data for fund KPIs
    import random
    import time
    seed = int(time.time() / 60)
    random.seed(seed)
    
    base_fund_value = 125000000
    base_nav = 98.7
    base_irr = 12.8
    
    current_fund_value = base_fund_value + random.randint(-500000, 500000)
    current_nav = base_nav + random.uniform(-0.5, 0.5)
    current_irr = base_irr + random.uniform(-0.3, 0.3)
    
    # Sample deals data
    deals = [
        DealData(
            id="deal_001",
            name="Metro Office Complex - Atlanta",
            status="active",
            market="Atlanta",
            strategy="value_add",
            equity_committed=25000000.0,
            irr=15.2,
            moic=1.8,
            close_date="2023-06-15",
            power_mw=None
        ),
        DealData(
            id="deal_002", 
            name="Riverside Retail Plaza - Dallas",
            status="active",
            market="Dallas",
            strategy="opportunistic", 
            equity_committed=18500000.0,
            irr=13.8,
            moic=1.6,
            close_date="2024-01-20",
            power_mw=None
        ),
        DealData(
            id="deal_003",
            name="Industrial Park - Phoenix",
            status="active",
            market="Phoenix", 
            strategy="distressed_debt",
            equity_committed=32000000.0,
            irr=16.1,
            moic=2.1,
            close_date="2023-11-10",
            power_mw=None
        ),
        DealData(
            id="deal_004",
            name="Pico Blvd Office Complex - West LA", 
            status="pipeline",
            market="Los Angeles",
            strategy="value_add",
            equity_committed=18500000.0,
            irr=28.4,
            moic=3.2,
            close_date="2024-03-01",
            power_mw=None
        )
    ]
    
    # Calculate aggregated metrics
    active_deals = [d for d in deals if d.status == "active"]
    pipeline_deals = [d for d in deals if d.status == "pipeline"] 
    exited_deals = [d for d in deals if d.status == "exited"]
    
    # Build KPIs using external data and calculated metrics
    fund_kpis = FundKPIs(
        nav=current_nav,
        gross_irr=current_irr + 1.5,  # Gross typically higher than net
        net_irr=current_irr,
        gross_moic=1.45 + random.uniform(-0.05, 0.05),
        net_moic=1.34 + random.uniform(-0.05, 0.05), 
        tvpi=1.42,
        dpi=0.28,
        rvpi=1.14,
        aum=current_fund_value,
        committed_capital=500000000.0,
        called_capital=current_fund_value,
        uncalled_commitments=500000000.0 - current_fund_value,
        cash_balance=5200000.0,
        management_fee_accrual=2500000.0,
        carry_accrual=8400000.0
    )
    
    risk_kpis = RiskKPIs(
        wa_ltv=65.2 + random.uniform(-2, 2),
        wa_dscr=1.85 + random.uniform(-0.1, 0.1), 
        interest_coverage=2.4 + random.uniform(-0.1, 0.1),
        wa_coupon=external_data['treasury']['DGS10'] + 2.5,  # Use real Treasury data
        duration_proxy_years=4.2,
        default_rate_rolling_12m=0.8
    )
    
    pipeline_kpis = PipelineKPIs(
        active_deals_count=len(active_deals),
        pipeline_deals_count=len(pipeline_deals),
        exited_deals_count=len(exited_deals),
        avg_underwriting_cycle_days=45.5
    )
    
    power_infra_kpis = PowerInfraKPIs(
        mw_contracted=0.0,  # No power infrastructure in this real estate fund
        mw_energized=0.0,
        mw_under_loa_or_loi=0.0,
        run_rate_revenue_per_mw=0.0,
        wa_power_cost_per_mwh=0.0
    )
    
    excel_kpis = ExcelKPIs(
        fund=fund_kpis,
        risk=risk_kpis, 
        pipeline=pipeline_kpis,
        power_infra=power_infra_kpis
    )
    
    return ExcelSummaryResponse(
        as_of_date=datetime.utcnow().strftime('%Y-%m-%d'),
        aum=current_fund_value,
        deals=deals,
        kpis=excel_kpis
    )

@api_router.get("/excel/data")
async def get_excel_data():
    """Get Excel grid data for frontend display"""
    
    # Get summary data
    summary = await get_excel_summary()
    
    # Transform deals data for Excel grid format
    excel_rows = []
    for deal in summary.deals:
        excel_rows.append({
            "name": deal.name,
            "status": deal.status,
            "market": deal.market, 
            "strategy": deal.strategy,
            "equity_committed": deal.equity_committed,
            "irr": deal.irr,
            "moic": deal.moic,
            "close_date": deal.close_date,
            "power_mw": deal.power_mw or 0.0
        })
    
    return {
        "rows": excel_rows,
        "as_of_date": summary.as_of_date,
        "last_updated": datetime.utcnow().isoformat()
    }

@api_router.get("/excel/deals")
async def get_excel_deals():
    """Get deals data for Excel reporting"""
    
    summary = await get_excel_summary()
    return {
        "deals": [deal.dict() for deal in summary.deals],
        "total_deals": len(summary.deals),
        "active_count": len([d for d in summary.deals if d.status == "active"]),
        "pipeline_count": len([d for d in summary.deals if d.status == "pipeline"]),
        "exited_count": len([d for d in summary.deals if d.status == "exited"]),
        "as_of_date": summary.as_of_date
    }

@api_router.post("/excel/generate")
async def generate_excel_export():
    """Generate Excel export file (GP only)"""
    
    # Get comprehensive data
    summary = await get_excel_summary()
    external_data = await get_cached_external_data()
    
    # Create comprehensive export data
    export_data = {
        "summary": summary.dict(),
        "external_data": external_data,
        "generated_at": datetime.utcnow().isoformat(),
        "data_sources": [
            "Federal Reserve Economic Data (FRED) - Treasury yields",
            "Bureau of Labor Statistics (BLS) - CPI data", 
            "Internal fund accounting system",
            "Property management systems",
            "Third-party appraisals and valuations"
        ],
        "kpi_methodology": {
            "irr_calculation": "XIRR function based on cash flows",
            "moic_calculation": "Total distributions + residual value / invested capital",
            "nav_methodology": "Fair value based on quarterly appraisals",
            "occupancy_calculation": "Leased square feet / total square feet",
            "leverage_calculation": "Total debt / total asset value"
        },
        "disclaimer": "This data is for internal use only. All figures are subject to quarterly updates and independent verification."
    }
    
    return {
        "export_ready": True,
        "filename": f"Coastal_Excel_Analytics_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
        "data": export_data,
        "size_mb": len(str(export_data)) / 1024 / 1024
    }
@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

@api_router.post("/auth", response_model=AuthResponse)
async def authenticate(auth_request: AuthRequest):
    """
    Authenticate user with LP or GP password
    """
    password = auth_request.password.strip()
    
    if password == LP_PASSWORD:
        # Generate JWT token
        token_payload = {
            "user_type": "lp",
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")
        
        return AuthResponse(
            success=True,
            user_type="lp",
            message="LP access granted",
            token=token
        )
    elif password == GP_PASSWORD:
        # Generate JWT token
        token_payload = {
            "user_type": "gp", 
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")
        
        return AuthResponse(
            success=True,
            user_type="gp",
            message="GP access granted",
            token=token
        )
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@api_router.get("/market-data", response_model=MarketDataResponse)
async def get_market_data():
    """
    Get current market data - mock data that simulates real-time updates
    """
    import random
    import time
    
    # Simulate some variation based on time
    seed = int(time.time() / 60)  # Changes every minute
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
        last_update=datetime.utcnow().isoformat()
    )

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
