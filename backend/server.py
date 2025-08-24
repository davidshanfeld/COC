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
