import React, { useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { User } from 'lucide-react';
import { GoogleLogin } from '@react-oauth/google';
import { useMousePosition } from '../hooks/useMousePosition';
import logo from '../assets/logo-em.png';
import api from '../services/api';

function Login({ onLogin }) {
  const navigate = useNavigate();
  const pageRef = useRef(null);
  useMousePosition(pageRef);
  
  const [error, setError] = React.useState('');
  const [loading, setLoading] = React.useState(false);

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
      navigate('/chatbot');
    } catch (err) {
      setError('Google Sign-in failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    const formData = new FormData(e.target);
    const email = formData.get('userEmail');
    const password = e.target.querySelectorAll('input')[1].value;
    
    try {
      await api.login(email, password);
      
      // Fetch user info after login
      const userInfo = await api.getMe();
      localStorage.setItem('user', JSON.stringify({ 
        name: userInfo.username, 
        email: userInfo.email 
      }));
      
      onLogin();
      navigate('/chatbot');
    } catch (err) {
      setError(err.message || 'Incorrect email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div ref={pageRef} className="auth-page bg-radial">
      <div className="brand-header">
        <img src={logo} alt="Energymind Logo" className="brand-logo" />
        <span className="brand-name">Energymind</span>
      </div>
      {/* 5 Circles */}
      <div className="glowing-orb"></div>
      <div className="glowing-orb"></div>
      <div className="glowing-orb"></div>
      <div className="glowing-orb"></div>
      <div className="glowing-orb"></div>
      <div className="glowing-orb"></div>

      {/* 6 Squares */}
      <span className="glowing-square"></span>
      <span className="glowing-square"></span>
      <span className="glowing-square"></span>
      <span className="glowing-square"></span>
      <span className="glowing-square"></span>
      <span className="glowing-square"></span>

      {/* 6 Rhombus (Diamonds) */}
      <i className="glowing-rhombus"></i>
      <i className="glowing-rhombus"></i>
      <i className="glowing-rhombus"></i>
      <i className="glowing-rhombus"></i>

      <div className="premium-card glass fold-corner">
        <div className="auth-icon-container">
          <div className="auth-icon glass">
            <img src={logo} className="auth-card-logo" alt="Energymind Logo" />
          </div>
        </div>

        <h1 className="auth-title">Welcome Back</h1>
        <p className="auth-subtitle">Please enter your info to sign in to EnergyMind</p>

        {error && <div className="error-message">{error}</div>}

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email Address</label>
            <input name="userEmail" type="email" className="input-field" placeholder="Enter your email.." required />
          </div>

          <div className="form-group">
            <div className="label-row">
              <label>Password</label>
            </div>
            <div className="password-input-container">
              <input type="password" className="input-field" placeholder="**********" required />
              <Link to="/forgot-password" style={{ position: 'absolute', right: '0', bottom: '-1.25rem', fontSize: '0.7rem', color: '#fff', opacity: '0.8' }}>Forgot Password?</Link>
            </div>
          </div>

          <button 
            className="btn-primary w-full" 
            style={{ marginTop: '1.75rem' }}
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        <div className="auth-divider">
          <span>OR</span>
        </div>

        <div className="google-btn-wrapper">
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => setError('Google Sign-in failed')}
            width="340"
            theme="filled_black"
            shape="pill"
          />
        </div>

        <p className="auth-footer">
          Don't have an account yet? <Link to="/signup">Sign up</Link>
        </p>
      </div>

      <style>{`
        .auth-page {
          height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .premium-card { width: 100%; max-width: 380px; padding: 1.25rem 1.5rem; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }
        .auth-icon-container { display: flex; justify-content: center; margin-bottom: 0.75rem; }
        .auth-icon { width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center; justify-content: center; overflow: hidden; }
        .auth-card-logo { width: 100%; height: 100%; object-fit: cover; mix-blend-mode: screen; filter: brightness(1.1); }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; margin-bottom: 0.4rem; font-size: 0.85rem; font-weight: 600; color: var(--text-main); }
        .password-input-container { position: relative; }
        .auth-form { margin-top: 0.5rem; }
        .auth-footer { margin-top: 1rem; text-align: center; font-size: 0.85rem; color: rgba(255, 255, 255, 0.85); }
        .auth-divider { margin: 1.25rem 0; display: flex; align-items: center; justify-content: center; position: relative; }
        .auth-divider::before, .auth-divider::after { content: ""; flex: 1; height: 1px; background: rgba(255, 255, 255, 0.1); }
        .auth-divider span { padding: 0 0.75rem; font-size: 0.75rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; }
        
        .error-message {
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.2);
          color: #ef4444;
          padding: 0.75rem;
          border-radius: 12px;
          font-size: 0.85rem;
          margin-bottom: 1rem;
          text-align: center;
        }
        .btn-google { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); color: #fff; padding: 0.75rem; border-radius: 12px; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 0.75rem; transition: var(--transition); cursor: pointer; backdrop-filter: blur(8px); }
        .btn-google:hover { background: rgba(255, 255, 255, 0.1); border-color: rgba(255, 255, 255, 0.3); transform: translateY(-2px); }
        .btn-google img { width: 18px; height: 18px; }
        .google-btn-wrapper {
          display: flex;
          justify-content: center;
          width: 100%;
          margin-top: 0.5rem;
          min-height: 40px;
        }
        .w-full { width: 100%; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3); }
      `}</style>
    </div>
  );
}

export default Login;
