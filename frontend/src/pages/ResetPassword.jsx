import React, { useState, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Lock, CheckCircle2, AlertCircle } from 'lucide-react';
import { useMousePosition } from '../hooks/useMousePosition';
import logo from '../assets/logo-em.png';

function ResetPassword() {
  const navigate = useNavigate();
  const pageRef = useRef(null);
  useMousePosition(pageRef);

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isReset, setIsReset] = useState(false);

  const validation = {
    length: password.length >= 8,
    number: /[0-9]/.test(password),
    capital: /[A-Z]/.test(password),
    special: /[^A-Za-z0-9]/.test(password)
  };

  const isPasswordStrong = validation.length && validation.number && validation.capital && validation.special;
  const passwordsMatch = password && confirmPassword && password === confirmPassword;
  const canReset = isPasswordStrong && passwordsMatch;
  const showMismatchWarning = password && confirmPassword && password !== confirmPassword;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (canReset) {
      // Logic for password reset...
      setIsReset(true);
      setTimeout(() => navigate('/login'), 3000);
    }
  };

  if (isReset) {
    return (
      <div ref={pageRef} className="auth-page bg-radial">
        <div className="premium-card glass fold-corner" style={{ textAlign: 'center', padding: '3rem 2rem' }}>
          <CheckCircle2 size={64} color="#10b981" style={{ marginBottom: '1.5rem' }} />
          <h1 className="auth-title" style={{ fontSize: '2.5rem' }}>Success!</h1>
          <p className="auth-subtitle" style={{ fontSize: '1rem' }}>
            Your password has been reset successfully. Redirecting you to login...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div ref={pageRef} className="auth-page bg-radial">
      <div className="brand-header">
        <img src={logo} alt="Energymind Logo" className="brand-logo" />
        <span className="brand-name">Energymind</span>
      </div>

      {/* 6 Circles */}
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

      {/* 4 Rhombus */}
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

        <h1 className="auth-title" style={{ fontSize: '2.1rem', marginBottom: '0.25rem' }}>New Password</h1>
        <p className="auth-subtitle" style={{ fontSize: '0.85rem', marginBottom: '1rem' }}>Set a secure password for your account</p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>New Password</label>
            <input 
              type="password" 
              className="input-field" 
              placeholder="**********" 
              required 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            
            <div className="password-requirements">
              {!validation.length && password && <div className="requirement invalid"><AlertCircle size={10} /><span>Min 8 characters</span></div>}
              {!validation.number && password && <div className="requirement invalid"><AlertCircle size={10} /><span>Include a number (0-9)</span></div>}
              {!validation.capital && password && <div className="requirement invalid"><AlertCircle size={10} /><span>Include a capital (A-Z)</span></div>}
              {!validation.special && password && <div className="requirement invalid"><AlertCircle size={10} /><span>Include a special char (@,#,etc.)</span></div>}
            </div>
          </div>

          <div className="form-group" style={{ marginBottom: '1.25rem' }}>
            <label>Confirm Password</label>
            <input 
              type="password" 
              className="input-field" 
              placeholder="**********" 
              required 
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              style={{ borderColor: showMismatchWarning ? '#ef4444' : '' }}
            />
            {showMismatchWarning && (
              <p style={{ color: '#ef4444', fontSize: '0.7rem', marginTop: '0.4rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <AlertCircle size={12} /> Passwords do not match
              </p>
            )}
            {passwordsMatch && isPasswordStrong && (
              <p style={{ color: '#10b981', fontSize: '0.7rem', marginTop: '0.4rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <CheckCircle2 size={12} /> Ready to reset!
              </p>
            )}
          </div>

          <button 
            type="submit" 
            className="btn-primary w-full" 
            disabled={!canReset}
            style={{ opacity: canReset ? 1 : 0.6 }}
          >
            Reset Password
          </button>
        </form>

        <div className="auth-footer" style={{ marginTop: '1.25rem' }}>
          <Link to="/login" style={{ color: '#fff', fontSize: '0.85rem', opacity: '0.8' }}>Back to Login</Link>
        </div>
      </div>

      <style>{`
        .auth-page {
          height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .premium-card { width: 100%; max-width: 440px; padding: 1.5rem 1.75rem; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }
        .auth-icon-container { display: flex; justify-content: center; margin-bottom: 0.5rem; }
        .auth-icon { width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center; justify-content: center; overflow: hidden; }
        .auth-card-logo { width: 100%; height: 100%; object-fit: cover; mix-blend-mode: screen; filter: brightness(1.1); }
        .form-group { margin-bottom: 0.75rem; }
        .form-group label { display: block; margin-bottom: 0.3rem; font-size: 0.8rem; font-weight: 600; color: var(--text-main); }
        .auth-form { margin-top: 0.25rem; }
        .auth-footer { text-align: center; }
        .w-full { width: 100%; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3); }
        
        .password-requirements { margin-top: 0.4rem; display: flex; flex-direction: column; gap: 0.2rem; }
        .requirement { display: flex; align-items: center; gap: 0.4rem; font-size: 0.65rem; transition: var(--transition); }
        .requirement.invalid { color: #ef4444; }
        .requirement span { white-space: nowrap; }
      `}</style>
    </div>
  );
}

export default ResetPassword;
