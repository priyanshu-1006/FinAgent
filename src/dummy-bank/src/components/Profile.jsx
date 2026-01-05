import { useState } from "react";
import "./Profile.css";

function Profile({ user, onBack, onSubmit }) {
  const [fullname, setFullname] = useState("John Doe");
  const [email, setEmail] = useState("john.doe@email.com");
  const [phone, setPhone] = useState("9876543210");
  const [address, setAddress] = useState(
    "123 Main Street, Mumbai, Maharashtra 400001"
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ fullname, email, phone, address });
  };

  return (
    <div className="profile-page page active">
      <nav className="navbar">
        <button className="btn-back" onClick={onBack}>
          ← Back
        </button>
        <span className="page-title">My Profile</span>
        <div className="nav-spacer"></div>
      </nav>

      <div className="form-container">
        <div className="profile-header">
          <div className="profile-avatar">👤</div>
          <h2>{fullname}</h2>
          <p className="profile-id">Customer ID: JFB123456</p>
        </div>

        <form onSubmit={handleSubmit} className="payment-form">
          <div className="form-group">
            <label htmlFor="profile-fullname">Full Name</label>
            <input
              type="text"
              id="profile-fullname"
              value={fullname}
              onChange={(e) => setFullname(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label htmlFor="profile-email">Email Address</label>
            <input
              type="email"
              id="profile-email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label htmlFor="profile-phone">Mobile Number</label>
            <input
              type="tel"
              id="profile-phone"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label htmlFor="profile-address">Address</label>
            <textarea
              id="profile-address"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              rows="3"
            />
          </div>

          <button type="submit" className="btn btn-primary btn-block">
            Update Profile
          </button>
        </form>
      </div>
    </div>
  );
}

export default Profile;
