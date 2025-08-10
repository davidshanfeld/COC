import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';

const LoginPage = ({ onLogin }) => {
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Disable keyboard shortcuts and dev tools
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Disable F12, Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+U, Ctrl+S, Ctrl+A, Ctrl+C, Ctrl+V
      if (
        e.key === 'F12' ||
        (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'J')) ||
        (e.ctrlKey && (e.key === 'u' || e.key === 'U')) ||
        (e.ctrlKey && (e.key === 's' || e.key === 'S')) ||
        (e.ctrlKey && (e.key === 'a' || e.key === 'A')) ||
        (e.ctrlKey && (e.key === 'c' || e.key === 'C')) ||
        (e.ctrlKey && (e.key === 'v' || e.key === 'V')) ||
        (e.ctrlKey && (e.key === 'x' || e.key === 'X'))
      ) {
        e.preventDefault();
        e.stopPropagation();
        toast.error('This action is not permitted.');
        return false;
      }
    };

    const handleContextMenu = (e) => {
      e.preventDefault();
      toast.error('Right-click is disabled for security.');
      return false;
    };

    // Detect dev tools
    const detectDevTools = () => {
      const widthThreshold = window.outerWidth - window.innerWidth > 160;
      const heightThreshold = window.outerHeight - window.innerHeight > 160;
      
      if (widthThreshold || heightThreshold) {
        toast.error('Developer tools detected. Please close them to continue.');
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('contextmenu', handleContextMenu);
    
    // Check for dev tools every 500ms
    const devToolsInterval = setInterval(detectDevTools, 500);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('contextmenu', handleContextMenu);
      clearInterval(devToolsInterval);
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Check password (these would be stored securely in production)
      const LP_PASSWORD = 'DigitalDepression';
      const GP_PASSWORD = 'NicoleWest0904!!';

      if (password === GP_PASSWORD) {
        toast.success('Welcome back, General Partner!');
        onLogin('gp');
      } else if (password === LP_PASSWORD) {
        toast.success('Access granted. Welcome to Coastal Oak Capital.');
        onLogin('lp');
      } else {
        setError('Invalid access code. Please verify your credentials.');
        toast.error('Access denied.');
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
      toast.error('Login failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-logo">
          <h1>COASTAL OAK CAPITAL</h1>
          <div className="subtitle">CAPITAL</div>
          <p style={{ 
            fontSize: '0.75rem', 
            marginTop: '10px', 
            color: 'rgba(255,255,255,0.7)' 
          }}>
            Distressed & Opportunistic Real Estate Fund
          </p>
        </div>
        
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="password">Access Code</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your access code"
              required
              disabled={loading}
              autoComplete="off"
            />
          </div>
          
          {error && <div className="error-message">{error}</div>}
          
          <button 
            type="submit" 
            className="login-button"
            disabled={loading || !password.trim()}
          >
            {loading ? 'Authenticating...' : 'Access Fund Prospectus'}
          </button>
        </form>
        
        <div style={{ 
          marginTop: '30px', 
          textAlign: 'center', 
          fontSize: '0.8rem', 
          color: 'rgba(255,255,255,0.6)' 
        }}>
          This platform contains confidential and proprietary information.<br />
          Unauthorized access is strictly prohibited.
        </div>
      </div>
    </div>
  );
};

export default LoginPage;