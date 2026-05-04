import React, { useRef, useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Mail, ShieldCheck, Loader2 } from 'lucide-react';
import { useMousePosition } from '../hooks/useMousePosition';
import api from '../services/api';
import logo from '../assets/logo-em.png';

function VerifyOtp({ onLogin }) {
  const navigate = useNavigate();
  const location = useLocation();
  const pageRef = useRef(null);
  useMousePosition(pageRef);

  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  
  const inputRefs = [useRef(), useRef(), useRef(), useRef(), useRef(), useRef()];

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const emailParam = params.get('email');
    if (emailParam) {
      setEmail(emailParam);
    } else {
      navigate('/signup');
    }
  }, [location, navigate]);

  const handleChange = (index, value) => {
    // Only allow numbers
    if (value && !/^\d+$/.test(value)) return;
    
    const newOtp = [...otp];
    newOtp[index] = value.substring(value.length - 1);
    setOtp(newOtp);

    // Auto-focus next input
    if (value && index < 5) {
      inputRefs[index + 1].current.focus();
    }
  };

  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs[index - 1].current.focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pasteData = e.clipboardData.getData('text').slice(0, 6);
    if (!/^\d+$/.test(pasteData)) return;

    const newOtp = [...otp];
    pasteData.split('').forEach((char, i) => {
      if (i < 6) newOtp[i] = char;
    });
    setOtp(newOtp);
    
    const focusIndex = pasteData.length < 6 ? pasteData.length : 5;
    inputRefs[focusIndex].current.focus();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const otpString = otp.join('');
    if (otpString.length !== 6) return;

    setError('');
    setLoading(true);

    try {
      const response = await api.verifyOtp(email, otpString);
      
      // Auto-login: save token and user info
      api.setToken(response.access_token);
      localStorage.setItem('user', JSON.stringify({ 
        name: response.username, 
        email: response.email 
      }));

      setSuccess(true);
      setTimeout(() => {
        onLogin(); // Trigger isLoggedIn state in App.jsx
        navigate('/chatbot');
      }, 1500);
    } catch (err) {
      setError(err.message || 'Verification failed. Please check the code.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div ref={pageRef} className="auth-page bg-radial" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
      <div className="brand-header">
        <img src={logo} alt="Energymind Logo" className="brand-logo" />
        <span className="brand-name">Energymind</span>
      </div>

      <div className="premium-card glass fold-corner" style={{ maxWidth: '450px', width: '100%' }}>
        <div className="auth-icon-container">
          <div className="auth-icon glass">
            <Mail size={32} style={{ color: '#8b5cf6' }} />
          </div>
        </div>

        <h1 className="auth-title" style={{ textAlign: 'center' }}>Verify Email</h1>
        <p className="auth-subtitle" style={{ textAlign: 'center', marginBottom: '2rem' }}>
          We've sent a 6-digit code to <br />
          <strong style={{ color: '#fff' }}>{email}</strong>
        </p>

        {error && <div className="error-message" style={{ marginBottom: '1.5rem' }}>{error}</div>}
        {success && (
          <div style={{ backgroundColor: 'rgba(16, 185, 129, 0.1)', color: '#10b981', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem', textAlign: 'center', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
            <ShieldCheck size={24} style={{ margin: '0 auto 0.5rem' }} />
            Verification successful! Opening Chatbot...
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center', marginBottom: '2rem' }}>
            {otp.map((digit, index) => (
              <input
                key={index}
                ref={inputRefs[index]}
                type="text"
                maxLength="1"
                value={digit}
                onChange={(e) => handleChange(index, e.target.value)}
                onKeyDown={(e) => handleKeyDown(index, e)}
                onPaste={handlePaste}
                style={{
                  width: '3rem',
                  height: '3.5rem',
                  fontSize: '1.5rem',
                  textAlign: 'center',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '10px',
                  color: '#fff',
                  outline: 'none',
                  transition: 'all 0.3s ease',
                }}
                onFocus={(e) => {
                  e.target.style.border = '1px solid #8b5cf6';
                  e.target.style.boxShadow = '0 0 15px rgba(139, 92, 246, 0.3)';
                }}
                onBlur={(e) => {
                  e.target.style.border = '1px solid rgba(255, 255, 255, 0.1)';
                  e.target.style.boxShadow = 'none';
                }}
              />
            ))}
          </div>

          <button 
            type="submit" 
            className="btn-primary w-full"
            disabled={otp.join('').length !== 6 || loading || success}
            style={{ height: '3.5rem', fontSize: '1rem' }}
          >
            {loading ? (
              <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                <Loader2 className="animate-spin" size={18} /> Verifying...
              </span>
            ) : 'Verify OTP'}
          </button>
        </form>

        <p className="auth-footer" style={{ marginTop: '2rem', textAlign: 'center' }}>
          Didn't receive the code? <br />
          <button 
            style={{ background: 'none', border: 'none', color: '#8b5cf6', cursor: 'pointer', fontSize: '0.9rem', marginTop: '0.5rem', textDecoration: 'underline' }}
            onClick={() => navigate('/signup')}
          >
            Try another email
          </button>
        </p>
      </div>
    </div>
  );
}

export default VerifyOtp;
