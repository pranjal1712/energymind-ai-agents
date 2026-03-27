import React, { useState, useRef, useEffect } from 'react';
import { MoreVertical, Send, Plus, History, LogOut, User, MessageSquare, Image, MoreHorizontal, Search, Settings } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

function Chatbot({ onLogout }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [showInputMenu, setShowInputMenu] = useState(false);
  const inputMenuRef = useRef(null);
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  const historyItems = [
    "Translation of Ruhi Sharif",
    "Translation of Ruhi Sharif",
    "Translation of Ruhi Sharif",
    "Translation of Ruhi Sharif"
  ];

  useEffect(() => {
    function handleClickOutside(event) {
      if (inputMenuRef.current && !inputMenuRef.current.contains(event.target)) {
        setShowInputMenu(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSend = () => {
    if (!input.trim()) return;
    const newMsg = { id: messages.length + 1, text: input, sender: 'user' };
    setMessages([...messages, newMsg]);
    setInput("");
  };

  return (
    <div className="chat-layout bg-grid">
      {/* Sidebar */}
      <aside className="sidebar glass">
        <div className="sidebar-header">
          <div className="logo-section">
            <MessageSquare size={20} className="logo-icon" />
            <span className="logo-text">EnergyMind</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          <button className="new-chat-btn" onClick={() => setMessages([])}>
            <Plus size={18} /> New Chat
          </button>

          <div className="nav-section">
            <h3 className="section-title">History</h3>
            <div className="history-list">
              {historyItems.map((item, idx) => (
                <div key={idx} className="history-item">
                  <MessageSquare size={14} />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </nav>

        <div className="sidebar-footer">
          <button className="user-profile-btn" onClick={() => navigate('/profile')}>
            <div className="user-avatar">
              <User size={16} />
            </div>
            <div className="user-info">
              <span className="user-name">Shahzaib</span>
              <span className="user-email">shahzaib@example.com</span>
            </div>
            <div className="footer-actions">
              <Settings size={14} className="settings-icon" />
              <LogOut size={14} className="logout-icon" onClick={(e) => { e.stopPropagation(); handleLogout(); }} />
            </div>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-chat">
        <header className="main-header">
          <div className="model-selector glass">
            Model 2.5 <ChevronDown size={14} />
          </div>
        </header>

        <div className="chat-viewport">
          {messages.length === 0 ? (
            <div className="welcome-section">
              <h1 className="welcome-title">What's on your mind today?</h1>
              <div className="input-container-large glass">
                <textarea 
                  placeholder="Message AI chat..." 
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSend())}
                />
                <div className="input-toolbar">
                  <div className="toolbar-left" ref={inputMenuRef}>
                    <button className="icon-btn" onClick={() => setShowInputMenu(!showInputMenu)}>
                      <MoreHorizontal size={18} />
                    </button>
                    {showInputMenu && (
                      <div className="input-dropdown glass">
                        <button className="dropdown-item">
                          <Image size={16} /> Upload Image
                        </button>
                      </div>
                    )}
                    <button className="toolbar-pill">
                      <Search size={14} /> Search
                    </button>
                    <button className="toolbar-pill">
                      <Image size={14} /> Create image
                    </button>
                  </div>
                  <div className="toolbar-right">
                    <button className="send-btn-new" onClick={handleSend} disabled={!input.trim()}>
                      <Send size={18} />
                    </button>
                  </div>
                </div>
              </div>
              
              <div className="suggestion-tags">
                {["AI script writer", "Coding Assistant", "Essay writer", "Business", "Translate"].map(tag => (
                  <span key={tag} className="tag glass">{tag}</span>
                ))}
              </div>
            </div>
          ) : (
            <div className="messages-list-new">
              {messages.map((msg) => (
                <div key={msg.id} className={`msg-bubble ${msg.sender}`}>
                  {msg.text}
                </div>
              ))}
              <div className="bottom-spacing"></div>
            </div>
          )}
        </div>

        {messages.length > 0 && (
          <div className="sticky-input-container">
            <div className="input-container-compact glass">
              <input 
                type="text" 
                placeholder="Message AI chat..." 
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              />
              <button className="send-btn-small" onClick={handleSend} disabled={!input.trim()}>
                <Send size={16} />
              </button>
            </div>
          </div>
        )}
      </main>

      <style>{`
        .chat-layout { display: flex; height: 100vh; overflow: hidden; }
        
        /* Sidebar Styles */
        .sidebar {
          width: var(--sidebar-width);
          height: 100%;
          display: flex;
          flex-direction: column;
          border-right: 1px solid var(--border);
          z-index: 50;
        }
        .sidebar-header { padding: 1.5rem; }
        .logo-section { display: flex; align-items: center; gap: 0.75rem; }
        .logo-icon { color: var(--primary); }
        .logo-text { font-weight: 700; font-size: 1.1rem; }

        .sidebar-nav { flex: 1; padding: 0 1rem; overflow-y: auto; }
        .new-chat-btn {
          width: 100%;
          padding: 0.75rem;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          color: white;
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 2rem;
          font-weight: 500;
          transition: var(--transition);
        }
        .new-chat-btn:hover { background: rgba(255, 255, 255, 0.1); }

        .section-title { font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 1rem; letter-spacing: 0.05em; }
        .history-list { display: flex; flex-direction: column; gap: 0.5rem; }
        .history-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.6rem 0.75rem;
          font-size: 0.85rem;
          color: var(--text-muted);
          border-radius: 8px;
          cursor: pointer;
          transition: var(--transition);
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .history-item:hover { background: rgba(255, 255, 255, 0.05); color: white; }

        .sidebar-footer { padding: 1rem; border-top: 1px solid var(--border); }
        .user-profile-btn {
          width: 100%;
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem;
          background: transparent;
          border-radius: var(--radius);
          text-align: left;
          color: white;
          transition: var(--transition);
        }
        .user-profile-btn:hover { background: rgba(255, 255, 255, 0.05); }
        .user-avatar { width: 32px; height: 32px; background: var(--primary); border-radius: 50%; display: flex; align-items: center; justify-content: center; }
        .user-info { flex: 1; display: flex; flex-direction: column; }
        .user-name { font-size: 0.85rem; font-weight: 600; }
        .user-email { font-size: 0.7rem; color: var(--text-muted); }

        /* Main Content Styles */
        .main-chat { flex: 1; display: flex; flex-direction: column; position: relative; }
        .main-header { padding: 1rem 2rem; display: flex; justify-content: flex-end; }
        .model-selector { padding: 0.5rem 1rem; border-radius: 100px; font-size: 0.85rem; display: flex; align-items: center; gap: 0.5rem; cursor: pointer; }

        .chat-viewport { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 2rem; overflow-y: auto; }
        .welcome-section { width: 100%; max-width: 800px; display: flex; flex-direction: column; align-items: center; margin-top: 10vh; }
        .welcome-title { font-size: 2.5rem; font-weight: 700; margin-bottom: 2.5rem; text-align: center; }
        
        .input-container-large {
          width: 100%;
          border-radius: 20px;
          padding: 1.25rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
          box-shadow: 0 20px 50px rgba(0,0,0,0.3);
        }
        .input-container-large textarea {
          width: 100%;
          background: transparent;
          border: none;
          outline: none;
          color: white;
          font-size: 1.1rem;
          resize: none;
          min-height: 100px;
        }

        .input-toolbar { display: flex; justify-content: space-between; align-items: center; }
        .toolbar-left { display: flex; align-items: center; gap: 0.75rem; position: relative; }
        .icon-btn { background: rgba(255, 255, 255, 0.05); color: var(--text-muted); width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; transition: var(--transition); }
        .icon-btn:hover { background: rgba(255, 255, 255, 0.1); color: white; }
        
        .toolbar-pill {
          padding: 0.4rem 0.75rem;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 100px;
          color: var(--text-muted);
          font-size: 0.75rem;
          display: flex;
          align-items: center;
          gap: 0.4rem;
          transition: var(--transition);
        }
        .toolbar-pill:hover { background: rgba(255, 255, 255, 0.1); color: white; }

        .input-dropdown {
          position: absolute;
          bottom: calc(100% + 0.5rem);
          left: 0;
          width: 160px;
          border-radius: var(--radius);
          padding: 0.5rem;
          display: flex;
          flex-direction: column;
          z-index: 10;
        }
        .dropdown-item {
          padding: 0.6rem 0.75rem;
          width: 100%;
          background: transparent;
          color: white;
          font-size: 0.8rem;
          display: flex;
          align-items: center;
          gap: 0.6rem;
          border-radius: 8px;
          transition: var(--transition);
        }
        .dropdown-item:hover { background: rgba(255, 255, 255, 0.1); }

        .send-btn-new {
          background: var(--primary);
          color: white;
          width: 40px;
          height: 40px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: var(--transition);
        }
        .send-btn-new:disabled { opacity: 0.3; cursor: not-allowed; }
        .send-btn-new:not(:disabled):hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4); }

        .suggestion-tags { display: flex; flex-wrap: wrap; gap: 0.75rem; justify-content: center; margin-top: 3rem; }
        .tag { padding: 0.5rem 1rem; border-radius: 100px; font-size: 0.8rem; color: var(--text-muted); cursor: pointer; transition: var(--transition); }
        .tag:hover { border-color: var(--primary); color: white; }

        /* Compact Input for Active Chat */
        .sticky-input-container {
          position: sticky;
          bottom: 0;
          width: 100%;
          padding: 1.5rem 2rem;
          display: flex;
          justify-content: center;
          background: linear-gradient(transparent, #0f172a 20%);
        }
        .input-container-compact {
          width: 100%;
          max-width: 800px;
          display: flex;
          align-items: center;
          padding: 0.5rem 0.75rem 0.5rem 1.25rem;
          border-radius: 100px;
        }
        .input-container-compact input { flex: 1; background: transparent; border: none; outline: none; color: white; padding: 0.5rem 0; }
        .send-btn-small { background: var(--primary); color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; opacity: 0.3; }
        .send-btn-small:not(:disabled) { opacity: 1; }
        .footer-actions { display: flex; align-items: center; gap: 0.5rem; }
        .logout-icon { color: var(--text-muted); transition: var(--transition); }
        .logout-icon:hover { color: var(--error); transform: scale(1.1); }
      `}</style>
    </div>
  );
}

function ChevronDown({ size, style }) {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 24 24" 
      fill="none" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round" 
      style={style}
    >
      <path d="m6 9 6 6 6-6"/>
    </svg>
  );
}

export default Chatbot;
