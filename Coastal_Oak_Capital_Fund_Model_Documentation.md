# COASTAL OAK CAPITAL FUND MODEL DOCUMENTATION

## Excel File Structure: "Coastal_Oak_Capital_Fund_Model.xlsx"

### Sheet 1: Executive Summary
**Purpose:** High-level fund performance metrics and key assumptions
**Key Outputs:**
- Fund-level IRR and equity multiple
- Total returns to LPs vs GP
- Capital deployment timeline
- Key performance indicators dashboard

**Input Cells (Blue highlighting):**
- Fund size: $50-75M
- Target IRR: 17-22%
- Preferred return: 8%
- Management fee: 2.0%/1.5%
- Investment period: 24 months
- Fund term: 10 years

### Sheet 2: Capital Call Schedule
**Purpose:** Models timing and amount of capital calls from LPs
**Key Calculations:**
- Monthly capital deployment schedule
- Management fee calculations
- LP capital commitments and drawdowns
- Cash flow timing for investment activities

**Formula Structure:**
```
Capital Call Amount = Investment Amount + Management Fee + Expenses
Cumulative Calls = SUM(Prior Calls + Current Call)
Management Fee = Committed Capital × Fee Rate × Time Period
```

### Sheet 3: Deal-Level Pro Forma
**Purpose:** Individual asset investment analysis template
**Key Components:**
- Acquisition assumptions (price, costs, financing)
- Revenue projections ($/SF and $/MW models)
- Operating expense forecasts
- Capital expenditure schedules
- Exit valuation analysis

**Sample Deal Structure:**
- Acquisition cost: $10M
- Renovation budget: $5M  
- Total investment: $15M
- Stabilized NOI: $2.1M
- Exit cap rate: 6.5%
- Hold period: 5 years

### Sheet 4: Portfolio Aggregation
**Purpose:** Combines multiple deals into portfolio-level analysis
**Key Features:**
- 12-15 individual deal inputs
- Portfolio diversification by asset type
- Geographic concentration limits
- Tenant credit analysis
- Portfolio-wide cash flows

**Risk Controls:**
- Maximum 15% in any single asset
- Maximum 30% in any submarket
- Minimum 60% investment-grade tenants
- Diversification by vintage year

### Sheet 5: Waterfall Distribution
**Purpose:** Models cash flow distribution between LPs and GP
**Waterfall Structure:**
1. Return of LP capital: 100% to LPs
2. 8% preferred return: 100% to LPs  
3. Excess returns: 50% LP / 50% GP split

**Key Calculations:**
```
LP Preferred = LP Capital × 8% × Years Outstanding
LP Share of Excess = (Total Returns - LP Capital - LP Preferred) × 50%
GP Carried Interest = Excess Returns × 50%
```

### Sheet 6: Sensitivity Analysis
**Purpose:** Tests performance under various scenarios
**Scenario Variables:**
- Acquisition discount: 10-25%
- Construction cost overruns: 0-30%
- Stabilization period: 12-36 months
- Exit cap rates: 5.5-7.5%
- Rent growth: 0-5% annually

**Output Metrics:**
- IRR sensitivity matrix
- Equity multiple ranges
- Probability-weighted returns
- Stress test results

### Sheet 7: Financing Analysis
**Purpose:** Models debt financing across portfolio
**Debt Parameters:**
- LTV ratios: 60-75%
- Interest rates: 6-8%
- Amortization periods: 25-30 years
- DSCR requirements: 1.25-1.50x

**Interest Rate Sensitivity:**
- Base case: 7.0%
- Upside scenario: 6.0%
- Downside scenario: 8.5%

### Sheet 8: Tax Analysis
**Purpose:** Estimates tax implications for LPs
**Key Components:**
- Depreciation schedules
- Capital gains/ordinary income allocation  
- State tax considerations
- 1031 exchange benefits
- Opportunity Zone impacts

### Sheet 9: ESG Impact Metrics
**Purpose:** Quantifies environmental and social benefits
**Tracked Metrics:**
- Carbon emissions reduction
- Energy consumption savings
- Job creation (construction and permanent)
- Community investment amounts
- LEED/sustainability certifications

**Financial Integration:**
- ESG premium capture: 25-50 bps cap rate compression
- Utility incentives and rebates
- Tax credit monetization
- Insurance cost reductions

### Sheet 10: Market Comparables
**Purpose:** Benchmarks against public and private market alternatives
**Comparison Categories:**
- Public data center REITs
- Opportunistic real estate funds  
- Infrastructure debt funds
- Value-add real estate strategies

**Performance Metrics:**
- Total returns (5-year)
- Dividend/distribution yields
- NAV growth rates
- Risk-adjusted returns (Sharpe ratios)

## Key Model Features

### Dynamic Scenarios
All sheets link to scenario assumptions allowing users to model:
- Conservative (probability: 20%)
- Base case (probability: 60%)  
- Aggressive (probability: 20%)

### Data Validation
Input cells include dropdown menus and range restrictions to prevent modeling errors.

### Error Checking
Built-in formulas verify:
- Cash flow balancing
- Distribution waterfall accuracy
- Percentage allocations sum to 100%
- Timeline consistency across sheets

### Presentation Ready
All outputs formatted for investor presentations with:
- Consistent chart styling
- Professional color schemes
- Clear data labels and annotations
- Print-optimized layouts

## Usage Instructions

1. **Start with Executive Summary sheet** to set fund-level parameters
2. **Modify Deal-Level Pro Forma** for specific investment analysis  
3. **Adjust Portfolio Aggregation** to reflect actual deal pipeline
4. **Review Sensitivity Analysis** to understand risk factors
5. **Check Waterfall Distribution** to confirm LP/GP economics
6. **Validate against Market Comparables** for competitive positioning

## Model Assumptions Documentation

### Revenue Assumptions
- Data center rents: $150-200/MW-month
- EV charging revenue: $35-55k per dispenser annually
- Annual rent escalations: 2-3%
- Stabilized occupancy: 90-95%

### Cost Assumptions  
- Construction costs: $200-400/SF depending on use
- Annual expense growth: 2.5-3.0%
- Property taxes: 1.1% of assessed value
- Insurance: 0.3-0.5% of replacement cost

### Market Assumptions
- Exit cap rates: 6.0-7.0% for stabilized assets
- Discount rates: 10-12% unlevered, 15-18% levered
- Hold periods: 4-7 years average
- Transaction costs: 2-3% of sale price

### Financing Assumptions
- Interest rates: 6.5-8.0% for stabilized properties
- LTV ratios: 65-75% maximum
- Loan terms: 10 years with amortization
- Debt yield requirements: 9-11%

This comprehensive model provides institutional-grade analysis supporting the investment thesis while maintaining transparency and auditability for Limited Partner due diligence.