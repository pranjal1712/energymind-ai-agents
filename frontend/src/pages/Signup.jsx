import React from 'react';
import { Link } from 'react-router-dom';
import { User } from 'lucide-react';

function Signup() {
  return (
    <div className="auth-page bg-radial">
      <div className="premium-card glass fold-corner">
        <h1 className="auth-title">Create Account</h1>
        <p className="auth-subtitle">Join EnergyMind AI Agents today</p>
        
        <form className="auth-form" onSubmit={(e) => e.preventDefault()}>
          <div className="form-group">
            <label>Full Name</label>
            <input type="text" className="input-field" placeholder="John Doe" required />
          </div>
          
          <div className="form-group">
            <label>Email Address</label>
            <input type="email" className="input-field" placeholder="Enter your email.." required />
          </div>
          
          <div className="form-group">
            <label>Password</label>
            <input type="password" className="input-field" placeholder="**********" required />
          </div>
          
          <button className="btn-primary w-full" style={{ marginTop: '1.5rem' }}>Create Account</button>
        </form>
        
        <p className="auth-footer">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </div>
      
      <style>{`
        .auth-page {
          height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .premium-card { width: 100%; max-width: 420px; }
        .auth-title { margin-bottom: 0.5rem; text-align: center; font-size: 2rem; font-weight: 700; }
        .auth-subtitle { margin-bottom: 2.5rem; text-align: center; color: var(--text-muted); font-size: 0.95rem; }
        .form-group { margin-bottom: 1.5rem; }
        .form-group label { display: block; margin-bottom: 0.75rem; font-size: 0.875rem; font-weight: 600; color: var(--text-main); }
        .auth-footer { margin-top: 2rem; text-align: center; font-size: 0.875rem; color: var(--text-muted); }
        .w-full { width: 100%; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3); }
      `}</style>
    </div>
  );
}

export default Signup;
