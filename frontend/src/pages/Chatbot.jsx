import React, { useState, useRef, useEffect } from 'react';
import { MoreVertical, Send, Plus, History, LogOut, User, MessageSquare } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

function Chatbot() {
  const [messages, setMessages] = useState([
    { id: 1, text: "Hello! How can I help you today?", sender: 'bot' }
  ]);
  const [input, setInput] = useState("");
  const [showMenu, setShowMenu] = useState(false);
  const menuRef = useRef(null);
  const navigate = useNavigate();

  // Close menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowMenu(false);
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
    
    // Simulate bot response
    setTimeout(() => {
      setMessages(prev => [...prev, { 
        id: prev.length + 1, 
        text: "I'm a React-based EnergyMind Agent. How can I assist you with your energy data?", 
        sender: 'bot' 
      }]);
    }, 1000);
  };

  return (
    <div className="chat-page">
      {/* Header */}
      <header className="chat-header glass">
        <div className="header-left">
          <div className="logo-icon"><MessageSquare size={24} /></div>
          <h1 className="header-title">EnergyMind AI</h1>
        </div>
        
        <div className="header-right" ref={menuRef}>
          <button className="menu-trigger" onClick={() => setShowMenu(!showMenu)}>
            <MoreVertical size={24} />
          </button>
          
          {showMenu && (
            <div className="dropdown-menu glass">
              <button className="menu-item" onClick={() => { setMessages([{ id: 1, text: "Starting a new chat...", sender: 'bot' }]); setShowMenu(false); }}>
                <Plus size={18} /> New Chat
              </button>
              <button className="menu-item">
                <History size={18} /> History
              </button>
              <button className="menu-item" onClick={() => navigate('/profile')}>
                <User size={18} /> Profile
              </button>
              <div className="menu-divider"></div>
              <button className="menu-item logout" onClick={() => navigate('/login')}>
                <LogOut size={18} /> Logout
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Chat Area */}
      <main className="chat-container">
        <div className="messages-list">
          {messages.map((msg) => (
            <div key={msg.id} className={`message-wrapper ${msg.sender}`}>
              <div className={`message-bubble ${msg.sender === 'bot' ? 'glass' : 'user'}`}>
                {msg.text}
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* Input Area */}
      <footer className="chat-input-area">
        <div className="input-wrapper glass">
          <input 
            type="text" 
            placeholder="Ask me anything..." 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          />
          <button className="send-btn" onClick={handleSend}>
            <Send size={20} />
          </button>
        </div>
      </footer>

      <style>{`
        .chat-page {
          height: 100vh;
          display: flex;
          flex-direction: column;
          background-color: var(--bg-dark);
          color: var(--text-main);
        }

        .chat-header {
          padding: 1rem 2rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
          z-index: 100;
        }
        .header-left { display: flex; align-items: center; gap: 0.75rem; }
        .logo-icon { color: var(--primary); }
        .header-title { font-size: 1.25rem; font-weight: 700; }
        
        .header-right { position: relative; }
        .menu-trigger { background: transparent; color: var(--text-muted); padding: 0.5rem; border-radius: 50%; transition: var(--transition); }
        .menu-trigger:hover { background: rgba(255, 255, 255, 0.1); color: var(--text-main); }

        .dropdown-menu {
          position: absolute;
          top: calc(100% + 0.5rem);
          right: 0;
          width: 200px;
          border-radius: var(--radius);
          padding: 0.5rem;
          box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }
        .menu-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem;
          width: 100%;
          background: transparent;
          color: var(--text-main);
          font-size: 0.875rem;
          font-weight: 500;
          text-align: left;
          border-radius: 8px;
          transition: var(--transition);
        }
        .menu-item:hover { background: rgba(255, 255, 255, 0.05); color: var(--primary); }
        .menu-item.logout { color: var(--error); }
        .menu-item.logout:hover { background: rgba(239, 68, 68, 0.1); }
        .menu-divider { height: 1px; background: var(--border); margin: 0.5rem; }

        .chat-container {
          flex: 1;
          overflow-y: auto;
          padding: 2rem;
          display: flex;
          flex-direction: column;
        }
        .messages-list {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
          max-width: 800px;
          margin: 0 auto;
          width: 100%;
        }
        .message-wrapper { display: flex; width: 100%; }
        .message-wrapper.user { justify-content: flex-end; }
        .message-wrapper.bot { justify-content: flex-start; }
        
        .message-bubble {
          max-width: 80%;
          padding: 1rem 1.25rem;
          border-radius: 12px;
          font-size: 0.95rem;
        }
        .message-bubble.bot { border-top-left-radius: 2px; }
        .message-bubble.user { 
          background: var(--primary); 
          color: white; 
          border-top-right-radius: 2px;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        .chat-input-area {
          padding: 2rem;
          display: flex;
          justify-content: center;
        }
        .input-wrapper {
          width: 100%;
          max-width: 800px;
          display: flex;
          align-items: center;
          padding: 0.5rem 1rem;
          border-radius: 100px;
          border: 1px solid var(--border);
        }
        .input-wrapper input {
          flex: 1;
          background: transparent;
          border: none;
          outline: none;
          color: var(--text-main);
          padding: 0.75rem;
          font-size: 1rem;
        }
        .send-btn {
          background: var(--primary);
          color: white;
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: var(--transition);
        }
        .send-btn:hover { background: var(--primary-hover); transform: scale(1.05); }
      `}</style>
    </div>
  );
}

export default Chatbot;
