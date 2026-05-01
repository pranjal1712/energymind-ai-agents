import React, { useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Mail, CheckCircle } from 'lucide-react';
import { useMousePosition } from '../hooks/useMousePosition';
import api from '../services/api';
import logo from '../assets/logo-em.png';

const ForgotPassword = () => {
  const pageRef = useRef(null);
  useMousePosition(pageRef);
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await api.forgotPassword(email);
      setSent(true);
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.');
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
      <div className="glowing-orb"></div>
      <div className="glowing-orb"></div>
      <span className="glowing-square"></span>
      <span className="glowing-square"></span>
      <i className="glowing-rhombus"></i>
      <i className="glowing-rhombus"></i>

      <div className="premium-card glass fold-corner">
        <div className="auth-icon-container">
          <div className="auth-icon glass">
            <img src={logo} className="auth-card-logo" alt="Energymind Logo" />
          </div>
        </div>

        {sent ? (
          <div style={{ textAlign: 'center', margin: '1.5rem 0' }}>
            <CheckCircle size={52} style={{ color: '#10b981', margin: '0 auto 1rem' }} />
            <h1 className="auth-title" style={{ fontSize: '1.8rem' }}>Check your inbox</h1>
            <p className="auth-subtitle" style={{ marginBottom: '1.5rem' }}>
              If this email exists, a password reset link has been sent. Please check your email.
            </p>
            <Link to="/login" className="btn-primary" style={{ textDecoration: 'none' }}>
              Back to Login
            </Link>
          </div>
        ) : (
          <>
            <h1 className="auth-title">Reset Password</h1>
            <p className="auth-subtitle">Enter your email for the reset link</p>

            {error && <div className="error-message">{error}</div>}

            <form className="auth-form" onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Email Address</label>
                <input
                  type="email"
                  className="input-field"
                  placeholder="Enter your email.."
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <button className="btn-primary w-full" style={{ marginTop: '1rem' }} disabled={loading}>
                {loading ? 'Sending...' : 'Send Reset Link'}
              </button>
            </form>

            <p className="auth-footer">
              <Link to="/login" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                <ArrowLeft size={16} /> Back to Login
              </Link>
            </p>
          </>
        )}
      </div>
    </div>
  );
};

export default ForgotPassword;
