import React, { useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { UserPlus, Check, Circle } from 'lucide-react';
import { GoogleLogin } from '@react-oauth/google';
import { useMousePosition } from '../hooks/useMousePosition';
import api from '../services/api';
import logo from '../assets/logo-em.png';

function Signup({ onSignup }) {
  const navigate = useNavigate();
  const pageRef = useRef(null);
  useMousePosition(pageRef);

  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const validation = {
    length: password.length >= 8,
    number: /[0-9]/.test(password),
    capital: /[A-Z]/.test(password),
    special: /[^A-Za-z0-9]/.test(password)
  };

  const isFormValid = validation.length && validation.number && validation.capital && validation.special;

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
      
      onSignup();
      navigate('/chatbot');
    } catch (err) {
      setError('Google Signup failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isFormValid) {
      setError('');
      setLoading(true);
      const formData = new FormData(e.target);
      const name = formData.get('userName');
      const email = formData.get('userEmail');
      
      try {
        // We slugify the name to use as a username since backend requires it
        const username = name.toLowerCase().replace(/\s+/g, '_');
        await api.signup(username, email, password);
        
        // After signup, we log them in to get the token
        await api.login(username, password);
        
        localStorage.setItem('user', JSON.stringify({ name, email }));
        onSignup();
        navigate('/chatbot');
      } catch (err) {
        setError(err.message || 'Signup failed. Please try again.');
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div ref={pageRef} className="auth-page bg-radial">
      <div className="brand-header">
        <img src={logo} alt="Energymind Logo" className="brand-logo" />
        <span className="brand-name">Energymind</span>
      </div>
      {/* Background Shapes */}
      <div className="glowing-orb"></div>
      <div className="glowing-orb"></div>
      <div className="glowing-orb"></div>
      <div className="glowing-orb"></div>
      
      <span className="glowing-square"></span>
      <span className="glowing-square"></span>
      <span className="glowing-square"></span>
      <span className="glowing-square"></span>

      <i className="glowing-rhombus"></i>
      <i className="glowing-rhombus"></i>
      <i className="glowing-rhombus"></i>

      <div className="premium-card glass fold-corner">
        <div className="auth-icon-container">
          <div className="auth-icon glass">
            <img src={logo} className="auth-card-logo" alt="Energymind Logo" />
          </div>
        </div>

        <h1 className="auth-title" style={{ fontSize: '2.1rem', marginBottom: '0.25rem' }}>Create Account</h1>
        <p className="auth-subtitle" style={{ fontSize: '0.85rem', marginBottom: '0.5rem' }}>Join EnergyMind AI Agents today</p>

        {error && <div className="error-message">{error}</div>}

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Full Name</label>
            <input name="userName" type="text" className="input-field" placeholder="John Doe" required />
          </div>

          <div className="form-group">
            <label>Email Address</label>
            <input name="userEmail" type="email" className="input-field" placeholder="john@example.com" required />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input 
              type="password" 
              className="input-field" 
              placeholder="**********" 
              required 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            
            <div className="password-requirements">
              {!validation.length && (
                <div className="requirement invalid">
                  <Circle size={10} />
                  <span>At least 8 characters</span>
                </div>
              )}
              {!validation.number && (
                <div className="requirement invalid">
                  <Circle size={10} />
                  <span>Include a number (0-9)</span>
                </div>
              )}
              {!validation.capital && (
                <div className="requirement invalid">
                  <Circle size={10} />
                  <span>Include a capital letter (A-Z)</span>
                </div>
              )}
              {!validation.special && (
                <div className="requirement invalid">
                  <Circle size={10} />
                  <span>Include a special character (@, #, etc.)</span>
                </div>
              )}
            </div>
          </div>

          <button 
            className="btn-primary w-full" 
            style={{ marginTop: '0.5rem', opacity: isFormValid && !loading ? 1 : 0.6 }} 
            disabled={!isFormValid || loading}
          >
            {loading ? 'Creating Account...' : 'Get Started'}
          </button>
        </form>

        <div className="auth-divider">
          <span>OR</span>
        </div>

        <div className="google-btn-wrapper">
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => setError('Google Sign-up failed')}
            width={window.innerWidth < 400 ? "250" : "340"}
            theme="filled_black"
            shape="pill"
          />
        </div>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>

    </div>
  );
}

export default Signup;
