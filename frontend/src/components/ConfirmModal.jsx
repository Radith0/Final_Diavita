import './ConfirmModal.css'

function ConfirmModal({ isOpen, onClose, onConfirm, title, message, confirmText = 'Confirm', cancelText = 'Cancel', type = 'danger' }) {
  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{title}</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <div className="modal-body">
          <p>{message}</p>
        </div>
        <div className="modal-footer">
          <button className="modal-button cancel" onClick={onClose}>
            {cancelText}
          </button>
          <button className={`modal-button ${type}`} onClick={onConfirm}>
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ConfirmModal
