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
            width={window.innerWidth < 400 ? "250" : "340"}
            theme="filled_black"
            shape="pill"
          />
        </div>

        <p className="auth-footer">
          Don't have an account yet? <Link to="/signup">Sign up</Link>
        </p>
      </div>

    </div>
  );
}

export default Login;
