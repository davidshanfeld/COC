import os
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from agent_models import (
    AgentRequest, AgentResponse, ExecutionRequest, ExecutionResponse, 
    Footnote, AgentAsset, AccessLog, SingleUseToken
)
from data_feeds import data_feed_service
import asyncio

class AgentContext:
    def __init__(self, logger, security_api, db_client):
        self.logger = logger
        self.security = security_api
        self.data = data_feed_service
        self.db_client = db_client
    
    def now(self) -> str:
        return datetime.utcnow().isoformat() + "Z"

class SecurityAPI:
    def __init__(self, db_client, logger):
        self.db_client = db_client
        self.logger = logger
    
    async def issue_single_use_password(self, user_id: str) -> Dict[str, str]:
        """Issue a single-use token for secure access"""
        token = f"sut_{uuid.uuid4().hex[:16]}"
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        token_record = SingleUseToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at
        )
        
        # Store in database
        try:
            collection = self.db_client.get_database("coastal_oak").get_collection("tokens")
            await collection.insert_one(token_record.dict())
        except Exception as e:
            self.logger.error(f"Token storage error: {e}")
        
        return {
            "token": token,
            "expires_at": expires_at.isoformat() + "Z"
        }
    
    async def watermark(self, file_path: str, watermark_text: str) -> str:
        """Add watermark to file - stub implementation"""
        # In production, this would add actual watermarks
        return file_path
    
    def audit(self, event: str, meta: Optional[Dict[str, Any]] = None):
        """Log audit events"""
        log_entry = AccessLog(
            user_id=meta.get("user", "system") if meta else "system",
            event=event,
            meta=meta or {}
        )
        
        try:
            # Store async in background
            asyncio.create_task(self._store_audit_log(log_entry))
        except Exception as e:
            self.logger.error(f"Audit logging error: {e}")
    
    async def _store_audit_log(self, log_entry: AccessLog):
        try:
            collection = self.db_client.get_database("coastal_oak").get_collection("audit_logs")
            await collection.insert_one(log_entry.dict())
        except Exception as e:
            self.logger.error(f"Audit storage error: {e}")

class Logger:
    def info(self, msg: str, meta: Optional[Dict[str, Any]] = None):
        print(f"INFO: {msg} {json.dumps(meta) if meta else ''}")
    
    def warn(self, msg: str, meta: Optional[Dict[str, Any]] = None):
        print(f"WARN: {msg} {json.dumps(meta) if meta else ''}")
    
    def error(self, msg: str, meta: Optional[Dict[str, Any]] = None):
        print(f"ERROR: {msg} {json.dumps(meta) if meta else ''}")

class Agent:
    def __init__(self, name: str, handles: List[str]):
        self.name = name
        self.handles = handles
    
    async def run(self, req: AgentRequest, ctx: AgentContext) -> AgentResponse:
        raise NotImplementedError("Subclasses must implement run method")

class AgentRegistry:
    def __init__(self):
        self.agents: List[Agent] = []
    
    def register(self, agent: Agent):
        self.agents.append(agent)
    
    def list(self) -> List[Dict[str, Any]]:
        return [{"name": agent.name, "handles": agent.handles} for agent in self.agents]
    
    def pick(self, tags: List[str]) -> List[Agent]:
        tag_set = set(tag.lower() for tag in tags)
        return [agent for agent in self.agents 
                if any(handle.lower() in tag_set for handle in agent.handles)]

class Orchestrator:
    def __init__(self, registry: AgentRegistry, ctx: AgentContext):
        self.registry = registry
        self.ctx = ctx
    
    async def execute(self, goal: ExecutionRequest) -> ExecutionResponse:
        agents = self.registry.pick(goal.tags)
        if not agents:
            raise ValueError(f"No agents found for tags: {', '.join(goal.tags)}")
        
        packets: List[AgentResponse] = []
        
        # Convert ExecutionRequest to AgentRequest format
        agent_req = AgentRequest(
            objective=goal.objective,
            audience=goal.audience,
            inputs=goal.inputs,
            required_charts=goal.required_charts,
            required_models=goal.required_models,
            deadlines=goal.deadlines,
            style_notes=goal.style_notes,
            footnote_requirements=goal.footnote_requirements,
            security_tier=goal.security_tier
        )
        
        for agent in agents:
            self.ctx.logger.info("dispatch", {"agent": agent.name, "objective": goal.objective})
            try:
                response = await agent.run(agent_req, self.ctx)
                packets.append(response)
            except Exception as e:
                self.ctx.logger.error(f"Agent {agent.name} error: {e}")
                # Create error response
                error_response = AgentResponse(
                    executive_takeaway=f"Agent {agent.name} encountered an error",
                    analysis=f"Error during execution: {str(e)}",
                    findings={"error": str(e)},
                    recommendations=[f"Review {agent.name} implementation"],
                    footnotes=[],
                    version="v1.0.0",
                    checks=[],
                    errors=[str(e)]
                )
                packets.append(error_response)
        
        # Flatten footnotes into register
        footnote_register: Dict[str, str] = {}
        for packet in packets:
            for footnote in packet.footnotes:
                footnote_register[footnote.id] = (
                    f"{footnote.label} | {footnote.source} | "
                    f"retrieved {footnote.retrieved_at} | refresh {footnote.refresh} | "
                    f"{footnote.transform}"
                )
        
        summary = f"Completed {len(packets)} work packets for {goal.objective}."
        
        return ExecutionResponse(
            summary=summary,
            packets=packets,
            footnote_register=footnote_register
        )

# Global instances - will be initialized in server.py
logger = Logger()
security_api = None  # Will be set in server.py
agent_context = None  # Will be set in server.py
orchestrator = None  # Will be set in server.py