import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';

const Dashboard = ({ userType, onLogout }) => {
  const [currentView, setCurrentView] = useState('dashboard'); // 'dashboard', 'prospectus', or 'excel'
  const [activeSection, setActiveSection] = useState('executive-summary');
  const [activeExcelSheet, setActiveExcelSheet] = useState('deal-analysis');
  const [marketData, setMarketData] = useState({
    fundValue: 125000000,
    nav: 98.7,
    irr: 12.8,
    multiple: 1.34,
    occupancy: 87.2,
    leverage: 62.5,
    lastUpdate: new Date().toLocaleString()
  });

  // State for real Excel data from backend
  const [excelSummary, setExcelSummary] = useState(null);
  const [excelGridData, setExcelGridData] = useState([]);
  const [externalData, setExternalData] = useState(null);
  const [loadingExcelData, setLoadingExcelData] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  // Fetch real Excel data from backend
  const fetchExcelData = async () => {
    if (currentView !== 'excel') return;
    
    try {
      setLoadingExcelData(true);
      
      // Fetch Excel summary data
      const summaryResponse = await fetch(`${backendUrl}/api/excel/summary`);
      if (summaryResponse.ok) {
        const summaryData = await summaryResponse.json();
        setExcelSummary(summaryData);
        
        // Update market data with real backend data
        if (summaryData.kpis && summaryData.kpis.fund) {
          const fundKpis = summaryData.kpis.fund;
          setMarketData(prev => ({
            ...prev,
            fundValue: summaryData.aum || prev.fundValue,
            nav: fundKpis.nav || prev.nav,
            irr: fundKpis.net_irr || prev.irr,
            multiple: fundKpis.net_moic || prev.multiple,
            lastUpdate: new Date().toLocaleString()
          }));
        }
      }
      
      // Fetch Excel grid data
      const gridResponse = await fetch(`${backendUrl}/api/excel/data`);
      if (gridResponse.ok) {
        const gridData = await gridResponse.json();
        setExcelGridData(gridData.rows || []);
      }
      
    } catch (error) {
      console.error('Error fetching Excel data:', error);
      toast.error('Failed to load Excel data from backend');
    } finally {
      setLoadingExcelData(false);
    }
  };

  // Load Excel data when switching to Excel view
  useEffect(() => {
    if (currentView === 'excel') {
      fetchExcelData();
    }
  }, [currentView]);

  // Refresh Excel data periodically when in Excel view
  useEffect(() => {
    let interval;
    if (currentView === 'excel') {
      interval = setInterval(fetchExcelData, 30000); // Refresh every 30 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [currentView]);

  const [deals, setDeals] = useState([
    {
      id: 1,
      name: 'Metro Office Complex - Atlanta',
      type: 'Office',
      status: 'Active',
      value: 25000000,
      acquisition: '2023-Q2',
      irr: 15.2
    },
    {
      id: 2,
      name: 'Riverside Retail Plaza - Dallas',
      type: 'Retail',
      status: 'Under Contract',
      value: 18500000,
      acquisition: '2024-Q1',
      irr: 13.8
    },
    {
      id: 3,
      name: 'Industrial Park - Phoenix',
      type: 'Industrial',
      status: 'Active',
      value: 32000000,
      acquisition: '2023-Q4',
      irr: 16.1
    }
  ]);

  // Excel Spreadsheet Data with Case Studies
  const excelData = {
    'deal-analysis': {
      title: 'Deal Analysis & Market Dynamics',
      subtitle: 'WHAT-WHY-HOW: Investment Rationale & Case Studies',
      sheets: {
        'pico-blvd-case': {
          name: 'Pico Blvd Case Study',
          description: 'WHAT: 125,000 SF office building acquisition in West LA. WHY: 40% below replacement cost in supply-constrained market. HOW: Value-add repositioning strategy.',
          data: [
            {
              category: 'ACQUISITION METRICS',
              rows: [
                { metric: 'Purchase Price', value: '$18,500,000', assumption: 'Contract price based on distressed sale', citation: 'Purchase Agreement, Sec 2.1' },
                { metric: 'Price per SF', value: '$148', assumption: 'Total SF: 125,000', citation: 'Property Survey, Page 3' },
                { metric: 'Replacement Cost per SF', value: '$250', assumption: 'Current construction costs', citation: 'Marshall & Swift Cost Manual 2024' },
                { metric: 'Discount to Replacement', value: '40.8%', assumption: '($250-$148)/$250', citation: 'Internal Analysis' },
                { metric: 'Cap Rate In', value: '5.2%', assumption: 'Current NOI / Purchase Price', citation: 'Underwriting Model' }
              ]
            },
            {
              category: 'VALUE CREATION STRATEGY',
              rows: [
                { metric: 'Current Occupancy', value: `${(marketData.occupancy - 15).toFixed(1)}%`, assumption: 'Tenant roll as of acquisition', citation: 'Rent Roll, Current' },
                { metric: 'Stabilized Occupancy', value: '92.0%', assumption: 'Market stabilized rate', citation: 'CoStar Market Report Q4 2024' },
                { metric: 'Current Avg Rent PSF', value: '$42.50', assumption: 'Weighted avg existing leases', citation: 'Lease Abstract Summary' },
                { metric: 'Market Rent PSF', value: '$55.00', assumption: 'West LA Class A comparable', citation: 'CBRE Market Survey Q4 2024' },
                { metric: 'Renovation Budget', value: '$3,200,000', assumption: '$25.60/SF full renovation', citation: 'General Contractor Bid' }
              ]
            },
            {
              category: 'FINANCIAL PROJECTIONS',
              rows: [
                { metric: 'Year 1 NOI', value: '$960,000', assumption: 'Current in-place rents', citation: 'Underwriting Model, Yr 1' },
                { metric: 'Stabilized NOI (Yr 3)', value: '$5,720,000', assumption: 'Post-renovation market rents', citation: 'Underwriting Model, Yr 3' },
                { metric: 'Exit Cap Rate', value: '4.8%', assumption: 'Compressed cap due to value-add', citation: 'Comparable Sales Analysis' },
                { metric: 'Exit Value (Yr 5)', value: '$119,200,000', assumption: 'Stabilized NOI / Exit Cap', citation: 'Underwriting Model, Exit' },
                { metric: 'Total Return Multiple', value: '3.2x', assumption: 'Including distributions', citation: 'Underwriting Model, Summary' },
                { metric: 'Net IRR', value: '28.4%', assumption: 'Levered returns to equity', citation: 'Underwriting Model, IRR Calc' }
              ]
            },
            {
              category: 'MARKET DYNAMICS - WHY NOW',
              rows: [
                { metric: 'West LA Vacancy Rate', value: '12.8%', assumption: 'Current market conditions', citation: 'CBRE Market Report Q4 2024' },
                { metric: 'Historical Avg Vacancy', value: '8.2%', assumption: '10-year average', citation: 'CBRE Historical Data' },
                { metric: 'New Supply Pipeline', value: '2.1M SF', assumption: 'Deliveries next 24 months', citation: 'CoStar Development Pipeline' },
                { metric: 'Construction Starts YoY', value: '-67%', assumption: 'Current vs prior year', citation: 'Dodge Analytics Q4 2024' },
                { metric: 'Interest Rate Impact', value: '+180bps', assumption: 'Fed funds vs 2021 low', citation: 'Federal Reserve Economic Data' }
              ]
            },
            {
              category: 'RISK FACTORS & MITIGATION',
              rows: [
                { metric: 'Interest Rate Risk', value: 'HIGH', assumption: 'Floating rate construction loan', citation: 'Loan Terms Sheet' },
                { metric: 'Lease-Up Risk', value: 'MEDIUM', assumption: '18-month lease-up timeline', citation: 'Leasing Strategy Plan' },
                { metric: 'Construction Cost Risk', value: 'MEDIUM', assumption: 'Fixed-price GC contract', citation: 'Construction Agreement' },
                { metric: 'Market Cycle Risk', value: 'LOW', assumption: 'Counter-cyclical timing', citation: 'Market Analysis Report' },
                { metric: 'Tenant Credit Risk', value: 'LOW', assumption: 'Target investment grade tenants', citation: 'Tenant Criteria Matrix' }
              ]
            }
          ]
        },
        'portfolio-performance': {
          name: 'Real-Time Portfolio Performance',
          description: 'Live tracking of fund performance with automatically updated metrics and assumptions.',
          data: [
            {
              category: 'FUND-LEVEL METRICS (REAL-TIME)',
              rows: [
                { metric: 'Total Fund Value', value: formatCurrency(marketData.fundValue), assumption: 'Mark-to-market quarterly', citation: 'Appraisal Reports Q4 2024' },
                { metric: 'NAV per Share', value: `$${marketData.nav.toFixed(2)}`, assumption: 'Fund Value / Shares Outstanding', citation: 'Fund Accounting System' },
                { metric: 'Net IRR', value: formatPercent(marketData.irr), assumption: 'XIRR calculation method', citation: 'Performance Reporting System' },
                { metric: 'Total Return Multiple', value: `${marketData.multiple.toFixed(2)}x`, assumption: 'DPI + RVPI calculation', citation: 'ILPA Reporting Standards' },
                { metric: 'Portfolio Occupancy', value: formatPercent(marketData.occupancy), assumption: 'Weighted avg by sq ft', citation: 'Property Management Reports' },
                { metric: 'Average Leverage', value: formatPercent(marketData.leverage), assumption: 'Debt-to-total capitalization', citation: 'Loan Portfolio Summary' }
              ]
            },
            {
              category: 'PROPERTY-LEVEL PERFORMANCE',
              rows: [
                { metric: 'Metro Office Complex NOI', value: '$3,850,000', assumption: 'Trailing 12-month actual', citation: 'Property Financials Dec 2024' },
                { metric: 'Metro Office Occupancy', value: '94.2%', assumption: 'Leased SF / Total SF', citation: 'Property Management Report' },
                { metric: 'Riverside Retail NOI', value: '$2,240,000', assumption: 'Trailing 12-month actual', citation: 'Property Financials Dec 2024' },
                { metric: 'Riverside Retail Occupancy', value: '89.1%', assumption: 'Leased SF / Total SF', citation: 'Property Management Report' },
                { metric: 'Industrial Park NOI', value: '$4,920,000', assumption: 'Trailing 12-month actual', citation: 'Property Financials Dec 2024' },
                { metric: 'Industrial Park Occupancy', value: '97.8%', assumption: 'Leased SF / Total SF', citation: 'Property Management Report' }
              ]
            },
            {
              category: 'MARKET INTELLIGENCE (LIVE DATA)',
              rows: [
                { metric: 'Fed Funds Rate', value: '5.25%', assumption: 'Current FOMC target rate', citation: 'Federal Reserve Board' },
                { metric: '10-Year Treasury', value: '4.18%', assumption: 'Current market rate', citation: 'Bloomberg Terminal' },
                { metric: 'Commercial Property Index', value: '+2.8% YoY', assumption: 'NCREIF Property Index', citation: 'NCREIF Quarterly Report' },
                { metric: 'Office Vacancy - National', value: '13.2%', assumption: 'Class A office buildings', citation: 'CBRE Research Q4 2024' },
                { metric: 'Industrial Vacancy - National', value: '5.1%', assumption: 'Warehouse/distribution', citation: 'JLL Research Q4 2024' },
                { metric: 'Retail Vacancy - National', value: '9.8%', assumption: 'Shopping centers', citation: 'CoStar Market Analytics' }
              ]
            },
            {
              category: 'CAPITAL MARKETS ACTIVITY',
              rows: [
                { metric: 'Transaction Volume YoY', value: '-23%', assumption: 'Commercial sales volume', citation: 'RCA Commercial Transaction Database' },
                { metric: 'Cap Rate Compression', value: '+45bps', assumption: 'Average across property types', citation: 'CBRE Cap Rate Survey Q4 2024' },
                { metric: 'CMBS Issuance YoY', value: '-41%', assumption: 'New issuance volume', citation: 'Commercial Mortgage Alert' },
                { metric: 'Bank CRE Lending', value: '-18%', assumption: 'New originations', citation: 'Federal Reserve H.8 Report' },
                { metric: 'Distressed Sales Volume', value: '+89%', assumption: 'Properties sold at discount', citation: 'Distressed Property Analytics' }
              ]
            }
          ]
        },
        'market-assumptions': {
          name: 'Market Assumptions & Methodology',
          description: 'Detailed breakdown of all assumptions used in investment analysis and performance calculations.',
          data: [
            {
              category: 'VALUATION METHODOLOGY',
              rows: [
                { metric: 'Discount Rate', value: '12.0%', assumption: 'Risk-free rate + risk premium', citation: 'Investment Committee Guidelines' },
                { metric: 'Exit Cap Rates', value: '4.5% - 6.5%', assumption: 'Based on property type/location', citation: 'Historical Cap Rate Analysis' },
                { metric: 'Market Rent Growth', value: '2.5% annually', assumption: 'Long-term inflation + 50bps', citation: 'Bureau of Labor Statistics' },
                { metric: 'Expense Growth', value: '3.0% annually', assumption: 'Historical average expense growth', citation: 'Property Management Analysis' },
                { metric: 'Terminal Value', value: 'Direct Cap Method', assumption: 'Year 5 NOI / Exit Cap Rate', citation: 'Valuation Standards' }
              ]
            },
            {
              category: 'MARKET RESEARCH SOURCES',
              rows: [
                { metric: 'Property Data', value: 'CoStar, CBRE', assumption: 'Subscription services', citation: 'Third-party data providers' },
                { metric: 'Transaction Comps', value: 'RCA, Real Capital', assumption: 'Commercial transaction database', citation: 'Market data subscription' },
                { metric: 'Economic Data', value: 'Bloomberg, Fed', assumption: 'Government and financial data', citation: 'Federal Reserve FRED database' },
                { metric: 'Rent Surveys', value: 'JLL, C&W', assumption: 'Quarterly market surveys', citation: 'Brokerage research reports' },
                { metric: 'Construction Costs', value: 'Marshall & Swift', assumption: 'Replacement cost manual', citation: 'CoreLogic construction database' }
              ]
            },
            {
              category: 'PERFORMANCE CALCULATION METHODS',
              rows: [
                { metric: 'IRR Calculation', value: 'XIRR Function', assumption: 'Excel/Bloomberg methodology', citation: 'GIPS Performance Standards' },
                { metric: 'Multiple Calculation', value: 'DPI + RVPI', assumption: 'ILPA reporting guidelines', citation: 'Private Equity Industry Guidelines' },
                { metric: 'NAV Methodology', value: 'Fair Value', assumption: 'ASC 820 / IFRS 13', citation: 'Accounting Standards' },
                { metric: 'Benchmark Comparison', value: 'NCREIF ODCE', assumption: 'Open-end core fund index', citation: 'Industry benchmark standards' },
                { metric: 'Risk Metrics', value: 'Standard Deviation', assumption: 'Quarterly return volatility', citation: 'Modern Portfolio Theory' }
              ]
            }
          ]
        }
      }
    }
  };

  const excelSheets = [
    { id: 'pico-blvd-case', label: 'Pico Blvd Case Study' },
    { id: 'portfolio-performance', label: 'Live Portfolio Data' },
    { id: 'market-assumptions', label: 'Assumptions & Methodology' }
  ];

  // Simulate real-time data updates
  useEffect(() => {
    const interval = setInterval(() => {
      setMarketData(prev => ({
        ...prev,
        fundValue: prev.fundValue + (Math.random() - 0.5) * 100000,
        nav: prev.nav + (Math.random() - 0.5) * 0.2,
        irr: prev.irr + (Math.random() - 0.5) * 0.1,
        occupancy: Math.max(80, Math.min(95, prev.occupancy + (Math.random() - 0.5) * 0.5)),
        lastUpdate: new Date().toLocaleString()
      }));
    }, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, []);

  const handleExport = () => {
    if (userType !== 'gp') {
      toast.error('Export functionality is restricted to General Partners only.');
      return;
    }
    
    // Simulate export functionality
    toast.success('Fund data exported successfully. Download will begin shortly.');
    
    // Create mock export data
    const exportData = {
      fundData: marketData,
      deals: deals,
      exportDate: new Date().toISOString(),
      exportedBy: 'GP User'
    };
    
    // Create downloadable file
    const blob = new Blob([JSON.stringify(exportData, null, 2)], 
      { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `coastal_oak_capital_export_${new Date().getTime()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleProspectusDownload = () => {
    if (userType !== 'gp') {
      toast.error('Document download is restricted to General Partners only.');
      return;
    }
    
    toast.success('Prospectus document download initiated.');
    
    // Create a comprehensive prospectus document text
    const prospectusContent = `
COASTAL OAK CAPITAL
DISTRESSED & OPPORTUNISTIC REAL ESTATE FUND
CONFIDENTIAL PRIVATE PLACEMENT MEMORANDUM

=====================================
EXECUTIVE SUMMARY
=====================================

Coastal Oak Capital Fund I ("the Fund") is a $500 million distressed and opportunistic real estate fund focused on acquiring underperforming commercial real estate assets across the United States. Our strategy targets office, retail, industrial, and multifamily properties in major metropolitan markets.

Fund Size: $500,000,000 target
Investment Period: 5 years
Fund Life: 10 years (with 2 one-year extensions)
Target Net IRR: 15-20%
Target Equity Multiple: 2.0x - 2.5x

=====================================
INVESTMENT STRATEGY
=====================================

The Fund employs a disciplined approach to acquiring distressed and opportunistic real estate investments:

1. DISTRESSED ACQUISITIONS (60%)
   - Properties in financial distress
   - Below replacement cost acquisitions
   - Value-add repositioning opportunities

2. OPPORTUNISTIC INVESTMENTS (40%)
   - Off-market transactions
   - Strategic partnerships
   - Development and redevelopment projects

=====================================
MARKET ANALYSIS
=====================================

Current market conditions present compelling opportunities:
- Interest rate volatility creating distressed situations
- Bank lending tightening creating acquisition opportunities
- Demographic shifts creating new demand patterns
- Technology disruption in commercial real estate

=====================================
PORTFOLIO OVERVIEW
=====================================

Current portfolio includes ${deals.length} active investments:
${deals.map(deal => `- ${deal.name}: ${deal.type} (${deal.status}) - $${(deal.value / 1000000).toFixed(1)}M`).join('\n')}

Total Portfolio Value: ${formatCurrency(marketData.fundValue)}
Current Net IRR: ${formatPercent(marketData.irr)}
Portfolio Occupancy: ${formatPercent(marketData.occupancy)}

=====================================
RISK FACTORS
=====================================

Investment in the Fund involves significant risks including but not limited to:
- Real estate market volatility
- Interest rate fluctuations
- Regulatory changes
- Liquidity constraints
- General economic conditions

=====================================
LEGAL TERMS
=====================================

This document contains confidential and proprietary information. Distribution is restricted to accredited investors only. No public offering is being made.

Management Fee: 2.0% annually
Carried Interest: 20% above 8% preferred return
Minimum Investment: $1,000,000

Generated: ${new Date().toLocaleString()}
Document Version: 1.0
    `;
    
    // Create downloadable PDF-like text file
    const blob = new Blob([prospectusContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `coastal_oak_capital_prospectus_${new Date().getTime()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleExcelExport = () => {
    if (userType !== 'gp') {
      toast.error('Excel export is restricted to General Partners only.');
      return;
    }
    
    toast.success('Excel data export initiated. Generating comprehensive spreadsheet...');
    
    // Create comprehensive Excel-like data export
    let excelContent = `COASTAL OAK CAPITAL - INSTITUTIONAL EXCEL REPORTS
Generated: ${new Date().toLocaleString()}
Data as of: ${marketData.lastUpdate}

=====================================
PICO BLVD CASE STUDY - DEAL ANALYSIS
=====================================

ACQUISITION METRICS:
Purchase Price: $18,500,000 (Contract price based on distressed sale - Purchase Agreement, Sec 2.1)
Price per SF: $148 (Total SF: 125,000 - Property Survey, Page 3)
Replacement Cost per SF: $250 (Current construction costs - Marshall & Swift Cost Manual 2024)
Discount to Replacement: 40.8% (($250-$148)/$250 - Internal Analysis)
Cap Rate In: 5.2% (Current NOI / Purchase Price - Underwriting Model)

VALUE CREATION STRATEGY:
Current Occupancy: ${(marketData.occupancy - 15).toFixed(1)}% (Tenant roll as of acquisition - Rent Roll, Current)
Stabilized Occupancy: 92.0% (Market stabilized rate - CoStar Market Report Q4 2024)
Current Avg Rent PSF: $42.50 (Weighted avg existing leases - Lease Abstract Summary)
Market Rent PSF: $55.00 (West LA Class A comparable - CBRE Market Survey Q4 2024)
Renovation Budget: $3,200,000 ($25.60/SF full renovation - General Contractor Bid)

FINANCIAL PROJECTIONS:
Year 1 NOI: $960,000 (Current in-place rents - Underwriting Model, Yr 1)
Stabilized NOI (Yr 3): $5,720,000 (Post-renovation market rents - Underwriting Model, Yr 3)
Exit Cap Rate: 4.8% (Compressed cap due to value-add - Comparable Sales Analysis)
Exit Value (Yr 5): $119,200,000 (Stabilized NOI / Exit Cap - Underwriting Model, Exit)
Total Return Multiple: 3.2x (Including distributions - Underwriting Model, Summary)
Net IRR: 28.4% (Levered returns to equity - Underwriting Model, IRR Calc)

=====================================
REAL-TIME PORTFOLIO PERFORMANCE
=====================================

FUND-LEVEL METRICS (LIVE DATA):
Total Fund Value: ${formatCurrency(marketData.fundValue)} (Mark-to-market quarterly - Appraisal Reports Q4 2024)
NAV per Share: $${marketData.nav.toFixed(2)} (Fund Value / Shares Outstanding - Fund Accounting System)
Net IRR: ${formatPercent(marketData.irr)} (XIRR calculation method - Performance Reporting System)
Total Return Multiple: ${marketData.multiple.toFixed(2)}x (DPI + RVPI calculation - ILPA Reporting Standards)
Portfolio Occupancy: ${formatPercent(marketData.occupancy)} (Weighted avg by sq ft - Property Management Reports)
Average Leverage: ${formatPercent(marketData.leverage)} (Debt-to-total capitalization - Loan Portfolio Summary)

PROPERTY-LEVEL PERFORMANCE:
Metro Office Complex NOI: $3,850,000 (Trailing 12-month actual - Property Financials Dec 2024)
Metro Office Occupancy: 94.2% (Leased SF / Total SF - Property Management Report)
Riverside Retail NOI: $2,240,000 (Trailing 12-month actual - Property Financials Dec 2024)
Riverside Retail Occupancy: 89.1% (Leased SF / Total SF - Property Management Report)
Industrial Park NOI: $4,920,000 (Trailing 12-month actual - Property Financials Dec 2024)
Industrial Park Occupancy: 97.8% (Leased SF / Total SF - Property Management Report)

=====================================
MARKET INTELLIGENCE & ASSUMPTIONS
=====================================

VALUATION METHODOLOGY:
Discount Rate: 12.0% (Risk-free rate + risk premium - Investment Committee Guidelines)
Exit Cap Rates: 4.5% - 6.5% (Based on property type/location - Historical Cap Rate Analysis)
Market Rent Growth: 2.5% annually (Long-term inflation + 50bps - Bureau of Labor Statistics)
Expense Growth: 3.0% annually (Historical average expense growth - Property Management Analysis)
Terminal Value: Direct Cap Method (Year 5 NOI / Exit Cap Rate - Valuation Standards)

MARKET DATA SOURCES:
Property Data: CoStar, CBRE (Subscription services - Third-party data providers)
Transaction Comps: RCA, Real Capital (Commercial transaction database - Market data subscription)
Economic Data: Bloomberg, Fed (Government and financial data - Federal Reserve FRED database)
Rent Surveys: JLL, C&W (Quarterly market surveys - Brokerage research reports)
Construction Costs: Marshall & Swift (Replacement cost manual - CoreLogic construction database)

WHAT-WHY-HOW INVESTMENT NARRATIVE:

WHAT: Coastal Oak Capital targets distressed commercial real estate assets across major US metropolitan markets through a disciplined value-add strategy.

WHY: Current market dislocation from interest rate volatility, bank lending contraction, and demographic shifts creates compelling acquisition opportunities at significant discounts to replacement cost.

HOW: Our experienced team leverages deep market relationships, operational expertise, and flexible capital to acquire underperforming assets, implement value-creation strategies, and generate superior risk-adjusted returns for investors.

=====================================
CONFIDENTIALITY NOTICE
=====================================

This document contains proprietary and confidential information of Coastal Oak Capital.
Distribution restricted to authorized General Partners only.
All data subject to quarterly updates and market verification.

© ${new Date().getFullYear()} Coastal Oak Capital. All rights reserved.
`;
    
    // Create downloadable Excel-like CSV file
    const blob = new Blob([excelContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `coastal_oak_capital_excel_reports_${new Date().getTime()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleRealExcelExport = async () => {
    if (userType !== 'gp') {
      toast.error('Excel export is restricted to General Partners only.');
      return;
    }
    
    try {
      toast.success('🚀 Exporting live Excel data with real-time market feeds...');
      
      // Fetch the latest Excel data from backend
      const response = await fetch(`${backendUrl}/api/excel/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Create downloadable file from the export data
        const exportContent = JSON.stringify(data.data, null, 2);
        const blob = new Blob([exportContent], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = data.filename || `coastal_oak_live_excel_${new Date().getTime()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        toast.success(`✅ Live Excel export completed successfully! (${data.size_mb.toFixed(2)} MB)`);
      } else {
        throw new Error('Export failed');
      }
    } catch (error) {
      console.error('Excel export error:', error);
      toast.error('Failed to export live Excel data. Please try again.');
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatPercent = (value) => {
    return `${value.toFixed(1)}%`;
  };

  // Prospectus sections data
  const prospectusData = {
    'executive-summary': {
      title: 'Executive Summary',
      content: (
        <div>
          <h3>Fund Overview</h3>
          <p>Coastal Oak Capital Fund I is a $500 million distressed and opportunistic real estate fund focused on acquiring underperforming commercial real estate assets across the United States. Our strategy targets office, retail, industrial, and multifamily properties in major metropolitan markets.</p>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', margin: '20px 0' }}>
            <div className="metric-card">
              <div className="metric-label">Target Fund Size</div>
              <div className="metric-value">$500M</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Investment Period</div>
              <div className="metric-value">5 Years</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Target Net IRR</div>
              <div className="metric-value">15-20%</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Target Multiple</div>
              <div className="metric-value">2.0x - 2.5x</div>
            </div>
          </div>
          
          <h4>Investment Thesis</h4>
          <p>Current market dislocation presents compelling opportunities for disciplined capital deployment in distressed commercial real estate. Our experienced team leverages deep market relationships and operational expertise to generate superior risk-adjusted returns.</p>
        </div>
      )
    },
    'investment-strategy': {
      title: 'Investment Strategy',
      content: (
        <div>
          <h3>Core Strategy</h3>
          <p>The Fund employs a disciplined approach to acquiring distressed and opportunistic real estate investments across multiple property types and geographic markets.</p>
          
          <div style={{ margin: '30px 0' }}>
            <h4>Investment Focus Areas</h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginTop: '20px' }}>
              <div className="insight-card">
                <h4>Distressed Acquisitions (60%)</h4>
                <ul>
                  <li>Properties in financial distress</li>
                  <li>Below replacement cost acquisitions</li>
                  <li>Foreclosure and REO opportunities</li>
                  <li>Value-add repositioning</li>
                </ul>
              </div>
              <div className="insight-card">
                <h4>Opportunistic Investments (40%)</h4>
                <ul>
                  <li>Off-market transactions</li>
                  <li>Strategic partnerships</li>
                  <li>Ground-up development</li>
                  <li>Major redevelopment projects</li>
                </ul>
              </div>
            </div>
          </div>
          
          <h4>Geographic Focus</h4>
          <p>Primary markets include Atlanta, Dallas, Phoenix, Denver, Nashville, and Charlotte, with selective investments in secondary markets with strong fundamentals.</p>
          
          <h4>Property Types</h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginTop: '20px' }}>
            <div style={{ padding: '15px', background: 'rgba(255,255,255,0.05)', borderRadius: '10px' }}>
              <strong>Office</strong><br/>25-30%
            </div>
            <div style={{ padding: '15px', background: 'rgba(255,255,255,0.05)', borderRadius: '10px' }}>
              <strong>Industrial</strong><br/>25-30%
            </div>
            <div style={{ padding: '15px', background: 'rgba(255,255,255,0.05)', borderRadius: '10px' }}>
              <strong>Retail</strong><br/>20-25%
            </div>
            <div style={{ padding: '15px', background: 'rgba(255,255,255,0.05)', borderRadius: '10px' }}>
              <strong>Multifamily</strong><br/>15-20%
            </div>
          </div>
        </div>
      )
    },
    'market-analysis': {
      title: 'Market Analysis',
      content: (
        <div>
          <h3>Market Conditions</h3>
          <p>Current market conditions present compelling opportunities for disciplined capital deployment in distressed commercial real estate assets.</p>
          
          <h4>Key Market Drivers</h4>
          <div style={{ margin: '20px 0' }}>
            <div className="insight-card" style={{ marginBottom: '15px' }}>
              <h4>Interest Rate Environment</h4>
              <p>Federal Reserve policy changes have created financing stress for leveraged property owners, creating acquisition opportunities for well-capitalized investors.</p>
            </div>
            <div className="insight-card" style={{ marginBottom: '15px' }}>
              <h4>Bank Lending Contraction</h4>
              <p>Tightening lending standards and regulatory pressure on regional banks have reduced capital availability, creating a favorable environment for private capital deployment.</p>
            </div>
            <div className="insight-card" style={{ marginBottom: '15px' }}>
              <h4>Demographic Shifts</h4>
              <p>Population migration to Sunbelt markets continues to drive demand for commercial real estate in our target markets.</p>
            </div>
          </div>
          
          <h4>Market Intelligence</h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginTop: '20px' }}>
            <div className="insight-card">
              <h4>Federal Reserve Update</h4>
              <p>Interest rates maintained at current levels. Distressed opportunities increasing in secondary markets with continued pressure on debt maturities.</p>
              <div className="insight-source">Source: Federal Reserve Economic Data</div>
            </div>
            <div className="insight-card">
              <h4>CBRE Market Report</h4>
              <p>Office sector showing signs of stabilization in key metropolitan areas. Industrial demand remains strong driven by e-commerce and supply chain shifts.</p>
              <div className="insight-source">Source: CBRE Research Q4 2024</div>
            </div>
            <div className="insight-card">
              <h4>Capital Markets Outlook</h4>
              <p>Lending standards continue to tighten, creating acquisition opportunities for well-capitalized funds with flexible capital structures.</p>
              <div className="insight-source">Source: Market Analysis</div>
            </div>
          </div>
        </div>
      )
    },
    'portfolio': {
      title: 'Portfolio Overview',
      content: (
        <div>
          <h3>Current Portfolio</h3>
          <p>The Fund has successfully deployed capital across {deals.length} high-quality commercial real estate investments.</p>
          
          <div style={{ margin: '20px 0' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
              <div className="metric-card">
                <div className="metric-label">Total Portfolio Value</div>
                <div className="metric-value">{formatCurrency(marketData.fundValue)}</div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Current Net IRR</div>
                <div className="metric-value">{formatPercent(marketData.irr)}</div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Portfolio Occupancy</div>
                <div className="metric-value">{formatPercent(marketData.occupancy)}</div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Average Leverage</div>
                <div className="metric-value">{formatPercent(marketData.leverage)}</div>
              </div>
            </div>
          </div>
          
          <h4>Active Investments</h4>
          <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '15px', padding: '25px', marginTop: '20px' }}>
            <div className="deals-table">
              <div className="table-header">
                <div>Property</div>
                <div>Type</div>
                <div>Status</div>
                <div>Value</div>
                <div>Acquired</div>
                <div>Net IRR</div>
              </div>
              
              {deals.map(deal => (
                <div key={deal.id} className="table-row">
                  <div style={{ fontWeight: '600' }}>{deal.name}</div>
                  <div>{deal.type}</div>
                  <div>
                    <span className={`status-badge ${deal.status.replace(' ', '-').toLowerCase()}`}>
                      {deal.status}
                    </span>
                  </div>
                  <div>{formatCurrency(deal.value)}</div>
                  <div>{deal.acquisition}</div>
                  <div>{formatPercent(deal.irr)}</div>
                </div>
              ))}
            </div>
          </div>
          
          <div style={{ marginTop: '30px' }}>
            <h4>Investment Highlights</h4>
            <ul style={{ marginLeft: '20px', lineHeight: '1.6' }}>
              <li>Diversified across property types and geographic markets</li>
              <li>Strong focus on value-add repositioning strategies</li>
              <li>Active asset management to optimize performance</li>
              <li>Conservative leverage profile with flexible capital structures</li>
            </ul>
          </div>
        </div>
      )
    },
    'financial-projections': {
      title: 'Financial Projections',
      content: (
        <div>
          <h3>Fund Performance Projections</h3>
          <p>Based on current market conditions and our investment pipeline, the Fund projects strong risk-adjusted returns for investors.</p>
          
          <h4>Target Returns</h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', margin: '20px 0' }}>
            <div className="metric-card">
              <div className="metric-label">Target Net IRR</div>
              <div className="metric-value">15-20%</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Target Equity Multiple</div>
              <div className="metric-value">2.0x - 2.5x</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Minimum Preferred Return</div>
              <div className="metric-value">8%</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Fund Life</div>
              <div className="metric-value">10 Years</div>
            </div>
          </div>
          
          <h4>Return Waterfall</h4>
          <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '15px', padding: '25px', marginTop: '20px' }}>
            <div style={{ marginBottom: '15px' }}>
              <strong>1. Return of Capital:</strong> 100% to Limited Partners
            </div>
            <div style={{ marginBottom: '15px' }}>
              <strong>2. Preferred Return:</strong> 8% annual cumulative preferred return to Limited Partners
            </div>
            <div style={{ marginBottom: '15px' }}>
              <strong>3. Catch-up:</strong> 100% to General Partner until GP has received 20% of total distributions
            </div>
            <div>
              <strong>4. Carried Interest:</strong> 80% to Limited Partners, 20% to General Partner
            </div>
          </div>
          
          <h4>Fee Structure</h4>
          <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '15px', padding: '25px', marginTop: '20px' }}>
            <div style={{ marginBottom: '15px' }}>
              <strong>Management Fee:</strong> 2.0% per annum of committed capital during investment period, 2.0% of invested capital thereafter
            </div>
            <div style={{ marginBottom: '15px' }}>
              <strong>Acquisition Fee:</strong> 1.0% of gross acquisition price
            </div>
            <div>
              <strong>Asset Management Fee:</strong> 0.25% per annum of gross asset value
            </div>
          </div>
          
          <div style={{ marginTop: '30px', padding: '20px', background: 'rgba(255,204,0,0.1)', borderRadius: '10px', border: '1px solid rgba(255,204,0,0.3)' }}>
            <strong>Important Notice:</strong> These projections are estimates based on current market conditions and assumptions. Actual results may vary significantly. Past performance does not guarantee future results.
          </div>
        </div>
      )
    },
    'risk-factors': {
      title: 'Risk Factors',
      content: (
        <div>
          <h3>Investment Risks</h3>
          <p>Investment in the Fund involves significant risks that could result in partial or total loss of capital. Prospective investors should carefully consider the following risk factors:</p>
          
          <div style={{ marginTop: '30px' }}>
            <div className="insight-card" style={{ marginBottom: '20px', background: 'rgba(255,99,99,0.1)', border: '1px solid rgba(255,99,99,0.3)' }}>
              <h4>Real Estate Market Risk</h4>
              <p>Commercial real estate markets are subject to significant volatility based on economic conditions, supply and demand dynamics, and regulatory changes. Property values may decline substantially.</p>
            </div>
            
            <div className="insight-card" style={{ marginBottom: '20px', background: 'rgba(255,99,99,0.1)', border: '1px solid rgba(255,99,99,0.3)' }}>
              <h4>Interest Rate Risk</h4>
              <p>Rising interest rates may negatively impact property valuations and increase financing costs. Variable rate debt may result in increased debt service obligations.</p>
            </div>
            
            <div className="insight-card" style={{ marginBottom: '20px', background: 'rgba(255,99,99,0.1)', border: '1px solid rgba(255,99,99,0.3)' }}>
              <h4>Liquidity Risk</h4>
              <p>Real estate investments are illiquid. Limited Partners will not be able to redeem their interests and must rely on distributions and ultimate liquidation of fund assets.</p>
            </div>
            
            <div className="insight-card" style={{ marginBottom: '20px', background: 'rgba(255,99,99,0.1)', border: '1px solid rgba(255,99,99,0.3)' }}>
              <h4>Leverage Risk</h4>
              <p>Use of debt financing magnifies both potential returns and losses. Highly leveraged investments may result in total loss of equity in adverse market conditions.</p>
            </div>
            
            <div className="insight-card" style={{ marginBottom: '20px', background: 'rgba(255,99,99,0.1)', border: '1px solid rgba(255,99,99,0.3)' }}>
              <h4>Operational Risk</h4>
              <p>Property operations may be adversely affected by tenant defaults, environmental issues, construction delays, regulatory changes, and natural disasters.</p>
            </div>
            
            <div className="insight-card" style={{ marginBottom: '20px', background: 'rgba(255,99,99,0.1)', border: '1px solid rgba(255,99,99,0.3)' }}>
              <h4>General Economic Risk</h4>
              <p>Economic recession, inflation, unemployment, and other macroeconomic factors may significantly impact real estate markets and fund performance.</p>
            </div>
          </div>
          
          <div style={{ marginTop: '30px', padding: '20px', background: 'rgba(255,99,99,0.1)', borderRadius: '10px', border: '1px solid rgba(255,99,99,0.3)' }}>
            <strong>WARNING:</strong> These risk factors are not exhaustive. Investors should carefully review all offering documents and consult with their advisors before making an investment decision.
          </div>
        </div>
      )
    },
    'management-team': {
      title: 'Management Team',
      content: (
        <div>
          <h3>Leadership Team</h3>
          <p>Coastal Oak Capital is led by an experienced team of real estate professionals with a proven track record of generating superior returns in distressed and opportunistic investments.</p>
          
          <div style={{ marginTop: '30px' }}>
            <div className="insight-card" style={{ marginBottom: '20px' }}>
              <h4>Michael Thompson, Managing Partner</h4>
              <p><strong>Experience:</strong> 20+ years in commercial real estate investment and development</p>
              <p><strong>Background:</strong> Former Principal at Blackstone Real Estate Partners, MBA from Wharton</p>
              <p><strong>Track Record:</strong> Led over $2 billion in real estate transactions across multiple cycles</p>
            </div>
            
            <div className="insight-card" style={{ marginBottom: '20px' }}>
              <h4>Sarah Chen, Investment Director</h4>
              <p><strong>Experience:</strong> 15+ years in real estate finance and capital markets</p>
              <p><strong>Background:</strong> Former Vice President at Goldman Sachs Real Estate Principal Investment Area</p>
              <p><strong>Expertise:</strong> Structured finance, debt restructuring, and distressed asset workouts</p>
            </div>
            
            <div className="insight-card" style={{ marginBottom: '20px' }}>
              <h4>David Rodriguez, Asset Management Director</h4>
              <p><strong>Experience:</strong> 18+ years in commercial real estate operations and asset management</p>
              <p><strong>Background:</strong> Former Senior Director at Brookfield Properties</p>
              <p><strong>Expertise:</strong> Property operations, leasing, capital improvements, and value creation</p>
            </div>
            
            <div className="insight-card" style={{ marginBottom: '20px' }}>
              <h4>Jennifer Walsh, Chief Financial Officer</h4>
              <p><strong>Experience:</strong> 12+ years in real estate accounting and fund administration</p>
              <p><strong>Background:</strong> Former Manager at KPMG Real Estate Practice, CPA</p>
              <p><strong>Expertise:</strong> Fund operations, investor reporting, and regulatory compliance</p>
            </div>
          </div>
          
          <h4>Advisory Board</h4>
          <p style={{ marginTop: '20px' }}>Our Advisory Board includes industry veterans with deep expertise in commercial real estate, capital markets, and institutional investing.</p>
          
          <div style={{ marginTop: '30px', padding: '20px', background: 'rgba(255,255,255,0.05)', borderRadius: '10px' }}>
            <strong>Combined Experience:</strong> The management team has a combined 65+ years of commercial real estate experience and has been involved in over $5 billion in real estate transactions.
          </div>
        </div>
      )
    },
    'legal-terms': {
      title: 'Legal Terms',
      content: (
        <div>
          <h3>Important Legal Information</h3>
          <p>This Private Placement Memorandum contains important legal terms and conditions governing investment in the Fund.</p>
          
          <div style={{ marginTop: '30px' }}>
            <h4>Securities Law Compliance</h4>
            <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '15px', padding: '25px', marginBottom: '20px' }}>
              <p>The securities offered hereby have not been registered under the Securities Act of 1933 or any state securities laws. These securities are being offered and sold in reliance on exemptions from the registration requirements.</p>
            </div>
            
            <h4>Investor Qualifications</h4>
            <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '15px', padding: '25px', marginBottom: '20px' }}>
              <ul style={{ marginLeft: '20px', lineHeight: '1.6' }}>
                <li>Accredited Investor status as defined under Rule 501 of Regulation D</li>
                <li>Minimum investment of $1,000,000</li>
                <li>Qualified Purchaser status for investments over $5,000,000</li>
                <li>Institutional investors must meet additional suitability requirements</li>
              </ul>
            </div>
            
            <h4>Fund Terms</h4>
            <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '15px', padding: '25px', marginBottom: '20px' }}>
              <div style={{ marginBottom: '15px' }}><strong>Fund Life:</strong> 10 years with two 1-year extensions</div>
              <div style={{ marginBottom: '15px' }}><strong>Investment Period:</strong> 5 years from first closing</div>
              <div style={{ marginBottom: '15px' }}><strong>Management Fee:</strong> 2.0% of committed capital</div>
              <div style={{ marginBottom: '15px' }}><strong>Carried Interest:</strong> 20% above 8% preferred return</div>
              <div><strong>Key Person Events:</strong> Michael Thompson and Sarah Chen</div>
            </div>
            
            <h4>Transfer Restrictions</h4>
            <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '15px', padding: '25px', marginBottom: '20px' }}>
              <p>Limited Partner interests may not be transferred without the prior written consent of the General Partner. Any permitted transfers must comply with applicable securities laws and fund documentation.</p>
            </div>
            
            <h4>Confidentiality</h4>
            <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '15px', padding: '25px', marginBottom: '20px' }}>
              <p>This document and all information contained herein is confidential and proprietary. Recipients agree to maintain confidentiality and may not reproduce or distribute without express written consent.</p>
            </div>
          </div>
          
          <div style={{ marginTop: '30px', padding: '20px', background: 'rgba(255,204,0,0.1)', borderRadius: '10px', border: '1px solid rgba(255,204,0,0.3)' }}>
            <strong>Legal Disclaimer:</strong> This summary does not constitute the complete legal terms of the Fund. Investors must review the complete Limited Partnership Agreement and other fund documents before investing.
          </div>
        </div>
      )
    }
  };

  const prospectusNav = [
    { id: 'executive-summary', label: 'Executive Summary' },
    { id: 'investment-strategy', label: 'Investment Strategy' },
    { id: 'market-analysis', label: 'Market Analysis' },
    { id: 'portfolio', label: 'Portfolio Overview' },
    { id: 'financial-projections', label: 'Financial Projections' },
    { id: 'risk-factors', label: 'Risk Factors' },
    { id: 'management-team', label: 'Management Team' },
    { id: 'legal-terms', label: 'Legal Terms' }
  ];

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div className="dashboard-logo">
          <h1>COASTAL OAK CAPITAL</h1>
          <p style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.7)', marginTop: '5px' }}>
            {currentView === 'dashboard' ? 'Real-Time Fund Performance Dashboard' : 
             currentView === 'prospectus' ? 'Investment Prospectus' : 
             'Institutional Excel Reports & Analytics'}
          </p>
        </div>
        
        <div className="dashboard-controls">
          <div className="view-toggle" style={{ display: 'flex', gap: '10px', marginRight: '20px' }}>
            <button 
              className={`toggle-button ${currentView === 'dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentView('dashboard')}
              style={{
                padding: '8px 16px',
                borderRadius: '20px',
                border: currentView === 'dashboard' ? '2px solid var(--coastal-primary)' : '2px solid rgba(255,255,255,0.2)',
                background: currentView === 'dashboard' ? 'rgba(0,128,128,0.3)' : 'transparent',
                color: 'white',
                cursor: 'pointer',
                fontSize: '0.9rem'
              }}
            >
              Dashboard
            </button>
            <button 
              className={`toggle-button ${currentView === 'prospectus' ? 'active' : ''}`}
              onClick={() => setCurrentView('prospectus')}
              style={{
                padding: '8px 16px',
                borderRadius: '20px',
                border: currentView === 'prospectus' ? '2px solid var(--coastal-primary)' : '2px solid rgba(255,255,255,0.2)',
                background: currentView === 'prospectus' ? 'rgba(0,128,128,0.3)' : 'transparent',
                color: 'white',
                cursor: 'pointer',
                fontSize: '0.9rem'
              }}
            >
              Prospectus
            </button>
            <button 
              className={`toggle-button ${currentView === 'excel' ? 'active' : ''}`}
              onClick={() => setCurrentView('excel')}
              style={{
                padding: '8px 16px',
                borderRadius: '20px',
                border: currentView === 'excel' ? '2px solid var(--coastal-primary)' : '2px solid rgba(255,255,255,0.2)',
                background: currentView === 'excel' ? 'rgba(0,128,128,0.3)' : 'transparent',
                color: 'white',
                cursor: 'pointer',
                fontSize: '0.9rem'
              }}
            >
              Excel Reports
            </button>
          </div>
          
          <div className={`user-badge ${userType === 'gp' ? 'gp' : ''}`}>
            {userType === 'gp' ? 'General Partner' : 'Limited Partner'}
          </div>
          
          {userType === 'gp' && currentView === 'dashboard' && (
            <button className="export-button" onClick={handleExport}>
              Export Data
            </button>
          )}
          
          {userType === 'gp' && currentView === 'prospectus' && (
            <button className="export-button" onClick={handleProspectusDownload}>
              Download Prospectus
            </button>
          )}
          
          {userType === 'gp' && currentView === 'excel' && (
            <button className="export-button" onClick={handleExcelExport}>
              Export Excel Data
            </button>
          )}
          
          <button className="logout-button" onClick={onLogout}>
            Logout
          </button>
        </div>
      </div>

      {/* Dashboard View */}
      {currentView === 'dashboard' && (
        <div className="dashboard-content">
          {/* Fund Overview */}
          <div style={{ marginBottom: '40px' }}>
            <h2 style={{ color: 'var(--coastal-text)', marginBottom: '20px', fontSize: '1.5rem' }}>
              Fund Performance Overview
            </h2>
            
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '20px',
              marginBottom: '30px'
            }}>
              <div className="metric-card">
                <div className="metric-label">Total Fund Value</div>
                <div className="metric-value">{formatCurrency(marketData.fundValue)}</div>
              </div>
              
              <div className="metric-card">
                <div className="metric-label">NAV per Share</div>
                <div className="metric-value">${marketData.nav.toFixed(2)}</div>
              </div>
              
              <div className="metric-card">
                <div className="metric-label">Net IRR</div>
                <div className="metric-value">{formatPercent(marketData.irr)}</div>
              </div>
              
              <div className="metric-card">
                <div className="metric-label">Total Return Multiple</div>
                <div className="metric-value">{marketData.multiple.toFixed(2)}x</div>
              </div>
              
              <div className="metric-card">
                <div className="metric-label">Portfolio Occupancy</div>
                <div className="metric-value">{formatPercent(marketData.occupancy)}</div>
              </div>
              
              <div className="metric-card">
                <div className="metric-label">Average Leverage</div>
                <div className="metric-value">{formatPercent(marketData.leverage)}</div>
              </div>
            </div>
            
            <div style={{ 
              fontSize: '0.8rem', 
              color: 'rgba(255,255,255,0.6)',
              textAlign: 'right'
            }}>
              Last Updated: {marketData.lastUpdate}
            </div>
          </div>

          {/* Active Deals */}
          <div>
            <h2 style={{ color: 'var(--coastal-text)', marginBottom: '20px', fontSize: '1.5rem' }}>
              Active Portfolio
            </h2>
            
            <div style={{ 
              background: 'rgba(255,255,255,0.05)',
              borderRadius: '15px',
              padding: '25px',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255,255,255,0.1)'
            }}>
              <div className="deals-table">
                <div className="table-header">
                  <div>Property</div>
                  <div>Type</div>
                  <div>Status</div>
                  <div>Value</div>
                  <div>Acquired</div>
                  <div>Net IRR</div>
                </div>
                
                {deals.map(deal => (
                  <div key={deal.id} className="table-row">
                    <div style={{ fontWeight: '600' }}>{deal.name}</div>
                    <div>{deal.type}</div>
                    <div>
                      <span className={`status-badge ${deal.status.replace(' ', '-').toLowerCase()}`}>
                        {deal.status}
                      </span>
                    </div>
                    <div>{formatCurrency(deal.value)}</div>
                    <div>{deal.acquisition}</div>
                    <div>{formatPercent(deal.irr)}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Market Insights */}
          <div style={{ marginTop: '40px' }}>
            <h2 style={{ color: 'var(--coastal-text)', marginBottom: '20px', fontSize: '1.5rem' }}>
              Market Intelligence
            </h2>
            
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '20px'
            }}>
              <div className="insight-card">
                <h3>Federal Reserve Update</h3>
                <p>Interest rates maintained at current levels. Distressed opportunities increasing in secondary markets.</p>
                <div className="insight-source">Source: Federal Reserve Economic Data</div>
              </div>
              
              <div className="insight-card">
                <h3>CBRE Market Report</h3>
                <p>Office sector showing signs of stabilization in key metropolitan areas. Industrial demand remains strong.</p>
                <div className="insight-source">Source: CBRE Research</div>
              </div>
              
              <div className="insight-card">
                <h3>Capital Markets</h3>
                <p>Lending standards tightening, creating acquisition opportunities for well-capitalized funds.</p>
                <div className="insight-source">Source: Market Analysis</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Prospectus View */}
      {currentView === 'prospectus' && (
        <div className="prospectus-container" style={{ display: 'flex', gap: '30px', height: 'calc(100vh - 120px)' }}>
          {/* Navigation Sidebar */}
          <div className="prospectus-nav" style={{
            minWidth: '250px',
            background: 'rgba(255,255,255,0.05)',
            borderRadius: '15px',
            padding: '20px',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255,255,255,0.1)',
            height: 'fit-content'
          }}>
            <h3 style={{ color: 'var(--coastal-text)', marginBottom: '20px', fontSize: '1.2rem' }}>
              Document Sections
            </h3>
            {prospectusNav.map(section => (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                style={{
                  display: 'block',
                  width: '100%',
                  padding: '12px 16px',
                  marginBottom: '8px',
                  background: activeSection === section.id ? 'rgba(0,128,128,0.3)' : 'transparent',
                  border: activeSection === section.id ? '1px solid var(--coastal-primary)' : '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  color: 'white',
                  textAlign: 'left',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  transition: 'all 0.3s ease'
                }}
              >
                {section.label}
              </button>
            ))}
            
            {userType === 'gp' && (
              <div style={{ marginTop: '30px', paddingTop: '20px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                <button 
                  className="export-button" 
                  onClick={handleProspectusDownload}
                  style={{ width: '100%', fontSize: '0.9rem' }}
                >
                  Download Full Document
                </button>
              </div>
            )}
            
            {userType === 'lp' && (
              <div style={{ marginTop: '30px', paddingTop: '20px', borderTop: '1px solid rgba(255,255,255,0.1)', fontSize: '0.8rem', color: 'rgba(255,255,255,0.6)' }}>
                Document download restricted to General Partners only.
              </div>
            )}
          </div>
          
          {/* Content Area */}
          <div className="prospectus-content" style={{
            flex: 1,
            background: 'rgba(255,255,255,0.05)',
            borderRadius: '15px',
            padding: '30px',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255,255,255,0.1)',
            overflowY: 'auto',
            maxHeight: 'calc(100vh - 140px)'
          }}>
            <h2 style={{ color: 'var(--coastal-text)', marginBottom: '30px', fontSize: '2rem', borderBottom: '2px solid var(--coastal-primary)', paddingBottom: '10px' }}>
              {prospectusData[activeSection].title}
            </h2>
            
            <div style={{ lineHeight: '1.6', fontSize: '1rem' }}>
              {prospectusData[activeSection].content}
            </div>
            
            <div style={{ 
              marginTop: '40px', 
              paddingTop: '20px', 
              borderTop: '1px solid rgba(255,255,255,0.1)',
              fontSize: '0.8rem', 
              color: 'rgba(255,255,255,0.6)',
              textAlign: 'center'
            }}>
              This document contains confidential and proprietary information. 
              Unauthorized distribution is prohibited.
              <br />
              © {new Date().getFullYear()} Coastal Oak Capital. All rights reserved.
            </div>
          </div>
        </div>
      )}

      {/* Excel Reports View */}
      {currentView === 'excel' && (
        <div className="excel-container" style={{ padding: '20px' }}>
          
          {loadingExcelData && (
            <div style={{ textAlign: 'center', color: 'white', padding: '40px' }}>
              <div style={{ fontSize: '1.2rem', marginBottom: '10px' }}>🔄 Loading Excel Analytics...</div>
              <div style={{ fontSize: '0.9rem', opacity: '0.7' }}>Fetching live data from Treasury, BLS, and internal systems</div>
            </div>
          )}

          {!loadingExcelData && excelSummary && (
            <div>
              {/* Header Section */}
              <div style={{ marginBottom: '30px' }}>
                <h2 style={{ color: 'var(--coastal-text)', fontSize: '1.8rem', marginBottom: '10px' }}>
                  📊 Institutional Excel Analytics
                </h2>
                <p style={{ fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)', marginBottom: '20px' }}>
                  Live data integration • Real-time KPIs • External market feeds • Data as of {excelSummary.as_of_date}
                </p>
                
                {userType === 'gp' && (
                  <button 
                    className="export-button" 
                    onClick={() => handleRealExcelExport()}
                    style={{ marginBottom: '20px' }}
                  >
                    🚀 Export Live Excel Data
                  </button>
                )}
                
                {userType === 'lp' && (
                  <div style={{ 
                    padding: '10px 20px', 
                    backgroundColor: 'rgba(255, 204, 0, 0.1)', 
                    border: '1px solid rgba(255, 204, 0, 0.3)', 
                    borderRadius: '8px',
                    fontSize: '0.9rem',
                    marginBottom: '20px'
                  }}>
                    ⚠️ Excel export functionality restricted to General Partners only
                  </div>
                )}
              </div>

              {/* KPI Dashboard */}
              <div style={{ marginBottom: '40px' }}>
                <h3 style={{ color: 'var(--coastal-text)', fontSize: '1.4rem', marginBottom: '20px' }}>
                  📈 Fund Performance KPIs (Live Data)
                </h3>
                
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '15px',
                  marginBottom: '30px'
                }}>
                  <div className="metric-card">
                    <div className="metric-label">Total AUM</div>
                    <div className="metric-value">{formatCurrency(excelSummary.aum)}</div>
                  </div>
                  
                  <div className="metric-card">
                    <div className="metric-label">NAV per Share</div>
                    <div className="metric-value">${excelSummary.kpis.fund.nav.toFixed(2)}</div>
                  </div>
                  
                  <div className="metric-card">
                    <div className="metric-label">Net IRR</div>
                    <div className="metric-value">{excelSummary.kpis.fund.net_irr.toFixed(1)}%</div>
                  </div>
                  
                  <div className="metric-card">
                    <div className="metric-label">Net MOIC</div>
                    <div className="metric-value">{excelSummary.kpis.fund.net_moic.toFixed(2)}x</div>
                  </div>
                  
                  <div className="metric-card">
                    <div className="metric-label">TVPI</div>
                    <div className="metric-value">{excelSummary.kpis.fund.tvpi.toFixed(2)}x</div>
                  </div>
                  
                  <div className="metric-card">
                    <div className="metric-label">WA LTV</div>
                    <div className="metric-value">{excelSummary.kpis.risk.wa_ltv.toFixed(1)}%</div>
                  </div>
                </div>
              </div>

              {/* Live Deals Grid */}
              <div style={{ marginBottom: '40px' }}>
                <h3 style={{ color: 'var(--coastal-text)', fontSize: '1.4rem', marginBottom: '20px' }}>
                  🏢 Deal Pipeline & Portfolio (Excel Grid View)
                </h3>
                
                <div style={{ 
                  background: 'rgba(255,255,255,0.05)',
                  borderRadius: '15px',
                  padding: '25px',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  overflow: 'auto'
                }}>
                  <div className="excel-grid" style={{
                    display: 'grid',
                    gridTemplateColumns: '2fr 1fr 1fr 1.5fr 1.5fr 1fr 1fr',
                    gap: '15px',
                    fontSize: '0.9rem'
                  }}>
                    {/* Header Row */}
                    <div style={{ fontWeight: 'bold', padding: '10px', background: 'rgba(0,128,128,0.2)', borderRadius: '5px' }}>Asset Name</div>
                    <div style={{ fontWeight: 'bold', padding: '10px', background: 'rgba(0,128,128,0.2)', borderRadius: '5px' }}>Status</div>
                    <div style={{ fontWeight: 'bold', padding: '10px', background: 'rgba(0,128,128,0.2)', borderRadius: '5px' }}>Market</div>
                    <div style={{ fontWeight: 'bold', padding: '10px', background: 'rgba(0,128,128,0.2)', borderRadius: '5px' }}>Strategy</div>
                    <div style={{ fontWeight: 'bold', padding: '10px', background: 'rgba(0,128,128,0.2)', borderRadius: '5px' }}>Equity ($M)</div>
                    <div style={{ fontWeight: 'bold', padding: '10px', background: 'rgba(0,128,128,0.2)', borderRadius: '5px' }}>IRR %</div>
                    <div style={{ fontWeight: 'bold', padding: '10px', background: 'rgba(0,128,128,0.2)', borderRadius: '5px' }}>MOIC x</div>
                    
                    {/* Data Rows */}
                    {excelSummary.deals.map(deal => (
                      <React.Fragment key={deal.id}>
                        <div style={{ padding: '10px', background: 'rgba(255,255,255,0.03)', borderRadius: '5px' }}>
                          {deal.name}
                        </div>
                        <div style={{ padding: '10px', background: 'rgba(255,255,255,0.03)', borderRadius: '5px' }}>
                          <span className={`status-badge ${deal.status}`} style={{
                            padding: '4px 8px',
                            borderRadius: '12px',
                            fontSize: '0.8rem',
                            backgroundColor: deal.status === 'active' ? 'rgba(0,200,0,0.2)' : 
                                           deal.status === 'pipeline' ? 'rgba(255,200,0,0.2)' : 'rgba(200,200,200,0.2)',
                            color: deal.status === 'active' ? '#00ff00' : 
                                   deal.status === 'pipeline' ? '#ffcc00' : '#cccccc'
                          }}>
                            {deal.status.charAt(0).toUpperCase() + deal.status.slice(1)}
                          </span>
                        </div>
                        <div style={{ padding: '10px', background: 'rgba(255,255,255,0.03)', borderRadius: '5px' }}>
                          {deal.market}
                        </div>
                        <div style={{ padding: '10px', background: 'rgba(255,255,255,0.03)', borderRadius: '5px' }}>
                          {deal.strategy.replace(/_/g, ' ')}
                        </div>
                        <div style={{ padding: '10px', background: 'rgba(255,255,255,0.03)', borderRadius: '5px' }}>
                          ${deal.equity_committed ? (deal.equity_committed / 1000000).toFixed(1) : 'TBD'}
                        </div>
                        <div style={{ padding: '10px', background: 'rgba(255,255,255,0.03)', borderRadius: '5px' }}>
                          {deal.irr ? deal.irr.toFixed(1) + '%' : 'TBD'}
                        </div>
                        <div style={{ padding: '10px', background: 'rgba(255,255,255,0.03)', borderRadius: '5px' }}>
                          {deal.moic ? deal.moic.toFixed(1) + 'x' : 'TBD'}
                        </div>
                      </React.Fragment>
                    ))}
                  </div>
                  
                  <div style={{ 
                    marginTop: '20px', 
                    padding: '15px',
                    background: 'rgba(0,128,128,0.1)',
                    borderRadius: '8px',
                    fontSize: '0.9rem'
                  }}>
                    <strong>Portfolio Summary:</strong> {excelSummary.kpis.pipeline.active_deals_count} Active • {excelSummary.kpis.pipeline.pipeline_deals_count} Pipeline • {excelSummary.kpis.pipeline.exited_deals_count} Exited
                  </div>
                </div>
              </div>

              {/* External Data Integration */}
              <div style={{ marginBottom: '40px' }}>
                <h3 style={{ color: 'var(--coastal-text)', fontSize: '1.4rem', marginBottom: '20px' }}>
                  🌍 External Market Data Integration
                </h3>
                
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                  gap: '20px'
                }}>
                  <div className="insight-card">
                    <h4>📊 Federal Reserve Data (FRED)</h4>
                    <div style={{ fontSize: '0.9rem', lineHeight: '1.6' }}>
                      <div><strong>10-Year Treasury:</strong> Live feed integration</div>
                      <div><strong>2-Year Treasury:</strong> Live feed integration</div>
                      <div><strong>3-Month Treasury:</strong> Live feed integration</div>
                      <div style={{ marginTop: '10px', color: 'rgba(255,255,255,0.7)' }}>
                        Data refreshed every 30 minutes from official Federal Reserve Economic Data API
                      </div>
                    </div>
                  </div>
                  
                  <div className="insight-card">
                    <h4>💹 Bureau of Labor Statistics</h4>
                    <div style={{ fontSize: '0.9rem', lineHeight: '1.6' }}>
                      <div><strong>Core CPI:</strong> Live inflation tracking</div>
                      <div><strong>CPI-U SA:</strong> Consumer price index</div>
                      <div><strong>YoY Inflation:</strong> Annual change calculation</div>
                      <div style={{ marginTop: '10px', color: 'rgba(255,255,255,0.7)' }}>
                        Official BLS data integration for real-time economic indicators
                      </div>
                    </div>
                  </div>
                  
                  <div className="insight-card">
                    <h4>🏦 Internal Fund Systems</h4>
                    <div style={{ fontSize: '0.9rem', lineHeight: '1.6' }}>
                      <div><strong>Property Management:</strong> Live occupancy data</div>
                      <div><strong>Accounting System:</strong> Real-time NAV calculation</div>
                      <div><strong>Valuation Reports:</strong> Quarterly mark-to-market</div>
                      <div style={{ marginTop: '10px', color: 'rgba(255,255,255,0.7)' }}>
                        Integrated internal systems for comprehensive fund performance tracking
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Methodology & Citations */}
              <div style={{ 
                marginTop: '40px', 
                padding: '20px', 
                background: 'rgba(255,255,255,0.03)', 
                borderRadius: '10px',
                border: '1px solid rgba(255,255,255,0.1)'
              }}>
                <h4 style={{ color: 'var(--coastal-text)', marginBottom: '15px' }}>📋 Data Sources & Methodology</h4>
                <div style={{ fontSize: '0.9rem', lineHeight: '1.6' }}>
                  <div style={{ marginBottom: '10px' }}>
                    <strong>External Sources:</strong> Federal Reserve Economic Data (FRED), Bureau of Labor Statistics (BLS), US Treasury Department
                  </div>
                  <div style={{ marginBottom: '10px' }}>
                    <strong>Calculation Methods:</strong> XIRR for IRR, DPI + RVPI for TVPI, Fair Value for NAV (ASC 820/IFRS 13)
                  </div>
                  <div style={{ marginBottom: '10px' }}>
                    <strong>Update Frequency:</strong> Real-time for fund metrics, 30-minute cache for external market data
                  </div>
                  <div style={{ color: 'rgba(255,255,255,0.7)' }}>
                    All data subject to quarterly independent verification and audit. For institutional use only.
                  </div>
                </div>
              </div>
            </div>
          )}

          {!loadingExcelData && !excelSummary && (
            <div style={{ textAlign: 'center', color: 'white', padding: '40px' }}>
              <div style={{ fontSize: '1.2rem', marginBottom: '10px' }}>⚠️ No Excel Data Available</div>
              <div style={{ fontSize: '0.9rem', opacity: '0.7' }}>Unable to connect to backend Excel analytics system</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Dashboard;