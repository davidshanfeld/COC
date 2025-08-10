import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './components/LoginPage';
import LegalDisclaimer from './components/LegalDisclaimer';
import Dashboard from './components/Dashboard';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [hasAcceptedTerms, setHasAcceptedTerms] = useState(false);
  const [userType, setUserType] = useState('lp'); // 'lp' or 'gp'
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session
    const authStatus = localStorage.getItem('coastal_oak_auth');
    const termsStatus = localStorage.getItem('coastal_oak_terms');
    const userTypeStored = localStorage.getItem('coastal_oak_user_type');
    
    if (authStatus === 'true') {
      setIsAuthenticated(true);
    }
    if (termsStatus === 'true') {
      setHasAcceptedTerms(true);
    }
    if (userTypeStored) {
      setUserType(userTypeStored);
    }
    setLoading(false);
  }, []);

  const handleLogin = (type) => {
    setIsAuthenticated(true);
    setUserType(type);
    localStorage.setItem('coastal_oak_auth', 'true');
    localStorage.setItem('coastal_oak_user_type', type);
  };

  const handleTermsAcceptance = () => {
    setHasAcceptedTerms(true);
    localStorage.setItem('coastal_oak_terms', 'true');
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setHasAcceptedTerms(false);
    setUserType('lp');
    localStorage.removeItem('coastal_oak_auth');
    localStorage.removeItem('coastal_oak_terms');
    localStorage.removeItem('coastal_oak_user_type');
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="coastal-oak-logo">
          <div className="logo-animation"></div>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={
            !isAuthenticated ? 
            <LoginPage onLogin={handleLogin} /> : 
            <Navigate to="/disclaimer" replace />
          } />
          
          <Route path="/disclaimer" element={
            isAuthenticated && !hasAcceptedTerms ? 
            <LegalDisclaimer onAccept={handleTermsAcceptance} userType={userType} /> : 
            isAuthenticated && hasAcceptedTerms ? 
            <Navigate to="/dashboard" replace /> :
            <Navigate to="/login" replace />
          } />
          
          <Route path="/dashboard" element={
            isAuthenticated && hasAcceptedTerms ? 
            <Dashboard userType={userType} onLogout={handleLogout} /> : 
            <Navigate to="/login" replace />
          } />
          
          <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
        <ToastContainer position="top-right" theme="dark" />
      </div>
    </Router>
  );
}

export default App;