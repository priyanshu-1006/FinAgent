import "./LoadingOverlay.css";

function LoadingOverlay() {
  return (
    <div className="loading-overlay active" id="loading-overlay">
      <div className="spinner"></div>
      <p>Processing...</p>
    </div>
  );
}

export default LoadingOverlay;
