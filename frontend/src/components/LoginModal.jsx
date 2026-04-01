import React, { useState } from 'react';
import { GoogleLogin } from '@react-oauth/google';
import api from '../services/api';
import logo from '../assets/logo-em.png';

function LoginModal({ onLogin }) {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      setError('');
      setLoading(true);
      await api.googleAuth(credentialResponse.credential);
      const userInfo = await api.getMe();
      localStorage.setItem('user', JSON.stringify({ 
        name: userInfo.username, 
        email: userInfo.email 
      }));
      onLogin();
    } catch (err) {
      setError('Google Sign-in failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    const formData = new FormData(e.target);
    const email = formData.get('email');
    const password = e.target.querySelectorAll('input')[1].value;
    try {
      await api.login(email, password);
      const userInfo = await api.getMe();
      localStorage.setItem('user', JSON.stringify({ 
        name: userInfo.username, 
        email: userInfo.email 
      }));
      onLogin();
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="login-modal-container">
        <div className="premium-card glass fold-corner" style={{ padding: '2rem' }}>
          <div className="auth-icon-container">
            <div className="auth-icon glass">
              <img src={logo} className="auth-card-logo" alt="Logo" />
            </div>
          </div>
          <h2 className="auth-title" style={{ fontSize: '1.75rem', marginBottom: '0.5rem', animation: 'none', width: 'auto', borderRight: 'none', textAlign: 'center' }}>
            Authorize Access
          </h2>
          <p className="auth-subtitle" style={{ marginBottom: '1.5rem', opacity: 1, animation: 'none', textAlign: 'center' }}>
            Sign in to continue to EnergyMind AI
          </p>

          {error && <div className="error-message">{error}</div>}

          <form className="auth-form" onSubmit={handleSubmit} style={{ marginTop: '0' }}>
            <div className="form-group">
              <label>Email Address</label>
              <input name="email" type="email" className="input-field" placeholder="name@company.com" required />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input type="password" className="input-field" placeholder="••••••••" required />
            </div>
            <button className="btn-primary w-full" disabled={loading} style={{ marginTop: '1rem' }}>
              {loading ? 'Processing...' : 'Sign In'}
            </button>
          </form>

          <div className="auth-divider"><span>OR</span></div>
          
          <div className="google-btn-wrapper">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={() => setError('Google Sign-in failed')}
              width="340"
              theme="filled_black"
              shape="pill"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginModal;
