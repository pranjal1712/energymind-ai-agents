import React from 'react';
import { Link } from 'react-router-dom';

function Login() {
  return (
    <div className="auth-page">
      <div className="premium-card glass">
        <h1 className="auth-title">Welcome Back</h1>
        <p className="auth-subtitle">Log in to EnergyMind AI Agents</p>
        
        <form className="auth-form" onSubmit={(e) => e.preventDefault()}>
          <div className="form-group">
            <label>Email Address</label>
            <input type="email" className="input-field" placeholder="name@example.com" required />
          </div>
          
          <div className="form-group">
            <div className="label-row">
              <label>Password</label>
              <Link to="/forgot-password">Forgot password?</Link>
            </div>
            <input type="password" className="input-field" placeholder="••••••••" required />
          </div>
          
          <button className="btn-primary w-full">Sign In</button>
        </form>
        
        <p className="auth-footer">
          Don't have an account? <Link to="/signup">Sign up</Link>
        </p>
      </div>
      
      <style>{`
        .auth-page {
          height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: radial-gradient(circle at top right, #1e1b4b, #0f172a);
        }
        .auth-title { margin-bottom: 0.5rem; text-align: center; font-size: 1.875rem; font-weight: 700; }
        .auth-subtitle { margin-bottom: 2rem; text-align: center; color: var(--text-muted); }
        .form-group { margin-bottom: 1.5rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; font-size: 0.875rem; font-weight: 500; }
        .label-row { display: flex; justify-content: space-between; align-items: center; }
        .auth-footer { margin-top: 1.5rem; text-align: center; font-size: 0.875rem; color: var(--text-muted); }
        .w-full { width: 100%; margin-top: 1rem; }
      `}</style>
    </div>
  );
}

export default Login;
