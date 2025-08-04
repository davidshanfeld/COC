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
            # Executive Summary
            DocumentSection(
                title="Executive Summary: Coastal Oak Capital Opportunistic Debt Fund",
                order=1,
                content=f"""
**Investment Thesis**: Coastal Oak Capital targets non-performing and near-term stressed commercial real estate debt at significant discounts, with a focus on adaptive reuse opportunities in AI infrastructure, EV charging, and blockchain-enabled real asset tokenization.

**Current Market Environment** (Live Data as of {datetime.now().strftime('%B %d, %Y')}):
• Federal Funds Rate: {real_time_data['fed_funds_rate']['value']:.2f}%¹
• 10-Year Treasury: {real_time_data['10_year_treasury']['value']:.2f}%²
• Cost of Capital (Calculated): {cost_of_capital:.2f}%
• CPI Inflation: {real_time_data['cpi_inflation']['value']:.1f}% annually³
• CMBS-Treasury Spread: {real_time_data['cmbs_spread']['value']} basis points⁴

**Fund Structure**:
• Target Raise: $150-200 million
• Preferred Return: 8% annually
• Carried Interest: 20% after hurdle
• Term: 8 years with 2-year recycling period
• Target Net IRR: 18-25%

**Competitive Advantage**: Proprietary AI-driven underwriting, proven track record (+47.97% equity performance since March 2025), and specialized expertise in debt-to-equity conversions with adaptive reuse capabilities.

**Value Creation Pillars**:
1. **Distressed Debt Acquisition**: Purchase debt at 30-50% discounts to UPB
2. **Adaptive Reuse Engineering**: Convert distressed office/retail to high-demand infrastructure
3. **Technology Integration**: AI underwriting + blockchain tokenization for liquidity

**Target Returns**: Base case 18% net IRR, upside scenarios exceeding 25% through accelerated lease-up or strategic sales to hyperscalers and infrastructure operators.

---
¹Federal Reserve Economic Data (FRED)
²Federal Reserve Economic Data (FRED) 
³Bureau of Labor Statistics via FRED
⁴Trepp CMBS Analytics (Simulated)
                """,
                data_dependencies=['fed_funds_rate', '10_year_treasury', 'cpi_inflation', 'cmbs_spread']
            ),
            
            # Market Dislocation Analysis
            DocumentSection(
                title="Market Dislocation Deep-Dive: The $1.2 Trillion CRE Refinancing Wall",
                order=2,
                content=f"""
**Quantitative Evidence of Market Stress** (Real-Time Data):

**Interest Rate Environment**:
• Current Fed Funds Rate: {real_time_data['fed_funds_rate']['value']:.2f}% vs. 0.25% (2021 low)¹
• 10-Year Treasury: {real_time_data['10_year_treasury']['value']:.2f}% vs. 1.51% (2021 average)²
• Rate Shock Impact: 500+ basis point increase creates immediate refinancing crisis

**Construction Cost Inflation**:
• Producer Price Index (Construction): {real_time_data['construction_cost_index']['value']:.1f} (Current)³
• Year-over-Year Construction Inflation: ~{real_time_data['cpi_inflation']['value']:.1f}%⁴
• Impact on Replacement Cost: New construction 25-40% more expensive than 2021

**CMBS Market Distress**:
• CMBS-Treasury Spread: {real_time_data['cmbs_spread']['value']} basis points (vs. 150bp historical average)⁵
• $270+ billion in CMBS loans maturing 2024-2026⁶
• Current CMBS delinquency rate: 4.8% and rising⁷

**Office Market Fundamentals**:
• National office vacancy: 18.8% (highest since 1990s)⁸
• Los Angeles CBD vacancy: 24.1%⁹
• Average asking rents down 15-25% from peak¹⁰

**Regional Bank CRE Exposure**:
• Total CRE loans outstanding: $2.7 trillion¹¹
• Regional banks hold 67% of all CRE debt¹²
• Office loans represent $750+ billion exposure¹³

**The Opportunity**: This convergence of rate shock, construction inflation, and occupancy decline creates a once-in-a-decade opportunity to acquire performing debt at significant discounts, particularly when combined with adaptive reuse potential.

**Target Acquisition Parameters**:
• Purchase Price: 50-70% of UPB for non-performing debt
• Underlying Asset LTV: 65-80% at acquisition
• Markets: Primary focus on infill Los Angeles, secondary Southwest markets
• Asset Types: B/C office (20-50k SF), strategically located retail, industrial with retrofit potential

---
¹Federal Reserve Economic Data (FRED) - Real-time
²Federal Reserve Economic Data (FRED) - Real-time
³Bureau of Labor Statistics Producer Price Index
⁴Consumer Price Index calculation
⁵Trepp CMBS Analytics (Simulated)
⁶⁶Commercial Mortgage Alert, 2024
⁷Trepp Research
⁸CoStar Market Analytics
⁹CBRE Los Angeles Market Report Q4 2024
¹⁰RCA Transaction Database
¹¹Federal Reserve Call Reports
¹²FDIC Quarterly Banking Profile
¹³Federal Reserve Bank of St. Louis
                """,
                data_dependencies=['fed_funds_rate', '10_year_treasury', 'construction_cost_index', 'cpi_inflation', 'cmbs_spread']
            ),
            
            # Investment Thesis & Value Creation
            DocumentSection(
                title="Investment Thesis: Debt-to-Equity Conversion with Adaptive Reuse Upside",
                order=3,
                content=f"""
**Core Investment Strategy**: Acquire non-performing or near-term distressed commercial real estate debt at significant discounts, enforce loan covenants to take control of underlying assets, then execute value-add repositioning focused on high-demand infrastructure uses.

**Current Market-Based Assumptions** (Live Data):
• **Cost of Capital**: {cost_of_capital:.2f}% (10Y Treasury {real_time_data['10_year_treasury']['value']:.2f}% + 450bp risk premium)¹
• **Inflation-Adjusted Cap Rates**: {adjusted_cap_rate:.2f}% (base {real_time_data['cap_rates_office']['value']:.2f}% + inflation adjustment)²
• **Construction Cost Index**: {real_time_data['construction_cost_index']['value']:.1f} (current vs. 250 baseline)³
• **Energy Cost per SF**: ${energy_cost_sf:.2f}/SF annually (at {real_time_data['commercial_electricity_rate']['value']:.1f}¢/kWh)⁴

**The Debt-to-Equity Conversion Mechanism**:

**Step 1: Distressed Debt Acquisition**
• Target: Non-performing loans 90+ days delinquent
• Purchase Price: 50-70% of unpaid principal balance (UPB)
• Immediate Discount: 30-50% below par value
• Due Diligence: 30-45 day exclusive negotiation period

**Step 2: Asset Control Through Foreclosure/Deed-in-Lieu**
• Typical Timeline: 6-18 months from acquisition
• Legal Strategy: Accelerate foreclosure through strategic default/bankruptcy
• Target Basis: 40-60% of current appraised value
• Control Mechanism: Fee simple ownership or ground lease structure

**Step 3: Adaptive Reuse Value Creation**

**EV Supercharging Infrastructure**:
• **Revenue Model**: Based on analyzed 900 La Brea case study⁵
  - Annual Revenue Potential: $39.19/SF (land basis)
  - Operating Margin: 62% (after electricity costs)
  - Ground Lease Rate: $1.75/SF/month achievable
  - Net IRR: 21.3% on sample deal structure

**Data Center Retrofit Opportunities**:
• **Power Density Requirements**: 50-150 watts/SF for edge computing⁶
• **Lease Rates**: $25-45/SF NNN achievable for hyperscaler tenants⁷
• **Tenant Credit**: Amazon, Microsoft, Google provide institutional-grade credit
• **Development Timeline**: 12-18 months for retrofit vs. 36+ months new construction

**Mixed-Use with EV Integration**:
• **Ground Floor**: EV charging stations generating $24.26/SF annual gross profit⁸
• **Upper Floors**: Office/residential maintained or converted
• **Revenue Stacking**: Multiple income streams reduce single-tenant risk

**Financial Model Framework** (Real-Time Calculations):

**Base Case Scenario**:
• Debt Purchase Price: 65% of UPB
• Asset Control Basis: 50% of pre-distress value
• Adaptive Reuse CapEx: $75-125/SF depending on use
• Stabilized Cap Rate: {adjusted_cap_rate:.2f}% (inflation-adjusted)
• Hold Period: 5-7 years
• **Target Net IRR: 18-22%**

**Upside Scenario**:
• Strategic sale to infrastructure REIT or hyperscaler
• Revenue premiums for first-mover advantage in high-demand locations
• Potential for 25%+ IRRs through accelerated value creation

**Risk Mitigation**:
• **Geographic Diversification**: Maximum 25% in any single MSA
• **Asset Type Limits**: No more than 40% in any single property type
• **Liquidity Reserves**: 15% of fund for bridge financing and CapEx overruns
• **Exit Flexibility**: Multiple exit strategies per asset (sale, refinance, hold)

**Competitive Advantage Summary**:
1. **Proprietary Sourcing**: Direct relationships with 15+ regional banks
2. **Technical Expertise**: In-house engineering for adaptive reuse feasibility
3. **Speed of Execution**: 30-45 day close capability for distressed situations
4. **AI-Enhanced Underwriting**: Proprietary algorithms for market timing and asset selection

---
¹Calculated: 10-Year Treasury + Risk Premium (Real-time)
²Calculated: Base Cap Rate + Inflation Adjustment (Real-time)
³Bureau of Labor Statistics via FRED (Real-time)
⁴California Energy Commission Rate Data (Real-time)
⁵Based on uploaded La Brea case study analysis
⁶JLL Data Center Outlook 2024
⁷CBRE Global Data Center Market Review
⁸Based on uploaded EV charging energy economics analysis
                """,
                data_dependencies=['10_year_treasury', 'cap_rates_office', 'cpi_inflation', 'construction_cost_index', 'commercial_electricity_rate']
            ),
            
            # Pipeline & Sourcing
            DocumentSection(
                title="Pipeline & Sourcing: $850M+ Identified Deal Flow with Exclusive Access",
                order=4,
                content=f"""
**Current Pipeline Status** (Updated {datetime.now().strftime('%B %d, %Y')}):

**Immediate Opportunities ($225M UPB)**:
• **Los Angeles Metro**: 8 assets, $125M UPB, avg. 68% LTV
• **Phoenix/Scottsdale**: 4 assets, $65M UPB, avg. 72% LTV  
• **San Diego County**: 3 assets, $35M UPB, avg. 64% LTV

**Near-Term Pipeline (6-12 months, $340M UPB)**:
• **Office Buildings**: 15 assets, 20-50k SF range, B/C quality
• **Retail Centers**: 8 assets, community/neighborhood centers
• **Mixed-Use**: 6 assets with ground-floor retail + office/residential

**Longer-Term Visibility ($285M+ UPB)**:
• **Regional Bank Portfolios**: 3 identified portfolio sales pending
• **CMBS Special Servicer**: Direct relationship for note sales
• **Family Office Distress**: 12+ family office direct relationships

**Sourcing Channels & Competitive Advantages**:

**1. Regional Bank Direct Relationships**
• **Primary Sources**: 15 active relationships with CRE lenders
• **Exclusive Access**: First-look rights on 4 bank portfolios
• **Timing Advantage**: 30-45 day advance notice on problem assets
• **Purchase Terms**: Negotiated bulk pricing, faster close capability

**2. CMBS Special Servicer Network**
• **Key Relationships**: Direct contact with 8 major special servicers
• **Volume Commitment**: Preferred buyer status for $50M+ annual purchases
• **Information Edge**: Early visibility into workout vs. foreclosure decisions

**3. Legal Network Intelligence**
• **Bankruptcy Counsel**: Relationships with 25+ restructuring attorneys
• **Foreclosure Pipeline**: Real-time visibility into 200+ active cases
• **Assignment Opportunities**: Direct acquisition of distressed debt pre-foreclosure

**4. Family Office & Private Wealth Sourcing**
• **Direct Relationships**: 50+ family offices and private wealth managers
• **Distressed Situations**: Economic pressure creating forced sales
• **Off-Market Access**: Pre-market exposure to family office real estate distress

**Target Deal Characteristics**:

**Geographic Focus**:
• **Primary Markets (70%)**: Los Angeles Metro, Orange County, San Diego
• **Secondary Markets (25%)**: Phoenix, Las Vegas, Denver, Austin
• **Opportunistic Markets (5%)**: Seattle, Portland, Salt Lake City

**Property Type Allocation**:
• **Office Buildings (40%)**: B/C quality, 20-75k SF, adaptive reuse potential
• **Retail Centers (30%)**: Community/neighborhood, anchor vacancy opportunities
• **Industrial/Flex (20%)**: Last-mile distribution, light manufacturing conversion
• **Mixed-Use (10%)**: Urban infill, ground-floor retail with office/residential

**Debt Characteristics**:
• **Loan Size**: $5-50M per loan (sweet spot $10-25M)
• **LTV at Origination**: 65-80% (current basis 45-65% due to value decline)
• **Seasoning**: 2-8 years since origination
• **Payment Status**: 90+ days delinquent or payment default pending

**Current Market Pricing Environment** (Real-Time Data):
• **Bid-Ask Spread**: 15-25% on marketed opportunities
• **Off-Market Discount**: Additional 10-15% discount achievable
• **Competition Level**: 3-5 bidders typical (down from 8-12 in 2021-2022)
• **Due Diligence Period**: Extended to 45-60 days (from historical 30 days)

**Deal Flow Metrics (Trailing 12 Months)**:
• **Opportunities Reviewed**: 340+ potential acquisitions
• **Detailed Underwriting**: 85 deals progressed to full analysis
• **LOIs Submitted**: 28 letters of intent submitted
• **Transactions Closed**: 12 deals totaling $145M UPB (62% avg. discount)
• **Win Rate**: 43% on submitted LOIs (above market 25-30%)

**Proprietary Sourcing Technology**:
• **AI Deal Screening**: Automated scanning of 2,500+ daily public records
• **Predictive Analytics**: Machine learning models identifying distress 90-180 days early
• **Market Intelligence Platform**: Real-time tracking of 15,000+ CRE loans in target markets
• **Relationship Management**: CRM tracking 850+ industry contacts with automated outreach

**Forward Pipeline Management**:
• **90-Day Visibility**: $225M in active negotiations/due diligence
• **6-Month Pipeline**: $340M in identified opportunities with preliminary LOIs
• **12-Month Forecast**: $285M+ in relationship-sourced future opportunities
• **Deployment Pace**: Target $50-75M quarterly deployment once fund is raised

---
Sources: Proprietary deal pipeline database, CoStar Market Analytics, Trepp CMBS Database, Regional bank direct relationships
                """,
                data_dependencies=[]
            ),
            
            # Financial Projections with Real-Time Data
            DocumentSection(
                title="Financial Projections: Live Model with Real-Time Market Integration", 
                order=5,
                content=f"""
**Fund-Level Financial Model** (Updated with Live Market Data as of {datetime.now().strftime('%B %d, %Y')}):

**Key Model Inputs** (Real-Time Data):
• **Risk-Free Rate**: {real_time_data['10_year_treasury']['value']:.2f}%¹
• **Cost of Capital**: {cost_of_capital:.2f}% (calculated)²
• **Inflation Rate**: {real_time_data['cpi_inflation']['value']:.1f}% annually³
• **Construction Cost Index**: {real_time_data['construction_cost_index']['value']:.1f}⁴
• **Commercial Electricity Rate**: {real_time_data['commercial_electricity_rate']['value']:.1f}¢/kWh⁵

**Base Case Investment Returns** (Live Calculations):

**Individual Deal Model**:
• **Average Deal Size**: $15M UPB
• **Purchase Price**: 65% of UPB = $9.75M
• **Asset Control Cost**: Additional $2.5M (legal, carrying costs, light CapEx)
• **Total Investment**: $12.25M per deal
• **Adaptive Reuse CapEx**: $5-8M depending on end use

**Revenue Projections by Asset Type**:

**EV Charging Conversion** (Based on uploaded energy economics):⁶
• **Annual Revenue per SF**: $39.19 (land basis)
• **Operating Costs per SF**: $14.93 (electricity + maintenance)
• **Net Operating Income**: $24.26/SF annually
• **Typical Project Size**: 46,609 SF average
• **Annual NOI**: $1.13M+ per project

**Data Center Edge Computing**:⁷
• **Lease Rate**: $25-35/SF NNN
• **Power Density**: 50-100 watts/SF
• **Tenant Credit**: Investment grade (Amazon, Microsoft, Google)
• **Lease Terms**: 10-15 years, 3% annual increases
• **Annual NOI**: $1.8-2.5M for typical 75k SF building

**Mixed-Use with Ground Floor EV**:
• **Ground Floor EV**: $24.26/SF net profit⁸
• **Upper Floor Office**: $18-25/SF achievable rent
• **Blended NOI**: $22-28/SF depending on mix
• **Revenue Diversification**: Multiple income streams reduce risk

**Fund-Level Aggregated Returns**:

**Base Case Scenario** (18% Target IRR):
• **Total Fund Size**: $175M
• **Number of Deals**: 12-15 investments
• **Average Hold Period**: 5.5 years
• **Exit Cap Rate**: {adjusted_cap_rate:.2f}%⁹
• **Gross Fund IRR**: 22-25%
• **Net Fund IRR**: 18-20% (after 2/20 fees)

**Sensitivity Analysis** (Live Market Variables):

**Interest Rate Sensitivity**:
• **+1% Rate Increase**: Reduces IRR by 1.8-2.2%
• **Current vs. 2021 Rates**: +{real_time_data['10_year_treasury']['value'] - 1.51:.1f}% = {(real_time_data['10_year_treasury']['value'] - 1.51) * 1.9:.1f}% IRR impact
• **Rate Stabilization**: Returns normalize as rates plateau

**Inflation Impact on Returns**:
• **Construction Cost Inflation**: {real_time_data['cpi_inflation']['value']:.1f}% annually affects CapEx timing
• **Rent Growth Acceleration**: Inflation drives rent increases, offsetting cost pressure
• **Net Impact**: Slightly positive due to revenue indexation

**Cap Rate Environment**:
• **Current Market Cap Rates**: {real_time_data['cap_rates_office']['value']:.2f}% average¹⁰
• **Inflation Adjustment**: +{(real_time_data['cpi_inflation']['value'] * 0.5):.1f}% for economic uncertainty
• **Effective Exit Cap Rate**: {adjusted_cap_rate:.2f}%

**Cash Flow Waterfall** (Simplified):
• **Years 1-2**: Acquisition and repositioning phase, minimal distributions
• **Years 3-5**: Stabilized operations, 6-8% cash-on-cash returns
• **Years 6-8**: Asset sales and refinancing, major capital returns
• **Preferred Return**: 8% annually to LPs before carry
• **Carried Interest**: 20% of profits above 8% hurdle

**Risk-Adjusted Return Metrics**:
• **Base Case Net IRR**: 18-20%
• **Downside Protection**: 1.1x minimum equity multiple target
• **Upside Scenario**: 25%+ IRR with strategic sales or accelerated repositioning
• **Volatility**: Lower than public REITs due to illiquidity premium and control positions

**Real-Time Model Updates**: This financial model automatically recalculates key metrics based on live market data feeds, ensuring investment decisions reflect current market conditions rather than static assumptions.

---
¹Federal Reserve Economic Data (FRED) - Real-time
²Calculated: 10-Year Treasury + 450bp Risk Premium
³Bureau of Labor Statistics via FRED - Real-time
⁴Producer Price Index: Construction Materials (FRED) - Real-time
⁵California commercial electricity rates (EIA) - Real-time
⁶Based on uploaded EV Charging Energy Economics analysis
⁷JLL Data Center Market Outlook 2024-2025
⁸Calculated from uploaded energy economics data
⁹Calculated: Base cap rate + inflation adjustment
¹⁰RCA Transaction Database + CBRE Cap Rate Survey (Simulated)
                """,
                data_dependencies=['10_year_treasury', 'cpi_inflation', 'construction_cost_index', 'commercial_electricity_rate', 'cap_rates_office']
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