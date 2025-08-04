import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { RefreshCw, Download, FileText, TrendingUp, Eye } from 'lucide-react';

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
      } else {
        return `${value.toFixed(2)} ${unit}`;
      }
    }
    return `${value} ${unit}`;
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Coastal Oak Capital - Living Master Deck System
          </h1>
          <p className="text-gray-600 mt-2">
            Comprehensive real-time master deck with AI data center integration, cryptocurrency insights, and daily market data refresh
          </p>
        </div>
        <div className="flex space-x-3">
          {!document && (
            <Button onClick={createDocument} disabled={loading} className="bg-blue-600 hover:bg-blue-700">
              <FileText className="w-4 h-4 mr-2" />
              Create Master Deck
            </Button>
          )}
          {document && (
            <>
              <Button onClick={updateDocument} disabled={loading} variant="outline">
                <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Update Data
              </Button>
              <Button onClick={exportDocument} variant="outline">
                <Download className="w-4 h-4 mr-2" />
                Export Markdown
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

      {/* Live Data Dashboard */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <TrendingUp className="w-5 h-5 mr-2" />
            Real-Time Market Data
            {lastUpdated && (
              <Badge variant="secondary" className="ml-3">
                Updated: {new Date(lastUpdated).toLocaleTimeString()}
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {Object.entries(liveData).map(([key, data]) => (
              <div key={key} className="bg-gray-50 p-3 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">{data.description}</div>
                <div className="text-lg font-semibold text-gray-900">
                  {formatValue(data.value, data.unit)}
                </div>
                <div className="text-xs text-gray-500 mt-1">{data.source}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Document Content */}
      {document && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Section Navigation */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Table of Contents</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {document.sections?.map((section, index) => (
                  <button
                    key={section.id}
                    onClick={() => setSelectedSection(index)}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      selectedSection === index
                        ? 'bg-blue-100 text-blue-800 border border-blue-200'
                        : 'hover:bg-gray-50 text-gray-700'
                    }`}
                  >
                    <div className="font-medium">{section.order}. {section.title}</div>
                    {section.data_dependencies?.length > 0 && (
                      <div className="text-xs text-gray-500 mt-1">
                        Live data: {section.data_dependencies.length} sources
                      </div>
                    )}
                  </button>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Section Content */}
          <div className="lg:col-span-3">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>
                    {document.sections?.[selectedSection]?.title || 'Section Content'}
                  </span>
                  <Badge variant="outline">
                    <Eye className="w-3 h-3 mr-1" />
                    Section {selectedSection + 1}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose max-w-none">
                  <div 
                    className="whitespace-pre-wrap text-gray-900 leading-relaxed"
                    style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
                  >
                    {document.sections?.[selectedSection]?.content || 'Select a section to view content'}
                  </div>
                  
                  {/* Data Dependencies */}
                  {document.sections?.[selectedSection]?.data_dependencies?.length > 0 && (
                    <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                      <h4 className="font-medium text-blue-900 mb-2">Live Data Integration</h4>
                      <div className="text-sm text-blue-800">
                        This section automatically updates based on:{' '}
                        {document.sections[selectedSection].data_dependencies.join(', ')}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Document Metadata */}
      {document && (
        <Card>
          <CardHeader>
            <CardTitle>Document Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <div className="text-gray-600">Document ID</div>
                <div className="font-mono text-xs text-gray-900">{document.id}</div>
              </div>
              <div>
                <div className="text-gray-600">Version</div>
                <div className="font-semibold">{document.version}</div>
              </div>
              <div>
                <div className="text-gray-600">Sections</div>
                <div className="font-semibold">{document.sections?.length || 0}</div>
              </div>
              <div>
                <div className="text-gray-600">Data Sources</div>
                <div className="font-semibold">{Object.keys(document.data_sources || {}).length}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg flex items-center space-x-3">
            <RefreshCw className="w-5 h-5 animate-spin text-blue-600" />
            <span className="text-gray-900">Processing...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default LiveDocument;