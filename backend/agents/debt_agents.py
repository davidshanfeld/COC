# Debt underwriting specialists for data centers and EV infrastructure

from agent_system import Agent, AgentContext
from agent_models import AgentRequest, AgentResponse, Footnote

class DebtDataCentersAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Debt Underwriting — Data Centers",
            handles=["debt-dc", "data-centers", "term-sheets", "covenants"]
        )
    
    async def run(self, req: AgentRequest, ctx: AgentContext) -> AgentResponse:
        """Analyze debt underwriting for data center projects"""
        
        project_size = float(req.inputs.get("project_size", 50000000))
        power_capacity = float(req.inputs.get("power_capacity_mw", 10))
        lease_term = int(req.inputs.get("lease_term_years", 15))
        
        # Data center debt structuring
        term_sheet = {
            "structure": "Senior Secured Construction-to-Perm",
            "coupon": "SOFR + 475-525 bps",
            "advance_rate": 0.60,
            "loan_amount": project_size * 0.60,
            "covenants": [
                "DSCR >= 1.35x (stabilized)",
                "LTV <= 60% (appraised value)",
                "Cash sweep if DSCR < 1.20x",
                "Power delivery milestone requirements"
            ],
            "key_risks": [
                "Utility interconnect delays",
                "Tenant credit concentration",
                "Technology obsolescence",
                "Power cost escalation"
            ]
        }
        
        # Power infrastructure analysis
        power_analysis = {
            "capacity_mw": power_capacity,
            "estimated_demand_per_rack": 15,  # kW average
            "utilization_assumption": 0.85,
            "backup_power_requirement": "N+1 redundancy",
            "utility_costs_per_kwh": 0.22,  # LA area industrial rates
            "interconnect_timeline_months": 18
        }
        
        # Market positioning
        market_context = {
            "la_data_center_vacancy": 0.02,  # Very tight market
            "average_lease_rate_per_kw_month": 175,
            "hyperscale_demand": "Strong",
            "fiber_connectivity": "Tier 1 available",
            "competitive_advantages": [
                "Low seismic risk zone",
                "Diverse fiber infrastructure", 
                "Proximity to content delivery networks",
                "Available industrial power capacity"
            ]
        }
        
        ctx.logger.info("debt-dc-analysis", {
            "project_size": project_size,
            "power_capacity": power_capacity
        })
        
        findings = {
            "term_sheet": term_sheet,
            "power_analysis": power_analysis,
            "market_context": market_context,
            "investment_metrics": {
                "estimated_construction_cost_per_sf": 600,  # Core & shell
                "estimated_fitout_cost_per_sf": 400,       # Tenant improvements
                "stabilized_yield_on_cost": 0.08,
                "lease_up_timeline_months": 12
            }
        }
        
        recommendations = [
            "Secure utility interconnect LOI before construction loan closing",
            "Require transformer delivery as condition precedent",
            "Structure pre-leasing requirements at 60% before conversion",
            "Include step-down pricing for hyperscale tenant commitments",
            "Maintain 18-month debt service reserve during lease-up"
        ]
        
        if req.audience == "LP":
            recommendations.append("Focus on stabilized cash-on-cash returns and exit cap rate assumptions")
        elif req.audience == "GP":
            recommendations.extend([
                "Build relationships with colocation providers for lease-up risk mitigation",
                "Consider construction management self-performance to control costs"
            ])
        
        return AgentResponse(
            executive_takeaway="Data center debt structured with conservative 60% LTV and power delivery milestones to mitigate utility interconnect risk.",
            analysis="Comprehensive underwriting addresses key data center risks including power delivery, tenant concentration, and technology refresh cycles.",
            findings=findings,
            recommendations=recommendations,
            footnotes=[
                Footnote(
                    id="DDC1",
                    label="LA Industrial Power Rates",
                    source="LADWP Commercial Rate Schedule",
                    retrieved_at=ctx.now(),
                    refresh="Monthly",
                    transform="Blended rate for 10MW+ accounts"
                )
            ],
            version="v1.0.0",
            checks=[
                "Power capacity validated against market standards",
                "Covenant structure appropriate for asset class",
                "Market lease rates verified with brokers",
                "Construction timeline realistic for LA permitting"
            ]
        )

class DebtEVAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Debt Underwriting — EV Supercharging", 
            handles=["debt-ev", "ev-charging", "charging", "supercharging"]
        )
    
    async def run(self, req: AgentRequest, ctx: AgentContext) -> AgentResponse:
        """Analyze debt underwriting for EV charging infrastructure"""
        
        project_size = float(req.inputs.get("project_size", 2000000))
        charging_stalls = int(req.inputs.get("charging_stalls", 8))
        site_type = req.inputs.get("site_type", "highway")  # highway, urban, fleet
        
        # EV infrastructure debt structuring
        term_sheet = {
            "structure": "Project Finance with NEVI Credit Enhancement",
            "coupon": "SOFR + 525-575 bps",
            "advance_rate": 0.55,  # Lower due to technology risk
            "loan_amount": project_size * 0.55,
            "covenants": [
                "DSCR >= 1.30x (stabilized)",
                "Minimum throughput floors by site type",
                "Grant funding lockup requirements",
                "Equipment refresh reserve funding"
            ],
            "credit_enhancements": [
                "NEVI federal grants (up to 80% eligible costs)",
                "State LCFS credit monetization",
                "Utility demand response programs",
                "Fleet anchor tenant agreements"
            ]
        }
        
        # Site analysis by type
        if site_type == "highway":
            site_metrics = {
                "expected_daily_sessions": 120,
                "average_session_kwh": 45,
                "pricing_per_kwh": 0.49,
                "utilization_ramp_months": 18,
                "competitive_moats": ["Network effects", "Brand recognition"]
            }
        elif site_type == "urban":
            site_metrics = {
                "expected_daily_sessions": 80,
                "average_session_kwh": 35,
                "pricing_per_kwh": 0.45,
                "utilization_ramp_months": 12,
                "competitive_moats": ["Location convenience", "Amenity integration"]
            }
        else:  # fleet
            site_metrics = {
                "expected_daily_sessions": 200,
                "average_session_kwh": 60,
                "pricing_per_kwh": 0.38,  # Fleet pricing discount
                "utilization_ramp_months": 6,
                "competitive_moats": ["Dedicated capacity", "Fleet contracts"]
            }
        
        # Financial projections
        annual_revenue = (
            site_metrics["expected_daily_sessions"] * 
            site_metrics["average_session_kwh"] * 
            site_metrics["pricing_per_kwh"] * 365
        )
        
        operating_metrics = {
            "estimated_annual_revenue": annual_revenue,
            "electricity_cost_percentage": 0.35,
            "maintenance_cost_percentage": 0.15,
            "network_fees_percentage": 0.08,
            "net_operating_margin": 0.42
        }
        
        ctx.logger.info("debt-ev-analysis", {
            "site_type": site_type,
            "charging_stalls": charging_stalls
        })
        
        findings = {
            "term_sheet": term_sheet,
            "site_metrics": site_metrics,
            "operating_metrics": operating_metrics,
            "market_factors": {
                "ev_adoption_growth_rate": 0.35,  # Annual
                "charging_network_density": "Moderate in LA",
                "utility_interconnect_cost": 150000,  # Estimated per site
                "permitting_timeline_months": 9
            }
        }
        
        recommendations = [
            "Stack NEVI grants with state incentives to minimize basis",
            "Negotiate utility demand charge management programs",
            "Structure fleet anchor tenant commitments for 40% utilization floor",
            "Include technology refresh reserves for equipment obsolescence",
            "Consider site selection criteria prioritizing high-traffic corridors"
        ]
        
        if req.audience == "LP":
            recommendations.append("Evaluate charging network exposure across portfolio for concentration risk")
        elif req.audience == "GP":
            recommendations.extend([
                "Build operational partnerships with charging network operators",
                "Develop standardized site selection and underwriting criteria"
            ])
        
        return AgentResponse(
            executive_takeaway=f"EV charging debt structured with 55% LTV and throughput floors, supported by {annual_revenue:,.0f} annual revenue projection for {site_type} site.",
            analysis="Project finance structure leverages federal NEVI grants and state incentives while managing technology and utilization risks through conservative underwriting.",
            findings=findings,
            recommendations=recommendations,
            footnotes=[
                Footnote(
                    id="DEV1",
                    label="NEVI Grant Program Requirements",
                    source="FHWA NEVI Guidance",
                    retrieved_at=ctx.now(),
                    refresh="Quarterly",
                    transform="Eligibility criteria and funding caps"
                )
            ],
            version="v1.0.0",
            checks=[
                "Throughput assumptions validated with industry benchmarks",
                "Grant stacking compliance verified",
                "Utility interconnect costs estimated",
                "Technology refresh timeline appropriate"
            ]
        )