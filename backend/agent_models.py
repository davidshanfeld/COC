from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid

# Agent SDK Models
class Audience(BaseModel):
    value: str  # "LP" | "GP" | "Internal"

class Footnote(BaseModel):
    id: str
    label: str
    source: str
    retrieved_at: str
    refresh: str
    transform: str

class AgentRequest(BaseModel):
    objective: str
    audience: str  # "LP" | "GP" | "Internal"
    inputs: Dict[str, Any] = {}
    required_charts: Optional[List[str]] = None
    required_models: Optional[List[str]] = None
    deadlines: Optional[Dict[str, str]] = None
    style_notes: Optional[List[str]] = None
    footnote_requirements: Optional[bool] = None
    security_tier: Optional[str] = "public"  # "public" | "restricted" | "confidential"

class AgentAsset(BaseModel):
    kind: str  # "svg"|"png"|"csv"|"xlsx"|"json"|"pdf"
    path: str
    title: Optional[str] = None

class AgentResponse(BaseModel):
    executive_takeaway: str
    analysis: str
    findings: Dict[str, Any]
    recommendations: List[str]
    assets: Optional[List[AgentAsset]] = []
    footnotes: List[Footnote]
    version: str
    checks: List[str]
    errors: Optional[List[str]] = None

class ExecutionRequest(BaseModel):
    objective: str
    audience: str
    inputs: Dict[str, Any] = {}
    tags: List[str]
    required_charts: Optional[List[str]] = None
    required_models: Optional[List[str]] = None
    deadlines: Optional[Dict[str, str]] = None
    style_notes: Optional[List[str]] = None
    footnote_requirements: Optional[bool] = None
    security_tier: Optional[str] = "public"

class ExecutionResponse(BaseModel):
    summary: str
    packets: List[AgentResponse]
    footnote_register: Dict[str, str]

# Database Models
class FootnoteDB(BaseModel):
    id: str = None
    footnote_id: str
    label: str
    source: str
    retrieved_at: datetime
    refresh: str
    transform: str
    created_at: datetime = None

    def __init__(self, **data):
        if 'id' not in data or data['id'] is None:
            data['id'] = str(uuid.uuid4())
        if 'created_at' not in data or data['created_at'] is None:
            data['created_at'] = datetime.utcnow()
        super().__init__(**data)

class FeedCache(BaseModel):
    id: str = None
    source: str
    data: Dict[str, Any]
    last_updated: datetime
    expires_at: datetime
    status: str = "active"

    def __init__(self, **data):
        if 'id' not in data or data['id'] is None:
            data['id'] = str(uuid.uuid4())
        super().__init__(**data)

class AccessLog(BaseModel):
    id: str = None
    user_id: str
    event: str
    meta: Optional[Dict[str, Any]] = {}
    timestamp: datetime = None
    ip_address: Optional[str] = None

    def __init__(self, **data):
        if 'id' not in data or data['id'] is None:
            data['id'] = str(uuid.uuid4())
        if 'timestamp' not in data or data['timestamp'] is None:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)

class SingleUseToken(BaseModel):
    id: str = None
    token: str
    user_id: str
    expires_at: datetime
    used: bool = False
    created_at: datetime = None

    def __init__(self, **data):
        if 'id' not in data or data['id'] is None:
            data['id'] = str(uuid.uuid4())
        if 'created_at' not in data or data['created_at'] is None:
            data['created_at'] = datetime.utcnow()
        super().__init__(**data)

# Data Feed Models
class TreasuryYieldResponse(BaseModel):
    tenor: str
    value: float
    as_of: str

class FredResponse(BaseModel):
    series_id: str
    rows: List[Dict[str, Union[str, float]]]

class FdicResponse(BaseModel):
    rows: List[Dict[str, Any]]

class CreMaturitiesResponse(BaseModel):
    rows: List[Dict[str, Any]]

class ZoningLAResponse(BaseModel):
    rows: List[Dict[str, Any]]

# Regulatory + FDIC Adapter Models
class RegItem(BaseModel):
    scope: str  # "federal", "state", "municipal"
    code: str
    title: str
    summary: str
    citations: List[str]
    footnoteId: str

class FDICSnapshot(BaseModel):
    bankId: str
    bankName: str
    exposurePct: float
    stack: Dict[str, float]  # {"mf": 0.4, "off": 0.3, "ind": 0.2, "other": 0.1}
    footnoteId: str