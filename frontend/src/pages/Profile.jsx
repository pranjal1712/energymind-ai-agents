import React from 'react';
import { Link } from 'react-router-dom';
import { User, Mail, Settings, LogOut, ChevronRight } from 'lucide-react';

function Profile({ onLogout }) {
  const navigate = useNavigate();
  const user = {
    name: "Shahzaib",
    email: "shahzaib@example.com",
    joined: "March 2026"
  };

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  return (
    <div className="profile-page">
      <div className="profile-container">
        <header className="profile-header">
          <Link to="/chatbot" className="back-link">
            <ChevronRight style={{ transform: 'rotate(180deg)' }} /> Back to Chat
          </Link>
          <h1 className="page-title">Profile Settings</h1>
        </header>

        <main className="profile-content">
          <section className="profile-card premium-card glass">
            <div className="user-info">
              <div className="avatar">
                <User size={40} />
              </div>
              <div className="user-details">
                <h2>{user.name}</h2>
                <p>{user.email}</p>
              </div>
            </div>
            <div className="stats-row">
              <div className="stat-item">
                <span className="stat-label">Joined</span>
                <span className="stat-value">{user.joined}</span>
              </div>
            </div>
          </section>

          <section className="settings-list">
            <div className="settings-item premium-card glass clickable">
              <div className="item-icon"><User size={20} /></div>
              <div className="item-text">Account Information</div>
              <ChevronRight size={20} className="chevron" />
            </div>
            <div className="settings-item premium-card glass clickable">
              <div className="item-icon"><Mail size={20} /></div>
              <div className="item-text">Email Preferences</div>
              <ChevronRight size={20} className="chevron" />
            </div>
            <div className="settings-item premium-card glass clickable">
              <div className="item-icon"><Settings size={20} /></div>
              <div className="item-text">Privacy & Security</div>
              <ChevronRight size={20} className="chevron" />
            </div>
            <div className="settings-item premium-card glass clickable logout-prominent" onClick={handleLogout}>
              <div className="item-icon"><LogOut size={20} /></div>
              <div className="item-text">Log Out</div>
              <ChevronRight size={20} className="chevron" />
            </div>
          </section>
        </main>
      </div>

      <style>{`
        .profile-page {
          min-height: 100vh;
          background-color: var(--bg-dark);
          padding: 2rem;
          display: flex;
          justify-content: center;
        }
        .profile-container { width: 100%; max-width: 600px; }
        .profile-header { margin-bottom: 2rem; display: flex; flex-direction: column; gap: 0.5rem; }
        .back-link { display: flex; align-items: center; gap: 0.25rem; font-size: 0.875rem; color: var(--text-muted); }
        .page-title { font-size: 2rem; font-weight: 700; color: var(--text-main); }
        
        .profile-card { display: flex; flex-direction: column; gap: 1.5rem; margin-bottom: 2rem; }
        .user-info { display: flex; align-items: center; gap: 1.5rem; }
        .avatar { width: 80px; height: 80px; background: var(--primary); border-radius: 50%; display: flex; align-items: center; justify-content: center; }
        .user-details h2 { font-size: 1.5rem; font-weight: 600; }
        .user-details p { color: var(--text-muted); }
        
        .stat-item { display: flex; flex-direction: column; }
        .stat-label { font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.05em; }
        .stat-value { font-weight: 600; }

        .settings-list { display: flex; flex-direction: column; gap: 1rem; }
        .settings-item { display: flex; align-items: center; gap: 1rem; padding: 1.25rem; cursor: pointer; transition: var(--transition); }
        .settings-item:hover { border-color: var(--primary); transform: translateX(4px); }
        .item-icon { color: var(--primary); display: flex; }
        .item-text { flex: 1; font-weight: 500; }
        .chevron { color: var(--text-muted); }
        .logout { color: var(--error); }
        .logout .item-icon { color: var(--error); }
      `}</style>
    </div>
  );
}

export default Profile;
