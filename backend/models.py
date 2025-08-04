from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class DataSource(BaseModel):
    name: str
    url: str
    last_updated: datetime
    value: float
    unit: str
    source_type: str  # 'fed', 'trepp', 'rca', 'cbre', etc.


class DocumentSection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    order: int
    content: str
    subsections: List['DocumentSection'] = []
    data_dependencies: List[str] = []  # List of data source IDs this section depends on
    last_updated: datetime = Field(default_factory=datetime.now)


class LiveDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    sections: List[DocumentSection]
    data_sources: Dict[str, DataSource] = {}
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    version: str = "1.0"


class FinancialModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    parameters: Dict[str, Any]
    formulas: Dict[str, str]
    outputs: Dict[str, float]
    last_calculated: datetime = Field(default_factory=datetime.now)


class MarketData(BaseModel):
    data_type: str  # 'interest_rate', 'construction_cost', 'inflation', etc.
    value: float
    unit: str
    source: str
    timestamp: datetime
    location: Optional[str] = None


class UpdateRequest(BaseModel):
    document_id: str
    force_refresh: bool = False


class RealTimeDataResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    sources_updated: List[str]
    timestamp: datetime
    message: str


# Enable forward references
DocumentSection.model_rebuild()