import React, { useRef } from 'react';
import { Link } from 'react-router-dom';
import { KeyRound, ArrowLeft } from 'lucide-react';
import { useMousePosition } from '../hooks/useMousePosition';
import logo from '../assets/logo-em.png';

const ForgotPassword = () => {
  const pageRef = useRef(null);
  useMousePosition(pageRef);

  const handleSubmit = (e) => {
    e.preventDefault();
    alert('Reset link sent to your email!');
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

        <h1 className="auth-title">Reset Password</h1>
        <p className="auth-subtitle">Enter your email for the reset link</p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email Address</label>
            <input type="email" className="input-field" placeholder="Enter your email.." required />
          </div>

          <button className="btn-primary w-full" style={{ marginTop: '1rem' }}>Send Reset Link</button>
        </form>

        <p className="auth-footer">
          <Link to="/login" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
            <ArrowLeft size={16} /> Back to Login
          </Link>
        </p>
      </div>

      <style>{`
        .auth-page {
          height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .premium-card { width: 100%; max-width: 380px; padding: 1.25rem 1.5rem; }
        .auth-icon-container { display: flex; justify-content: center; margin-bottom: 0.75rem; }
        .auth-icon { width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center; justify-content: center; overflow: hidden; }
        .auth-card-logo { width: 100%; height: 100%; object-fit: cover; mix-blend-mode: screen; filter: brightness(1.1); }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; font-size: 0.85rem; font-weight: 500; }
        .auth-footer { margin-top: 1rem; text-align: center; font-size: 0.85rem; color: rgba(255, 255, 255, 0.85); }
        .auth-footer a { color: #fff; font-weight: 600; text-decoration: underline; opacity: 0.9; }
        .auth-footer a:hover { opacity: 1; text-shadow: 0 0 10px rgba(255,255,255,0.3); }
        .w-full { width: 100%; margin-top: 0.75rem; border: 1px solid rgba(255,255,255,0.1); }
      `}</style>
    </div>
  );
};

export default ForgotPassword;
