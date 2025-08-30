from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, HTMLResponse
from pymongo import MongoClient
from bson import ObjectId
import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import uuid

# Import our models and services - using absolute imports
from models import LiveDocument, UpdateRequest, RealTimeDataResponse
from enhanced_document_service import EnhancedDocumentService

# Import Agent SDK components
from agent_models import ExecutionRequest, ExecutionResponse
from agent_registry_setup import build_orchestrator
from data_feeds import data_feed_service

# Additional imports for regulatory and FDIC endpoints
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = MongoClient(MONGO_URL)
db = client.coastal_oak_db

# Create MongoDB indexes for proper performance and uniqueness
try:
    db.credentials.create_index("token", unique=True)
    db.credentials.create_index("expiresAt")
    db.access_log.create_index([("ts", 1)])
    logger.info("MongoDB indexes created successfully")
except Exception as e:
    logger.warning(f"Index creation warning: {e}")

def _utc(dt):  # tolerant datetime parser
    """Convert datetime string to UTC datetime object"""
    return datetime.fromisoformat(dt.replace("Z","+00:00")).astimezone(timezone.utc)

def log_audit(action: str, details: Dict[str, Any]):
    try:
        db.audit_logs.insert_one({
            "id": str(uuid.uuid4()),
            "action": action,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Audit log error: {e}")

# Initialize document service
document_service = EnhancedDocumentService()

# Initialize Agent SDK orchestrator
orchestrator = build_orchestrator(client)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Coastal Oak Capital Live Document System...")
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    lifespan=lifespan,
    title="Coastal Oak Capital Live Document API",
    description="Real-time institutional document system with live market data integration",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import APIRouter
router = APIRouter(prefix="/api")

@router.get("/")
async def root():
    return {
        "message": "Coastal Oak Capital Live Document System", 
        "version": "1.0.0",
        "description": "Institution-grade master deck with real-time market data integration"
    }

@router.get("/status")
async def status():
    try:
        # Test database connection
        db.command('ping')
        return {
            "status": "healthy", 
            "database": "connected",
            "system": "Coastal Oak Capital Live Document System",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "database": "disconnected", 
            "system": "Coastal Oak Capital Live Document System",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/document/create", response_model=Dict[str, Any])
async def create_document():
    """Create the comprehensive Coastal Oak Capital master deck with real-time data and all integrated content"""
    try:
        logger.info("Creating comprehensive Coastal Oak Capital master deck with all integrated content...")
        
        # Create the enhanced document with all integrated content
        document = await document_service.create_comprehensive_master_deck()
        
        # Store in database
        doc_dict = document.model_dump()
        doc_dict['_id'] = document.id
        
        # Store in MongoDB
        collection = db.documents
        collection.replace_one(
            {"_id": document.id}, 
            doc_dict, 
            upsert=True
        )
        
        logger.info(f"Comprehensive master deck created successfully with ID: {document.id}")
        
        return {
            "success": True,
            "document_id": document.id,
            "title": document.title,
            "sections_count": len(document.sections),
            "data_sources_count": len(document.data_sources),
            "last_updated": document.last_updated.isoformat(),
            "version": document.version,
            "message": "Comprehensive Coastal Oak Capital master deck created with all integrated content and live market data"
        }
        
    except Exception as e:
        logger.error(f"Error creating comprehensive document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create comprehensive document: {str(e)}")

@router.get("/document/{document_id}")
async def get_document(document_id: str):
    """Retrieve a document with its current real-time data"""
    try:
        collection = db.documents
        doc_data = collection.find_one({"_id": document_id})
        
        if not doc_data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Convert MongoDB document back to Pydantic model
        document = LiveDocument(**doc_data)
        
        return {
            "success": True,
            "document": document.model_dump(),
            "export_formats": ["markdown", "json"],
            "real_time_data_age": "Live data as of request time"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve document: {str(e)}")

@router.post("/document/{document_id}/update")
async def update_document(document_id: str, request: UpdateRequest):
    """Update a document with the latest real-time data"""
    try:
        collection = db.documents
        doc_data = collection.find_one({"_id": document_id})
        
        if not doc_data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Convert to Pydantic model
        document = LiveDocument(**doc_data)
        
        # Update with latest data
        updated_document = await document_service.update_document(document, request.force_refresh)
        
        # Save back to database
        doc_dict = updated_document.model_dump()
        doc_dict['_id'] = updated_document.id
        collection.replace_one({"_id": document_id}, doc_dict)
        
        logger.info(f"Document {document_id} updated successfully")
        
        return RealTimeDataResponse(
            success=True,
            data=updated_document.model_dump(),
            sources_updated=list(updated_document.data_sources.keys()),
            timestamp=datetime.now(),
            message="Document updated with latest real-time market data"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update document: {str(e)}")

@router.get("/document/{document_id}/export/markdown")
async def export_markdown(document_id: str):
    """Export document as markdown format"""
    try:
        collection = db.documents
        doc_data = collection.find_one({"_id": document_id})
        
        if not doc_data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document = LiveDocument(**doc_data)
        markdown_content = document_service.export_to_markdown(document)
        
        return {
            "success": True,
            "format": "markdown",
            "content": markdown_content,
            "title": document.title,
            "last_updated": document.last_updated.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export document: {str(e)}")

@router.get("/data/live")
async def get_live_data():
    """Get current real-time market data"""
    try:
        real_time_data = await document_service.data_manager.fetch_all_data()
        
        return {
            "success": True,
            "data": real_time_data,
            "timestamp": datetime.now().isoformat(),
            "sources_count": len(real_time_data),
            "message": "Real-time market data retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error fetching live data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch live data: {str(e)}")

@router.get("/documents/list")
async def list_documents():
    """List all available documents"""
    try:
        collection = db.documents
        documents = list(collection.find({}, {
            "_id": 1, 
            "title": 1, 
            "description": 1, 
            "last_updated": 1, 
            "version": 1
        }))
        
        return {
            "success": True,
            "documents": documents,
            "count": len(documents),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@router.post("/system/refresh-all")
async def refresh_all_documents():
    """Refresh all documents with latest real-time data - Daily auto-refresh endpoint"""
    try:
        logger.info("Starting daily refresh of all documents...")
        
        collection = db.documents
        documents = list(collection.find({}))
        
        refreshed_count = 0
        for doc_data in documents:
            try:
                # Convert to Pydantic model
                document = LiveDocument(**doc_data)
                
                # Update with latest data
                updated_document = await document_service.update_document(document, force_refresh=True)
                
                # Save back to database
                doc_dict = updated_document.model_dump()
                doc_dict['_id'] = updated_document.id
                collection.replace_one({"_id": updated_document.id}, doc_dict)
                
                refreshed_count += 1
                logger.info(f"Refreshed document: {updated_document.title}")
                
            except Exception as doc_error:
                logger.error(f"Error refreshing document {doc_data.get('_id', 'unknown')}: {doc_error}")
                continue
        
        return {
            "success": True,
            "refreshed_count": refreshed_count,
            "total_documents": len(documents),
            "timestamp": datetime.now().isoformat(),
            "message": f"Daily refresh completed - {refreshed_count} documents updated with latest market data"
        }
        
    except Exception as e:
        logger.error(f"Error during daily refresh: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to refresh documents: {str(e)}")

# ======= AGENT SDK ENDPOINTS =======

@router.post("/agents/execute")
async def execute_agents(request: ExecutionRequest):
    """Execute specialized agents for investment analysis"""
    try:
        logger.info(f"Executing agents for: {request.objective}")
        
        # Execute the orchestrated agent analysis
        result = await orchestrator.execute(request)
        
        return {
            "success": True,
            "result": result.model_dump(),
            "agents_executed": len(result.packets),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error executing agents: {e}")
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

@router.get("/agents/registry")
async def get_agent_registry():
    """Get available agents and their capabilities"""
    try:
        from agent_registry_setup import AGENT_CAPABILITIES, get_recommended_agents_for_task
        
        registry_info = orchestrator.registry.list()
        
        return {
            "success": True,
            "agents": registry_info,
            "capabilities": AGENT_CAPABILITIES,
            "total_agents": len(registry_info)
        }
        
    except Exception as e:
        logger.error(f"Error getting agent registry: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent registry: {str(e)}")

@router.post("/agents/recommend")
async def recommend_agents(request: dict):
    """Recommend agents based on task description"""
    try:
        from agent_registry_setup import get_recommended_agents_for_task
        
        task_description = request.get("task", "")
        recommended_tags = get_recommended_agents_for_task(task_description)
        
        return {
            "success": True,
            "task": task_description,
            "recommended_agents": recommended_tags,
            "count": len(recommended_tags)
        }
        
    except Exception as e:
        logger.error(f"Error recommending agents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to recommend agents: {str(e)}")

# ======= DATA FEEDS ENDPOINTS =======

@router.get("/rates")
async def get_current_rates():
    """Get current Treasury and Fed rates"""
    try:
        # Fetch current rate data
        ten_year = await data_feed_service.treasury_yield("10Y")
        five_year = await data_feed_service.treasury_yield("5Y")
        thirty_year = await data_feed_service.treasury_yield("30Y")
        fed_funds = await data_feed_service.fred("DFF")
        
        rates_data = {
            "treasury_rates": {
                "5Y": five_year.model_dump(),
                "10Y": ten_year.model_dump(),
                "30Y": thirty_year.model_dump()
            },
            "fed_funds_rate": {
                "current": fed_funds.rows[0]["value"] if fed_funds.rows else 0.0,
                "last_updated": fed_funds.rows[0]["date"] if fed_funds.rows else None
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "data": rates_data
        }
        
    except Exception as e:
        logger.error(f"Error fetching rates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch rates: {str(e)}")

@router.get("/rates/history")
async def get_rates_history(days: int = Query(180, ge=1, le=1825)):
    """Get historical Treasury and Fed rates for the past N days"""
    try:
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        series_map = {"5Y": "GS5", "10Y": "GS10", "30Y": "GS30", "DFF": "DFF"}
        
        gs5 = await data_feed_service.fred(series_map["5Y"], {"start_date": start_date, "limit": 5000})
        gs10 = await data_feed_service.fred(series_map["10Y"], {"start_date": start_date, "limit": 5000})
        gs30 = await data_feed_service.fred(series_map["30Y"], {"start_date": start_date, "limit": 5000})
        dff = await data_feed_service.fred(series_map["DFF"], {"start_date": start_date, "limit": 5000})
        
        return {
            "success": True,
            "data": {
                "5Y": gs5.rows[::-1],
                "10Y": gs10.rows[::-1],
                "30Y": gs30.rows[::-1],
                "DFF": dff.rows[::-1],
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching rate history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch rate history: {str(e)}")

@router.get("/maturities")
async def get_cre_maturities():
    """Get CRE maturity ladder data"""
    try:
        maturities_data = await data_feed_service.cre_maturities()
        
        return {
            "success": True,
            "data": maturities_data.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching CRE maturities: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch CRE maturities: {str(e)}")

@router.get("/banks")
async def get_fdic_data():
    """Get FDIC call reports data"""
    try:
        fdic_data = await data_feed_service.fdic_call_reports()
        
        return {
            "success": True,
            "data": fdic_data.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching FDIC data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch FDIC data: {str(e)}")

@router.get("/zoning/la")
async def get_la_zoning():
    """Get Los Angeles zoning data"""
    try:
        zoning_data = await data_feed_service.zoning_la()
        
        return {
            "success": True,
            "data": zoning_data.model_dump(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching LA zoning data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch LA zoning data: {str(e)}")

# ======= SECURITY AND ACCESS ENDPOINTS =======

@router.post("/deck/request")
async def request_deck_access(payload: dict):
    """Request secure access to pitch deck with single-use token"""
    try:
        email = (payload or {}).get("email")
        if not email:
            raise HTTPException(400, "email required")
        
        token = f"tok_{uuid.uuid4().hex}"
        now = datetime.now(timezone.utc)
        ttl_min = int(os.getenv("TOKEN_TTL_MINUTES", "15"))
        
        doc = {
            "token": token,
            "email": email.lower(),
            "issuedAt": now.isoformat(),
            "expiresAt": (now + timedelta(minutes=ttl_min)).isoformat(),
            "used": False,
            "usedAt": None,
            "ip": payload.get("ip"),
            "ua": payload.get("ua"),
        }
        
        db.credentials.insert_one(doc)
        db.access_log.insert_one({
            "user": email, 
            "action": "deck_request", 
            "ts": now.isoformat(), 
            "ip": doc["ip"], 
            "ua": doc["ua"]
        })
        
        return {"token": token, "expiresAt": doc["expiresAt"]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error issuing deck access: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to issue access token: {str(e)}")

@router.get("/deck/download")
async def deck_download(request: Request, token: str, format: str = "pdf"):
    """Download watermarked executive summary with single-use token enforcement"""
    try:
        cred = db.credentials.find_one({"token": token})
        now = datetime.now(timezone.utc)
        
        if not cred:
            raise HTTPException(404, "invalid token")
            
        if cred.get("used"):
            # Already used once → hard stop
            db.access_log.insert_one({
                "user": cred["email"], 
                "action": "deck_download_reuse", 
                "ts": now.isoformat(), 
                "ip": request.client.host
            })
            raise HTTPException(403, "token already used")
        
        # expiry check (if present)
        exp = cred.get("expiresAt")
        if exp and now > _utc(exp):
            db.access_log.insert_one({
                "user": cred["email"], 
                "action": "deck_download_expired", 
                "ts": now.isoformat(), 
                "ip": request.client.host
            })
            raise HTTPException(403, "token expired")

        # Mark used *atomically* before returning the file
        res = db.credentials.update_one(
            {"token": token, "used": False},
            {"$set": {"used": True, "usedAt": now.isoformat()}}
        )
        if res.modified_count != 1:
            # Race condition safety: someone else flipped it
            raise HTTPException(403, "token already used")

        # Serve PDF or fallback HTML; always watermark (use ASCII-safe separator)
        wm = f"{cred['email']} | {now.isoformat()} | Coastal Oak"
        headers = {"Cache-Control": "no-store", "X-Watermark": wm}
        
        try:
            # Try to render PDF if WeasyPrint is available
            from weasyprint import HTML
            html_content = f"""
            <html><head><meta charset='utf-8'><style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .wm {{ position: fixed; top: 10px; right: 10px; color: #888; font-size: 10px; }}
            h1 {{ color: #064e3b; }}
            .meta {{ color:#475569; font-size:12px; margin-bottom:20px; }}
            </style></head><body>
            <div class='wm'>{wm}</div>
            <h1>Executive Summary — Coastal Oak Capital</h1>
            <div class='meta'>Generated {now.strftime('%Y-%m-%d %H:%M:%S')}</div>
            <p>Distressed CRE debt with AI/Data Infrastructure and EV Super-charging conversions. Institutional discipline, clear underwriting, and real-time market intelligence.</p>
            </body></html>
            """
            pdf_bytes = HTML(string=html_content).write_pdf()
            db.access_log.insert_one({
                "user": cred["email"], 
                "action": "deck_download_pdf", 
                "ts": now.isoformat(), 
                "ip": request.client.host
            })
            return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
        except Exception:
            # Fallback to HTML
            html = f"""
            <html><head><meta charset='utf-8'><style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .wm {{ position: fixed; top: 10px; right: 10px; color: #888; font-size: 10px; }}
            h1 {{ color: #064e3b; }}
            .meta {{ color:#475569; font-size:12px; margin-bottom:20px; }}
            </style></head><body>
            <div class='wm'>{wm}</div>
            <h1>Executive Summary — Coastal Oak Capital</h1>
            <div class='meta'>Generated {now.strftime('%Y-%m-%d %H:%M:%S')}</div>
            <p>Opportunistic Commercial Real Estate Distressed Debt Fund with conversion strategies into AI/Data Centers and EV infrastructure.</p>
            </body></html>
            """
            headers["X-PDF-Mode"] = "fallback-html"
            db.access_log.insert_one({
                "user": cred["email"], 
                "action": "deck_download_html", 
                "ts": now.isoformat(), 
                "ip": request.client.host
            })
            return Response(content=html, media_type="text/html; charset=utf-8", headers=headers)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during deck download: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download deck: {str(e)}")

@router.get("/execsum.pdf")
async def executive_summary_pdf():
    """Direct executive summary PDF (falls back to HTML if PDF engine unavailable)"""
    try:
        watermark = f"Direct View | {datetime.now().isoformat()}"
        html = f"""
        <html><head><meta charset='utf-8'><style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .wm {{ position: fixed; top: 10px; right: 10px; color: #888; font-size: 10px; }}
        h1 {{ color: #064e3b; }}
        .meta {{ color:#475569; font-size:12px; margin-bottom:20px; }}
        </style></head><body>
        <div class='wm'>{watermark}</div>
        <h1>Executive Summary — Coastal Oak Capital</h1>
        <div class='meta'>Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        <p>Opportunistic Commercial Real Estate Distressed Debt Fund with conversion strategies into AI/Data Centers and EV infrastructure.</p>
        </body></html>
        """
        try:
            from weasyprint import HTML
            pdf_bytes = HTML(string=html).write_pdf()
            return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "inline; filename=executive_summary.pdf"})
        except Exception as e:
            return HTMLResponse(content=html, headers={"X-PDF-Mode": "fallback-html", "Cache-Control":"no-store, no-cache, must-revalidate, max-age=0", "Pragma":"no-cache", "Expires":"0"})
    except Exception as e:
        logger.error(f"Error generating /execsum.pdf: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate executive summary: {str(e)}")

@router.get("/audit")
async def get_audit(limit: int = 20):
    """Return latest audit log entries"""
    try:
        docs = list(db.audit_logs.find({}, {"_id": 0}).sort([("timestamp", -1)]).limit(limit))
        return {"success": True, "data": docs, "count": len(docs)}
    except Exception as e:
        logger.error(f"Error fetching audit logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit logs: {str(e)}")

@router.get("/healthz/deps")
async def healthz_deps():
    """Dependency health check"""
    status = {"mongo": "unknown", "fred_api_key": bool(os.getenv("FRED_API_KEY")), "weasyprint": False, "agents_registered": 0}
    try:
        db.command('ping')
        status["mongo"] = "connected"
    except Exception as e:
        status["mongo"] = f"error: {e}"
    try:
        import weasyprint  # noqa: F401
        status["weasyprint"] = True
    except Exception:
        status["weasyprint"] = False
    try:
        status["agents_registered"] = len(orchestrator.registry.list())
    except Exception:
        status["agents_registered"] = 0
    return {"success": True, "status": status, "timestamp": datetime.now().isoformat()}

# ======= DATA SOURCES AND FOOTNOTES =======

@router.get("/footnotes")
async def get_footnotes():
    """Get all footnotes and source citations"""
    try:
        # Sample structure, includes registry keys expected in v1.3.0
        now = datetime.now().isoformat()
        footnotes_data = {
            "footnotes": [
                {"id": "T1", "label": "10Y Treasury Rate", "source": "FRED GS10 Series", "retrieved_at": now, "refresh": "Daily", "transform": "Latest close"},
                {"id": "F1", "label": "Fed Funds Rate", "source": "FRED DFF Series", "retrieved_at": now, "refresh": "Daily", "transform": "Effective rate"},
                {"id": "M1", "label": "CRE Maturity Ladder", "source": "Trepp/MSCI compatible mock", "retrieved_at": now, "refresh": "Weekly", "transform": "Aggregated by year"},
                {"id": "B1", "label": "FDIC Call Reports", "source": "FDIC API (simplified)", "retrieved_at": now, "refresh": "Quarterly", "transform": "Selected fields"},
                {"id": "H1", "label": "Rates History", "source": "FRED GS5/GS10/GS30/DFF", "retrieved_at": now, "refresh": "Daily", "transform": "Observation series"},
                {"id": "R1", "label": "Regulatory Tracker", "source": "Federal Register + CA/LA", "retrieved_at": now, "refresh": "Weekly", "transform": "Normalized statuses"},
                {"id": "S1", "label": "Sentiment Composite", "source": "VNQ/IYR P/C, VIX, IG/HY Spreads (FRED)", "retrieved_at": now, "refresh": "Daily", "transform": "Composite signal"},
                {"id": "C1", "label": "CA Transactions Feed", "source": "County trustee filings + press", "retrieved_at": now, "refresh": "Weekly", "transform": "Tagged type/counterparty"},
                # New regulatory and FDIC footnotes
                {"id": "NEVI", "label": "NEVI Formula Program", "source": "FHWA NEVI Program", "retrieved_at": now, "refresh": "Periodic", "transform": "Federal funding constraints"},
                {"id": "ITC30C", "label": "Alternative Fuel Refueling Credit", "source": "IRS §30C Guidelines", "retrieved_at": now, "refresh": "Static", "transform": "Tax credit calculations"},
                {"id": "AB1236", "label": "AB 1236 Streamlined EVCS Permitting", "source": "CA Legislature", "retrieved_at": now, "refresh": "Static", "transform": "Permitting requirements"},
                {"id": "AB970", "label": "AB 970 EVCS Permit Deadlines", "source": "CA Legislature", "retrieved_at": now, "refresh": "Static", "transform": "Timeline requirements"},
                {"id": "CEQA32", "label": "CEQA Class 32 Infill Exemption", "source": "CA Code of Regulations", "retrieved_at": now, "refresh": "Static", "transform": "Exemption criteria"},
                {"id": "LAZ1", "label": "LA New Zoning Code", "source": "LA City Planning", "retrieved_at": now, "refresh": "Weekly", "transform": "CPA rollout status"},
                {"id": "LACode", "label": "LA Municipal Planning Code", "source": "AmLegal LA PZ", "retrieved_at": now, "refresh": "Weekly", "transform": "Current ordinances"},
                {"id": "LAGP", "label": "LA General Plan Updates", "source": "LA City Planning", "retrieved_at": now, "refresh": "Weekly", "transform": "Policy changes"},
                {"id": "LADBS", "label": "LADBS EV Charging Permits", "source": "LA Department of Building and Safety", "retrieved_at": now, "refresh": "Weekly", "transform": "Permit requirements"}
            ],
            "total_count": 16,
            "last_updated": now
        }
        
        return {
            "success": True,
            "data": footnotes_data
        }
        
    except Exception as e:
        logger.error(f"Error fetching footnotes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch footnotes: {str(e)}")

# ======= REGULATORY AND FDIC ADAPTERS =======

@router.get("/regulatory/federal")
async def get_federal_regulatory():
    """Get federal regulatory items affecting CRE/EV development"""
    try:
        now = datetime.now(timezone.utc)
        # Mock data matching the specified schema
        items = [
            {
                "code": "ITC30C",
                "title": "IRC §30C Alternative Fuel Refueling Property Credit",
                "status": "active",
                "summary": "Credit up to 30% for qualifying EV charging property; elective pay for eligible entities; location restrictions may apply.",
                "effectOnCOC": "Reduces basis for EVCS capex in consumer and fleet sites; increases IRR when stacked with utility rebates.",
                "citations": [{"url": "https://www.irs.gov/credits-deductions/businesses/alternative-fuel-vehicle-refueling-property-credit", "label": "IRS guidance"}],
                "footnoteId": "ITC30C",
                "retrievalAt": now.isoformat(),
                "refresh": "static"
            },
            {
                "code": "NEVI",
                "title": "NEVI Formula Program",
                "status": "active",
                "summary": "Federal funding for highway corridor charging with state plan constraints and uptime requirements.",
                "effectOnCOC": "Supports corridor sites; capex offset contingent on plan compliance and reporting.",
                "citations": [{"url": "https://www.fhwa.dot.gov/bipartisan-infrastructure-law/nevi_formula_program.cfm", "label": "FHWA NEVI"}],
                "footnoteId": "NEVI",
                "retrievalAt": now.isoformat(),
                "refresh": "periodic"
            }
        ]
        
        return {
            "asOf": now.isoformat(),
            "items": items
        }
        
    except Exception as e:
        logger.error(f"Error fetching federal regulatory data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch federal regulatory data: {str(e)}")

@router.get("/regulatory/state")
async def get_state_regulatory():
    """Get California state regulatory items affecting CRE/EV development"""
    try:
        now = datetime.now(timezone.utc)
        # Mock data matching the specified schema
        items = [
            {
                "code": "AB1236",
                "title": "AB 1236 – Streamlined EVCS Permitting",
                "status": "active",
                "summary": "Requires local ministerial checklists and streamlined approvals for EVCS.",
                "effectOnCOC": "Shorter permitting timelines; supports CEQA ministerial route.",
                "citations": [{"url": "https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202120220AB1236", "label": "Statute / CA OPR"}],
                "footnoteId": "AB1236",
                "retrievalAt": now.isoformat(),
                "refresh": "static"
            },
            {
                "code": "AB970",
                "title": "AB 970 – Permit Deadlines for EVCS",
                "status": "active",
                "summary": "Sets shot clocks and deemed-complete standards for EVCS permits.",
                "effectOnCOC": "Improves schedule certainty; SLA-driven.",
                "citations": [{"url": "https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202120220AB970", "label": "Statute"}],
                "footnoteId": "AB970",
                "retrievalAt": now.isoformat(),
                "refresh": "static"
            },
            {
                "code": "CEQA32",
                "title": "CEQA Class 32 – Infill Development Exemption",
                "status": "available",
                "summary": "Categorical exemption for infill projects meeting criteria; exceptions apply.",
                "effectOnCOC": "Provides a CEQA off-ramp for qualifying adaptive reuse; verify exceptions.",
                "citations": [{"url": "https://casetext.com/regulation/california-code-of-regulations-title-14-natural-resources-division-6-resources-agency-chapter-3-guidelines-for-implementation-of-the-california-environmental-quality-act-article-19-categorical-exemptions-section-15332-in-fill-development-projects", "label": "CA Code of Regulations"}],
                "footnoteId": "CEQA32",
                "retrievalAt": now.isoformat(),
                "refresh": "static"
            }
        ]
        
        return {
            "asOf": now.isoformat(),
            "items": items
        }
        
    except Exception as e:
        logger.error(f"Error fetching state regulatory data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch state regulatory data: {str(e)}")

@router.get("/regulatory/municipal")
async def get_municipal_regulatory():
    """Get Los Angeles municipal regulatory items affecting CRE/EV development"""
    try:
        now = datetime.now(timezone.utc)
        # Mock data matching the specified schema
        items = [
            {
                "code": "LAZ1",
                "title": "LA City New Zoning Code (Chapter 1A)",
                "status": "rolling",
                "summary": "New zoning framework rolling out by Community Plan Area.",
                "effectOnCOC": "Entitlement mechanics and use standards vary by CPA; check applicability map.",
                "citations": [{"url": "https://planning.lacity.gov/zoning/new-code", "label": "LA City Planning"}],
                "footnoteId": "LAZ1",
                "retrievalAt": now.isoformat(),
                "refresh": "weekly"
            },
            {
                "code": "LACode",
                "title": "LA Municipal Code – Planning & Zoning",
                "status": "current",
                "summary": "Codified planning and zoning ordinances (publisher posting lag possible).",
                "effectOnCOC": "Primary municipal authority for entitlements and conditions.",
                "citations": [{"url": "https://codelibrary.amlegal.com/codes/los_angeles/latest/lapz/0-0-0-57924", "label": "AmLegal LA PZ"}],
                "footnoteId": "LACode",
                "retrievalAt": now.isoformat(),
                "refresh": "weekly"
            },
            {
                "code": "LAGP",
                "title": "LA General Plan — Updates",
                "status": "rolling",
                "summary": "General Plan elements and community plan updates with policy changes.",
                "effectOnCOC": "Signals future entitlement friction or relief.",
                "citations": [{"url": "https://planning.lacity.gov/plans-policies/general-plan-overview#updates", "label": "General Plan"}],
                "footnoteId": "LAGP",
                "retrievalAt": now.isoformat(),
                "refresh": "weekly"
            },
            {
                "code": "LADBS",
                "title": "LADBS — EV Charging Permits",
                "status": "current",
                "summary": "Permit checklists, accessibility, layout, and inspection rules for EVCS.",
                "effectOnCOC": "Defines submittals and field constraints across building types.",
                "citations": [{"url": "https://dbs.lacity.gov/?sfvrsn=7", "label": "LADBS"}],
                "footnoteId": "LADBS",
                "retrievalAt": now.isoformat(),
                "refresh": "weekly"
            }
        ]
        
        return {
            "asOf": now.isoformat(),
            "items": items
        }
        
    except Exception as e:
        logger.error(f"Error fetching municipal regulatory data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch municipal regulatory data: {str(e)}")

@router.get("/fdic/exposure")
async def get_fdic_exposure():
    """Get FDIC bank CRE exposure digest"""
    try:
        now = datetime.now(timezone.utc)
        # Mock data matching the specified schema
        rows = [
            {
                "bankId": "cert_12345",
                "bankName": "City National West",
                "category": "Regional",
                "exposurePct": 29.0,
                "stack": {"mf": 34, "off": 41, "ind": 15, "other": 10},
                "footnoteId": "B1",
                "retrievalAt": now.isoformat(),
                "source": "FDIC/FFIEC Call Reports"
            },
            {
                "bankId": "cert_67890",
                "bankName": "First Republic Bank",
                "category": "Regional",
                "exposurePct": 18.5,
                "stack": {"mf": 42, "off": 35, "ind": 13, "other": 10},
                "footnoteId": "B1",
                "retrievalAt": now.isoformat(),
                "source": "FDIC/FFIEC Call Reports"
            },
            {
                "bankId": "cert_54321",
                "bankName": "Wells Fargo Bank",
                "category": "Institutional",
                "exposurePct": 12.3,
                "stack": {"mf": 38, "off": 32, "ind": 18, "other": 12},
                "footnoteId": "B1",
                "retrievalAt": now.isoformat(),
                "source": "FDIC/FFIEC Call Reports"
            }
        ]
        
        return {
            "asOf": now.date().isoformat(),
            "rows": rows
        }
        
    except Exception as e:
        logger.error(f"Error fetching FDIC exposure data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch FDIC exposure data: {str(e)}")

@router.get("/fdic/banks/{bank_id}")
async def get_fdic_bank_detail(bank_id: str):
    """Get detailed FDIC data for a specific bank"""
    try:
        now = datetime.now(timezone.utc)
        
        # Mock detailed data for specific bank
        bank_details = {
            "bankId": bank_id,
            "bankName": f"Bank Details for {bank_id}",
            "category": "Regional",
            "exposurePct": 25.7,
            "stack": {"mf": 35, "off": 40, "ind": 15, "other": 10},
            "footnoteId": "B1",
            "retrievalAt": now.isoformat(),
            "source": "FDIC/FFIEC Call Reports",
            "details": {
                "assets_total": 45600000000,  # $45.6B
                "loans_cre_total": 11726400000,  # $11.7B
                "risk_metrics": {
                    "tier1_capital_ratio": 12.4,
                    "leverage_ratio": 8.9,
                    "cre_concentration_ratio": 25.7
                },
                "quarterly_trend": [
                    {"quarter": "Q4-2024", "exposure_pct": 26.1},
                    {"quarter": "Q3-2024", "exposure_pct": 25.9},
                    {"quarter": "Q2-2024", "exposure_pct": 25.7}
                ]
            }
        }
        
        return {
            "asOf": now.date().isoformat(),
            "bank": bank_details
        }
        
    except Exception as e:
        logger.error(f"Error fetching bank detail for {bank_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch bank detail: {str(e)}")

app.include_router(router)