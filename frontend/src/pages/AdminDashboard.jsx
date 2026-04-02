import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getStoredUser, logout, getAllUsers, getAllHistory, deleteUser } from '../services/auth'
import ConfirmModal from '../components/ConfirmModal'
import NotificationModal from '../components/NotificationModal'
import './AdminDashboard.css'

function AdminDashboard() {
  const [user, setUser] = useState(null)
  const [users, setUsers] = useState([])
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('users')
  const [confirmModal, setConfirmModal] = useState({ isOpen: false, userId: null, username: '' })
  const [notification, setNotification] = useState({ isOpen: false, type: 'success', title: '', message: '' })
  const navigate = useNavigate()

  useEffect(() => {
    const loadAdminData = async () => {
      try {
        const storedUser = getStoredUser()
        if (!storedUser || storedUser.role !== 'admin') {
          navigate('/login')
          return
        }
        setUser(storedUser)

        // Load users and history
        const [usersData, historyData] = await Promise.all([
          getAllUsers(),
          getAllHistory(1, 20)
        ])

        setUsers(usersData.users || [])
        setHistory(historyData.history || [])
      } catch (error) {
        console.error('Error loading admin data:', error)
        if (error.response?.status === 401 || error.response?.status === 403) {
          navigate('/login')
        }
      } finally {
        setLoading(false)
      }
    }

    loadAdminData()
  }, [navigate])

  const handleLogout = async () => {
    await logout()
    navigate('/')  // Redirect to home page instead of login
  }

  const handleDeleteUser = (userId, username) => {
    setConfirmModal({
      isOpen: true,
      userId,
      username
    })
  }

  const confirmDelete = async () => {
    const { userId, username } = confirmModal
    setConfirmModal({ isOpen: false, userId: null, username: '' })

    try {
      await deleteUser(userId)
      setUsers(users.filter(u => u.id !== userId))
      showNotification('success', 'Success', `User "${username}" has been deleted successfully`)
    } catch (error) {
      showNotification('error', 'Delete Failed', error.response?.data?.message || 'Failed to delete user')
    }
  }

  const showNotification = (type, title, message) => {
    setNotification({ isOpen: true, type, title, message })
    setTimeout(() => {
      setNotification({ isOpen: false, type: 'success', title: '', message: '' })
    }, 4000)
  }

  if (loading) {
    return (
      <div className="admin-container">
        <div className="loading">Loading admin dashboard...</div>
      </div>
    )
  }

  return (
    <div className="admin-container">
      <div className="admin-header">
        <div>
          <h1>Admin Dashboard</h1>
          <p className="admin-welcome">Welcome, {user?.username}</p>
        </div>
        <div className="header-actions">
          <button onClick={() => navigate('/dashboard')} className="regular-dashboard-button">
            User Dashboard
          </button>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </div>

      <div className="admin-tabs">
        <button
          className={`tab-button ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          Users ({users.length})
        </button>
        <button
          className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          Activity History
        </button>
      </div>

      <div className="admin-content">
        {activeTab === 'users' && (
          <div className="users-section">
            <h2>All Users</h2>
            <div className="users-table">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th>Last Login</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id}>
                      <td>{u.id}</td>
                      <td><strong>{u.username}</strong></td>
                      <td>{u.email}</td>
                      <td>
                        <span className={`role-badge ${u.role}`}>
                          {u.role}
                        </span>
                      </td>
                      <td>
                        <span className={`status-badge ${u.is_active ? 'active' : 'inactive'}`}>
                          {u.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td>{u.last_login ? new Date(u.last_login).toLocaleString() : 'Never'}</td>
                      <td>
                        {u.id !== user?.id && (
                          <button
                            onClick={() => handleDeleteUser(u.id, u.username)}
                            className="delete-button"
                          >
                            Delete
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="history-section">
            <h2>Activity History</h2>
            <div className="history-table">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>User ID</th>
                    <th>Action</th>
                    <th>IP Address</th>
                    <th>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((entry) => (
                    <tr key={entry.id}>
                      <td>{entry.id}</td>
                      <td>{entry.user_id}</td>
                      <td>
                        <span className="action-type">{entry.action_type}</span>
                      </td>
                      <td>{entry.ip_address || 'N/A'}</td>
                      <td>{new Date(entry.timestamp).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      <ConfirmModal
        isOpen={confirmModal.isOpen}
        onClose={() => setConfirmModal({ isOpen: false, userId: null, username: '' })}
        onConfirm={confirmDelete}
        title="Delete User"
        message={`Are you sure you want to delete user "${confirmModal.username}"? This action cannot be undone and will remove all associated data.`}
        confirmText="Delete"
        cancelText="Cancel"
        type="danger"
      />

      <NotificationModal
        isOpen={notification.isOpen}
        onClose={() => setNotification({ isOpen: false, type: 'success', title: '', message: '' })}
        type={notification.type}
        title={notification.title}
        message={notification.message}
      />
    </div>
  )
}

export default AdminDashboard
