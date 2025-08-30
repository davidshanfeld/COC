import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Separator } from "./ui/separator";
import { 
  TrendingUp, 
  Database, 
  Zap, 
  Shield, 
  Users, 
  FileText, 
  Clock, 
  CheckCircle,
  AlertCircle,
  ArrowRight,
  BarChart3,
  Building2,
  Calculator,
  Download,
  Eye
} from 'lucide-react';

// Backend base via env with /api prefix enforced at call sites
const API_BASE = (process.env.REACT_APP_BACKEND_URL || '').replace(/\/$/, '');
const LivingPitchDeck = () => {
  const [activeAudience, setActiveAudience] = useState('LP');
  const [agentResults, setAgentResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [footnotes, setFootnotes] = useState({});
  const [currentRates, setCurrentRates] = useState(null);
  const [accessToken, setAccessToken] = useState(null);
  const [downloadMsg, setDownloadMsg] = useState("");
  const [rangeDays, setRangeDays] = useState(180);
  const [historyData, setHistoryData] = useState(null);
  const [slopeText, setSlopeText] = useState("");

  // State for new regulatory and FDIC features
  const [regulatoryData, setRegulatoryData] = useState({
    federal: [],
    state: [],
    municipal: []
  });
  const [fdicData, setFdicData] = useState({
    exposure: null,
    selectedBank: null
  });
  const [regulatoryLoading, setRegulatoryLoading] = useState(false);
  const [fdicLoading, setFdicLoading] = useState(false);
  const [selectedRegItem, setSelectedRegItem] = useState(null);
  const [selectedBankDetail, setSelectedBankDetail] = useState(null);

  // Fetch initial data on component mount
  async function fetchRatesHistory(days = 180) {
    try {
      const response = await apiFetch(`/api/rates/history?days=${days}`);
      const data = await response.json();
      if (data.success) {
        setHistoryData(data.data);
        // Compute slope context for 10Y series vs 6M and 1Y
        const series = data.data?.['10Y'] || [];
        if (series.length > 0) {
          const latest = series[series.length - 1];
          const sixIdx = Math.max(0, series.length - 130);
          const oneIdx = Math.max(0, series.length - 260);
          const sixM = series[sixIdx];
          const oneY = series[oneIdx];
          const slope6 = latest && sixM ? (latest.value - sixM.value) : 0;
          const slope12 = latest && oneY ? (latest.value - oneY.value) : 0;
          setSlopeText(`10Y vs 6M: ${(slope6>=0?'+':'')}${slope6.toFixed(2)} • 10Y vs 1Y: ${(slope12>=0?'+':'')}${slope12.toFixed(2)}`);
        } else {
          setSlopeText('');
        }
      }
    } catch (e) {
      console.error('Error fetching rate history:', e);
    }
  }

  useEffect(() => {
    fetchCurrentRates();
    fetchFootnotes();
    fetchRatesHistory(180);
    fetchRegulatoryData();
    fetchFdicData();
  }, []);

  const apiFetch = (path, opts) => fetch(path.startsWith('http') ? path : `${API_BASE}${path}`, opts);

  const fetchCurrentRates = async () => {
    try {
      const response = await apiFetch(`/api/rates`);
      const data = await response.json();
      if (data.success) {
        setCurrentRates(data.data);
      }
    } catch (error) {
      console.error('Error fetching rates:', error);
    }
  };

  const fetchFootnotes = async () => {
    try {
      const response = await apiFetch(`/api/footnotes`);
      const data = await response.json();
      if (data.success) {
        setFootnotes(data.data);
      }
    } catch (error) {
      console.error('Error fetching footnotes:', error);
    }
  };

  // New functions for regulatory and FDIC data
  const fetchRegulatoryData = async () => {
    setRegulatoryLoading(true);
    try {
      const [federal, state, municipal] = await Promise.all([
        apiFetch(`/api/regulatory/federal`).then(r => r.json()),
        apiFetch(`/api/regulatory/state`).then(r => r.json()),
        apiFetch(`/api/regulatory/municipal`).then(r => r.json())
      ]);
      
      setRegulatoryData({
        federal: federal.items || [],
        state: state.items || [],
        municipal: municipal.items || []
      });
    } catch (error) {
      console.error('Error fetching regulatory data:', error);
    } finally {
      setRegulatoryLoading(false);
    }
  };

  const fetchFdicData = async () => {
    setFdicLoading(true);
    try {
      const response = await apiFetch(`/api/fdic/exposure`);
      const data = await response.json();
      if (response.ok && data.rows) {
        setFdicData(prev => ({
          ...prev,
          exposure: {
            asOf: data.asOf,
            banks: data.rows,
            avgExposure: data.rows.reduce((sum, bank) => sum + bank.exposurePct, 0) / data.rows.length / 100,
            footnoteId: data.rows[0]?.footnoteId || 'B1'
          }
        }));
      }
    } catch (error) {
      console.error('Error fetching FDIC exposure data:', error);
    } finally {
      setFdicLoading(false);
    }
  };

  const fetchBankDetail = async (fdicCert) => {
    try {
      const response = await apiFetch(`/api/fdic/banks/${fdicCert}`);
      const data = await response.json();
      if (response.ok) {
        setSelectedBankDetail(data);
      }
    } catch (error) {
      console.error('Error fetching bank detail:', error);
    }
  };

  const executeAgents = async (objective, tags, inputs = {}) => {
    setLoading(true);
    try {
      const response = await apiFetch(`/api/agents/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          objective,
          audience: activeAudience,
          inputs,
          tags,
          security_tier: 'restricted'
        })
      });

      const data = await response.json();
      if (data.success) {
        setAgentResults(data.result.packets);
        // Update footnotes register
        if (data.result.footnote_register) {
          setFootnotes(prev => ({
            ...prev,
            register: data.result.footnote_register
          }));
        }
      }
    } catch (error) {
      console.error('Error executing agents:', error);
    } finally {
      setLoading(false);
    }
  };

  const requestDeckAccess = async () => {
    try {
      const response = await apiFetch(`/api/deck/request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'demo@coastaloakcapital.com',
          audience: activeAudience
        })
      });

      const data = await response.json();
      if (response.ok && data.token) {
        setAccessToken(data.token);
      }
    } catch (error) {
      console.error('Error requesting access:', error);
    }
  };

  const predefinedAnalyses = [
    {
      title: "Market Intelligence Dashboard",
      description: "Real-time market data with Treasury rates, Fed policy, and CRE distress indicators",
      tags: ["data", "charts", "ui"],
      icon: <TrendingUp className="h-5 w-5" />,
      inputs: { include_cre_data: true, include_fdic_data: true, chart_type: "market_overview" }
    },
    {
      title: "Data Center Investment Analysis", 
      description: "Complete feasibility and debt structuring analysis for data center development",
      tags: ["dev-dc", "debt-dc", "quant", "charts"],
      icon: <Database className="h-5 w-5" />,
      inputs: { project_size: 50000000, power_capacity_mw: 10, analysis_type: "dcf" }
    },
    {
      title: "EV Charging Infrastructure Study",
      description: "Development feasibility and financing analysis for EV supercharging network",
      tags: ["dev-ev", "debt-ev", "esg", "charts"],
      icon: <Zap className="h-5 w-5" />,
      inputs: { site_count: 5, stalls_per_site: 8, site_type: "highway" }
    },
    {
      title: "LA Zoning & Entitlements Roadmap",
      description: "Legal analysis and permitting timeline for Los Angeles development projects",
      tags: ["land-use", "risk", "esg"],
      icon: <Building2 className="h-5 w-5" />,
      inputs: { project_type: "data_center", zone: "M3-1" }
    },
    {
      title: "Fund Waterfall & Returns Analysis",
      description: "Quantitative modeling of LP/GP distributions with scenario analysis",
      tags: ["quant", "charts"],
      icon: <Calculator className="h-5 w-5" />,
      inputs: { 
        analysis_type: "waterfall", 
        mgmt_fee: 0.02, 
        pref: 0.08, 
        split_lp: 0.80, 
        gross_irr: 0.18 
      }
    },
    {
      title: "Risk Management Framework",
      description: "Comprehensive risk assessment with KRI monitoring and mitigation strategies", 
      tags: ["risk", "quant"],
      icon: <Shield className="h-5 w-5" />,
      inputs: { focus: "mixed" }
    },
    {
      title: "Red Team Investment Review",
      description: "Independent validation from LP and GP perspectives with scoring framework",
      tags: ["red-team"],
      icon: <Users className="h-5 w-5" />,
      inputs: { 
        executive_summary: true, 
        key_metrics: true, 
        data_sources: true,
        methodology: true,
        assumptions: true,
        scenarios: true,
        risks: true,
        market_analysis: true,
        financial_projections: true,
        risk_factors: true,
        management_team: true
      }
    }
  ];

  const formatFindings = (findings) => {
    if (typeof findings !== 'object') return findings;
    
    return Object.entries(findings).map(([key, value]) => (
      <div key={key} className="mb-2">
        <span className="font-semibold text-emerald-700 capitalize">
          {key.replace(/_/g, ' ')}:
        </span>
        <span className="ml-2">
          {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
        </span>
      </div>
    ));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50 to-slate-100 p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-slate-800 mb-2">
              🏢 Living Pitch Deck
            </h1>
            <p className="text-slate-600 text-lg">
              AI-Powered Investment Analysis Platform • Coastal Oak Capital
            </p>
          </div>
          
          {/* Audience Toggle */}
          <div className="flex items-center space-x-3">
            <span className="text-sm font-medium text-slate-600">Audience:</span>
            <div className="flex bg-white rounded-lg p-1 shadow-sm border">
              {['LP', 'GP', 'Internal'].map((audience) => (
                <button
                  key={audience}
                  onClick={() => setActiveAudience(audience)}
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${
                    activeAudience === audience
                      ? 'bg-emerald-600 text-white shadow-sm'
                      : 'text-slate-600 hover:text-emerald-600 hover:bg-emerald-50'
                  }`}
                >
                  {audience}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Current Market Data */}
      {currentRates && (
        <div className="max-w-7xl mx-auto mb-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BarChart3 className="h-5 w-5 mr-2 text-emerald-600" />
                Live Market Intelligence
              </CardTitle>
            </CardHeader>
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm text-slate-600">History window: {rangeDays}d</div>
          <div className="flex gap-2">
            {[180,365,730].map(d => (
              <button key={d} onClick={()=>{setRangeDays(d); fetchRatesHistory(d);}} className={`px-2 py-1 text-xs rounded border ${rangeDays===d?'bg-emerald-600 text-white':'bg-white text-slate-600'}`}>{d===180?'6M':d===365?'1Y':'2Y'}</button>
            ))}
          </div>
        </div>
        {slopeText && (
          <div className="text-xs text-slate-600 mb-4">Slope context: {slopeText}</div>
        )}

            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-4 rounded-lg">
                  <div className="text-sm text-blue-600 font-medium">10Y Treasury</div>
                  <div className="text-2xl font-bold text-blue-800">
                    {currentRates.treasury_rates?.['10Y']?.value?.toFixed(2)}%
                  </div>
                </div>
                <div className="bg-gradient-to-r from-green-50 to-green-100 p-4 rounded-lg">
                  <div className="text-sm text-green-600 font-medium">Fed Funds</div>
                  <div className="text-2xl font-bold text-green-800">
                    {currentRates.fed_funds_rate?.current?.toFixed(2)}%
                  </div>
                </div>
                <div className="bg-gradient-to-r from-purple-50 to-purple-100 p-4 rounded-lg">
                  <div className="text-sm text-purple-600 font-medium">5Y Treasury</div>
                  <div className="text-2xl font-bold text-purple-800">
                    {currentRates.treasury_rates?.['5Y']?.value?.toFixed(2)}%
                  </div>
                </div>
                <div className="bg-gradient-to-r from-orange-50 to-orange-100 p-4 rounded-lg">
                  <div className="text-sm text-orange-600 font-medium">30Y Treasury</div>
                  <div className="text-2xl font-bold text-orange-800">
                    {currentRates.treasury_rates?.['30Y']?.value?.toFixed(2)}%
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto">
        <Tabs defaultValue="analyses" className="w-full">
          <TabsList className="grid w-full grid-cols-6 mb-8">
            <TabsTrigger value="analyses">Investment Analyses</TabsTrigger>
            <TabsTrigger value="results">Agent Results</TabsTrigger>
            <TabsTrigger value="regulatory">Laws & Incentives Monitor</TabsTrigger>
            <TabsTrigger value="banks">Bank Exposure</TabsTrigger>
            <TabsTrigger value="footnotes">Data Sources</TabsTrigger>
            <TabsTrigger value="security">Secure Access</TabsTrigger>
          </TabsList>

          {/* Investment Analyses Tab */}
          <TabsContent value="analyses" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {predefinedAnalyses.map((analysis, index) => (
                <Card key={index} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <div className="flex items-center">
                        {analysis.icon}
                        <span className="ml-2">{analysis.title}</span>
                      </div>
                      <Badge variant="secondary" className="bg-emerald-100 text-emerald-700">
                        {activeAudience}
                      </Badge>
                    </CardTitle>
                    <CardDescription>{analysis.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2 mb-4">
                      {analysis.tags.map((tag) => (
                        <Badge key={tag} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                    <Button
                      onClick={() => executeAgents(analysis.title, analysis.tags, analysis.inputs)}
                      disabled={loading}
                      className="w-full bg-emerald-600 hover:bg-emerald-700"
                    >
                      {loading ? (
                        <>
                          <Clock className="h-4 w-4 mr-2 animate-spin" />
                          Executing Agents...
                        </>
                      ) : (
                        <>
                          Execute Analysis
                          <ArrowRight className="h-4 w-4 ml-2" />
                        </>
                      )}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Agent Results Tab */}
          <TabsContent value="results" className="space-y-6">
            {agentResults.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center">
                  <FileText className="h-12 w-12 mx-auto text-slate-400 mb-4" />
                  <h3 className="text-lg font-medium text-slate-600 mb-2">
                    No Analysis Results Yet
                  </h3>
                  <p className="text-slate-500">
                    Execute an investment analysis to see agent results here.
                  </p>
                </CardContent>
              </Card>
            ) : (
              agentResults.map((result, index) => (
                <Card key={index} className="overflow-hidden">
                  <CardHeader className="bg-gradient-to-r from-emerald-50 to-blue-50">
                    <CardTitle className="flex items-center justify-between">
                      <span>{result.executive_takeaway}</span>
                      <Badge className="bg-emerald-600 text-white">
                        v{result.version}
                      </Badge>
                    </CardTitle>
                    <CardDescription>{result.analysis}</CardDescription>
                  </CardHeader>
                  <CardContent className="pt-6">
                    {/* Findings */}
                    <div className="mb-6">
                      <h4 className="font-semibold text-slate-700 mb-3 flex items-center">
                        <TrendingUp className="h-4 w-4 mr-2" />
                        Key Findings
                      </h4>
                      <div className="bg-slate-50 p-4 rounded-lg text-sm">
                        {formatFindings(result.findings)}
                      </div>
                    </div>

                    {/* Recommendations */}
                    {result.recommendations && result.recommendations.length > 0 && (
                      <div className="mb-6">
                        <h4 className="font-semibold text-slate-700 mb-3 flex items-center">
                          <CheckCircle className="h-4 w-4 mr-2" />
                          Recommendations
                        </h4>
                        <ul className="space-y-2">
                          {result.recommendations.map((rec, i) => (
                            <li key={i} className="flex items-start">
                              <ArrowRight className="h-4 w-4 mt-0.5 mr-2 text-emerald-600 flex-shrink-0" />
                              <span className="text-sm">{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Quality Checks */}
                    {result.checks && result.checks.length > 0 && (
                      <div className="mb-6">
                        <h4 className="font-semibold text-slate-700 mb-3 flex items-center">
                          <Shield className="h-4 w-4 mr-2" />
                          Quality Assurance
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {result.checks.map((check, i) => (
                            <Badge key={i} variant="secondary" className="text-xs bg-green-100 text-green-700">
                              <CheckCircle className="h-3 w-3 mr-1" />
                              {check}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Errors */}
                    {result.errors && result.errors.length > 0 && (
                      <Alert className="border-orange-200 bg-orange-50">
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>
                          <strong>Notes:</strong> {result.errors.join(', ')}
                        </AlertDescription>
                      </Alert>
                    )}
                  </CardContent>
                </Card>
              ))
            )}
          </TabsContent>

          {/* Laws & Incentives Monitor Tab */}
          <TabsContent value="regulatory" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Federal Regulatory Pane */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Shield className="h-5 w-5 mr-2 text-blue-600" />
                    Federal Regulations
                  </CardTitle>
                  <CardDescription>
                    Federal incentives and compliance requirements
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {regulatoryLoading ? (
                    <div className="text-center py-8">
                      <Clock className="h-8 w-8 mx-auto text-slate-400 animate-spin mb-2" />
                      <p className="text-slate-500">Loading regulatory data...</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {regulatoryData.federal.map((item, index) => (
                        <div
                          key={index}
                          className="p-3 border border-slate-200 rounded-lg hover:bg-blue-50 cursor-pointer transition-colors"
                          onClick={() => setSelectedRegItem({ ...item, scope: 'federal' })}
                        >
                          <div className="flex justify-between items-start mb-2">
                            <Badge variant="secondary" className="bg-blue-100 text-blue-700 text-xs">
                              {item.code}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              FN: {item.footnoteId}
                            </Badge>
                          </div>
                          <h4 className="font-medium text-slate-800 text-sm mb-1">
                            {item.title}
                          </h4>
                          <p className="text-xs text-slate-600 line-clamp-2">
                            {item.summary}
                          </p>
                        </div>
                      ))}
                      {regulatoryData.federal.length === 0 && (
                        <p className="text-center text-slate-500 py-4">No federal items available</p>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* State Regulatory Pane */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Building2 className="h-5 w-5 mr-2 text-green-600" />
                    State Regulations
                  </CardTitle>
                  <CardDescription>
                    California state-level regulatory framework
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {regulatoryLoading ? (
                    <div className="text-center py-8">
                      <Clock className="h-8 w-8 mx-auto text-slate-400 animate-spin mb-2" />
                      <p className="text-slate-500">Loading regulatory data...</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {regulatoryData.state.map((item, index) => (
                        <div
                          key={index}
                          className="p-3 border border-slate-200 rounded-lg hover:bg-green-50 cursor-pointer transition-colors"
                          onClick={() => setSelectedRegItem({ ...item, scope: 'state' })}
                        >
                          <div className="flex justify-between items-start mb-2">
                            <Badge variant="secondary" className="bg-green-100 text-green-700 text-xs">
                              {item.code}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              FN: {item.footnoteId}
                            </Badge>
                          </div>
                          <h4 className="font-medium text-slate-800 text-sm mb-1">
                            {item.title}
                          </h4>
                          <p className="text-xs text-slate-600 line-clamp-2">
                            {item.summary}
                          </p>
                        </div>
                      ))}
                      {regulatoryData.state.length === 0 && (
                        <p className="text-center text-slate-500 py-4">No state items available</p>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Municipal Regulatory Pane */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Building2 className="h-5 w-5 mr-2 text-purple-600" />
                    Municipal Regulations
                  </CardTitle>
                  <CardDescription>
                    Los Angeles municipal requirements
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {regulatoryLoading ? (
                    <div className="text-center py-8">
                      <Clock className="h-8 w-8 mx-auto text-slate-400 animate-spin mb-2" />
                      <p className="text-slate-500">Loading regulatory data...</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {regulatoryData.municipal.map((item, index) => (
                        <div
                          key={index}
                          className="p-3 border border-slate-200 rounded-lg hover:bg-purple-50 cursor-pointer transition-colors"
                          onClick={() => setSelectedRegItem({ ...item, scope: 'municipal' })}
                        >
                          <div className="flex justify-between items-start mb-2">
                            <Badge variant="secondary" className="bg-purple-100 text-purple-700 text-xs">
                              {item.code}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              FN: {item.footnoteId}
                            </Badge>
                          </div>
                          <h4 className="font-medium text-slate-800 text-sm mb-1">
                            {item.title}
                          </h4>
                          <p className="text-xs text-slate-600 line-clamp-2">
                            {item.summary}
                          </p>
                        </div>
                      ))}
                      {regulatoryData.municipal.length === 0 && (
                        <p className="text-center text-slate-500 py-4">No municipal items available</p>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Regulatory Item Detail Drawer */}
            {selectedRegItem && (
              <Card className="mt-6 border-2 border-emerald-200">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <CardTitle className="flex items-center">
                      <FileText className="h-5 w-5 mr-2 text-emerald-600" />
                      {selectedRegItem.title}
                    </CardTitle>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setSelectedRegItem(null)}
                    >
                      ✕
                    </Button>
                  </div>
                  <CardDescription>
                    <Badge className="mr-2 bg-slate-100 text-slate-700">
                      {selectedRegItem.scope.toUpperCase()}
                    </Badge>
                    <Badge variant="outline">
                      {selectedRegItem.code}
                    </Badge>
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-semibold text-slate-700 mb-2">Summary</h4>
                      <p className="text-sm text-slate-600">{selectedRegItem.summary}</p>
                    </div>
                    
                    {selectedRegItem.citations && selectedRegItem.citations.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-slate-700 mb-2">Legal Citations</h4>
                        <div className="space-y-1">
                          {selectedRegItem.citations.map((citation, index) => (
                            <div key={index} className="text-sm text-slate-600 bg-slate-50 p-2 rounded">
                              {citation}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    <div className="flex items-center pt-2 border-t">
                      <Badge variant="outline" className="text-xs">
                        Footnote: {selectedRegItem.footnoteId}
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Bank Exposure Tab */}
          <TabsContent value="banks" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="h-5 w-5 mr-2 text-orange-600" />
                  FDIC Bank CRE Exposure Analysis
                </CardTitle>
                <CardDescription>
                  Commercial real estate exposure across major banking institutions
                </CardDescription>
              </CardHeader>
              <CardContent>
                {fdicLoading ? (
                  <div className="text-center py-12">
                    <Clock className="h-12 w-12 mx-auto text-slate-400 animate-spin mb-4" />
                    <p className="text-slate-500">Loading FDIC exposure data...</p>
                  </div>
                ) : fdicData.exposure ? (
                  <div className="space-y-6">
                    {/* Summary Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="bg-gradient-to-r from-orange-50 to-orange-100 p-4 rounded-lg">
                        <div className="text-sm text-orange-600 font-medium">Total Banks</div>
                        <div className="text-2xl font-bold text-orange-800">
                          {fdicData.exposure.banks?.length || 0}
                        </div>
                      </div>
                      <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-4 rounded-lg">
                        <div className="text-sm text-blue-600 font-medium">Avg CRE Exposure</div>
                        <div className="text-2xl font-bold text-blue-800">
                          {fdicData.exposure.avgExposure ? 
                            (fdicData.exposure.avgExposure * 100).toFixed(1) + '%' : 
                            'N/A'
                          }
                        </div>
                      </div>
                      <div className="bg-gradient-to-r from-green-50 to-green-100 p-4 rounded-lg">
                        <div className="text-sm text-green-600 font-medium">Footnote</div>
                        <div className="text-lg font-bold text-green-800">
                          {fdicData.exposure.footnoteId || 'B1'}
                        </div>
                      </div>
                    </div>

                    {/* Bank Exposure Table */}
                    <div className="overflow-x-auto">
                      <table className="w-full border-collapse border border-slate-200">
                        <thead>
                          <tr className="bg-slate-50">
                            <th className="border border-slate-200 px-4 py-3 text-left text-sm font-medium text-slate-700">
                              Bank Name
                            </th>
                            <th className="border border-slate-200 px-4 py-3 text-center text-sm font-medium text-slate-700">
                              Total Exposure
                            </th>
                            <th className="border border-slate-200 px-4 py-3 text-center text-sm font-medium text-slate-700">
                              Multifamily
                            </th>
                            <th className="border border-slate-200 px-4 py-3 text-center text-sm font-medium text-slate-700">
                              Office
                            </th>
                            <th className="border border-slate-200 px-4 py-3 text-center text-sm font-medium text-slate-700">
                              Industrial
                            </th>
                            <th className="border border-slate-200 px-4 py-3 text-center text-sm font-medium text-slate-700">
                              Other
                            </th>
                            <th className="border border-slate-200 px-4 py-3 text-center text-sm font-medium text-slate-700">
                              Actions
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          {(fdicData.exposure.banks || []).map((bank, index) => (
                            <tr key={index} className="hover:bg-slate-50">
                              <td className="border border-slate-200 px-4 py-3 text-sm font-medium text-slate-800">
                                {bank.bankName}
                              </td>
                              <td className="border border-slate-200 px-4 py-3 text-center text-sm">
                                <Badge className="bg-orange-100 text-orange-800">
                                  {(bank.exposurePct * 100).toFixed(1)}%
                                </Badge>
                              </td>
                              <td className="border border-slate-200 px-4 py-3 text-center text-sm">
                                {bank.stack?.mf ? (bank.stack.mf * 100).toFixed(1) + '%' : 'N/A'}
                              </td>
                              <td className="border border-slate-200 px-4 py-3 text-center text-sm">
                                {bank.stack?.off ? (bank.stack.off * 100).toFixed(1) + '%' : 'N/A'}
                              </td>
                              <td className="border border-slate-200 px-4 py-3 text-center text-sm">
                                {bank.stack?.ind ? (bank.stack.ind * 100).toFixed(1) + '%' : 'N/A'}
                              </td>
                              <td className="border border-slate-200 px-4 py-3 text-center text-sm">
                                {bank.stack?.other ? (bank.stack.other * 100).toFixed(1) + '%' : 'N/A'}
                              </td>
                              <td className="border border-slate-200 px-4 py-3 text-center">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => {
                                    fetchBankDetail(bank.bankId);
                                    setFdicData(prev => ({ ...prev, selectedBank: bank }));
                                  }}
                                  className="text-xs"
                                >
                                  <Eye className="h-3 w-3 mr-1" />
                                  Details
                                </Button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <BarChart3 className="h-12 w-12 mx-auto text-slate-400 mb-4" />
                    <p className="text-slate-500">No FDIC exposure data available</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Bank Detail Modal/Card */}
            {selectedBankDetail && fdicData.selectedBank && (
              <Card className="mt-6 border-2 border-blue-200">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <CardTitle className="flex items-center">
                      <Building2 className="h-5 w-5 mr-2 text-blue-600" />
                      {selectedBankDetail.bank?.bankName || 'Bank Details'}
                    </CardTitle>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setSelectedBankDetail(null);
                        setFdicData(prev => ({ ...prev, selectedBank: null }));
                      }}
                    >
                      ✕
                    </Button>
                  </div>
                  <CardDescription>
                    FDIC Cert: {selectedBankDetail.bank?.bankId} | 
                    Total Assets: ${(selectedBankDetail.bank?.details?.assets_total / 1e9).toFixed(1)}B
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {/* Key Metrics */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="bg-blue-50 p-3 rounded-lg">
                        <div className="text-xs text-blue-600 font-medium">CRE Exposure</div>
                        <div className="text-lg font-bold text-blue-800">
                          {(selectedBankDetail.bank?.exposurePct || 0).toFixed(1)}%
                        </div>
                      </div>
                      <div className="bg-green-50 p-3 rounded-lg">
                        <div className="text-xs text-green-600 font-medium">Total Assets</div>
                        <div className="text-lg font-bold text-green-800">
                          ${(selectedBankDetail.bank?.details?.assets_total / 1e9 || 0).toFixed(1)}B
                        </div>
                      </div>
                      <div className="bg-purple-50 p-3 rounded-lg">
                        <div className="text-xs text-purple-600 font-medium">Tier 1 Capital</div>
                        <div className="text-lg font-bold text-purple-800">
                          {selectedBankDetail.bank?.details?.risk_metrics?.tier1_capital_ratio?.toFixed(1) || 'N/A'}%
                        </div>
                      </div>
                      <div className="bg-orange-50 p-3 rounded-lg">
                        <div className="text-xs text-orange-600 font-medium">Last Update</div>
                        <div className="text-lg font-bold text-orange-800">
                          {selectedBankDetail.asOf ? 
                            new Date(selectedBankDetail.asOf).toLocaleDateString() : 
                            'N/A'
                          }
                        </div>
                      </div>
                    </div>

                    {/* Quarterly Trends */}
                    {selectedBankDetail.bank?.details?.quarterly_trend && (
                      <div>
                        <h4 className="font-semibold text-slate-700 mb-3">Quarterly CRE Exposure Trends</h4>
                        <div className="overflow-x-auto">
                          <table className="w-full text-sm">
                            <thead>
                              <tr className="bg-slate-100">
                                <th className="px-3 py-2 text-left">Quarter</th>
                                <th className="px-3 py-2 text-center">CRE Exposure %</th>
                              </tr>
                            </thead>
                            <tbody>
                              {selectedBankDetail.bank.details.quarterly_trend.map((trend, index) => (
                                <tr key={index} className="border-t">
                                  <td className="px-3 py-2">{trend.quarter}</td>
                                  <td className="px-3 py-2 text-center">
                                    {(trend.exposure_pct).toFixed(1)}%
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}

                    <div className="flex items-center pt-4 border-t">
                      <Badge variant="outline" className="text-xs">
                        Footnote: {selectedBankDetail.bank?.footnoteId || 'B1'}
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Data Sources Tab */}
          <TabsContent value="footnotes" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileText className="h-5 w-5 mr-2" />
                  Data Sources & Citations
                </CardTitle>
                <CardDescription>
                  All data sources with refresh policies and provenance tracking
                </CardDescription>
              </CardHeader>
              <CardContent>
                {footnotes.footnotes ? (
                  <div className="space-y-4">
                    {footnotes.footnotes.map((footnote, index) => (
                      <div key={index} className="border-l-4 border-emerald-500 pl-4 py-2 bg-slate-50 rounded-r-lg">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="font-semibold text-slate-800">
                              [{footnote.id}] {footnote.label}
                            </div>
                            <div className="text-sm text-slate-600 mt-1">
                              Source: {footnote.source}
                            </div>
                            <div className="text-sm text-slate-500 mt-1">
                              Transform: {footnote.transform}
                            </div>
                          </div>
                          <div className="text-xs text-slate-500">
                            <div>Refresh: {footnote.refresh}</div>
                            <div>Updated: {new Date(footnote.retrieved_at).toLocaleDateString()}</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-slate-500">
                    No footnotes available yet. Execute an analysis to generate data source citations.
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value="security" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Shield className="h-5 w-5 mr-2" />
                  Secure Access & Distribution
                </CardTitle>
                <CardDescription>
                  Single-use tokens and watermarked document distribution
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <Button 
                    onClick={requestDeckAccess}
                    className="w-full bg-blue-600 hover:bg-blue-700"
                  >
                    <Eye className="h-4 w-4 mr-2" />
                    Request Secure Access Token
                  </Button>
                  
                  {accessToken && (
                    <Alert className="border-green-200 bg-green-50">
                      <CheckCircle className="h-4 w-4" />
                      <AlertDescription>
                        <div className="font-semibold">Access Token Generated</div>
                        <div className="font-mono text-sm mt-2 p-2 bg-white rounded border">
                          {accessToken}
                        </div>
                        <div className="text-xs mt-2 text-green-700">
                          Token expires in 24 hours and is single-use for {activeAudience} access.
                        </div>
                      </AlertDescription>
                    </Alert>
                  )}
                  
                  <Separator />
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Button variant="outline" className="w-full">
                      <Download className="h-4 w-4 mr-2" />
                      Export Watermarked PDF
                    </Button>
                    <Button variant="outline" className="w-full">
                      <FileText className="h-4 w-4 mr-2" />
                      Generate Audit Report
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default LivingPitchDeck;