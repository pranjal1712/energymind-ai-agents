import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Signup from './pages/Signup';
import ForgotPassword from './pages/ForgotPassword';
import Profile from './pages/Profile';
import Chatbot from './pages/Chatbot';
import './index.css';

// ProtectedRoute component
const ProtectedRoute = ({ children, isLoggedIn }) => {
  if (!isLoggedIn) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  return (
    <Router>
      <div className="app-container">
        <Routes>
          <Route path="/" element={<Navigate to="/login" />} />
          <Route 
            path="/login" 
            element={<Login onLogin={() => setIsLoggedIn(true)} />} 
          />
          <Route path="/signup" element={<Signup />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          
          <Route 
            path="/profile" 
            element={
              <ProtectedRoute isLoggedIn={isLoggedIn}>
                <Profile onLogout={() => setIsLoggedIn(false)} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/chatbot" 
            element={
              <ProtectedRoute isLoggedIn={isLoggedIn}>
                <Chatbot onLogout={() => setIsLoggedIn(false)} />
              </ProtectedRoute>
            } 
          />
          
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
