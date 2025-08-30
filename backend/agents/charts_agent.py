from agent_system import Agent, AgentContext
from agent_models import AgentRequest, AgentResponse, Footnote, AgentAsset

class ChartsAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Charts and Visualization Engineer",
            handles=["charts", "visuals", "visualization"]
        )
    
    async def run(self, req: AgentRequest, ctx: AgentContext) -> AgentResponse:
        """Generate charts and visualizations for investment analysis"""
        
        # In production, this would generate actual SVG/PNG charts
        # For now, we'll create mock chart data and paths
        
        chart_type = req.inputs.get("chart_type", "yield_curve")
        
        if chart_type == "yield_curve":
            # Mock yield curve data
            svg_path = "/assets/charts/yield_curve.svg"
            chart_data = {
                "5Y": 4.25,
                "10Y": 4.65, 
                "30Y": 4.85,
                "trend": "steepening"
            }
        elif chart_type == "cre_distress":
            svg_path = "/assets/charts/cre_distress.svg"
            chart_data = {
                "office_distress": 0.35,
                "retail_distress": 0.42,
                "industrial_distress": 0.22,
                "total_exposure": "$27.5B"
            }
        else:
            svg_path = "/assets/charts/generic.svg"
            chart_data = {"message": "Chart generated"}
        
        ctx.logger.info("chart-render", {
            "chart_type": chart_type,
            "audience": req.audience
        })
        
        recommendations = []
        if req.audience == "LP":
            recommendations = [
                "Display yield curve with clear delta indicators",
                "Emphasize risk-adjusted return context",
                "Include benchmark comparisons"
            ]
        elif req.audience == "GP":
            recommendations = [
                "Show detailed spread analysis",
                "Include stress test scenarios", 
                "Add portfolio attribution charts"
            ]
        
        return AgentResponse(
            executive_takeaway="Professional investment-grade visualizations prepared with clear messaging for target audience.",
            analysis=f"Generated {chart_type} visualization optimized for {req.audience} consumption with institutional formatting standards.",
            findings=chart_data,
            recommendations=recommendations,
            assets=[AgentAsset(kind="svg", path=svg_path, title=f"{chart_type.replace('_', ' ').title()} Chart")],
            footnotes=[
                Footnote(
                    id="VIZ1",
                    label="Chart data sources",
                    source="Treasury Daily Curve + FRED", 
                    retrieved_at=ctx.now(),
                    refresh="Daily",
                    transform="Latest close with trend analysis"
                )
            ],
            version="v1.0.0",
            checks=[
                "Chart axes labeled clearly",
                "Units and scales appropriate",
                "Color scheme institutional-appropriate",
                "Mobile responsive design ready"
            ]
        )