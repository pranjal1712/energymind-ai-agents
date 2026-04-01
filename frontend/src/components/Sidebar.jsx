import React from 'react';
import { 
  PanelLeft, MessageSquare, Edit3, ChevronRight, 
  MoreVertical, Share2, Trash2, User, LogOut, MoreHorizontal 
} from 'lucide-react';
import logo from '../assets/logo-em.png';

const Sidebar = ({
  isSidebarOpen,
  setIsSidebarOpen,
  isHistoryOpen,
  setIsHistoryOpen,
  historyItems,
  onSelectHistory,
  onDeleteChat,
  onShareChat,
  activeMenuId,
  setActiveMenuId,
  isProfileMenuOpen,
  setIsProfileMenuOpen,
  userData,
  onOpenProfile,
  onLogout,
  profileMenuRef,
  getInitials,
  onNewChat
}) => {
  const toggleHistoryMenu = (e, id) => {
    e.stopPropagation();
    setActiveMenuId(activeMenuId === id ? null : id);
  };

  return (
    <aside className={`sidebar glass ${!isSidebarOpen ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div
          className="logo-section-sidebar"
          onClick={() => !isSidebarOpen && setIsSidebarOpen(true)}
          style={{ cursor: !isSidebarOpen ? 'pointer' : 'default' }}
        >
          <img src={logo} alt="Logo" style={{ width: '26px', height: '26px', mixBlendMode: 'screen' }} />
        </div>
        {isSidebarOpen && (
          <button className="sidebar-toggle-btn-original" onClick={() => setIsSidebarOpen(false)}>
            <PanelLeft size={18} />
          </button>
        )}
      </div>

      <nav className="sidebar-nav">
        <button className="new-chat-btn-slim" onClick={onNewChat} title="New chat">
          <Edit3 size={16} />
          <span className="nav-label">New chat</span>
        </button>

        <div className="nav-section">
          <button
            className="section-header-clickable-btn"
            onClick={() => isSidebarOpen && setIsHistoryOpen(!isHistoryOpen)}
          >
            <h3 className="section-title-new">Your chats</h3>
            {isSidebarOpen && (
              <ChevronRight
                size={16}
                className={`chevron-icon-anim ${isHistoryOpen ? 'rotated' : ''}`}
              />
            )}
          </button>
          <div className={`history-list-container ${isHistoryOpen && isSidebarOpen ? 'open' : ''}`}>
            <div className="history-list">
              {historyItems.map((item, idx) => (
                <div
                  key={item.id || idx}
                  className="history-item"
                  onClick={() => onSelectHistory(item)}
                  style={{ position: 'relative' }}
                >
                  <MessageSquare size={14} />
                  <span className="nav-label">{item.query}</span>
                  <button
                    className="history-more-btn"
                    onClick={(e) => toggleHistoryMenu(e, item.id)}
                  >
                    <MoreVertical size={14} />
                  </button>

                  {activeMenuId === item.id && (
                    <div className="history-dropdown glass">
                      <button className="dropdown-item" onClick={(e) => onShareChat(e, item)}>
                        <Share2 size={14} /> Share
                      </button>
                      <button className="dropdown-item delete-item" onClick={(e) => onDeleteChat(e, item.id)}>
                        <Trash2 size={14} /> Delete
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </nav>

      <div className="sidebar-footer" ref={profileMenuRef}>
        {isProfileMenuOpen && isSidebarOpen && (
          <div className="user-profile-menu glass">
            <button className="menu-item" onClick={onOpenProfile}>
              <User size={16} />
              <span>Profile</span>
            </button>
            <button className="menu-item logout" onClick={onLogout}>
              <LogOut size={16} />
              <span>Logout</span>
            </button>
          </div>
        )}

        <div
          className={`user-profile-block ${!isSidebarOpen ? 'slim' : ''} ${isProfileMenuOpen ? 'active' : ''}`}
          onClick={() => isSidebarOpen && setIsProfileMenuOpen(!isProfileMenuOpen)}
        >
          <div className="user-avatar-circle">
            {getInitials(userData.name)}
          </div>
          {isSidebarOpen && (
            <div className="user-info-text">
              <div className="user-name-display">{userData.name}</div>
              <div className="user-email-display">{userData.email || 'Free Plan'}</div>
            </div>
          )}
          {isSidebarOpen && (
            <div className="profile-dots">
              <MoreHorizontal size={16} />
            </div>
          )}
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
