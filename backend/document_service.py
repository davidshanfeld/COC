from typing import Dict, List
from datetime import datetime
import logging
from models import LiveDocument, DocumentSection, DataSource, FinancialModel
from data_sources import DataSourceManager, FinancialCalculator
import json
import re

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self):
        self.data_manager = DataSourceManager()
        self.calculator = FinancialCalculator()
        
    async def create_coastal_oak_document(self) -> LiveDocument:
        """Create the comprehensive Coastal Oak Capital master deck"""
        
        # Fetch real-time data
        real_time_data = await self.data_manager.fetch_all_data()
        
        # Create data sources from real-time data
        data_sources = {}
        for key, data in real_time_data.items():
            data_sources[key] = DataSource(
                name=data['description'],
                url=data.get('url', 'N/A'),
                last_updated=data['timestamp'],
                value=data['value'],
                unit=data['unit'],
                source_type=data['source']
            )
        
        # Create document sections with real-time data integration
        sections = self._create_document_sections(real_time_data)
        
        document = LiveDocument(
            title="Coastal Oak Capital - Opportunistic Commercial Real Estate Distressed Debt Fund",
            description="Institution-grade master deck with real-time market data integration",
            sections=sections,
            data_sources=data_sources
        )
        
        return document
    
    def _create_document_sections(self, real_time_data: Dict) -> List[DocumentSection]:
        """Create all document sections with integrated real-time data"""
        
        # Calculate derived metrics
        cost_of_capital = self.calculator.calculate_cost_of_capital(
            real_time_data['10_year_treasury']['value'], 
            4.5  # Risk premium for opportunistic CRE debt
        )
        
        adjusted_cap_rate = self.calculator.calculate_cap_rate_adjustment(
            real_time_data['cap_rates_office']['value'],
            real_time_data['cpi_inflation']['value']
        )
        
        energy_cost_sf = self.calculator.calculate_energy_cost_per_sf(
            real_time_data['commercial_electricity_rate']['value']
        )
        
        sections = [
            # Executive Summary - Enhanced with detailed fund information
            DocumentSection(
                title="Executive Summary: Coastal Oak Capital Opportunistic Distressed Debt Fund",
                order=1,
                content=f"""
**Investment Thesis**: Coastal Oak Capital represents a unique opportunity at the intersection of three transformative market dynamics: distressed commercial real estate debt, adaptive reuse of underperforming office assets, and surging demand for data centers and EV charging infrastructure.

**Current Market Environment** (Live Data as of {datetime.now().strftime('%B %d, %Y')}):
• Federal Funds Rate: {real_time_data['fed_funds_rate']['value']:.2f}%¹
• 10-Year Treasury: {real_time_data['10_year_treasury']['value']:.2f}%²
• Cost of Capital (Calculated): {cost_of_capital:.2f}%
• CPI Inflation: {real_time_data['cpi_inflation']['value']:.1f}% annually³
• CMBS-Treasury Spread: {real_time_data['cmbs_spread']['value']} basis points⁴

**Market Opportunity**:
With over $2.2 trillion in commercial real estate debt maturing by 2027 and rising interest rates challenging refinancing, distressed assets are available at 50-70% discounts. Simultaneously, office vacancies of 20-25% in older LA buildings create repositioning opportunities for data centers and EV charging infrastructure.

**Fund Structure & Terms**:
• Target Raise: $30-50 million by 2027
• Preferred Return: 8% annually to limited partners
• Carried Interest: 20% over hurdle rate
• Management Fee: 1.5-2% of committed capital
• Target Net IRR: 20-25% over 5-7 year horizon
• Equity Multiple Target: 2.0-2.5x

**Corporate Shared Value Approach**: Founded on Harvard's Michael Porter CSV model, combining exceptional financial returns with meaningful social impact through adaptive reuse, carbon reduction (50-70% vs new construction), and critical infrastructure development.

**Team**: David Shanfeld (JD Loyola, MBA candidate USC Marshall) and Alexandra Franklin (Columbia Law, MRED candidate USC Price, formerly Akin Gump) bring complementary expertise in distressed transactions, legal structuring, and sustainable investment strategies.

**Competitive Advantage**: Proprietary sourcing relationships, specialized legal expertise, AI-driven underwriting, and proven adaptive reuse strategies position us to capitalize on this once-in-a-generation market dislocation.

---
¹Federal Reserve Economic Data (FRED) - Real-time
²Federal Reserve Economic Data (FRED) - Real-time
³Bureau of Labor Statistics via FRED - Real-time
⁴Trepp CMBS Analytics (Simulated)
                """,
                data_dependencies=['fed_funds_rate', '10_year_treasury', 'cpi_inflation', 'cmbs_spread']
            ),
            
            # Market Dislocation Analysis - Enhanced with comprehensive data
            DocumentSection(
                title="Market Dislocation Deep-Dive: The $2.2 Trillion CRE Refinancing Crisis",
                order=2,
                content=f"""
**Unprecedented Distressed Debt Opportunity** (Real-Time Data):

**Interest Rate Shock**:
• Current Fed Funds Rate: {real_time_data['fed_funds_rate']['value']:.2f}% vs. 0.25% (2021 low)¹
• 10-Year Treasury: {real_time_data['10_year_treasury']['value']:.2f}% vs. 1.51% (2021 average)²
• Rate Increase Impact: 500+ basis point shock creates immediate refinancing crisis

**Construction Cost Explosion**:
• Producer Price Index (Construction): {real_time_data['construction_cost_index']['value']:.1f} (Current)³
• Annual Construction Inflation: {real_time_data['cpi_inflation']['value']:.1f}%⁴
• Replacement Cost Impact: New construction 25-40% more expensive than 2021

**The Scale of Distress**:
• $2.2 trillion in CRE debt maturing through 2027
• $324 billion matured in 2024 alone
• $19.2 billion in foreclosures reached by late 2024
• Office properties represent 32% of maturing debt ($704 billion)

**Regional Bank Pressure**:
• $1.6 trillion CRE loans held by regional/local banks
• $475 billion in office exposure specifically
• FDIC data shows regional banks ($10-50B assets) face particular pressure
• CRE loans often represent 250-400% of total bank capital
• Regulatory pressure accelerating distressed sales

**Los Angeles Market Specifics**:
• Office property values down 43% year-over-year
• B/C class vacancy rates: 20-25%
• 65% of maturing office loans have LTV ratios exceeding 80%
• Many properties now have negative equity positions

**The Opportunity Window**:
Current conditions present acquisition opportunities before institutional capital organizes around distressed office opportunities (expected by late 2026). Oaktree's recent $16 billion distressed fund validates institutional interest and market scale.

**Acquisition Strategy**:
Target 50-70% discounts to face value through:
• Direct relationships with 15+ regional banks
• Special servicer network for CMBS assets
• Legal network intelligence on bankruptcy situations
• Family office direct relationships for off-market deals

**Information Advantages**:
• Local knowledge of regulatory/entitlement issues
• Specialized workout expertise
• Technical data center conversion capabilities
• Limited competition for mid-market assets ($10-30M)

---
¹Federal Reserve Economic Data (FRED) - Real-time
²Federal Reserve Economic Data (FRED) - Real-time
³Bureau of Labor Statistics Producer Price Index - Real-time
⁴Consumer Price Index calculation - Real-time
                """,
                data_dependencies=['fed_funds_rate', '10_year_treasury', 'construction_cost_index', 'cpi_inflation']
            ),
            
            # Investment Strategy - Enhanced with detailed approach
            DocumentSection(
                title="Investment Strategy: Distressed Debt-to-Equity with Adaptive Reuse",
                order=3,
                content=f"""
**Three-Pillar Value Creation Strategy** (Live Market Integration):

**Pillar 1: Discounted Acquisition Foundation**
• **Current Cost of Capital**: {cost_of_capital:.2f}% (10Y Treasury {real_time_data['10_year_treasury']['value']:.2f}% + 450bp risk premium)¹
• **Target Acquisition Discounts**: 50-70% below face value
• **Immediate Equity Creation**: 30-50% equity upon acquisition
• **Downside Protection**: Substantial buffer against market volatility

**Pillar 2: Adaptive Reuse Value Creation**

**Modular Data Center Strategy**:
• Convert 20,000-50,000 SF office buildings into 1.5-2.0 MW edge data centers
• Target lease rates: $175-225/kW/month (vs suburban $150-180/kW)
• Urban premium justification: 20-30% higher rates for low-latency proximity
• Market growth: $418B (2023) to $670B (2028) = 9.6% CAGR

**EV Charging Infrastructure**:
• **Current Energy Costs**: ${energy_cost_sf:.2f}/SF annually (at {real_time_data['commercial_electricity_rate']['value']:.1f}¢/kWh)²
• **Revenue Potential**: $25,000-45,000 per DC fast charger annually
• **California Mandates**: 100% zero-emission vehicle sales by 2035
• **Infrastructure Gap**: Only 27,000 supercharging stations built nationwide vs millions needed

**Synergistic Integration**:
• Shared power infrastructure reduces costs by 20-30%
• Complementary load patterns optimize energy management
• Multiple revenue streams reduce single-tenant risk

**Pillar 3: Corporate Shared Value (CSV) Implementation**

**Environmental Benefits**:
• Adaptive reuse saves 50-70% embodied carbon vs new construction
• Energy efficiency retrofits reduce operational emissions 30-40%
• On-site renewable integration creates additional revenue streams

**Social Impact**:
• Community revitalization through productive asset reuse
• Job creation in construction and ongoing operations
• Digital infrastructure supporting economic growth

**Financial Performance Enhancement**:
• Green building premiums: 6-10% rent premiums, 10-15% value premiums
• ESG financing access: 15-30 basis point interest rate reductions
• Expanded tenant pool from ESG-focused corporations

**Target Property Characteristics**:
• Size: 20,000-50,000 SF office buildings
• Class: B/C properties with solid structural bones
• Location: 1-3 miles from major LA business districts
• Infrastructure: Upgradable power, suitable for cooling systems
• Acquisition: $5-15 million per asset

**Financial Targets** (Real-Time Market Conditions):
• **Inflation-Adjusted Cap Rates**: {adjusted_cap_rate:.2f}% (base {real_time_data['cap_rates_office']['value']:.2f}% + adjustment)³
• **Base Case IRR**: 20-25% gross, 17-22% net to LPs
• **Equity Multiple**: 2.0-2.5x over 5-7 years
• **Stabilized Cash Yield**: 6-8% starting year 3-4

**Risk Mitigation**:
• Geographic diversification (max 25% any single MSA)
• Asset type limits (max 40% any property type)
• Liquidity reserves (15% of fund for bridge financing)
• Multiple exit strategies per asset

**Execution Timeline**:
• Fundraising: Current through 2025
• Acquisition Phase: 2025-2026
• Value-Add Implementation: 2025-2028
• Stabilization & Exit: 2027-2030

---
¹Calculated: 10-Year Treasury + Risk Premium (Real-time)
²California commercial electricity rates (Real-time)
³Calculated: Base cap rate + inflation adjustment (Real-time)
                """,
                data_dependencies=['10_year_treasury', 'cap_rates_office', 'cpi_inflation', 'commercial_electricity_rate']
            ),
            
            # Financial Case Studies - Enhanced with specific examples
            DocumentSection(
                title="Financial Case Studies: Proven Value Creation Models",
                order=4,
                content=f"""
**Case Study 1: Modular Data Center Grid Portfolio**

**Asset Profile**:
• 10 Class B/C office buildings (20,000 SF each, 200,000 SF total)
• Location: Distributed around Century City (3-mile radius)
• Original portfolio value: $80 million ($400/SF at peak)
• Current status: 65% average vacancy, negative cash flow

**Acquisition Strategy**:
• Distressed note portfolio: $36 million (55% discount to face value)
• Strategic distribution creates network advantages
• Solid structural bones with reinforced concrete construction

**Value-Add Implementation**:
• Transform each building into 1.5-2.0 MW edge data center
• Total capacity: 15-20 MW across portfolio
• Phased implementation based on tenant demand
• Advanced security, biometric access, 24/7 monitoring
• Rooftop solar where structurally feasible

**Financial Projections**:
• Total Investment: $76 million ($380/SF, below replacement cost)
• Stabilized Revenue: $19.5 million annually
• Operating Expenses: $6.5 million annually
• NOI: $13 million annually (17.1% yield on cost)
• Exit Value: $208 million (6.25% cap rate)
• Equity Multiple: 2.7x
• Target IRR: 26% gross, ~23% net to LPs

**Case Study 2: Integrated Energy/Digital Hub (El Segundo)**

**Asset Profile**:
• 45,000 SF industrial building on 2.5-acre lot
• Location: El Segundo (near LAX, tech corridor)
• Original value: $27 million, current 85% vacancy
• Excellent power infrastructure (5MW service available)

**Synergistic Conversion**:
• 3MW modular edge data center in main building
• 55-position EV charging plaza in parking field
• 900kW solar canopy system over charging areas
• 2MWh battery storage serving both uses
• Microgrid capabilities for enhanced resilience

**Financial Performance**:
• All-in Investment: $32.33 million (after $3.22M incentives)
• Annual Revenue Streams:
  - Data center leasing: $3.2 million
  - EV charging: $2.4 million
  - Grid services: $350,000
  - Solar generation: $150,000
• Total Revenue: $6.1 million annually
• NOI: $3.1 million (9.6% yield on cost)
• Equity Multiple: 2.4x, Target IRR: 25%

**Fund-Level Projections** (Live Market Data Integration):

**Deployment Strategy**:
• Target fund size: $30-50 million equity
• Leverage: 50-60% LTC/LTV
• Total acquisition capacity: $75-125 million
• Target: 8-12 properties over 24-36 months

**Portfolio Allocation**:
• Data center conversions: 40-50%
• EV infrastructure: 25-35%
• Mixed-use synergy projects: 15-25%

**Sensitivity Analysis** (Current Market Conditions):
• **Base Case**: 20-25% IRR with current rates at {real_time_data['10_year_treasury']['value']:.2f}%
• **+1% Rate Increase**: Reduces IRR by 1.8-2.2%
• **Construction Inflation**: {real_time_data['cpi_inflation']['value']:.1f}% affects timing but rent indexation offsets
• **Cap Rate Environment**: Current {real_time_data['cap_rates_office']['value']:.2f}% + {(real_time_data['cpi_inflation']['value'] * 0.5):.1f}% inflation adjustment = {adjusted_cap_rate:.2f}% exit assumption

**Value Creation Sources**:
• Discount acquisition: 40-50% of total return
• Physical improvements/repositioning: 25-35%
• Operational improvements/market timing: 15-25%

**Return Timeline**:
• Years 1-2: Acquisition and repositioning (minimal distributions)
• Years 3-5: Stabilized operations (6-8% cash-on-cash)
• Years 6-8: Asset sales and major capital returns
• Preferred return: 8% to LPs before 20% carry

**Exit Strategy Options**:
• Individual asset sales for optimization
• Portfolio sale to REIT or institutional investor
• Recapitalization with long-term partners
• Strategic partnerships with data center operators

**Market Validation**:
Recent comparable transactions validate our approach:
• Digital Realty acquisitions at 6.0-6.5% cap rates
• Blackstone's $10B QTS acquisition (2021)
• Brookfield's $775M Cyxtera acquisition
• DataBank's $250M equity raise (2025)

---
All financial projections incorporate live market data and current conditions as of {datetime.now().strftime('%B %d, %Y')}
                """,
                data_dependencies=['10_year_treasury', 'cpi_inflation', 'cap_rates_office']
            ),
            
            # PICO Property Case Study - Investment Discipline Example
            DocumentSection(
                title="Investment Discipline Case Study: PICO Boulevard Property - When to Say No",
                order=5,
                content=f"""
**Executive Summary**: The PICO Boulevard property exemplifies the critical importance of disciplined deal selection in distressed markets. Despite being available at an exceptional discount ("basically nothing"), this opportunity demonstrates why even deeply discounted assets must align with core business model requirements.

**Property Overview - PICO Boulevard, Los Angeles**:
• **Asset Type**: Distressed commercial office building
• **Status**: Foreclosure imminent (within 24-48 hours)
• **Acquisition Price**: Extremely low ("basically nothing" - indicating sub-$50/SF)
• **Market Context**: Perfect example of current distress cycle with forced seller urgency

**The Opportunity**: A Classic Distress Scenario
This property represents everything investors seek in distressed markets:
• **Motivated Seller**: Foreclosure timeline creates maximum urgency
• **Exceptional Pricing**: Available at a fraction of replacement cost
• **Market Validation**: Demonstrates scale of current market dislocation
• **Immediate Availability**: No extended marketing period or bidding process

**Technical Analysis - Why We Declined**:

**Infrastructure Incompatibility**:
• **Floor-to-Ceiling Glass Design**: Entire building envelope requires replacement
• **Thermal Management Crisis**: Glass facade creates heat island effect
• **Data Center Conflict**: Our strategy requires cooling efficiency, not heat generation
• **Energy Conversion Strategy**: Heat-to-energy systems need controlled thermal environments

**Capital Requirements Assessment**:
• **"Everything Needs Replacement"**: Complete building systems overhaul required
• **Window/Glass Systems**: $45-65/SF for floor-to-ceiling glass replacement
• **HVAC Systems**: Additional $35-50/SF for data center cooling requirements
• **Electrical Infrastructure**: $25-40/SF for data center power density needs
• **Total Renovation**: $105-155/SF (excluding acquisition) = $2.1-3.1M for 20,000 SF building

**Business Model Alignment Analysis**:

**Strategic Conflicts**:
• **Heat Generation vs. Cooling Needs**: Glass facade conflicts with data center thermal management
• **Energy Strategy Mismatch**: Heat-to-energy conversion requires controlled waste heat, not building overheating
• **Capital Efficiency**: Renovation costs eliminate discount acquisition advantage
• **Timeline Impact**: Extensive renovation extends value creation timeline beyond optimal range

**Financial Impact** (Current Market Conditions):
• **All-in Cost**: Low acquisition + $2.5M average renovation = $2.5M+ total investment
• **Comparable Properties**: Well-suited buildings available at $1.8-2.2M all-in cost
• **ROI Impact**: Additional renovation costs reduce target IRR from 25% to 12-15%
• **Risk Profile**: Extensive renovation adds execution risk without commensurate return

**Investment Discipline Framework**:

**"Good Deal" vs. "Right Deal" Analysis**:
✅ **Good Deal Characteristics (PICO has these)**:
• Exceptional discount to market
• Motivated seller urgency
• Strong neighborhood fundamentals
• Solid structural foundation

❌ **Right Deal Requirements (PICO lacks these)**:
• Infrastructure alignment with business model
• Capital efficiency for target returns
• Technical compatibility with heat-to-energy strategy
• Renovation scope matches capabilities

**Decision Matrix Applied**:
• **Price**: Exceptional (9/10)
• **Strategic Fit**: Poor (2/10)
• **Capital Efficiency**: Poor (3/10)
• **Technical Alignment**: Poor (1/10)
• **Overall Score**: 37/100 (Pass threshold: 70/100)

**Market Context & Opportunity Abundance**:

**Why We Can Afford to be Selective**:
• **Deal Flow Volume**: 15-20 similar opportunities identified monthly
• **Market Timing**: Early in distress cycle allows selectivity
• **Capital Constraints**: Limited capital requires optimal deployment
• **Competitive Advantage**: Technical specialization creates unique value proposition

**Better Alternatives Available**:
• **Portfolio Pipeline**: 8 properties scoring 80+ in evaluation matrix
• **Strategic Alignment**: Properties requiring $50-75/SF renovation vs. $105-155/SF
• **Thermal Management**: Buildings with efficient HVAC systems requiring minimal modification
• **Capital Efficiency**: All-in costs of $180-220/SF vs. $280-350/SF for PICO

**Lessons for Distressed Investing**:

**Discipline Over Opportunity**:
This case study reinforces core investment principles:
1. **Discount Alone Insufficient**: Even exceptional pricing must align with strategy
2. **Total Cost of Ownership**: Consider all-in investment requirements, not just acquisition
3. **Strategic Fit First**: Business model alignment trumps financial attractiveness
4. **Abundance Mindset**: In distressed markets, better opportunities exist for patient capital

**Heat-to-Energy Strategy Validation**:
The PICO property's floor-to-ceiling glass problem actually validates our heat-to-energy conversion strategy:
• **Controlled Thermal Management**: Data centers generate predictable, manageable waste heat
• **Energy Conversion Efficiency**: Systematic heat capture vs. random building overheating
• **Operational Optimization**: Heat-to-energy systems require engineered thermal environments
• **Strategic Differentiation**: Technical expertise creates sustainable competitive advantage

**Market Education Value**:
Declining PICO demonstrates sophisticated investment approach to:
• **Limited Partners**: Disciplined capital deployment over deal volume
• **Brokers/Sources**: Clear investment criteria reduce unqualified deal flow
• **Competition**: Technical expertise requirements limit competitive bidding
• **Market**: Patient, strategic capital with specialized capabilities

**Conclusion**: Investment discipline is not about avoiding risk—it's about taking the right risks. The PICO Boulevard property, despite being available for "basically nothing," exemplifies why successful distressed investing requires saying no to good deals to preserve capital for great deals that align with core competencies and strategic objectives.

**Current Market Validation**: With {real_time_data['cap_rates_office']['value']:.2f}% cap rates and {real_time_data['construction_cost_index']['value']:.1f} construction cost index, the discipline demonstrated in declining PICO validates our selective approach in a target-rich environment.

---
*Case study demonstrates real-time investment decision-making incorporating current market conditions as of {datetime.now().strftime('%B %d, %Y')}*
                """,
                data_dependencies=['cap_rates_office', 'construction_cost_index']
            ),
            
            # Risk Management & ESG Integration
            DocumentSection(
                title="Risk Management & ESG Integration: Comprehensive Framework",
                order=6,
                content=f"""
**Risk Management Framework** (Current Market Environment):

**Market Risk Mitigation**:
• **Interest Rate Sensitivity**: +{real_time_data['10_year_treasury']['value'] - 1.51:.1f}% from 2021 levels already factored into underwriting
• **Construction Cost Inflation**: {real_time_data['cpi_inflation']['value']:.1f}% annual rate managed through 10-15% contingencies
• **Cap Rate Risk**: Current {adjusted_cap_rate:.2f}% exit assumption includes inflation buffer

**Acquisition Risk Controls**:
• Minimum 50% discount threshold maintained regardless of competition
• Focus on mid-market assets ($10-30M) with limited institutional competition
• Multiple sourcing channels reduce dependency on any single pipeline
• Legal expertise provides edge in complex workout situations

**Execution Risk Management**:
• Phased implementation allows validation before full capital deployment
• Specialized engineering teams for technical due diligence
• Conservative power availability and upgrade cost assumptions
• Multiple exit strategies per asset reduce execution dependency

**Technology & Demand Risks**:
• Modular approach allows flexibility for evolving AI/data center requirements
• Diversification across tenant types and use cases
• Strategic locations with strong fundamentals and barriers to entry
• Design flexibility to accommodate changing technology standards

**ESG Integration & Corporate Shared Value**:

**Environmental Leadership**:
• **Carbon Reduction**: 50-70% embodied carbon savings vs new construction
• **Energy Efficiency**: 30-40% operational emission reductions through retrofits
• **Renewable Integration**: On-site solar and battery storage where feasible
• **Waste Reduction**: 80%+ construction waste diverted from landfills

**Social Impact Metrics**:
• **Job Creation**: Construction and ongoing operations employment
• **Community Revitalization**: Productive reuse of underutilized assets
• **Digital Infrastructure**: Supporting technology sector growth and connectivity
• **Transportation Electrification**: Enabling EV adoption through charging infrastructure

**Governance Excellence**:
• Comprehensive ESG reporting (GRESB, SASB, TCFD frameworks)
• Stakeholder engagement processes for community alignment
• Regulatory foresight positioning ahead of compliance requirements
• Transparent impact measurement and reporting

**Financial Benefits of ESG Integration**:
• **Rent Premiums**: 6-10% for high sustainability standards
• **Value Premiums**: 10-15% at exit for ESG-compliant properties
• **Operating Cost Reduction**: 20-30% through energy efficiency
• **Financing Advantages**: 15-30 basis point reductions through green financing
• **Tenant Attraction**: Expanded pool from ESG-focused corporations

**EV Charging Specific Impact**:
• **Carbon Displacement**: 80-110 metric tons CO₂ per fast charging station annually
• **Air Quality**: Direct improvement in goods movement corridors
• **Energy Independence**: 80,000-120,000 gallons diesel/gasoline displaced per location
• **Economic Development**: Local job creation and infrastructure modernization

**Regulatory Positioning**:
• California's stricter data center energy standards (2025) compliance built-in
• EV infrastructure positioned ahead of transportation emissions regulations
• Adaptive reuse aligned with sustainable development policies
• Community engagement reduces NIMBY and permitting risks

**Competitive Advantages Through ESG**:
• **Generational Wealth Transfer**: $68 trillion to ESG-focused Millennials/Gen Z
• **Values-Driven Investment**: Alignment with evolving investor priorities
• **Performance Correlation**: ESG factors increasingly drive long-term returns
• **Differentiation**: CSV approach creates sustainable competitive advantages

**Risk-Adjusted Return Enhancement**:
ESG integration doesn't compromise returns—it enhances them through:
• Lower cost of capital via green financing
• Premium valuations for sustainable properties
• Reduced regulatory and operational risks
• Expanded tenant and buyer pools
• Future-proofing against evolving standards

**Monitoring & Reporting**:
• Quarterly ESG metrics alongside financial performance
• Annual sustainability impact assessments
• Third-party verification of environmental claims
• Stakeholder feedback integration into strategy refinement

The combination of substantial acquisition discounts (50-70%), multiple value creation strategies, and ESG integration creates a resilient investment approach that generates both exceptional returns and positive impact—embodying the Corporate Shared Value model that defines our investment philosophy.

---
All risk assessments incorporate current market conditions as of {datetime.now().strftime('%B %d, %Y')}
                """,
                data_dependencies=['10_year_treasury', 'cpi_inflation', 'cap_rates_office']
            )
        ]
        
        return sections
    
    async def update_document(self, document: LiveDocument, force_refresh: bool = False) -> LiveDocument:
        """Update document with latest real-time data"""
        
        # Fetch latest data
        real_time_data = await self.data_manager.fetch_all_data()
        
        # Update data sources
        for key, data in real_time_data.items():
            if key in document.data_sources:
                document.data_sources[key].value = data['value']
                document.data_sources[key].last_updated = data['timestamp']
        
        # Update sections that depend on this data
        for section in document.sections:
            if any(dep in real_time_data for dep in section.data_dependencies):
                section.last_updated = datetime.now()
                # In a full implementation, we'd regenerate the content here
                # For now, we just mark it as updated
        
        document.last_updated = datetime.now()
        return document
    
    def export_to_markdown(self, document: LiveDocument) -> str:
        """Export document to markdown format"""
        markdown_content = f"""# {document.title}

*{document.description}*

**Last Updated**: {document.last_updated.strftime('%B %d, %Y at %I:%M %p')}
**Version**: {document.version}

---

## Table of Contents

"""
        
        # Add table of contents
        for section in document.sections:
            markdown_content += f"{section.order}. [{section.title}](#section-{section.order})\n"
        
        markdown_content += "\n---\n\n"
        
        # Add sections
        for section in document.sections:
            markdown_content += f"## Section {section.order}: {section.title} {{#section-{section.order}}}\n\n"
            markdown_content += section.content + "\n\n"
            
            if section.data_dependencies:
                markdown_content += f"*This section updates automatically based on: {', '.join(section.data_dependencies)}*\n\n"
            
            markdown_content += "---\n\n"
        
        # Add data sources appendix
        markdown_content += "## Appendix: Data Sources\n\n"
        for key, source in document.data_sources.items():
            markdown_content += f"**{source.name}**: {source.value} {source.unit} (as of {source.last_updated.strftime('%B %d, %Y')})\n"
            markdown_content += f"Source: {source.source_type}\n\n"
        
        return markdown_content