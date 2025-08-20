import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import BotsPage from './pages/BotsPage';
import APIKeyPage from './pages/APIKeyPage';
import BacktestingPage from './pages/BacktestingPage';

function App() {
  // Logique simple pour vérifier si l'utilisateur est authentifié (à améliorer)
  const isAuthenticated = !!localStorage.getItem('access_token');

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route 
          path="/dashboard" 
          element={isAuthenticated ? <DashboardPage /> : <Navigate to="/login" />}
        />
        <Route 
          path="/bots" 
          element={isAuthenticated ? <BotsPage /> : <Navigate to="/login" />}
        />
        <Route 
          path="/api-key" 
          element={isAuthenticated ? <APIKeyPage /> : <Navigate to="/login" />}
        />
        <Route 
          path="/backtesting" 
          element={isAuthenticated ? <BacktestingPage /> : <Navigate to="/login" />}
        />
        <Route 
          path="*" 
          element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />}
        />
      </Routes>
    </Router>
  );
}

export default App;
