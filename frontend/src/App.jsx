import { Routes, Route, Navigate } from 'react-router-dom'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import AdminDashboard from './pages/AdminDashboard'
import PlanSelectionPage from './pages/PlanSelectionPage'
import ProgressPage from './pages/ProgressPage'
import AnalysisPage from './pages/AnalysisPage'
import ResultsPage from './pages/ResultsPage'
import SimulationPage from './pages/SimulationPage'
import AdvancedMetricsPage from './pages/AdvancedMetricsPage'
import { isAuthenticated, isAdmin } from './services/auth'

// Protected Route wrapper
function ProtectedRoute({ children, adminOnly = false }) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />
  }

  if (adminOnly && !isAdmin()) {
    return <Navigate to="/dashboard" replace />
  }

  return children
}

function App() {
  return (
    <div className="app">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/dashboard"
          element={
            <ProtectedRoute adminOnly>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/plans"
          element={
            <ProtectedRoute>
              <PlanSelectionPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/progress"
          element={
            <ProtectedRoute>
              <ProgressPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/analyze"
          element={
            <ProtectedRoute>
              <AnalysisPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/results"
          element={
            <ProtectedRoute>
              <ResultsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/simulations"
          element={
            <ProtectedRoute>
              <SimulationPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/advanced"
          element={
            <ProtectedRoute>
              <AdvancedMetricsPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </div>
  )
}

export default App
