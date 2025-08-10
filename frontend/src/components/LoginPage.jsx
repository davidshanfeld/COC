import React, { useState } from 'react';
import { toast } from 'react-toastify';

const LoginPage = ({ onLogin }) => {
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  // Password constants
  const LP_PASSWORD = 'DigitalDepression';
  const GP_PASSWORD = 'NicoleWest0904!!';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Simulate network delay for better UX
      await new Promise(resolve => setTimeout(resolve, 1000));

      if (password === LP_PASSWORD) {
        toast.success('LP Access Granted');
        onLogin('lp');
      } else if (password === GP_PASSWORD) {
        toast.success('GP Access Granted');
        onLogin('gp');
      } else {
        toast.error('Invalid password. Access denied.');
        setPassword('');
      }
    } catch (error) {
      toast.error('Authentication error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-logo">
          <h1>COASTAL OAK</h1>
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
            />
          </div>
          
          <button 
            type="submit" 
            className="login-button"
            disabled={loading || !password.trim()}
          >
            {loading ? 'Authenticating...' : 'Access Fund Prospectus'}
          </button>
        </form>
        
        <div style={{ 
          textAlign: 'center', 
          marginTop: '20px', 
          fontSize: '0.75rem', 
          color: 'rgba(255,255,255,0.5)' 
        }}>
          Authorized Personnel Only
        </div>
      </div>
    </div>
  );
};

export default LoginPage;