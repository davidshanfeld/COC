# Agent registry setup and initialization

from agent_system import AgentRegistry, Orchestrator, AgentContext, SecurityAPI, Logger
from agents.charts_agent import ChartsAgent
from agents.ui_agent import UIAgent  
from agents.data_steward_agent import DataStewardAgent
from agents.quant_agent import QuantAgent
from agents.debt_agents import DebtDataCentersAgent, DebtEVAgent
from agents.development_agents import DevDataCentersAgent, DevEVAgent
from agents.legal_risk_agents import TaxAgent, LandUseLAAgent, RiskAgent, ESGAgent
from agents.review_security_agents import RedTeamAgent, SecurityAgent

def build_agent_registry():
    """Build and configure the complete agent registry"""
    registry = AgentRegistry()
    
    # Register all specialized agents
    agents = [
        ChartsAgent(),
        UIAgent(),
        DataStewardAgent(),
        QuantAgent(),
        DebtDataCentersAgent(),
        DebtEVAgent(),
        DevDataCentersAgent(),
        DevEVAgent(),
        TaxAgent(),
        LandUseLAAgent(),
        RiskAgent(),
        ESGAgent(),
        RedTeamAgent(),
        SecurityAgent()
    ]
    
    for agent in agents:
        registry.register(agent)
    
    return registry

def build_orchestrator(db_client):
    """Build orchestrator with full context"""
    logger = Logger()
    security_api = SecurityAPI(db_client, logger)
    context = AgentContext(logger, security_api, db_client)
    registry = build_agent_registry()
    
    return Orchestrator(registry, context)

# Agent routing helper
def get_recommended_agents_for_task(task_description: str) -> list:
    """Recommend agents based on task description"""
    task_lower = task_description.lower()
    
    recommendations = []
    
    # Market and data analysis
    if any(word in task_lower for word in ["market", "data", "rates", "fed", "treasury"]):
        recommendations.extend(["data", "charts"])
    
    # Financial modeling
    if any(word in task_lower for word in ["dcf", "irr", "waterfall", "financial", "model"]):
        recommendations.extend(["quant", "charts"])
    
    # Development projects
    if any(word in task_lower for word in ["development", "construction", "feasibility"]):
        if "data center" in task_lower or "dc" in task_lower:
            recommendations.append("dev-dc")
        if "ev" in task_lower or "charging" in task_lower:
            recommendations.append("dev-ev")
        recommendations.extend(["land-use", "risk"])
    
    # Debt underwriting
    if any(word in task_lower for word in ["debt", "underwriting", "loan", "term sheet"]):
        if "data center" in task_lower:
            recommendations.append("debt-dc")
        if "ev" in task_lower or "charging" in task_lower:
            recommendations.append("debt-ev")
        recommendations.extend(["quant", "risk"])
    
    # Legal and regulatory
    if any(word in task_lower for word in ["legal", "zoning", "permit", "tax", "regulation"]):
        recommendations.extend(["land-use", "tax"])
    
    # ESG and incentives
    if any(word in task_lower for word in ["esg", "sustainability", "grants", "incentives"]):
        recommendations.append("esg")
    
    # Risk management
    if any(word in task_lower for word in ["risk", "stress", "scenario", "sensitivity"]):
        recommendations.extend(["risk", "quant"])
    
    # UI and presentation
    if any(word in task_lower for word in ["ui", "design", "layout", "presentation"]):
        recommendations.extend(["ui", "charts"])
    
    # Security and access
    if any(word in task_lower for word in ["security", "access", "audit", "token"]):
        recommendations.append("security")
    
    # Quality review
    if any(word in task_lower for word in ["review", "validate", "quality", "check"]):
        recommendations.append("red-team")
    
    # Default recommendations for LP/GP analysis
    if not recommendations:
        recommendations = ["data", "quant", "charts", "ui"]
    
    return list(set(recommendations))  # Remove duplicates

# Agent capability mapping
AGENT_CAPABILITIES = {
    "charts": {
        "description": "Charts and Visualization Engineer",
        "specialties": ["yield curves", "market data visualization", "investment performance charts"],
        "outputs": ["SVG charts", "data visualizations", "presentation graphics"]
    },
    "ui": {
        "description": "UI, Aesthetics, and Information Architecture",
        "specialties": ["design systems", "user interface", "institutional branding"],
        "outputs": ["design tokens", "layout specifications", "UI components"]
    },
    "data": {
        "description": "Real-Time Data and Citations Steward",
        "specialties": ["market data feeds", "source citations", "data quality assurance"],
        "outputs": ["live market data", "footnote management", "data provenance tracking"]
    },
    "quant": {
        "description": "Quantitative Analysis and Models",
        "specialties": ["DCF modeling", "waterfall analysis", "scenario planning"],
        "outputs": ["financial models", "sensitivity analysis", "return projections"]
    },
    "debt-dc": {
        "description": "Debt Underwriting — Data Centers",
        "specialties": ["data center financing", "power infrastructure risk", "lease underwriting"],
        "outputs": ["term sheets", "covenant structures", "risk assessment"]
    },
    "debt-ev": {
        "description": "Debt Underwriting — EV Supercharging",
        "specialties": ["EV charging financing", "utilization modeling", "grant integration"],
        "outputs": ["project finance structures", "throughput analysis", "incentive optimization"]
    },
    "dev-dc": {
        "description": "Development Feasibility — Data Centers",
        "specialties": ["construction planning", "MEP systems", "power delivery"],
        "outputs": ["development timelines", "cost estimates", "technical specifications"]
    },
    "dev-ev": {
        "description": "Development Feasibility — EV Supercharging",
        "specialties": ["site selection", "utility coordination", "grant applications"],
        "outputs": ["feasibility analysis", "permitting roadmaps", "incentive stacking"]
    },
    "tax": {
        "description": "Tax Attorney Consultant",
        "specialties": ["real estate taxation", "DST structures", "investor implications"],
        "outputs": ["tax analysis", "structure recommendations", "compliance guidance"]
    },
    "land-use": {
        "description": "Land Use Attorney — Los Angeles",
        "specialties": ["zoning compliance", "CEQA requirements", "permit processes"],
        "outputs": ["entitlement roadmaps", "regulatory analysis", "approval timelines"]
    },
    "risk": {
        "description": "Risk Management and Controls",
        "specialties": ["risk identification", "KRI frameworks", "mitigation strategies"],
        "outputs": ["risk registers", "monitoring dashboards", "scenario planning"]
    },
    "esg": {
        "description": "ESG, Incentives, and Grants",
        "specialties": ["sustainability frameworks", "incentive stacking", "impact measurement"],
        "outputs": ["ESG strategies", "grant applications", "impact reporting"]
    },
    "red-team": {
        "description": "LP-GP Red Team Reviewer",
        "specialties": ["investment thesis validation", "quality assurance", "stakeholder perspectives"],
        "outputs": ["review scores", "improvement recommendations", "validation reports"]
    },
    "security": {
        "description": "Security and Distribution",
        "specialties": ["access control", "document security", "audit logging"],
        "outputs": ["security tokens", "watermarked documents", "audit reports"]
    }
}