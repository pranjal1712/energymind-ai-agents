import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Share2, Clock, ChevronLeft } from 'lucide-react';
import api from '../services/api';
import logo from '../assets/logo-em.png';

function SharedReport() {
  const { id } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const data = await api.getSharedReport(id);
        setReport(data);
      } catch (err) {
        setError(err.message || 'Failed to load report');
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, [id]);

  if (loading) {
    return (
      <div className="auth-page bg-radial" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        <div className="typing-dots"><span></span><span></span><span></span></div>
        <p style={{ marginTop: '1rem', color: 'rgba(255,255,255,0.6)' }}>Loading shared report...</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="auth-page bg-radial" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '2rem' }}>
        <div className="premium-card glass fold-corner" style={{ textAlign: 'center' }}>
          <h1 className="auth-title">Report Not Found</h1>
          <p className="auth-subtitle">{error || "This report may have been deleted or the link is incorrect."}</p>
          <Link to="/" className="btn-primary" style={{ display: 'inline-block', marginTop: '1.5rem', textDecoration: 'none' }}>Go to Home</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page bg-radial" style={{ overflowY: 'auto', padding: '2rem 1rem', display: 'block', height: 'auto', minHeight: '100vh' }}>
      <div className="container" style={{ maxWidth: '900px', margin: '0 auto' }}>
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <Link to="/" className="brand-header" style={{ position: 'static', margin: 0, textDecoration: 'none' }}>
            <img src={logo} alt="Logo" className="brand-logo" />
            <span className="brand-name">EnergyMind</span>
          </Link>
          <div style={{ display: 'flex', gap: '1rem' }}>
             <Link to="/login" className="btn-primary" style={{ textDecoration: 'none', fontSize: '0.8rem', padding: '0.5rem 1rem' }}>Try EnergyMind</Link>
          </div>
        </header>

        <div className="premium-card glass fold-corner" style={{ padding: '2.5rem', marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-main)', fontSize: '0.8rem', fontWeight: 600, marginBottom: '1rem' }}>
            <Share2 size={16} /> PUBLIC RESEARCH REPORT
          </div>
          
          <h1 style={{ fontSize: '2rem', color: 'white', marginBottom: '1.5rem', lineHeight: 1.2 }}>{report.query}</h1>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem', color: 'rgba(255,255,255,0.5)', fontSize: '0.85rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Clock size={14} /> {new Date(report.timestamp).toLocaleDateString()}
            </div>
            <div style={{ width: '4px', height: '4px', borderRadius: '50%', background: 'rgba(255,255,255,0.3)' }}></div>
            <div>AI Generated Analysis</div>
          </div>

          <div className="markdown-body" style={{ color: 'rgba(255,255,255,0.9)', lineHeight: 1.6 }}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {report.response}
            </ReactMarkdown>
          </div>
        </div>

        <footer style={{ textAlign: 'center', padding: '2rem 0', color: 'rgba(255,255,255,0.4)', fontSize: '0.85rem' }}>
          <p>© {new Date().getFullYear()} EnergyMind AI. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
}

export default SharedReport;
