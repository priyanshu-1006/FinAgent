import "./Modal.css";

function Modal({ type, data, onClose, onConfirm }) {
  const renderContent = () => {
    switch (type) {
      case "success":
        return (
          <div className="modal-content success">
            <div className="modal-icon">✅</div>
            <h2>{data.title || "Success!"}</h2>
            <p>{data.message || "Operation completed successfully."}</p>
            {data.details && (
              <div className="modal-details">
                {data.details.map((detail, idx) => (
                  <p key={idx}>
                    <strong>{detail.label}:</strong> {detail.value}
                  </p>
                ))}
              </div>
            )}
            <button className="btn btn-primary" onClick={onClose}>
              OK
            </button>
          </div>
        );
      case "error":
        return (
          <div className="modal-content error">
            <div className="modal-icon">❌</div>
            <h2>{data.title || "Error!"}</h2>
            <p>{data.message || "Something went wrong. Please try again."}</p>
            <button className="btn btn-primary" onClick={onClose}>
              OK
            </button>
          </div>
        );
      case "confirm":
        return (
          <div className="modal-content confirm">
            <div className="modal-icon">⚠️</div>
            <h2>{data.title || "Confirm"}</h2>
            <p>{data.message || "Are you sure you want to proceed?"}</p>
            {data.details && (
              <div className="modal-details">
                {data.details.map((detail, idx) => (
                  <p key={idx}>
                    <strong>{detail.label}:</strong> {detail.value}
                  </p>
                ))}
              </div>
            )}
            <div className="modal-actions">
              <button className="btn btn-outline" onClick={onClose}>
                Cancel
              </button>
              <button className="btn btn-primary" onClick={onConfirm}>
                Confirm & Pay
              </button>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="modal active" onClick={onClose}>
      <div onClick={(e) => e.stopPropagation()}>{renderContent()}</div>
    </div>
  );
}

export default Modal;
