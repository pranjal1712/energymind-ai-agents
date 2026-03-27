import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { User } from 'lucide-react';

function Login({ onLogin }) {
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    onLogin();
    navigate('/chatbot');
  };

  return (
    <div className="auth-page bg-radial">
      <div className="premium-card glass fold-corner">
        <div className="auth-icon-container">
          <div className="auth-icon glass">
            <User size={32} />
          </div>
        </div>
        
        <h1 className="auth-title">Welcome Back</h1>
        <p className="auth-subtitle">Please enter your info to sign in to EnergyMind</p>
        
        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email Address</label>
            <input type="email" className="input-field" placeholder="Enter your email.." required />
          </div>
          
          <div className="form-group">
            <div className="label-row">
              <label>Password</label>
            </div>
            <div className="password-input-container">
              <input type="password" className="input-field" placeholder="**********" required />
              <Link to="/forgot-password" style={{ position: 'absolute', right: '0', bottom: '-1.5rem', fontSize: '0.75rem' }}>Forgot Password?</Link>
            </div>
          </div>
          
          <button className="btn-primary w-full" style={{ marginTop: '2rem' }}>Sign in</button>
        </form>
        
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
        .premium-card { width: 100%; max-width: 420px; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }
        .auth-icon-container { display: flex; justify-content: center; margin-bottom: 1.5rem; }
        .auth-icon { width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: var(--text-muted); }
        .auth-title { margin-bottom: 0.5rem; text-align: center; font-size: 2rem; font-weight: 700; letter-spacing: -0.025em; }
        .auth-subtitle { margin-bottom: 2.5rem; text-align: center; color: var(--text-muted); font-size: 0.95rem; }
        .form-group { margin-bottom: 1.75rem; }
        .form-group label { display: block; margin-bottom: 0.75rem; font-size: 0.875rem; font-weight: 600; color: var(--text-main); }
        .password-input-container { position: relative; }
        .auth-form { margin-top: 1rem; }
        .auth-footer { margin-top: 2rem; text-align: center; font-size: 0.875rem; color: var(--text-muted); }
        .w-full { width: 100%; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3); }
      `}</style>
    </div>
  );
}

export default Login;
