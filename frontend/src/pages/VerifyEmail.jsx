import React, { useEffect, useState, useRef } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useMousePosition } from '../hooks/useMousePosition';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';
import api from '../services/api';
import logo from '../assets/logo-em.png';

function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [status, setStatus] = useState('verifying'); // 'verifying', 'success', 'error'
  const [message, setMessage] = useState('');
  
  const pageRef = useRef(null);
  useMousePosition(pageRef);

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setMessage('No verification token provided.');
      return;
    }

    const verify = async () => {
      try {
        await api.verifyEmail(token);
        setStatus('success');
        setMessage('Your email has been successfully verified! You can now log in.');
      } catch (err) {
        setStatus('error');
        setMessage(err.message || 'Verification failed. The link might be expired or invalid.');
      }
    };

    verify();
  }, [token]);

  return (
    <div ref={pageRef} className="auth-page bg-radial">
      <div className="brand-header">
        <img src={logo} alt="Energymind Logo" className="brand-logo" />
        <span className="brand-name">Energymind</span>
      </div>
      
      {/* Background Shapes */}
      <div className="glowing-orb"></div>
      <div className="glowing-orb"></div>
      
      <div className="premium-card glass fold-corner" style={{ textAlign: 'center', minHeight: '400px', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
        
        {status === 'verifying' && (
          <>
            <Loader2 className="animate-spin text-blue-500" size={64} style={{ marginBottom: '20px', color: '#3b82f6' }} />
            <h2 style={{ fontSize: '1.5rem', marginBottom: '10px' }}>Verifying your email...</h2>
            <p style={{ color: '#aaaaaa' }}>Please wait while we confirm your email address.</p>
          </>
        )}

        {status === 'success' && (
          <>
            <CheckCircle size={64} style={{ marginBottom: '20px', color: '#10b981' }} />
            <h2 style={{ fontSize: '1.5rem', marginBottom: '10px' }}>Email Verified!</h2>
            <p style={{ color: '#aaaaaa', marginBottom: '30px' }}>{message}</p>
            <Link to="/login" className="btn-primary" style={{ textDecoration: 'none' }}>
              Go to Login
            </Link>
          </>
        )}

        {status === 'error' && (
          <>
            <XCircle size={64} style={{ marginBottom: '20px', color: '#ef4444' }} />
            <h2 style={{ fontSize: '1.5rem', marginBottom: '10px' }}>Verification Failed</h2>
            <p style={{ color: '#ef4444', marginBottom: '30px' }}>{message}</p>
            <Link to="/login" className="btn-primary" style={{ textDecoration: 'none' }}>
              Return to Login
            </Link>
          </>
        )}

      </div>
    </div>
  );
}

export default VerifyEmail;
