import './NotificationModal.css'

function NotificationModal({ isOpen, onClose, title, message, type = 'success' }) {
  if (!isOpen) return null

  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
  }

  return (
    <div className="notification-overlay" onClick={onClose}>
      <div className={`notification-content ${type}`} onClick={(e) => e.stopPropagation()}>
        <div className="notification-icon">
          {icons[type]}
        </div>
        <div className="notification-text">
          <h3>{title}</h3>
          <p>{message}</p>
        </div>
        <button className="notification-close" onClick={onClose}>&times;</button>
      </div>
    </div>
  )
}

export default NotificationModal
