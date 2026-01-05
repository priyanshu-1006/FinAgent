import { useState } from "react";
import "./PayBills.css";

function PayBills({ balance, onBack, onSubmit }) {
  const [category, setCategory] = useState("electricity");
  const [biller, setBiller] = useState("");
  const [consumerNo, setConsumerNo] = useState("");
  const [amount, setAmount] = useState("");
  const [remarks, setRemarks] = useState("");
  const [error, setError] = useState("");

  const categories = [
    { id: "electricity", icon: "💡", label: "Electricity" },
    { id: "gas", icon: "🔥", label: "Gas" },
    { id: "water", icon: "💧", label: "Water" },
    { id: "mobile", icon: "📱", label: "Mobile" },
    { id: "broadband", icon: "🌐", label: "Broadband" },
  ];

  const billers = {
    electricity: ["Adani Power", "Tata Power", "Reliance Energy", "BSES Delhi"],
    gas: ["IndianOil Gas", "GAIL Gas", "Gujarat Gas"],
    water: ["Mumbai Municipal", "Delhi Jal Board", "Bangalore Water"],
    mobile: ["Jio", "Airtel", "Vi", "BSNL"],
    broadband: ["Jio Fiber", "Airtel Xstream", "ACT Fibernet"],
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
      biller,
      consumerNo,
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
    <div id="pay-bills-page" className="pay-bills-page page active">
      <nav className="navbar">
        <button className="btn-back" onClick={onBack}>
          ← Back
        </button>
        <span className="page-title">Pay Bills</span>
        <div className="nav-spacer"></div>
      </nav>

      <div className="form-container">
        <h2>Bill Payment</h2>

        <div className="biller-categories">
          {categories.map((cat) => (
            <button
              key={cat.id}
              className={`biller-cat ${category === cat.id ? "active" : ""}`}
              onClick={() => setCategory(cat.id)}
            >
              {cat.icon} {cat.label}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="payment-form">
          <div className="form-group">
            <label htmlFor="biller-select">Select Biller</label>
            <select
              id="biller-select"
              value={biller}
              onChange={(e) => setBiller(e.target.value)}
              required
            >
              <option value="">-- Select Biller --</option>
              {billers[category].map((b) => (
                <option key={b} value={b}>
                  {b}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="consumer-number">
              Consumer Number / Account ID
            </label>
            <input
              type="text"
              id="consumer-number"
              value={consumerNo}
              onChange={(e) => setConsumerNo(e.target.value)}
              placeholder="Enter consumer number"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="bill-amount">Bill Amount (₹)</label>
            <input
              type="number"
              id="bill-amount"
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
            <label htmlFor="bill-remarks">Remarks (Optional)</label>
            <input
              type="text"
              id="bill-remarks"
              value={remarks}
              onChange={(e) => setRemarks(e.target.value)}
              placeholder="e.g., December bill"
            />
          </div>

          {amount && !error && (
            <div className="payment-summary">
              <h3>Payment Summary</h3>
              <div className="summary-row">
                <span>Biller:</span>
                <span>{biller || "-"}</span>
              </div>
              <div className="summary-row">
                <span>Consumer No:</span>
                <span>{consumerNo || "-"}</span>
              </div>
              <div className="summary-row total">
                <span>Amount:</span>
                <span>{formatCurrency(parseFloat(amount) || 0)}</span>
              </div>
            </div>
          )}

          <button
            type="submit"
            id="pay-bill-btn"
            className="btn btn-primary btn-block"
            disabled={!!error || !amount}
          >
            Pay Bill
          </button>
        </form>
      </div>
    </div>
  );
}

export default PayBills;
