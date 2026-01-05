import { useState } from "react";
import "./FundTransfer.css";

function FundTransfer({ balance, onBack, onSubmit }) {
  const [recipient, setRecipient] = useState("");
  const [account, setAccount] = useState("");
  const [ifsc, setIfsc] = useState("");
  const [amount, setAmount] = useState("");
  const [remarks, setRemarks] = useState("");
  const [error, setError] = useState("");

  const beneficiaries = [
    { name: "Mom", account: "9876543210", avatar: "👩" },
    { name: "Dad", account: "8765432109", avatar: "👨" },
    { name: "Friend", account: "7654321098", avatar: "🧑" },
  ];

  const selectBeneficiary = (ben) => {
    setRecipient(ben.name);
    setAccount(ben.account);
    setIfsc("JFIN0001234");
  };

  const validateAmount = (value) => {
    const num = parseFloat(value);
    if (num <= 0) {
      setError("Amount must be greater than zero");
      return false;
    }
    if (num > balance) {
      setError("Insufficient balance");
      return false;
    }
    setError("");
    return true;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const amountNum = parseFloat(amount);

    if (!validateAmount(amountNum)) return;

    onSubmit({
      recipient,
      account,
      ifsc,
      amount: amountNum,
      remarks,
    });
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
    }).format(value);
  };

  return (
    <div id="fund-transfer-page" className="fund-transfer-page page active">
      <nav className="navbar">
        <button className="btn-back" onClick={onBack}>
          ← Back
        </button>
        <span className="page-title">Fund Transfer</span>
        <div className="nav-spacer"></div>
      </nav>

      <div className="form-container">
        <h2>Transfer Money</h2>

        <div className="beneficiary-list">
          <h3>Saved Beneficiaries</h3>
          <div className="beneficiary-cards">
            {beneficiaries.map((ben, idx) => (
              <button
                key={idx}
                className={`beneficiary-card ${
                  account === ben.account ? "selected" : ""
                }`}
                data-name={ben.name}
                onClick={() => selectBeneficiary(ben)}
              >
                <span className="ben-avatar">{ben.avatar}</span>
                <span className="ben-name">{ben.name}</span>
                <span className="ben-account">****{ben.account.slice(-4)}</span>
              </button>
            ))}
          </div>
        </div>

        <form
          id="transfer-form"
          onSubmit={handleSubmit}
          className="payment-form"
        >
          <div className="form-group">
            <label htmlFor="recipient-name">Recipient Name</label>
            <input
              type="text"
              id="recipient-name"
              value={recipient}
              onChange={(e) => setRecipient(e.target.value)}
              placeholder="Enter recipient name"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="recipient-account">Account Number</label>
            <input
              type="text"
              id="recipient-account"
              value={account}
              onChange={(e) => setAccount(e.target.value)}
              placeholder="Enter account number"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="recipient-ifsc">IFSC Code</label>
            <input
              type="text"
              id="recipient-ifsc"
              value={ifsc}
              onChange={(e) => setIfsc(e.target.value)}
              placeholder="Enter IFSC code"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="transfer-amount">Amount (₹)</label>
            <input
              type="number"
              id="transfer-amount"
              value={amount}
              onChange={(e) => {
                setAmount(e.target.value);
                validateAmount(e.target.value);
              }}
              placeholder="Enter amount"
              min="1"
              required
            />
            {error && <span className="input-hint error">{error}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="transfer-remarks">Remarks (Optional)</label>
            <input
              type="text"
              id="transfer-remarks"
              value={remarks}
              onChange={(e) => setRemarks(e.target.value)}
              placeholder="e.g., Gift"
            />
          </div>

          {amount && !error && (
            <div className="payment-summary">
              <h3>Transfer Summary</h3>
              <div className="summary-row">
                <span>To:</span>
                <span>{recipient || "-"}</span>
              </div>
              <div className="summary-row">
                <span>Account:</span>
                <span>{account || "-"}</span>
              </div>
              <div className="summary-row total">
                <span>Amount:</span>
                <span>{formatCurrency(parseFloat(amount) || 0)}</span>
              </div>
            </div>
          )}

          <button
            type="submit"
            id="transfer-btn"
            className="btn btn-primary btn-block"
            disabled={!!error || !amount}
          >
            Transfer Money
          </button>
        </form>
      </div>
    </div>
  );
}

export default FundTransfer;
