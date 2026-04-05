import React from 'react';
import { useNavigate } from 'react-router-dom';
import logo from '../assets/logo-em.png';
import { LogIn, UserPlus } from 'lucide-react';

function LoginModal() {
  const navigate = useNavigate();

  return (
    <div className="modal-overlay">
      <div className="login-modal-container">
        <div className="premium-card glass fold-corner auth-card-modal" style={{ textAlign: 'center', padding: '2.5rem 2rem' }}>
          <div className="auth-icon-container" style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'center' }}>
            <div className="auth-icon glass" style={{ width: '64px', height: '64px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <img src={logo} className="auth-card-logo" alt="Logo" style={{ width: '100%', height: '100%', objectFit: 'cover', mixBlendMode: 'screen' }} />
            </div>
          </div>
          
          <h2 className="auth-title" style={{ fontSize: '1.8rem', marginBottom: '1rem', background: 'linear-gradient(to bottom, #fff, #888)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Access Restricted
          </h2>
          
          <p className="auth-subtitle" style={{ marginBottom: '2rem', fontSize: '1rem', color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.6' }}>
            To start searching and analyzing energy data with our AI agents, please <strong>Sign In</strong> first. 
            <br />
            New to the platform? <strong>Create an account</strong> to get started.
          </p>

          <div className="modal-actions" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <button 
              className="btn-primary w-full" 
              onClick={() => navigate('/login')}
              style={{ padding: '1rem', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', fontWeight: '700' }}
            >
              <LogIn size={20} />
              Sign In Now
            </button>
            
            <button 
              className="btn-ghost w-full" 
              onClick={() => navigate('/signup')}
              style={{ padding: '1rem', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', fontWeight: '600', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255, 255, 255, 0.1)' }}
            >
              <UserPlus size={20} />
              Create New Account
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginModal;
