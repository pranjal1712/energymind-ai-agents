import React from 'react';
import { Send } from 'lucide-react';

const ChatInput = ({ 
  input, 
  setInput, 
  onSend, 
  disabled, 
  isCompact = false, 
  placeholder = "Hi! What's on your mind?",
  onKeyPress
}) => {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  if (isCompact) {
    return (
      <div className="input-container-compact glass">
        <input
          type="text"
          placeholder={placeholder}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && onSend()}
        />
        <button className="send-btn-small" onClick={onSend} disabled={disabled || !input.trim()}>
          <Send size={16} />
        </button>
      </div>
    );
  }

  return (
    <div className="input-container-large glass">
      <textarea
        placeholder={placeholder}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
      />
      <div className="input-toolbar">
        <div className="toolbar-left"></div>
        <div className="toolbar-right">
          <button className="send-btn-new" onClick={onSend} disabled={disabled || !input.trim()}>
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;
