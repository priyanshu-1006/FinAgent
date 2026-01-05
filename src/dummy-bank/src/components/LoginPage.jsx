import { useState } from "react";
import "./LoginPage.css";

function LoginPage({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (username && password) {
      onLogin(username);
    }
  };

  return (
    <div className="login-page page active">
      <div className="login-container">
        <div className="bank-logo">
          <span className="logo-icon">🏦</span>
          <h1>JioFinance Bank</h1>
          <p className="tagline">Your Trusted Digital Partner</p>
        </div>
        <form id="login-form" onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Username / Mobile Number</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              required
            />
          </div>
          <button
            type="submit"
            id="login-btn"
            className="btn btn-primary btn-block"
          >
            Login Securely
          </button>
          <p className="demo-hint">Demo: Use any username/password to login</p>
        </form>
      </div>
    </div>
  );
}

export default LoginPage;
