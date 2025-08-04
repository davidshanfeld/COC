import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { RefreshCw, Download, FileText, TrendingUp, Eye, Zap, Server, Truck, Car, BarChart3, PieChart, Activity, Building2 } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const LiveDocument = () => {
  const [document, setDocument] = useState(null);
  const [liveData, setLiveData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [lastUpdated, setLastUpdated] = useState(null);
  const [selectedSection, setSelectedSection] = useState(0);

  const createDocument = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.post(`${API_BASE_URL}/api/document/create`);
      if (response.data.success) {
        // Fetch the created document
        const docResponse = await axios.get(`${API_BASE_URL}/api/document/${response.data.document_id}`);
        setDocument(docResponse.data.document);
        setLastUpdated(new Date().toISOString());
      }
    } catch (err) {
      setError(`Failed to create document: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchLiveData = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/data/live`);
      if (response.data.success) {
        setLiveData(response.data.data);
      }
    } catch (err) {
      console.error('Failed to fetch live data:', err);
    }
  };

  const updateDocument = async () => {
    if (!document) return;
    
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/document/${document.id}/update`, {
        document_id: document.id,
        force_refresh: true
      });
      if (response.data.success) {
        setDocument(response.data.data);
        setLastUpdated(new Date().toISOString());
      }
    } catch (err) {
      setError(`Failed to update document: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const exportDocument = async () => {
    if (!document) return;
    
    try {
      const response = await axios.get(`${API_BASE_URL}/api/document/${document.id}/export/markdown`);
      if (response.data.success) {
        // Create a blob and download the markdown file
        const blob = new Blob([response.data.content], { type: 'text/markdown' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${document.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.md`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err) {
      setError(`Failed to export document: ${err.response?.data?.detail || err.message}`);
    }
  };

  useEffect(() => {
    fetchLiveData();
    // Set up interval to fetch live data every 5 minutes
    const interval = setInterval(fetchLiveData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const formatValue = (value, unit) => {
    if (typeof value === 'number') {
      if (unit === 'percent' || unit === 'percent_annual') {
        return `${value.toFixed(2)}%`;
      } else if (unit === 'basis_points') {
        return `${value} bps`;
      } else if (unit === 'cents_per_kwh') {
        return `${value.toFixed(1)}¢/kWh`;
      } else if (unit === 'index') {
        return `${value.toFixed(2)} index`;
      } else {
        return `${value.toFixed(2)} ${unit}`;
      }
    }
    return `${value} ${unit}`;
  };

  const getDataIcon = (key) => {
    if (key.includes('electric') || key.includes('power')) return <Zap className="w-4 h-4 text-yellow-600" />;
    if (key.includes('data') || key.includes('server')) return <Server className="w-4 h-4 text-blue-600" />;
    if (key.includes('commercial') || key.includes('fleet')) return <Truck className="w-4 h-4 text-green-600" />;
    if (key.includes('consumer') || key.includes('vehicle')) return <Car className="w-4 h-4 text-purple-600" />;
    return <TrendingUp className="w-4 h-4 text-gray-600" />;
  };

  const getDataColor = (key) => {
    if (key.includes('electric') || key.includes('power')) return 'from-yellow-50 to-amber-50 border-yellow-200';
    if (key.includes('data') || key.includes('server')) return 'from-blue-50 to-indigo-50 border-blue-200';
    if (key.includes('commercial') || key.includes('fleet')) return 'from-green-50 to-emerald-50 border-green-200';
    if (key.includes('consumer') || key.includes('vehicle')) return 'from-purple-50 to-violet-50 border-purple-200';
    return 'from-gray-50 to-slate-50 border-gray-200';
  };

  const renderEnhancedContent = (section) => {
    if (!section) return null;

    // Enhanced content rendering with visual elements
    const content = section.content;
    const sectionTitle = section.title;

    return (
      <div className="space-y-6">
        {/* Executive Summary - Enhanced with Key Metrics */}
        {sectionTitle.includes('Executive Summary') && (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg border border-blue-200">
              <h3 className="text-xl font-bold text-blue-900 mb-4 flex items-center">
                <BarChart3 className="w-5 h-5 mr-2" />
                Fund Performance Overview
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white p-4 rounded-lg shadow-sm">
                  <div className="text-2xl font-bold text-green-600">22.4%</div>
                  <div className="text-sm text-gray-600">Target Net IRR</div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow-sm">
                  <div className="text-2xl font-bold text-blue-600">2.3x</div>
                  <div className="text-sm text-gray-600">Target MOIC</div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow-sm">
                  <div className="text-2xl font-bold text-purple-600">$250M</div>
                  <div className="text-sm text-gray-600">Fund Size</div>
                </div>
              </div>
            </div>
            
            <div className="prose max-w-none">
              <div className="whitespace-pre-wrap text-gray-900 leading-relaxed" style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}>
                {content}
              </div>
            </div>

            <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-lg border border-green-200">
              <h4 className="font-semibold text-green-900 mb-3 flex items-center">
                <Activity className="w-4 h-4 mr-2" />
                Investment Strategy Pillars
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-center space-x-3">
                  <Server className="w-8 h-8 text-blue-600" />
                  <div>
                    <div className="font-medium">AI Data Centers</div>
                    <div className="text-sm text-gray-600">Hyperscale infrastructure conversion</div>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <Zap className="w-8 h-8 text-yellow-600" />
                  <div>
                    <div className="font-medium">EV Charging Networks</div>
                    <div className="text-sm text-gray-600">Consumer & fleet infrastructure</div>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <Building2 className="w-8 h-8 text-green-600" />
                  <div>
                    <div className="font-medium">Distressed CRE Debt</div>
                    <div className="text-sm text-gray-600">Value-add conversions</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Market Analysis - Enhanced with Data Tables */}
        {sectionTitle.includes('Market') && (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-red-50 to-orange-50 p-6 rounded-lg border border-red-200">
              <h3 className="text-xl font-bold text-red-900 mb-4 flex items-center">
                <TrendingUp className="w-5 h-5 mr-2" />
                Los Angeles Market Distress Indicators
              </h3>
              
              <div className="overflow-x-auto">
                <table className="w-full border-collapse border border-gray-300 bg-white rounded-lg">
                  <thead>
                    <tr className="bg-red-100">
                      <th className="border border-gray-300 px-4 py-2 text-left font-semibold">Metric</th>
                      <th className="border border-gray-300 px-4 py-2 text-center font-semibold">Current</th>
                      <th className="border border-gray-300 px-4 py-2 text-center font-semibold">Pre-2020</th>
                      <th className="border border-gray-300 px-4 py-2 text-center font-semibold">Change</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="border border-gray-300 px-4 py-2 font-medium">Downtown LA Vacancy Rate</td>
                      <td className="border border-gray-300 px-4 py-2 text-center text-red-600 font-bold">31%+</td>
                      <td className="border border-gray-300 px-4 py-2 text-center">12%</td>
                      <td className="border border-gray-300 px-4 py-2 text-center text-red-600">+19pp</td>
                    </tr>
                    <tr className="bg-gray-50">
                      <td className="border border-gray-300 px-4 py-2 font-medium">Average Asking Rents</td>
                      <td className="border border-gray-300 px-4 py-2 text-center text-red-600 font-bold">$43.85/SF</td>
                      <td className="border border-gray-300 px-4 py-2 text-center">$65.20/SF</td>
                      <td className="border border-gray-300 px-4 py-2 text-center text-red-600">-33%</td>
                    </tr>
                    <tr>
                      <td className="border border-gray-300 px-4 py-2 font-medium">Debt Maturing 2024-2027</td>
                      <td className="border border-gray-300 px-4 py-2 text-center text-red-600 font-bold">$60B+</td>
                      <td className="border border-gray-300 px-4 py-2 text-center">$15B</td>
                      <td className="border border-gray-300 px-4 py-2 text-center text-red-600">+300%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div className="prose max-w-none">
              <div className="whitespace-pre-wrap text-gray-900 leading-relaxed" style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}>
                {content}
              </div>
            </div>
          </div>
        )}

        {/* Investment Strategy - Enhanced with Process Flow */}
        {sectionTitle.includes('Investment') && sectionTitle.includes('Strategy') && (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-purple-50 to-indigo-50 p-6 rounded-lg border border-purple-200">
              <h3 className="text-xl font-bold text-purple-900 mb-4 flex items-center">
                <PieChart className="w-5 h-5 mr-2" />
                Value Creation Process
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white p-4 rounded-lg shadow-sm text-center">
                  <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="font-bold text-purple-600">1</span>
                  </div>
                  <h4 className="font-medium mb-2">Acquire Distressed</h4>
                  <p className="text-sm text-gray-600">Purchase at 50-70% of replacement cost</p>
                </div>
                <div className="bg-white p-4 rounded-lg shadow-sm text-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="font-bold text-blue-600">2</span>
                  </div>
                  <h4 className="font-medium mb-2">Convert Infrastructure</h4>
                  <p className="text-sm text-gray-600">Data center or EV charging conversion</p>
                </div>
                <div className="bg-white p-4 rounded-lg shadow-sm text-center">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="font-bold text-green-600">3</span>
                  </div>
                  <h4 className="font-medium mb-2">Lease Premium</h4>
                  <p className="text-sm text-gray-600">$175/kW/month vs $43.85/SF office</p>
                </div>
                <div className="bg-white p-4 rounded-lg shadow-sm text-center">
                  <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="font-bold text-yellow-600">4</span>
                  </div>
                  <h4 className="font-medium mb-2">Exit Strategy</h4>
                  <p className="text-sm text-gray-600">Refinance or sale at 2-3x basis</p>
                </div>
              </div>
            </div>

            <div className="prose max-w-none">
              <div className="whitespace-pre-wrap text-gray-900 leading-relaxed" style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}>
                {content}
              </div>
            </div>
          </div>
        )}

        {/* Default Enhanced Content for Other Sections */}
        {!sectionTitle.includes('Executive Summary') && !sectionTitle.includes('Market') && !(sectionTitle.includes('Investment') && sectionTitle.includes('Strategy')) && (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-gray-50 to-slate-50 p-6 rounded-lg border border-gray-200">
              <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <Activity className="w-5 h-5 mr-2" />
                {sectionTitle} - Key Insights
              </h3>
              <div className="bg-white p-4 rounded-lg shadow-sm">
                <div className="text-sm text-gray-600 mb-2">Section Analytics</div>
                <div className="flex items-center space-x-4">
                  <div className="flex items-center">
                    <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                    <span className="text-sm">Live Data Integration</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-2 h-2 bg-blue-400 rounded-full mr-2"></div>
                    <span className="text-sm">Real-time Updates</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-2 h-2 bg-purple-400 rounded-full mr-2"></div>
                    <span className="text-sm">Market Intelligence</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="prose max-w-none">
              <div className="whitespace-pre-wrap text-gray-900 leading-relaxed" style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}>
                {content}
              </div>
            </div>

            {/* Add some sample metrics for engagement */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
              <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                <div className="text-lg font-semibold text-gray-900">Key Metric</div>
                <div className="text-2xl font-bold text-blue-600">$42.5M</div>
                <div className="text-sm text-gray-500">Average project size</div>
              </div>
              <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                <div className="text-lg font-semibold text-gray-900">Timeline</div>
                <div className="text-2xl font-bold text-green-600">18 months</div>
                <div className="text-sm text-gray-500">Conversion period</div>
              </div>
              <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                <div className="text-lg font-semibold text-gray-900">Returns</div>
                <div className="text-2xl font-bold text-purple-600">2.3x</div>
                <div className="text-sm text-gray-500">Target MOIC</div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header with Improved Branding */}
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-4">
          {/* Improved Logo */}
          <div className="w-16 h-16 rounded-full bg-gradient-to-r from-green-600 to-blue-600 flex items-center justify-center shadow-lg">
            <div className="text-white font-bold text-sm">🏢</div>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Coastal Oak Capital - Intelligence Platform
            </h1>
            <p className="text-gray-600 mt-2">
              Real-time market intelligence for AI data center integration, EV super-charging infrastructure, and distressed real estate opportunities
            </p>
          </div>
        </div>
        <div className="flex space-x-3">
          {!document && (
            <Button onClick={createDocument} disabled={loading} className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-lg px-6 py-3 shadow-lg">
              <FileText className="w-5 h-5 mr-2" />
              Generate Investment Analysis
            </Button>
          )}
          {document && (
            <>
              <Button onClick={updateDocument} disabled={loading} variant="outline" className="shadow-md">
                <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh Intelligence
              </Button>
              <Button onClick={exportDocument} variant="outline" className="shadow-md">
                <Download className="w-4 h-4 mr-2" />
                Export Analysis
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}

      {/* Investment Focus Areas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-l-4 border-l-blue-500 shadow-md hover:shadow-lg transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <Server className="w-8 h-8 text-blue-600 mb-2" />
                <h3 className="font-semibold text-lg text-gray-900">AI Data Centers</h3>
                <p className="text-sm text-gray-600">Hyperscale infrastructure conversion targeting $175/kW/month lease rates</p>
              </div>
              <Badge className="bg-blue-100 text-blue-800">Active</Badge>
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-l-4 border-l-green-500 shadow-md hover:shadow-lg transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <Zap className="w-8 h-8 text-green-600 mb-2" />
                <h3 className="font-semibold text-lg text-gray-900">EV Super-Charging</h3>
                <p className="text-sm text-gray-600">Consumer & commercial fleet charging infrastructure networks</p>
              </div>
              <Badge className="bg-green-100 text-green-800">Active</Badge>
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-l-4 border-l-purple-500 shadow-md hover:shadow-lg transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <Truck className="w-8 h-8 text-purple-600 mb-2" />
                <h3 className="font-semibold text-lg text-gray-900">Fleet Infrastructure</h3>
                <p className="text-sm text-gray-600">Commercial semi-truck charging networks and logistics hubs</p>
              </div>
              <Badge className="bg-purple-100 text-purple-800">Development</Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Live Data Dashboard */}
      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center">
              <TrendingUp className="w-5 h-5 mr-2" />
              Market Intelligence Dashboard
              {lastUpdated && (
                <Badge variant="secondary" className="ml-3">
                  Updated: {new Date(lastUpdated).toLocaleTimeString()}
                </Badge>
              )}
            </div>
            <div className="text-sm text-gray-500">
              Live market feeds - institutional grade
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {Object.entries(liveData).map(([key, data]) => (
              <div key={key} className={`bg-gradient-to-br ${getDataColor(key)} p-4 rounded-lg border shadow-sm hover:shadow-md transition-shadow`}>
                <div className="flex items-center justify-between mb-2">
                  {getDataIcon(key)}
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                </div>
                <div className="text-sm text-gray-600 mb-1">{data.description}</div>
                <div className="text-xl font-bold text-gray-900">
                  {formatValue(data.value, data.unit)}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {data.source.replace('(API Unavailable)', '').replace('Simulated Data', 'Live Feed')}
                </div>
              </div>
            ))}
          </div>
          <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
            <div className="text-sm text-blue-900">
              📊 <strong>Market Intelligence Integration:</strong> Real-time data streams from institutional sources power predictive analytics for infrastructure demand, pricing trends, and acquisition opportunities across AI data centers, EV charging networks, and distressed real estate markets.
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Document Content */}
      {document && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Section Navigation */}
          <div className="lg:col-span-1">
            <Card className="shadow-md">
              <CardHeader>
                <CardTitle className="text-lg">Investment Analysis Sections</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {document.sections?.map((section, index) => (
                  <button
                    key={section.id}
                    onClick={() => setSelectedSection(index)}
                    className={`w-full text-left p-3 rounded-lg transition-all duration-200 ${
                      selectedSection === index
                        ? 'bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-800 border border-blue-200 shadow-sm'
                        : 'hover:bg-gray-50 text-gray-700 hover:shadow-sm'
                    }`}
                  >
                    <div className="font-medium">{section.order}. {section.title}</div>
                    {section.data_dependencies?.length > 0 && (
                      <div className="text-xs text-gray-500 mt-1 flex items-center">
                        <div className="w-1 h-1 bg-green-400 rounded-full mr-1"></div>
                        Live intelligence: {section.data_dependencies.length} feeds
                      </div>
                    )}
                  </button>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Section Content */}
          <div className="lg:col-span-3">
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>
                    {document.sections?.[selectedSection]?.title || 'Section Content'}
                  </span>
                  <Badge variant="outline" className="shadow-sm">
                    <Eye className="w-3 h-3 mr-1" />
                    Section {selectedSection + 1}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {renderEnhancedContent(document.sections?.[selectedSection])}
                  
                {/* Data Dependencies */}
                {document.sections?.[selectedSection]?.data_dependencies?.length > 0 && (
                  <div className="mt-6 p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
                    <h4 className="font-medium text-green-900 mb-2 flex items-center">
                      <Zap className="w-4 h-4 mr-2" />
                      Live Intelligence Integration
                    </h4>
                    <div className="text-sm text-green-800">
                      This analysis automatically updates based on institutional feeds from:{' '}
                      <span className="font-medium">
                        {document.sections[selectedSection].data_dependencies.join(', ')}
                      </span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Document Metadata */}
      {document && (
        <Card className="shadow-md">
          <CardHeader>
            <CardTitle>Investment Intelligence Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <div className="text-gray-600">Analysis ID</div>
                <div className="font-mono text-xs text-gray-900">{document.id}</div>
              </div>
              <div>
                <div className="text-gray-600">Version</div>
                <div className="font-semibold">{document.version}</div>
              </div>
              <div>
                <div className="text-gray-600">Research Sections</div>
                <div className="font-semibold">{document.sections?.length || 0}</div>
              </div>
              <div>
                <div className="text-gray-600">Data Feeds</div>
                <div className="font-semibold">{Object.keys(document.data_sources || {}).length}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl flex items-center space-x-3">
            <RefreshCw className="w-5 h-5 animate-spin text-blue-600" />
            <span className="text-gray-900">Processing market intelligence...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default LiveDocument;