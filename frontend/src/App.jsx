import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import AdminDashboard from './pages/AdminDashboard';
import ChatInterface from './pages/ChatInterface';

function App() {
  const [role, setRole] = useState('user'); // 'user' or 'admin'

  return (
    <Router>
      <Layout role={role} setRole={setRole}>
        <Routes>
          <Route path="/" element={<Navigate to="/chat" />} />
          <Route path="/chat" element={<ChatInterface role={role} />} />
          <Route path="/admin" element={role === 'admin' ? <AdminDashboard /> : <Navigate to="/chat" />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
