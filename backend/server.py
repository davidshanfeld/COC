from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from bson import ObjectId
import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

# Import our models and services - using absolute imports
from models import LiveDocument, UpdateRequest, RealTimeDataResponse
from enhanced_document_service import EnhancedDocumentService

# Import Agent SDK components
from agent_models import ExecutionRequest, ExecutionResponse
from agent_registry_setup import build_orchestrator
from data_feeds import data_feed_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = MongoClient(MONGO_URL)
db = client.coastal_oak_db

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
async def request_deck_access(request: dict):
    """Request secure access to pitch deck with single-use token"""
    try:
        user_id = request.get("user_id", "guest")
        audience = request.get("audience", "LP")
        
        # Create agent request for security token
        from agent_models import AgentRequest
        
        security_request = AgentRequest(
            objective="Issue single-use access token",
            audience=audience,
            inputs={"user": user_id, "action": "issue_token"},
            security_tier="restricted"
        )
        
        # Find security agent and execute
        security_agents = orchestrator.registry.pick(["security"])
        if not security_agents:
            raise HTTPException(status_code=500, detail="Security agent not available")
        
        context = orchestrator.ctx
        result = await security_agents[0].run(security_request, context)
        
        return {
            "success": True,
            "access_token": result.findings.get("access_control", {}).get("token"),
            "expires_at": result.findings.get("access_control", {}).get("expires_at"),
            "audience": audience,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error issuing deck access: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to issue access token: {str(e)}")

@router.get("/footnotes")
async def get_footnotes():
    """Get all footnotes and source citations"""
    try:
        # This would typically query the footnotes collection
        # For now, return a sample structure
        footnotes_data = {
            "footnotes": [
                {
                    "id": "T1", 
                    "label": "10Y Treasury Rate",
                    "source": "FRED GS10 Series",
                    "retrieved_at": datetime.now().isoformat(),
                    "refresh": "Daily",
                    "transform": "Latest close"
                },
                {
                    "id": "F1",
                    "label": "Fed Funds Rate", 
                    "source": "FRED DFF Series",
                    "retrieved_at": datetime.now().isoformat(),
                    "refresh": "Daily",
                    "transform": "Effective rate"
                }
            ],
            "total_count": 2,
            "last_updated": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "data": footnotes_data
        }
        
    except Exception as e:
        logger.error(f"Error fetching footnotes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch footnotes: {str(e)}")

app.include_router(router)
