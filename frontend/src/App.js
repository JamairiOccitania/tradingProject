import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppShell, Navbar, Header, Text, NavLink, Group, Button } from '@mantine/core';
import { IconDashboard, IconRobot, IconKey, IconChartLine, IconLogout, IconUser } from '@tabler/icons-react';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import BotsPage from './pages/BotsPage';
import APIKeyPage from './pages/APIKeyPage';
import BacktestingPage from './pages/BacktestingPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import AccountPage from './pages/AccountPage';

function App() {
  const isAuthenticated = !!localStorage.getItem('access_token');

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
  };

  if (!isAuthenticated) {
    return (
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password/:uid/:token" element={<ResetPasswordPage />} />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </Router>
    );
  }

  return (
    <Router>
      <AppShell
        navbar={{
          width: 250,
          breakpoint: 'sm',
        }}
        header={{ height: 60 }}
        padding="md"
      >
        <AppShell.Header>
          <Group h="100%" px="md" justify="space-between">
            <Text size="xl" fw={700} c="blue">
              Trading Platform
            </Text>
            <Button
              variant="subtle"
              color="red"
              leftSection={<IconLogout size={16} />}
              onClick={handleLogout}
            >
              Déconnexion
            </Button>
          </Group>
        </AppShell.Header>

        <AppShell.Navbar p="md">
          <NavLink
            href="/dashboard"
            label="Tableau de bord"
            leftSection={<IconDashboard size="1rem" />}
          />
          <NavLink
            href="/bots"
            label="Mes Bots"
            leftSection={<IconRobot size="1rem" />}
          />
          <NavLink
            href="/api-key"
            label="Clé API"
            leftSection={<IconKey size="1rem" />}
          />
          <NavLink
            href="/backtesting"
            label="Backtesting"
            leftSection={<IconChartLine size="1rem" />}
          />
          <NavLink
            href="/account"
            label="Mon compte"
            leftSection={<IconUser size="1rem" />}
          />
        </AppShell.Navbar>

        <AppShell.Main>
          <Routes>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/bots" element={<BotsPage />} />
            <Route path="/api-key" element={<APIKeyPage />} />
            <Route path="/backtesting" element={<BacktestingPage />} />
            <Route path="/account" element={<AccountPage />} />
            <Route path="*" element={<Navigate to="/dashboard" />} />
          </Routes>
        </AppShell.Main>
      </AppShell>
    </Router>
  );
}

export default App;
