import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

// Components
import Sidebar from '../components/Sidebar';
import MessageList from '../components/MessageList';
import ChatInput from '../components/ChatInput';
import ProfileModal from '../components/ProfileModal';
import LoginModal from '../components/LoginModal';
import CookieConsent from '../components/CookieConsent';

// Utilities
import { handleExportPDF, handleExportDocs } from '../utils/exportUtils';

import './Chatbot.css';

function Chatbot({ isLoggedIn, onLogin, onLogout }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [questionIdx, setQuestionIdx] = useState(0);
  const [isFading, setIsFading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isHistoryOpen, setIsHistoryOpen] = useState(true);
  const [userData, setUserData] = useState({ name: 'Guest User', email: '' });
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  const [editName, setEditName] = useState("");
  const [editEmail, setEditEmail] = useState("");
  const [historyItems, setHistoryItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeMenuId, setActiveMenuId] = useState(null);
  const [activeMsgMenuId, setActiveMsgMenuId] = useState(null);
  const [researchStatus, setResearchStatus] = useState("Searching the web...");
  const [showCookieConsent, setShowCookieConsent] = useState(false);

  const profileMenuRef = useRef(null);
  const navigate = useNavigate();

  // Constants
  const energyQuestions = [
    "How can I help you today?",
    "Looking for some energy analysis?",
    "Want to optimize your power usage?",
    "Need help with solar projections?",
    "What's the outlook for green hydrogen in 2026?",
    "Optimize power usage in data centers.",
    "Role of AI in solar grid management?",
    "How can decentralized energy markets work?"
  ];

  const researchStatuses = [
    "Searching the web for energy data...",
    "Extracting key research points...",
    "Analyzing market trends & policies...",
    "Synthesizing your professional report...",
    "Finalizing SWOT analysis & case studies..."
  ];

  // Effects
  useEffect(() => {
    if (!isLoggedIn) return;
    const init = async () => {
      try {
        const currentUser = await api.getMe();
        setUserData({ name: currentUser.name || currentUser.username, email: currentUser.email });
      } catch (err) {
        console.error('Failed to load user data:', err);
      }
      try {
        const history = await api.getHistory();
        if (history) setHistoryItems(history);
      } catch (err) {
        console.error('Failed to load initial history:', err);
      }
    };
    init();
  }, [isLoggedIn]);

  useEffect(() => {
    if (isLoggedIn) {
      const consent = localStorage.getItem('cookie_consent');
      if (!consent) setShowCookieConsent(true);
    }
  }, [isLoggedIn]);

  useEffect(() => {
    const interval = setInterval(() => {
      setIsFading(true);
      setTimeout(() => {
        setQuestionIdx((prev) => (prev + 1) % energyQuestions.length);
        setIsFading(false);
      }, 500);
    }, 4000);
    return () => clearInterval(interval);
  }, [energyQuestions.length]);

  useEffect(() => {
    let interval;
    if (loading) {
      setResearchStatus(researchStatuses[0]);
      interval = setInterval(() => {
        setResearchStatus((prev) => {
          const currentIndex = researchStatuses.indexOf(prev);
          return researchStatuses[(currentIndex + 1) % researchStatuses.length];
        });
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [loading]);

  useEffect(() => {
    function handleClickOutside(event) {
      if (profileMenuRef.current && !profileMenuRef.current.contains(event.target)) {
        setIsProfileMenuOpen(false);
      }
      if (activeMsgMenuId && !event.target.closest('.msg-options-container')) {
        setActiveMsgMenuId(null);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [activeMsgMenuId]);

  // Handlers
  const getInitials = (name) => {
    if (!name) return 'U';
    const parts = name.trim().split(' ');
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
    return parts[0][0].toUpperCase();
  };

  const handleLogout = () => {
    api.clearToken();
    onLogout();
    navigate('/login');
  };

  const handleSelectHistory = (item) => {
    if (!item.query || !item.response) return;
    setMessages([
      { id: Date.now(), text: item.query, sender: 'user' },
      { id: Date.now() + 1, text: item.response, sender: 'ai' }
    ]);
    if (window.innerWidth < 768) setIsSidebarOpen(false);
  };

  const handleDeleteChat = async (e, chatId) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this research?')) {
      try {
        await api.deleteHistoryItem(chatId);
        setHistoryItems(prev => prev.filter(item => item.id !== chatId));
        setActiveMenuId(null);
      } catch (err) {
        alert('Failed to delete chat: ' + err.message);
      }
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const isFirstMessage = messages.length === 0;
    const userMsg = { id: Date.now(), text: input, sender: 'user' };
    setMessages((prev) => [...prev, userMsg]);
    const currentInput = input;
    setInput("");
    setLoading(true);

    try {
      const response = await api.runResearch(currentInput);
      const aiMsg = { id: Date.now() + 1, text: response.result, sender: 'ai' };
      setMessages((prev) => [...prev, aiMsg]);
      if (isFirstMessage) {
        const updatedHistory = await api.getHistory();
        setHistoryItems(updatedHistory);
      }
    } catch (err) {
      const msg = err.message || JSON.stringify(err);
      const isQuotaError = msg.toLowerCase().includes("limit") || msg.includes("15 chats");
      setMessages((prev) => [...prev, {
        id: Date.now() + 1, text: msg, sender: 'ai', type: isQuotaError ? 'quota' : 'error'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-layout bg-radial">
      <div className="chatbot-background-glow" style={{ top: '-10%', left: '-5%', background: 'radial-gradient(circle, rgba(4, 99, 74, 0.4) 0%, transparent 70%)' }}></div>
      <div className="chatbot-background-glow" style={{ bottom: '-10%', right: '-5%', background: 'radial-gradient(circle, rgba(4, 99, 74, 0.4) 0%, transparent 70%)' }}></div>
      <div className="chatbot-background-glow" style={{ top: '40%', left: '30%', width: '300px', height: '300px', background: 'radial-gradient(circle, rgba(4, 99, 74, 0.4) 0%, transparent 70%)' }}></div>

      {!isLoggedIn && <LoginModal onLogin={onLogin} />}
      {showCookieConsent && <CookieConsent onDecision={() => setShowCookieConsent(false)} />}

      <Sidebar 
        isSidebarOpen={isSidebarOpen}
        setIsSidebarOpen={setIsSidebarOpen}
        isHistoryOpen={isHistoryOpen}
        setIsHistoryOpen={setIsHistoryOpen}
        historyItems={historyItems}
        onSelectHistory={handleSelectHistory}
        onDeleteChat={handleDeleteChat}
        onShareChat={(e, item) => {
          e.stopPropagation();
          navigator.clipboard.writeText(`Query: ${item.query}\nResult: ${item.response}`);
          alert('Copied to clipboard!');
          setActiveMenuId(null);
        }}
        activeMenuId={activeMenuId}
        setActiveMenuId={setActiveMenuId}
        isProfileMenuOpen={isProfileMenuOpen}
        setIsProfileMenuOpen={setIsProfileMenuOpen}
        userData={userData}
        onOpenProfile={() => {
          setEditName(userData.name);
          setEditEmail(userData.email);
          setIsProfileModalOpen(true);
          setIsProfileMenuOpen(false);
        }}
        onLogout={handleLogout}
        profileMenuRef={profileMenuRef}
        getInitials={getInitials}
        onNewChat={() => setMessages([])}
      />

      <main className="main-chat" style={{ marginLeft: isSidebarOpen ? '240px' : '56px' }}>
        <header className="main-header">
          <div className="brand-name-chat">EnergyMind AI</div>
        </header>

        <MessageList 
          messages={messages}
          loading={loading}
          researchStatus={researchStatus}
          activeMsgMenuId={activeMsgMenuId}
          onToggleMsgMenu={(e, id) => {
            e.stopPropagation();
            setActiveMsgMenuId(activeMsgMenuId === id ? null : id);
          }}
          onCopy={(text) => {
            navigator.clipboard.writeText(text);
            alert("Copied!");
            setActiveMsgMenuId(null);
          }}
          onExportPDF={(text, query) => handleExportPDF(text, query, () => setActiveMsgMenuId(null))}
          onExportDocs={(text, query) => handleExportDocs(text, query, () => setActiveMsgMenuId(null))}
        />

        {messages.length === 0 ? (
          <div className="chat-viewport">
            <div className="welcome-section">
              <h1 className={`welcome-title fade-text ${isFading ? 'hiding' : ''}`}>
                {energyQuestions[questionIdx]}
              </h1>
              <div className="welcome-input-wrapper" style={{ width: '100%', maxWidth: '800px', margin: '0 auto' }}>
                <ChatInput 
                  input={input}
                  setInput={setInput}
                  onSend={handleSend}
                  disabled={loading}
                />
              </div>
            </div>
          </div>
        ) : (
          <div className={`sticky-input-container visible`}>
            <ChatInput 
              input={input}
              setInput={setInput}
              onSend={handleSend}
              disabled={loading}
              isCompact={true}
            />
          </div>
        )}
      </main>

      <ProfileModal 
        isOpen={isProfileModalOpen}
        onClose={() => setIsProfileModalOpen(false)}
        editName={editName}
        setEditName={setEditName}
        editEmail={editEmail}
        setEditEmail={setEditEmail}
        onSave={() => {
          const updatedUser = { ...userData, name: editName, email: editEmail };
          setUserData(updatedUser);
          localStorage.setItem('user', JSON.stringify(updatedUser));
          setIsProfileModalOpen(false);
        }}
        getInitials={getInitials}
      />

    </div>
  );
}

export default Chatbot;
