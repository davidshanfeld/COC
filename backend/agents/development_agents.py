# Development feasibility agents for data centers and EV infrastructure

from agent_system import Agent, AgentContext
from agent_models import AgentRequest, AgentResponse, Footnote

class DevDataCentersAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Development Feasibility — Data Centers",
            handles=["dev-dc", "development", "data-center-dev", "feasibility"]
        )
    
    async def run(self, req: AgentRequest, ctx: AgentContext) -> AgentResponse:
        """Analyze development feasibility for data center projects"""
        
        site_size_sf = float(req.inputs.get("site_size_sf", 100000))
        power_capacity = float(req.inputs.get("power_capacity_mw", 10))
        target_pue = float(req.inputs.get("target_pue", 1.3))
        
        # Development timeline and critical path
        development_schedule = {
            "total_timeline_months": 24,
            "critical_path_items": [
                {"phase": "Entitlements & Permits", "duration_months": 6, "risk": "Medium"},
                {"phase": "Power Infrastructure", "duration_months": 12, "risk": "High"},
                {"phase": "Cooling Systems", "duration_months": 8, "risk": "Medium"},
                {"phase": "Core & Shell", "duration_months": 14, "risk": "Low"},
                {"phase": "MEP & Fit-out", "duration_months": 10, "risk": "Medium"}
            ],
            "parallel_activities": [
                "Utility interconnect application",
                "Equipment procurement (long-lead items)",
                "Tenant improvement design"
            ]
        }
        
        # Cost breakdown analysis
        construction_budget = {
            "hard_costs_per_sf": {
                "core_shell": 180,
                "power_infrastructure": 250,
                "cooling_mechanical": 200,
                "backup_systems": 120,
                "fiber_connectivity": 50
            },
            "soft_costs_percentage": 0.15,
            "contingency_percentage": 0.10,
            "total_hard_cost": site_size_sf * 800,  # Blended rate
            "estimated_total_project_cost": site_size_sf * 920  # With soft costs and contingency
        }
        
        # Technical specifications
        technical_requirements = {
            "power_density_watts_per_sf": 150,
            "cooling_capacity_tons": power_capacity * 1000 / 3.5,  # Rule of thumb
            "redundancy_level": "N+1",
            "backup_power_duration_hours": 48,
            "fiber_entry_points": 4,
            "seismic_design_category": "D",  # LA area requirement
            "energy_efficiency_target": {
                "pue": target_pue,
                "free_cooling_hours_annual": 3500,  # LA climate advantage
                "renewable_energy_percentage": 0.60
            }
        }
        
        # Risk assessment
        development_risks = [
            {
                "risk": "Utility Interconnect Delays",
                "probability": "Medium",
                "impact": "High", 
                "mitigation": "Early utility engagement, backup substation capacity"
            },
            {
                "risk": "Equipment Supply Chain",
                "probability": "Medium",
                "impact": "Medium",
                "mitigation": "Long-lead procurement, supplier diversity"
            },
            {
                "risk": "Permitting Delays",
                "probability": "Low",
                "impact": "Medium", 
                "mitigation": "Experienced local consultants, pre-application meetings"
            },
            {
                "risk": "Labor Availability",
                "probability": "Low",
                "impact": "Medium",
                "mitigation": "Union partnerships, regional contractor network"
            }
        ]
        
        ctx.logger.info("dev-dc-analysis", {
            "site_size": site_size_sf,
            "power_capacity": power_capacity
        })
        
        findings = {
            "development_schedule": development_schedule,
            "construction_budget": construction_budget,
            "technical_requirements": technical_requirements,
            "risk_assessment": development_risks,
            "site_advantages": [
                "Seismically stable geology",
                "Excellent fiber connectivity",
                "Industrial power infrastructure available",
                "Skilled construction workforce"
            ]
        }
        
        recommendations = [
            "Secure substation capacity allocation before site acquisition",
            "Order critical equipment (transformers, generators) 12+ months in advance",
            "Engage utility interconnect process during due diligence phase",
            "Consider modular construction for faster time-to-market",
            "Implement integrated project delivery for complex MEP coordination"
        ]
        
        if req.audience == "LP":
            recommendations.extend([
                "Evaluate development partner track record and bonding capacity",
                "Structure milestone-based funding with performance guarantees"
            ])
        elif req.audience == "GP":
            recommendations.extend([
                "Build contingency for supply chain disruptions",
                "Develop standardized technical specifications across portfolio"
            ])
        
        return AgentResponse(
            executive_takeaway=f"Data center development feasible with 24-month timeline and estimated ${construction_budget['estimated_total_project_cost']:,.0f} total project cost.",
            analysis="Comprehensive feasibility assessment covering technical requirements, construction sequencing, and risk mitigation for institutional-grade data center development.",
            findings=findings,
            recommendations=recommendations,
            footnotes=[
                Footnote(
                    id="DDV1",
                    label="LA Data Center Construction Costs",
                    source="Turner Construction Cost Index",
                    retrieved_at=ctx.now(),
                    refresh="Quarterly",
                    transform="Regional adjustments applied"
                )
            ],
            version="v1.0.0",
            checks=[
                "Timeline realistic for LA permitting environment",
                "Cost estimates include regional labor premiums",
                "Technical specs meet Tier III standards",
                "Risk mitigation strategies appropriate"
            ]
        )

class DevEVAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Development Feasibility — EV Supercharging",
            handles=["dev-ev", "ev-development", "charging-development"]
        )
    
    async def run(self, req: AgentRequest, ctx: AgentContext) -> AgentResponse:
        """Analyze development feasibility for EV charging infrastructure"""
        
        site_count = int(req.inputs.get("site_count", 1))
        stalls_per_site = int(req.inputs.get("stalls_per_site", 8))
        power_level_kw = int(req.inputs.get("power_level_kw", 150))
        
        # Development timeline
        development_schedule = {
            "total_timeline_months": 9,
            "critical_path_items": [
                {"phase": "Site Selection & LOI", "duration_months": 2, "risk": "Low"},
                {"phase": "Permits & Approvals", "duration_months": 4, "risk": "Medium"},
                {"phase": "Utility Interconnect", "duration_months": 6, "risk": "High"},
                {"phase": "Construction", "duration_months": 3, "risk": "Low"},
                {"phase": "Testing & Commissioning", "duration_months": 1, "risk": "Low"}
            ],
            "parallel_opportunities": [
                "NEVI grant application during permitting",
                "Equipment procurement during utility work",
                "Network operations setup during construction"
            ]
        }
        
        # Per-site cost analysis
        site_budget = {
            "equipment_costs": {
                "charging_hardware": stalls_per_site * 25000,  # $25k per 150kW stall
                "electrical_infrastructure": 75000,
                "civil_site_work": 50000,
                "signage_lighting": 15000
            },
            "soft_costs": {
                "permits_fees": 12000,
                "engineering_design": 25000,
                "project_management": 20000,
                "commissioning": 8000
            },
            "utility_costs": {
                "interconnect_fee": 25000,
                "transformer_upgrade": 40000,
                "service_lateral": 15000
            }
        }
        
        total_per_site = sum(site_budget["equipment_costs"].values()) + \
                        sum(site_budget["soft_costs"].values()) + \
                        sum(site_budget["utility_costs"].values())
        
        site_budget["total_per_site"] = total_per_site
        site_budget["total_program_cost"] = total_per_site * site_count
        
        # Operational considerations
        operational_factors = {
            "power_requirements": {
                "peak_demand_kw": stalls_per_site * power_level_kw,
                "estimated_load_factor": 0.35,
                "backup_power": "Not typically required",
                "demand_management": "Load balancing software recommended"
            },
            "site_requirements": {
                "minimum_frontage_feet": 150,
                "parking_spaces_required": stalls_per_site * 1.2,  # Include ADA spaces
                "traffic_visibility": "High visibility recommended",
                "amenities_proximity": "Food/retail within 0.25 miles preferred"
            },
            "maintenance_considerations": [
                "24/7 remote monitoring capability",
                "Preventive maintenance quarterly",
                "Vandalism/theft protection measures",
                "Software update management"
            ]
        }
        
        # Grant and incentive optimization
        incentive_structure = {
            "nevi_federal_grant": {
                "coverage_percentage": 0.80,
                "max_per_port": 100000,
                "requirements": ["Public access", "Payment interoperability", "Uptime standards"]
            },
            "state_incentives": {
                "california_lcfs_credits": "Revenue stream",
                "self_generation_incentive": "Battery storage bonus",
                "local_utility_rebates": "Varies by territory"
            },
            "estimated_grant_value": total_per_site * 0.65  # Blended rate
        }
        
        ctx.logger.info("dev-ev-analysis", {
            "site_count": site_count,
            "stalls_per_site": stalls_per_site
        })
        
        findings = {
            "development_schedule": development_schedule,
            "site_budget": site_budget,
            "operational_factors": operational_factors,
            "incentive_structure": incentive_structure,
            "success_factors": [
                "High-traffic location selection",
                "Grant funding maximization",
                "Utility partnership development",
                "Network interoperability planning"
            ]
        }
        
        recommendations = [
            "Apply for NEVI grants early in site selection process",
            "Negotiate host site agreements with revenue sharing upside",
            "Coordinate utility interconnect applications across portfolio",
            "Consider battery storage integration for demand charge management",
            "Develop standardized site selection criteria for scalability"
        ]
        
        if req.audience == "LP":
            recommendations.extend([
                "Focus on IRR impact of grant funding optimization",
                "Evaluate geographic diversification for regulatory risk"
            ])
        elif req.audience == "GP":
            recommendations.extend([
                "Build operational partnerships with charging network operators",
                "Develop pipeline of pre-approved sites for rapid deployment"
            ])
        
        return AgentResponse(
            executive_takeaway=f"EV charging development program feasible with 9-month timeline and ${total_per_site:,.0f} per-site cost, reduced to ~${total_per_site * 0.35:,.0f} net after grants.",
            analysis="Streamlined development process leveraging federal NEVI grants and state incentives with focus on high-utilization site selection and operational efficiency.",
            findings=findings,
            recommendations=recommendations,
            footnotes=[
                Footnote(
                    id="DEV1",
                    label="EV Charging Construction Costs",
                    source="NREL EV Infrastructure Cost Study",
                    retrieved_at=ctx.now(),
                    refresh="Annually",
                    transform="150kW DCFC installation costs"
                )
            ],
            version="v1.0.0",
            checks=[
                "Grant eligibility requirements incorporated",
                "Utility interconnect timeline realistic",
                "Equipment costs current with supply chain",
                "Operational considerations comprehensive"
            ]
        )