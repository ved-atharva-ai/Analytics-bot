import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import AdminDashboard from './pages/AdminDashboard';
import ChatInterface from './pages/ChatInterface';

import { LanguageProvider } from './context/LanguageContext';

function App() {
  const [role] = useState('admin'); // Default to admin

  return (
    <LanguageProvider>
      <Router>
        <Layout role={role}>
          <Routes>
            <Route path="/" element={<Navigate to="/chat" />} />
            <Route path="/chat" element={<ChatInterface role={role} />} />
            <Route path="/admin" element={<AdminDashboard />} />
          </Routes>
        </Layout>
      </Router>
    </LanguageProvider>
  );
}

export default App;
