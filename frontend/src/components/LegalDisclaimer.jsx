import React, { useState } from 'react';
import { toast } from 'react-toastify';

const LegalDisclaimer = ({ onAccept, userType }) => {
  const [acknowledgments, setAcknowledgments] = useState({
    disclaimer: false,
    nda: false,
    accredited: false,
    risks: false,
    noAdvice: false
  });

  const handleCheckboxChange = (key) => {
    setAcknowledgments(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const allAcknowledged = Object.values(acknowledgments).every(val => val);

  const handleProceed = () => {
    if (!allAcknowledged) {
      toast.error('Please acknowledge all required statements');
      return;
    }
    
    toast.success('Legal terms accepted. Welcome to Coastal Oak Capital.');
    onAccept();
  };

  return (
    <div className="disclaimer-container">
      <div className="disclaimer-content">
        <div className="disclaimer-header">
          <h1>COASTAL OAK CAPITAL</h1>
          <h2>Legal Disclaimer & Non-Disclosure Agreement</h2>
          <p style={{ fontSize: '0.85rem', color: 'rgba(255,255,255,0.7)' }}>
            {userType === 'gp' ? 'General Partner Access' : 'Limited Partner Access'}
          </p>
        </div>

        <div className="disclaimer-text">
          <div className="disclaimer-section">
            <h3>INVESTMENT DISCLAIMER</h3>
            <p>
              The information contained herein regarding Coastal Oak Capital and its investment 
              opportunities is confidential and proprietary. This material is being provided solely 
              for informational purposes to qualified investors who have expressed interest in 
              learning about potential investment opportunities.
            </p>
            <p>
              <strong>Past performance is not indicative of future results.</strong> All investments 
              involve risk, including the potential for total loss of principal. Real estate 
              investments are subject to various risks including market volatility, liquidity 
              constraints, and economic downturns.
            </p>
          </div>

          <div className="disclaimer-section">
            <h3>ACCREDITED INVESTOR REQUIREMENT</h3>
            <p>
              Access to this information is restricted to accredited investors as defined under 
              Regulation D of the Securities Act of 1933. By proceeding, you represent and warrant 
              that you meet the accredited investor requirements and have the financial sophistication 
              to evaluate the risks and merits of potential investments.
            </p>
          </div>

          <div className="disclaimer-section">
            <h3>NON-DISCLOSURE AGREEMENT</h3>
            <p>
              The information provided is highly confidential and proprietary to Coastal Oak Capital. 
              You agree to maintain the confidentiality of all information accessed and not to 
              disclose, reproduce, or distribute any such information without express written 
              consent from Coastal Oak Capital.
            </p>
            <p>
              This confidentiality obligation shall survive termination of your access to these 
              materials and shall remain in effect indefinitely.
            </p>
          </div>

          <div className="disclaimer-section">
            <h3>NO INVESTMENT ADVICE</h3>
            <p>
              The information provided does not constitute investment advice, a recommendation, 
              or solicitation to buy or sell securities. You should consult with your own 
              investment, legal, tax, and financial advisors before making any investment decisions.
            </p>
          </div>

          <div className="disclaimer-section">
            <h3>FORWARD-LOOKING STATEMENTS</h3>
            <p>
              This presentation may contain forward-looking statements based on current expectations 
              and assumptions. Actual results may differ materially from those projected. No assurance 
              can be given that any investment objective will be achieved or that investors will 
              receive a return of their capital.
            </p>
          </div>
        </div>

        <div className="agreement-section">
          <h3>REQUIRED ACKNOWLEDGMENTS</h3>
          
          <div className="checkbox-group" onClick={() => handleCheckboxChange('disclaimer')}>
            <input 
              type="checkbox" 
              id="disclaimer"
              checked={acknowledgments.disclaimer}
              onChange={() => {}}
            />
            <label htmlFor="disclaimer">
              I acknowledge that I have read and understood the investment disclaimer and 
              understand that all investments involve risk of loss.
            </label>
          </div>

          <div className="checkbox-group" onClick={() => handleCheckboxChange('nda')}>
            <input 
              type="checkbox" 
              id="nda"
              checked={acknowledgments.nda}
              onChange={() => {}}
            />
            <label htmlFor="nda">
              I agree to the non-disclosure agreement and will maintain confidentiality 
              of all proprietary information accessed.
            </label>
          </div>

          <div className="checkbox-group" onClick={() => handleCheckboxChange('accredited')}>
            <input 
              type="checkbox" 
              id="accredited"
              checked={acknowledgments.accredited}
              onChange={() => {}}
            />
            <label htmlFor="accredited">
              I represent that I am an accredited investor as defined under federal 
              securities regulations.
            </label>
          </div>

          <div className="checkbox-group" onClick={() => handleCheckboxChange('risks')}>
            <input 
              type="checkbox" 
              id="risks"
              checked={acknowledgments.risks}
              onChange={() => {}}
            />
            <label htmlFor="risks">
              I understand the risks associated with real estate investments including 
              market volatility, liquidity constraints, and potential total loss.
            </label>
          </div>

          <div className="checkbox-group" onClick={() => handleCheckboxChange('noAdvice')}>
            <input 
              type="checkbox" 
              id="noAdvice"
              checked={acknowledgments.noAdvice}
              onChange={() => {}}
            />
            <label htmlFor="noAdvice">
              I understand this is not investment advice and I will consult my own 
              advisors before making investment decisions.
            </label>
          </div>
        </div>

        <button 
          className="proceed-button"
          onClick={handleProceed}
          disabled={!allAcknowledged}
        >
          I Acknowledge and Accept All Terms - Proceed to Fund Information
        </button>
      </div>
    </div>
  );
};

export default LegalDisclaimer;