import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Activity, User, LogOut, Menu, X, Target } from 'lucide-react'
import { getStoredUser, logout, isAdmin } from '../services/auth'
import logo from '../assets/logo.jpg'
import './Navigation.css'

function Navigation() {
  const [menuOpen, setMenuOpen] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const user = getStoredUser()

  const handleLogout = async () => {
    await logout()
    navigate('/')  // Redirect to home page instead of login
  }

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: Activity },
    { path: '/plans', label: 'My Plans', icon: Target },
    ...(isAdmin() ? [{ path: '/admin/dashboard', label: 'Admin', icon: User }] : [])
  ]

  return (
    <nav className="navigation">
      <div className="nav-container">
        <div className="nav-brand" onClick={() => navigate('/dashboard')}>
          <img src={logo} alt="Diavita Logo" className="brand-logo" style={{ height: '40px', width: 'auto', marginRight: '10px' }} />
          <span>DIAVITA</span>
        </div>

        <button className="mobile-menu-btn" onClick={() => setMenuOpen(!menuOpen)}>
          {menuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>

        <div className={`nav-menu ${menuOpen ? 'open' : ''}`}>
          <div className="nav-links">
            {navItems.map((item) => (
              <button
                key={item.path}
                className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
                onClick={() => {
                  navigate(item.path)
                  setMenuOpen(false)
                }}
              >
                <item.icon size={18} />
                <span>{item.label}</span>
              </button>
            ))}
          </div>

          <div className="nav-user">
            <div className="user-info">
              <div className="user-avatar">
                {user?.username?.charAt(0).toUpperCase()}
              </div>
              <div className="user-details">
                <div className="user-name">{user?.username}</div>
                <div className="user-role">{user?.role}</div>
              </div>
            </div>
            <button className="logout-btn" onClick={handleLogout}>
              <LogOut size={18} />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navigation
