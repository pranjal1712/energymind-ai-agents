import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { MoreHorizontal, Copy, FileText, Download, Clock } from 'lucide-react';

// Error Boundary for catching message rendering crashes
class MessageErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() { return { hasError: true }; }
  componentDidCatch(error, errorInfo) { console.error("Markdown rendering error caught:", error, errorInfo); }
  render() {
    if (this.state.hasError) {
      return <div className="msg-fallback">{this.props.fallbackText}</div>;
    }
    return this.props.children;
  }
}

const MessageList = ({ 
  messages, 
  loading, 
  researchStatus, 
  activeMsgMenuId,
  onToggleMsgMenu,
  onCopy,
  onExportPDF,
  onExportDocs
}) => {
  if (messages.length === 0) return null;

  return (
    <div className="chat-viewport">
      <div className="messages-list-new">
          {messages.map((msg) => (
            <div key={msg.id} className={`msg-bubble ${msg.sender}`}>
              {msg.sender === 'ai' && (
                <div className="msg-options-container">
                  <button
                    className="msg-options-btn"
                    onClick={(e) => onToggleMsgMenu(e, msg.id)}
                  >
                    <MoreHorizontal size={16} />
                  </button>

                  {activeMsgMenuId === msg.id && (
                    <div className="msg-options-dropdown glass">
                      <button className="msg-dropdown-item" onClick={() => onCopy(msg.text)}>
                        <Copy size={14} /> <span>Copy</span>
                      </button>
                      <div className="dropdown-divider"></div>
                      <button className="msg-dropdown-item" onClick={() => onExportPDF(msg.text, "Research Report")}>
                        <FileText size={14} /> <span>Export PDF</span>
                      </button>
                      <button className="msg-dropdown-item" onClick={() => onExportDocs(msg.text, "Research Report")}>
                        <Download size={14} /> <span>Export DOCS</span>
                      </button>
                    </div>
                  )}
                </div>
              )}
              <MessageErrorBoundary fallbackText={msg.text}>
                {msg.type === 'quota' ? (
                  <div className="limit-reached-content">
                    <div className="limit-icon-container">
                      <Clock size={20} className="clock-anim" />
                    </div>
                    <div className="limit-text-container">
                      <span className="limit-title">Daily Quota Reached</span>
                      <p className="limit-message">{msg.text}</p>
                    </div>
                  </div>
                ) : (
                  msg.sender === 'ai' ? (
                    typeof msg.text === 'string' ? (
                      <div className="markdown-body">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {msg.text || ""}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      <span className="error-text">Message format error.</span>
                    )
                  ) : (
                    <div style={{ wordBreak: 'break-word' }}>{msg.text || ""}</div>
                  )
                )}
              </MessageErrorBoundary>
            </div>
          ))}

          {loading && (
            <div className="msg-bubble ai thinking">
              <div className="thinking-content">
                <div className="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
                <div className="status-text-anim">
                  {researchStatus}
                </div>
              </div>
            </div>
          )}

          <div className="bottom-spacing"></div>
        </div>
    </div>
  );
};

export default MessageList;
