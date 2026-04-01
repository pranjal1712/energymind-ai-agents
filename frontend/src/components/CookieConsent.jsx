import React from 'react';
import api from '../services/api';

function CookieConsent({ onDecision }) {
  const handleDecision = (decision) => {
    localStorage.setItem('cookie_consent', decision);
    if (decision === 'accepted') {
      const token = api.getToken();
      if (token) {
        // Redo setToken to trigger cookie storage
        api.setToken(token);
      }
    }
    onDecision(decision);
  };

  return (
    <div className="cookie-consent-banner glass">
      <div className="cookie-content">
        <h4 className="cookie-title">Cookie Preference</h4>
        <p className="cookie-text">
          We use cookies to enhance your experience and keep you logged in. 
          Accepting cookies allows us to store your session securely for your next visit.
        </p>
      </div>
      <div className="cookie-actions">
        <button className="btn-ghost" onClick={() => handleDecision('rejected')}>Reject</button>
        <button className="btn-primary" style={{ padding: '0.6rem 1.5rem' }} onClick={() => handleDecision('accepted')}>Accept All</button>
      </div>
    </div>
  );
}

export default CookieConsent;
