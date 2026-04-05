import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Signup from './pages/Signup';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import Chatbot from './pages/Chatbot';
import api from './services/api';
import './index.css';

// ProtectedRoute component
const ProtectedRoute = ({ children, isLoggedIn }) => {
  if (!isLoggedIn) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

function App() {
  const [isLoggedIn, setIsLoggedIn] = React.useState(() => {
    // Check if token exists in localStorage or Cookies on startup
    return !!api.getToken();
  });

  return (
    <Router>
      <div className="app-container">
        <Routes>
          <Route path="/" element={<Navigate to="/chatbot" />} />
          <Route
            path="/login"
            element={isLoggedIn ? <Navigate to="/chatbot" /> : <Login onLogin={() => setIsLoggedIn(true)} />}
          />
          <Route
            path="/signup"
            element={isLoggedIn ? <Navigate to="/chatbot" /> : <Signup onSignup={() => setIsLoggedIn(true)} />}
          />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />


          <Route
            path="/chatbot"
            element={
              <Chatbot
                isLoggedIn={isLoggedIn}
                onLogin={() => setIsLoggedIn(true)}
                onLogout={() => setIsLoggedIn(false)}
              />
            }
          />

          <Route path="*" element={<Navigate to="/chatbot" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
