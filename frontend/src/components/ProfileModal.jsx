import React from 'react';
import { X, Camera } from 'lucide-react';

const ProfileModal = ({ 
  isOpen, 
  onClose, 
  editName, 
  setEditName, 
  editEmail, 
  setEditEmail, 
  onSave, 
  getInitials 
}) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="profile-modal glass" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Edit profile</h3>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          <div className="avatar-edit-section">
            <div className="large-avatar-circle">
              {getInitials(editName)}
              <div className="camera-overlay">
                <Camera size={14} />
              </div>
            </div>
          </div>

          <div className="edit-form">
            <div className="edit-group">
              <label>Display name</label>
              <input
                type="text"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                placeholder="Enter display name"
              />
            </div>
            <div className="edit-group">
              <label>Username</label>
              <input
                type="text"
                value={editEmail}
                onChange={(e) => setEditEmail(e.target.value)}
                placeholder="Enter email or handle"
              />
            </div>
            <p className="edit-hint">Your profile helps people recognize you. Your name and username are also used in the EnergyMind app.</p>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-cancel" onClick={onClose}>Cancel</button>
          <button className="btn-save" onClick={onSave}>Save</button>
        </div>
      </div>
    </div>
  );
};

export default ProfileModal;
