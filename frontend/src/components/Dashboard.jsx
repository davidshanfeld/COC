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
            {currentView === 'dashboard' ? 'Real-Time Fund Performance Dashboard' : 'Investment Prospectus'}
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
    </div>
  );
};

export default Dashboard;