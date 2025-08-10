import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';

const Dashboard = ({ userType, onLogout }) => {
  const [currentView, setCurrentView] = useState('dashboard'); // 'dashboard' or 'prospectus'
  const [activeSection, setActiveSection] = useState('executive-summary');
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

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div className="dashboard-logo">
          <h1>COASTAL OAK CAPITAL</h1>
          <p style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.7)', marginTop: '5px' }}>
            Real-Time Fund Performance Dashboard
          </p>
        </div>
        
        <div className="dashboard-controls">
          <div className={`user-badge ${userType === 'gp' ? 'gp' : ''}`}>
            {userType === 'gp' ? 'General Partner' : 'Limited Partner'}
          </div>
          
          {userType === 'gp' && (
            <button className="export-button" onClick={handleExport}>
              Export Data
            </button>
          )}
          
          <button className="logout-button" onClick={onLogout}>
            Logout
          </button>
        </div>
      </div>

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
    </div>
  );
};

export default Dashboard;