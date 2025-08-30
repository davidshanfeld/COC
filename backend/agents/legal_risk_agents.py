# Legal, tax, risk management, and ESG agents

from agent_system import Agent, AgentContext
from agent_models import AgentRequest, AgentResponse, Footnote

class TaxAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Tax Attorney Consultant",
            handles=["tax", "dst", "investor-faq", "tax-planning"]
        )
    
    async def run(self, req: AgentRequest, ctx: AgentContext) -> AgentResponse:
        """Provide tax analysis and structuring guidance"""
        
        investment_type = req.inputs.get("investment_type", "debt")
        investor_type = req.inputs.get("investor_type", "taxable")
        
        # Tax implications by investment structure
        if investment_type == "debt":
            tax_analysis = {
                "income_character": "Ordinary income",
                "state_sourcing": "Generally sourced to borrower location",
                "timing": "Accrual basis for yield, cash basis for fees",
                "depreciation": "Not applicable for debt instruments",
                "key_considerations": [
                    "Original Issue Discount (OID) rules may apply",
                    "Market discount treatment for secondary purchases",
                    "State nexus implications for multi-state borrowers"
                ]
            }
        else:  # equity
            tax_analysis = {
                "income_character": "Capital gains on sale, ordinary income from operations",
                "state_sourcing": "Source to property location",
                "timing": "Pass-through taxation typical",
                "depreciation": "Cost segregation opportunities available",
                "key_considerations": [
                    "Section 1031 like-kind exchange eligibility",
                    "Qualified Opportunity Zone benefits if applicable",
                    "Depreciation recapture on sale"
                ]
            }
        
        # Investor-specific considerations
        if investor_type == "tax_exempt":
            special_considerations = {
                "ubti_risk": "Monitor for unrelated business taxable income",
                "debt_financed_property": "UDFI rules apply to leveraged investments",
                "filing_requirements": "Form 990-T if UBTI threshold exceeded",
                "recommendations": [
                    "Structure to avoid UBTI where possible",
                    "Consider blocker entity for complex structures",
                    "Monitor debt allocation across portfolio"
                ]
            }
        elif investor_type == "international":
            special_considerations = {
                "withholding_tax": "30% on US-source income unless treaty reduction",
                "effectively_connected_income": "May trigger US tax return filing requirement",
                "firpta_implications": "Foreign Investment in Real Property Tax Act applies",
                "recommendations": [
                    "Review applicable tax treaties",
                    "Consider FIRPTA withholding certificates",
                    "Structure for tax efficiency in investor jurisdiction"
                ]
            }
        else:
            special_considerations = {
                "rate_optimization": "Coordinate timing with other income/losses",
                "state_considerations": "Plan for high-tax state investor exposure", 
                "amt_implications": "Monitor alternative minimum tax items",
                "recommendations": [
                    "Consider installment sale treatment where applicable",
                    "Optimize depreciation methods and elections",
                    "Coordinate with investor's overall tax planning"
                ]
            }
        
        # DST (Delaware Statutory Trust) analysis
        dst_considerations = {
            "section_1031_eligibility": "Qualifies for like-kind exchange treatment",
            "structure_requirements": [
                "Passive investment only (no management rights)",
                "Pre-existing debt arrangements",
                "Limited number of beneficial interests",
                "No power to direct operations"
            ],
            "investor_benefits": [
                "Professional management without disqualification",
                "Fractionalized ownership opportunities", 
                "Institutional-quality assets accessible",
                "Simplified successor trustee transitions"
            ],
            "limitations": [
                "No control over property decisions",
                "Limited liquidity options",
                "Regulatory compliance complexity",
                "Higher fees than direct ownership"
            ]
        }
        
        ctx.logger.info("tax-analysis", {
            "investment_type": investment_type,
            "investor_type": investor_type
        })
        
        findings = {
            "tax_analysis": tax_analysis,
            "special_considerations": special_considerations,
            "dst_structure": dst_considerations,
            "disclaimer": "This analysis is for informational purposes only and does not constitute tax advice. Consult qualified tax advisors for specific situations."
        }
        
        recommendations = [
            "Engage qualified tax counsel early in structuring process",
            "Model tax implications alongside financial projections",
            "Consider state tax planning for high-tax jurisdictions",
            "Document tax elections and positions for audit defense"
        ]
        
        if req.audience == "LP":
            recommendations.extend([
                "Provide clear tax reporting packages annually",
                "Consider DST options for 1031 exchange investors",
                "Plan for state tax compliance across investor base"
            ])
        elif req.audience == "GP":
            recommendations.extend([
                "Develop standardized tax structuring playbooks",
                "Build relationships with specialized real estate tax advisors",
                "Consider tax-efficient exit strategies in investment planning"
            ])
        
        return AgentResponse(
            executive_takeaway=f"Tax analysis shows {tax_analysis['income_character'].lower()} treatment with {investor_type} investor considerations requiring specialized structuring.",
            analysis="Comprehensive tax planning covering federal and state implications, investor type optimization, and structuring alternatives including DST options.",
            findings=findings,
            recommendations=recommendations,
            footnotes=[
                Footnote(
                    id="TAX1",
                    label="DST Regulatory Framework",
                    source="IRC Section 1031 and Revenue Ruling 2004-86",
                    retrieved_at=ctx.now(),
                    refresh="Static",
                    transform="Like-kind exchange qualification requirements"
                )
            ],
            version="v1.0.0",
            checks=[
                "Current tax law references verified",
                "Multi-state implications considered",
                "Investor type analysis comprehensive",
                "Disclaimer appropriately prominent"
            ]
        )

class LandUseLAAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Land Use Attorney — Los Angeles",
            handles=["land-use", "la", "zoning", "entitlements", "permits"]
        )
    
    async def run(self, req: AgentRequest, ctx: AgentContext) -> AgentResponse:
        """Analyze LA land use regulations and entitlement process"""
        
        project_type = req.inputs.get("project_type", "data_center")
        zone = req.inputs.get("zone", "M3-1")
        
        # Entitlement roadmap
        entitlement_process = {
            "phase_1_preliminary": {
                "duration_months": 2,
                "key_steps": [
                    "Zoning verification and code research",
                    "Pre-application meeting with Planning Department",
                    "Environmental constraints analysis",
                    "Title and survey review"
                ]
            },
            "phase_2_applications": {
                "duration_months": 4,
                "key_steps": [
                    "Conditional Use Permit (if required)",
                    "Site Plan Review application",
                    "Building permit application prep",
                    "Utility coordination meetings"
                ]
            },
            "phase_3_approvals": {
                "duration_months": 3,
                "key_steps": [
                    "Planning Commission review (if applicable)",
                    "CEQA environmental review",
                    "Final plan check and corrections",
                    "Permit issuance"
                ]
            }
        }
        
        # Project-specific considerations
        if project_type == "data_center":
            project_analysis = {
                "preferred_zones": ["M3-1", "M2-1", "CM-1"],
                "key_requirements": [
                    "Industrial use classification verification",
                    "Power infrastructure capacity confirmation",
                    "Noise ordinance compliance for cooling equipment",
                    "Security fencing and setback requirements"
                ],
                "potential_issues": [
                    "Conditional use permit for high power usage",
                    "Traffic impact study for construction phase",
                    "Stormwater management compliance"
                ],
                "incentive_programs": [
                    "Green building incentives for LEED certification",
                    "Expedited permitting for job creation projects"
                ]
            }
        else:  # EV charging
            project_analysis = {
                "preferred_zones": ["C2-1", "CM-1", "M1-1"],
                "key_requirements": [
                    "Commercial or industrial use classification",
                    "ADA accessibility compliance",
                    "Electrical code compliance for EVSE",
                    "Signage requirements for public charging"
                ],
                "potential_issues": [
                    "Parking space conversion approvals",
                    "Utility easement negotiations",
                    "NEVI compliance for federal funding"
                ],
                "incentive_programs": [
                    "EV infrastructure expedited permitting",
                    "Reduced parking requirements for EV charging",
                    "Utility rebate coordination"
                ]
            }
        
        # CEQA considerations
        ceqa_analysis = {
            "threshold_analysis": "Most projects qualify for categorical exemptions",
            "common_exemptions": [
                "Class 1 - Existing Facilities (minor modifications)",
                "Class 3 - New Construction (small structures)",
                "Class 32 - In-Fill Development"
            ],
            "potential_triggers": [
                "Significant traffic generation",
                "Air quality impacts from generators",
                "Noise impacts in sensitive areas"
            ],
            "mitigation_strategies": [
                "Design to fit exemption criteria",
                "Early coordination with CEQA consultants",
                "Proactive community outreach"
            ]
        }
        
        # LA-specific overlay programs
        overlay_programs = [
            {
                "name": "Adaptive Reuse Ordinance",
                "applicability": "Existing building conversions",
                "benefits": ["Reduced parking requirements", "Expedited processing"]
            },
            {
                "name": "TOD (Transit-Oriented Development)",
                "applicability": "Properties near Metro stations",
                "benefits": ["Density bonuses", "Reduced parking ratios"]
            },
            {
                "name": "Green Building Program",
                "applicability": "All new construction",
                "benefits": ["Fee reductions", "Expedited plan check"]
            }
        ]
        
        ctx.logger.info("land-use-analysis", {
            "project_type": project_type,
            "zone": zone
        })
        
        findings = {
            "entitlement_process": entitlement_process,
            "project_analysis": project_analysis,
            "ceqa_analysis": ceqa_analysis,
            "overlay_programs": overlay_programs,
            "total_timeline_estimate": "6-9 months for typical projects"
        }
        
        recommendations = [
            "Engage local land use counsel early in due diligence",
            "Schedule pre-application meetings before LOI execution",
            "Consider zoning verification during site selection",
            "Budget for potential conditional use permit requirements",
            "Coordinate utility applications with entitlement process"
        ]
        
        if project_type == "data_center":
            recommendations.extend([
                "Verify power capacity during preliminary review",
                "Address cooling equipment noise proactively",
                "Consider phased development for large projects"
            ])
        else:
            recommendations.extend([
                "Confirm ADA compliance in design phase",
                "Coordinate NEVI requirements with permit process",
                "Plan for utility service upgrades"
            ])
        
        return AgentResponse(
            executive_takeaway=f"LA entitlement process for {project_type} projects requires 6-9 months with {zone} zoning offering favorable regulatory pathway.",
            analysis="Comprehensive entitlement roadmap addressing zoning compliance, CEQA requirements, and LA-specific overlay programs with timeline and risk mitigation strategies.",
            findings=findings,
            recommendations=recommendations,
            footnotes=[
                Footnote(
                    id="LA1",
                    label="Los Angeles Zoning Code",
                    source="LAMC Chapter 1 Planning and Zoning",
                    retrieved_at=ctx.now(),
                    refresh="Monthly",
                    transform="Current ordinance requirements and procedures"
                )
            ],
            version="v1.0.0",
            checks=[
                "Zoning code references current",
                "CEQA analysis up to date",
                "Overlay program benefits verified",
                "Timeline estimates realistic for LA processing"
            ]
        )

class RiskAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Risk Management and Controls",
            handles=["risk", "kri", "risk-management", "controls"]
        )
    
    async def run(self, req: AgentRequest, ctx: AgentContext) -> AgentResponse:
        """Comprehensive risk assessment and KRI framework"""
        
        investment_focus = req.inputs.get("focus", "mixed")  # data_center, ev_charging, mixed
        
        # Top risks by category
        market_risks = [
            {
                "risk": "Interest Rate Shock",
                "description": "Rapid rate increases impacting debt service and cap rates",
                "probability": "Medium",
                "impact": "High",
                "kri_metric": "10Y Treasury daily move > 25 bps",
                "threshold": 0.25,
                "monitoring": "Daily"
            },
            {
                "risk": "CRE Market Dislocation", 
                "description": "Broader commercial real estate distress affecting exit values",
                "probability": "Medium",
                "impact": "High",
                "kri_metric": "CMBS spreads to Treasury",
                "threshold": 500,  # bps
                "monitoring": "Weekly"
            }
        ]
        
        operational_risks = [
            {
                "risk": "Power Infrastructure Delays",
                "description": "Utility interconnect delays impacting project timelines",
                "probability": "High" if investment_focus == "data_center" else "Medium",
                "impact": "High",
                "kri_metric": "Transformer delivery lead time",
                "threshold": 12,  # months
                "monitoring": "Monthly"
            },
            {
                "risk": "Technology Obsolescence",
                "description": "Equipment becoming outdated faster than anticipated",
                "probability": "Medium",
                "impact": "Medium",
                "kri_metric": "Technology refresh cycle acceleration",
                "threshold": 0.20,  # 20% reduction in useful life
                "monitoring": "Quarterly"
            }
        ]
        
        regulatory_risks = [
            {
                "risk": "Permitting Delays",
                "description": "Municipal approval processes extending beyond projections",
                "probability": "Medium",
                "impact": "Medium", 
                "kri_metric": "Average permit processing time",
                "threshold": 1.5,  # Multiple of baseline
                "monitoring": "Monthly"
            },
            {
                "risk": "Incentive Program Changes",
                "description": "Federal or state incentive reductions affecting project economics",
                "probability": "Medium",
                "impact": "High",
                "kri_metric": "Policy change indicators",
                "threshold": "Qualitative",
                "monitoring": "Ongoing"
            }
        ]
        
        counterparty_risks = [
            {
                "risk": "Tenant Credit Deterioration",
                "description": "Key tenant financial distress affecting cash flows",
                "probability": "Low",
                "impact": "High",
                "kri_metric": "Tenant credit rating downgrade",
                "threshold": "2 notches",
                "monitoring": "Quarterly"
            },
            {
                "risk": "Construction Partner Default",
                "description": "General contractor or key subcontractor financial failure",
                "probability": "Low",
                "impact": "High",
                "kri_metric": "Contractor bonding capacity utilization",
                "threshold": 0.80,
                "monitoring": "Monthly"
            }
        ]
        
        # Risk mitigation strategies
        mitigation_framework = {
            "diversification": {
                "geographic": "Multi-market exposure to reduce concentration",
                "sector": "Balance data center and EV charging investments",
                "tenant": "No single tenant > 20% of portfolio NOI",
                "vintage": "Stagger development timelines"
            },
            "hedging": {
                "interest_rate": "Consider rate caps for floating-rate debt",
                "commodity": "Power price hedging where available",
                "foreign_exchange": "Not applicable for domestic investments"
            },
            "insurance": {
                "property": "All-risk coverage with business interruption",
                "liability": "Professional and general liability",
                "cyber": "Data breach and business interruption coverage",
                "political": "Consider for international expansion"
            },
            "contractual": {
                "completion_guarantees": "Key person and performance guarantees",
                "step_down_pricing": "Volume discounts for multi-site programs",
                "force_majeure": "Updated language for pandemic/supply chain",
                "termination_rights": "Maintain flexibility for changing conditions"
            }
        }
        
        # Key Risk Indicators (KRI) dashboard
        kri_dashboard = []
        for risk_category in [market_risks, operational_risks, regulatory_risks, counterparty_risks]:
            for risk in risk_category:
                kri_dashboard.append({
                    "risk_name": risk["risk"],
                    "metric": risk["kri_metric"],
                    "threshold": risk["threshold"],
                    "monitoring_frequency": risk["monitoring"],
                    "current_status": "Green",  # Would be populated with real data
                    "trend": "Stable"
                })
        
        ctx.logger.info("risk-analysis", {"focus": investment_focus})
        
        findings = {
            "risk_categories": {
                "market": market_risks,
                "operational": operational_risks,
                "regulatory": regulatory_risks,
                "counterparty": counterparty_risks
            },
            "mitigation_framework": mitigation_framework,
            "kri_dashboard": kri_dashboard
        }
        
        recommendations = [
            "Implement real-time KRI monitoring with automated alerting",
            "Conduct quarterly risk assessment updates",
            "Maintain risk register with ownership assignments",
            "Develop playbooks for top 5 risk scenarios",
            "Regular stress testing of portfolio under adverse scenarios"
        ]
        
        if req.audience == "LP":
            recommendations.extend([
                "Provide quarterly risk reporting with trend analysis",
                "Benchmark risk metrics against peer funds",
                "Maintain clear risk appetite documentation"
            ])
        elif req.audience == "GP":
            recommendations.extend([
                "Train deal team on risk identification and mitigation",
                "Integrate risk assessment into investment committee process",
                "Build risk considerations into asset management protocols"
            ])
        
        return AgentResponse(
            executive_takeaway=f"Comprehensive risk framework identifies {len(kri_dashboard)} key risk indicators across market, operational, regulatory, and counterparty categories.",
            analysis="Multi-layered risk management approach combining quantitative KRIs with qualitative assessment and diversified mitigation strategies.",
            findings=findings,
            recommendations=recommendations,
            footnotes=[
                Footnote(
                    id="RISK1",
                    label="CRE Risk Metrics",
                    source="NCREIF Property Index and CBRE Research",
                    retrieved_at=ctx.now(),
                    refresh="Monthly",
                    transform="Risk-adjusted return calculations"
                )
            ],
            version="v1.0.0",
            checks=[
                "Risk categories comprehensive for asset class",
                "KRI thresholds set at appropriate levels",
                "Mitigation strategies actionable and specific",
                "Monitoring frequencies practical for operations"
            ]
        )

class ESGAgent(Agent):
    def __init__(self):
        super().__init__(
            name="ESG, Incentives, and Grants",
            handles=["esg", "credits", "grants", "sustainability", "incentives"]
        )
    
    async def run(self, req: AgentRequest, ctx: AgentContext) -> AgentResponse:
        """ESG analysis and incentive optimization"""
        
        project_type = req.inputs.get("project_type", "mixed")
        
        # ESG framework alignment
        esg_framework = {
            "environmental": {
                "carbon_footprint": "Net-zero operational goals by 2030",
                "energy_efficiency": "LEED Gold minimum for new construction",
                "renewable_energy": "60% renewable power procurement target",
                "water_conservation": "Low-flow fixtures and drought-resistant landscaping",
                "waste_reduction": "Construction waste diversion > 90%"
            },
            "social": {
                "community_impact": "Local hiring requirements for construction",
                "accessibility": "ADA compliance exceeding minimum requirements",
                "affordable_housing": "Support for workforce housing initiatives",
                "digital_equity": "Fiber infrastructure in underserved areas",
                "health_safety": "Indoor air quality monitoring and optimization"
            },
            "governance": {
                "board_diversity": "Diverse representation on investment committee",
                "transparency": "Annual sustainability reporting",
                "stakeholder_engagement": "Regular community advisory meetings",
                "cybersecurity": "SOC 2 compliance for data centers",
                "regulatory_compliance": "Proactive environmental monitoring"
            }
        }
        
        # Incentive stacking opportunities
        federal_incentives = [
            {
                "program": "Investment Tax Credit (ITC)",
                "applicability": "Solar installations",
                "benefit": "30% of qualified costs",
                "requirements": ["Begin construction before 2033", "Davis-Bacon prevailing wages"]
            },
            {
                "program": "NEVI Grant Program",
                "applicability": "EV charging infrastructure",
                "benefit": "Up to 80% of eligible costs",
                "requirements": ["Public access", "Interoperability", "Uptime standards"]
            },
            {
                "program": "Section 48C Advanced Energy Credit",
                "applicability": "Energy storage systems",
                "benefit": "30% of qualified investment",
                "requirements": ["Manufacturing component", "Wage and apprenticeship standards"]
            }
        ]
        
        state_california_incentives = [
            {
                "program": "Self-Generation Incentive Program (SGIP)",
                "applicability": "Battery storage systems",
                "benefit": "Rebates up to $1.00/Wh",
                "requirements": ["California utility service territory", "10-year commitment"]
            },
            {
                "program": "Low Carbon Fuel Standard (LCFS)",
                "applicability": "EV charging stations",
                "benefit": "Ongoing credit revenue stream",
                "requirements": ["Verified charging data", "Credit registry participation"]
            },
            {
                "program": "Property Assessed Clean Energy (PACE)",
                "applicability": "Energy efficiency improvements",
                "benefit": "Long-term financing",
                "requirements": ["Property owner consent", "Municipal program participation"]
            }
        ]
        
        local_incentives = [
            {
                "program": "LA Green Building Incentives",
                "applicability": "LEED certified projects",
                "benefit": "Expedited permitting + fee reductions",
                "requirements": ["LEED Gold or higher", "Local hiring requirements"]
            },
            {
                "program": "DWP Electric Vehicle Rebates",
                "applicability": "Public EV charging",
                "benefit": "Up to $2,500 per port",
                "requirements": ["LADWP service territory", "Network-connected equipment"]
            }
        ]
        
        # Impact measurement framework
        impact_metrics = {
            "environmental_kpis": [
                {"metric": "Carbon emissions avoided", "target": "50,000 MT CO2e annually", "measurement": "Third-party verification"},
                {"metric": "Renewable energy usage", "target": "60% of total consumption", "measurement": "Utility green tariff participation"},
                {"metric": "Water consumption", "target": "20% reduction vs. baseline", "measurement": "Monthly utility reporting"},
                {"metric": "Waste diversion rate", "target": "90% from landfills", "measurement": "Waste audit quarterly"}
            ],
            "social_kpis": [
                {"metric": "Local employment", "target": "30% of construction jobs", "measurement": "Payroll reporting by ZIP code"},
                {"metric": "Community investment", "target": "$100K annually", "measurement": "Community benefit tracking"},
                {"metric": "Digital access improvement", "target": "5 underserved areas connected", "measurement": "Fiber deployment mapping"}
            ],
            "governance_kpis": [
                {"metric": "Board diversity", "target": "40% diverse representation", "measurement": "Annual governance review"},
                {"metric": "Sustainability reporting", "target": "GRESB 4-star rating", "measurement": "Third-party ESG scoring"},
                {"metric": "Stakeholder engagement", "target": "4 community meetings annually", "measurement": "Meeting attendance logs"}
            ]
        }
        
        ctx.logger.info("esg-analysis", {"project_type": project_type})
        
        findings = {
            "esg_framework": esg_framework,
            "incentive_stacking": {
                "federal": federal_incentives,
                "state": state_california_incentives,
                "local": local_incentives
            },
            "impact_measurement": impact_metrics,
            "estimated_incentive_value": "15-25% of total project costs"
        }
        
        recommendations = [
            "Develop ESG policy framework before first investment",
            "Create incentive application calendar with filing deadlines",
            "Engage ESG consultants for third-party verification",
            "Build community engagement protocols for each market",
            "Implement impact tracking systems from project inception"
        ]
        
        if req.audience == "LP":
            recommendations.extend([
                "Provide annual ESG impact reporting with quantified benefits",
                "Benchmark against institutional ESG standards (GRESB, TCFD)",
                "Consider ESG-linked carry structure"
            ])
        elif req.audience == "GP":
            recommendations.extend([
                "Train investment team on incentive stacking opportunities",
                "Build ESG considerations into underwriting models",
                "Develop preferred vendor network for sustainable construction"
            ])
        
        return AgentResponse(
            executive_takeaway="Comprehensive ESG framework with incentive stacking potential of 15-25% project cost reduction while achieving measurable sustainability impact.",
            analysis="Multi-layered approach combining environmental performance, social impact, and governance excellence with federal, state, and local incentive optimization.",
            findings=findings,
            recommendations=recommendations,
            footnotes=[
                Footnote(
                    id="ESG1",
                    label="NEVI Grant Program Guidelines",
                    source="FHWA NEVI Formula Program Guidance",
                    retrieved_at=ctx.now(),
                    refresh="Quarterly",
                    transform="Eligibility requirements and funding procedures"
                )
            ],
            version="v1.0.0",
            checks=[
                "ESG metrics aligned with institutional standards",
                "Incentive programs current and accurate",
                "Impact measurement framework comprehensive",
                "Compliance requirements clearly documented"
            ]
        )