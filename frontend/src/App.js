import React, { useState } from 'react';

// === Backend base URL from env (no trailing slash) ===
const API_BASE = (process.env.REACT_APP_BACKEND_URL || '').replace(/\/$/, '');
const apiFetch = (path, opts) => fetch(path.startsWith('http') ? path : `${API_BASE}${path}`, opts);
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LiveDocument from './components/LiveDocument';
import LivingPitchDeck from './components/LivingPitchDeck';
import './App.css';

function App() {
  const [activeView, setActiveView] = useState('pitch-deck');

  return (
    <Router>
      <div className="App min-h-screen bg-slate-50">
        {/* Navigation Header */}
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex justify-between items-center">
              <h1 className="text-2xl font-bold text-slate-800">
                🏢 Coastal Oak Capital
              </h1>
              <div className="flex space-x-1 bg-slate-100 rounded-lg p-1">
                <button
                  onClick={() => setActiveView('pitch-deck')}
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${
                    activeView === 'pitch-deck'
                      ? 'bg-white text-slate-900 shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Living Pitch Deck
                </button>
                <button
                  onClick={() => setActiveView('legacy')}
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${
                    activeView === 'legacy'
                      ? 'bg-white text-slate-900 shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Legacy Viewer
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <div className="w-full">
          {activeView === 'pitch-deck' ? (
            <LivingPitchDeck />
          ) : (
            <div className="max-w-7xl mx-auto p-6">
              <LiveDocument />
            </div>
          )}
        </div>
        
        {/* Route-based navigation (for direct URLs) */}
        <Routes>
          {/* Ensure SPA calls use env-based backend; helper available as apiFetch */}
          <Route path="/legacy" element={<LiveDocument />} />
          <Route path="/live-document" element={<LiveDocument />} />
          <Route path="/pitch-deck" element={<LivingPitchDeck />} />
          <Route path="/" element={null} /> {/* Handled by state above */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
