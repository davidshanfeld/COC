import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';

const LegalDisclaimer = ({ onAccept, userType }) => {
  const [agreements, setAgreements] = useState({
    riskDisclosure: false,
    noOffering: false,
    forwardLooking: false,
    confidentiality: false,
    nda: false,
    warranties: false,
    jurisdiction: false,
    finalAcknowledgment: false
  });

  const allAgreed = Object.values(agreements).every(Boolean);

  // Disable keyboard shortcuts and dev tools
  useEffect(() => {
    const handleKeyDown = (e) => {
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
        toast.error('This action is not permitted.');
        return false;
      }
    };

    const handleContextMenu = (e) => {
      e.preventDefault();
      return false;
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('contextmenu', handleContextMenu);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('contextmenu', handleContextMenu);
    };
  }, []);

  const handleAgreementChange = (key) => {
    setAgreements(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const handleProceed = () => {
    if (allAgreed) {
      toast.success('Terms accepted. Welcome to the Coastal Oak Capital platform.');
      onAccept();
    }
  };

  return (
    <div className="disclaimer-container">
      <div className="disclaimer-content">
        <div className="disclaimer-header">
          <h1>Legal Disclosure & Agreement</h1>
          <p>Please read and acknowledge all terms before proceeding</p>
        </div>

        <div className="disclaimer-text">
          
          <div className="disclaimer-section">
            <h3>IMPORTANT LEGAL NOTICES</h3>
            <p>
              This platform contains confidential and proprietary information regarding Coastal Oak Capital 
              and its investment strategies. Access to this information is restricted to authorized parties only.
            </p>
          </div>

          <div className="disclaimer-section">
            <h3>NOT AN OFFERING OR SOLICITATION</h3>
            <p>
              The information contained herein does not constitute an offer to sell or a solicitation of an 
              offer to buy any securities. Any such offer or solicitation will be made only through definitive 
              offering documents and subject to applicable securities laws. No investment should be made based 
              solely on the information provided herein.
            </p>
          </div>

          <div className="disclaimer-section">
            <h3>RISK DISCLOSURE</h3>
            <p>
              Real estate investments involve substantial risks, including but not limited to: market volatility, 
              liquidity constraints, interest rate fluctuations, economic downturns, regulatory changes, and 
              complete loss of invested capital. Past performance is not indicative of future results. 
              All projections, forecasts, and targeted returns are estimates based on current market conditions 
              and assumptions that may prove incorrect.
            </p>
          </div>

          <div className="disclaimer-section">
            <h3>FORWARD-LOOKING STATEMENTS</h3>
            <p>
              This platform contains forward-looking statements based on current expectations and assumptions. 
              Actual results may differ materially from those projected. Such statements involve known and 
              unknown risks, uncertainties, and other factors that may cause actual performance to vary 
              significantly from anticipated results.
            </p>
          </div>

          <div className="disclaimer-section">
            <h3>NO WARRANTIES OR REPRESENTATIONS</h3>
            <p>
              Coastal Oak Capital makes no representations or warranties regarding the accuracy, completeness, 
              or timeliness of any information provided. All data is provided "as is" without warranty of any 
              kind, either express or implied. Users rely on this information at their own risk.
            </p>
          </div>

          <div className="disclaimer-section">
            <h3>CONFIDENTIALITY & NON-DISCLOSURE</h3>
            <p>
              All information accessed through this platform is strictly confidential and proprietary. 
              By proceeding, you agree to maintain complete confidentiality and not disclose, reproduce, 
              distribute, or use any information for purposes other than evaluating potential investment 
              opportunities with Coastal Oak Capital.
            </p>
          </div>

          <div className="disclaimer-section">
            <h3>JURISDICTION & GOVERNING LAW</h3>
            <p>
              This agreement and all related matters shall be governed by the laws of Delaware, United States, 
              without regard to conflict of law principles. Any disputes shall be resolved exclusively through 
              binding arbitration in Delaware.
            </p>
          </div>

        </div>

        <div className="agreement-section">
          <h3>REQUIRED ACKNOWLEDGMENTS</h3>
          <p style={{ marginBottom: '20px', fontSize: '0.9rem', color: 'var(--coastal-warning)' }}>
            You must acknowledge all items below to proceed:
          </p>

          <div className="checkbox-group">
            <input 
              type="checkbox" 
              id="riskDisclosure"
              checked={agreements.riskDisclosure}
              onChange={() => handleAgreementChange('riskDisclosure')}
            />
            <label htmlFor="riskDisclosure">
              I acknowledge and understand the substantial risks associated with real estate investments, 
              including the potential for complete loss of capital.
            </label>
          </div>

          <div className="checkbox-group">
            <input 
              type="checkbox" 
              id="noOffering"
              checked={agreements.noOffering}
              onChange={() => handleAgreementChange('noOffering')}
            />
            <label htmlFor="noOffering">
              I understand this is not an offering or solicitation, and any investment decisions will be 
              based on complete offering documents and proper legal counsel.
            </label>
          </div>

          <div className="checkbox-group">
            <input 
              type="checkbox" 
              id="forwardLooking"
              checked={agreements.forwardLooking}
              onChange={() => handleAgreementChange('forwardLooking')}
            />
            <label htmlFor="forwardLooking">
              I understand that all projections and forward-looking statements are estimates that may 
              not be achieved and actual results may vary materially.
            </label>
          </div>

          <div className="checkbox-group">
            <input 
              type="checkbox" 
              id="confidentiality"
              checked={agreements.confidentiality}
              onChange={() => handleAgreementChange('confidentiality')}
            />
            <label htmlFor="confidentiality">
              I agree to maintain strict confidentiality of all information accessed through this platform 
              and will not disclose any information to third parties.
            </label>
          </div>

          <div className="checkbox-group">
            <input 
              type="checkbox" 
              id="nda"
              checked={agreements.nda}
              onChange={() => handleAgreementChange('nda')}
            />
            <label htmlFor="nda">
              I agree to be bound by the terms of this Non-Disclosure Agreement and understand that 
              breach may result in legal action and damages.
            </label>
          </div>

          <div className="checkbox-group">
            <input 
              type="checkbox" 
              id="warranties"
              checked={agreements.warranties}
              onChange={() => handleAgreementChange('warranties')}
            />
            <label htmlFor="warranties">
              I acknowledge that no warranties or representations are made regarding the accuracy of 
              information and I rely on such information at my own risk.
            </label>
          </div>

          <div className="checkbox-group">
            <input 
              type="checkbox" 
              id="jurisdiction"
              checked={agreements.jurisdiction}
              onChange={() => handleAgreementChange('jurisdiction')}
            />
            <label htmlFor="jurisdiction">
              I agree that this agreement is governed by Delaware law and any disputes will be resolved 
              through binding arbitration in Delaware.
            </label>
          </div>

          <div className="checkbox-group">
            <input 
              type="checkbox" 
              id="finalAcknowledgment"
              checked={agreements.finalAcknowledgment}
              onChange={() => handleAgreementChange('finalAcknowledgment')}
            />
            <label htmlFor="finalAcknowledgment">
              <strong>FINAL ACKNOWLEDGMENT:</strong> I have read, understood, and agree to be legally 
              bound by all terms and conditions stated above. I confirm that I am authorized to access 
              this confidential information and accept all associated risks and obligations.
            </label>
          </div>
        </div>

        <button 
          className="proceed-button"
          onClick={handleProceed}
          disabled={!allAgreed}
        >
          {allAgreed ? 'I Agree - Proceed to Platform' : `Please acknowledge all terms (${Object.values(agreements).filter(Boolean).length}/8)`}
        </button>

        <div style={{ 
          marginTop: '20px', 
          textAlign: 'center', 
          fontSize: '0.8rem', 
          color: 'rgba(255,255,255,0.6)' 
        }}>
          {userType === 'gp' ? 'General Partner Access' : 'Limited Partner Access'} • 
          By proceeding, you create a legally binding agreement.
        </div>
      </div>
    </div>
  );
};

export default LegalDisclaimer;