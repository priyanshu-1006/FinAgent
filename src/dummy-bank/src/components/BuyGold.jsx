import { useState } from "react";
import "./BuyGold.css";

function BuyGold({ balance, goldRate, goldHoldings, onBack, onSubmit }) {
  const [buyType, setBuyType] = useState("amount");
  const [amount, setAmount] = useState("");
  const [grams, setGrams] = useState("");
  const [error, setError] = useState("");

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

  const handleAmountChange = (value) => {
    setAmount(value);
    if (value && validateAmount(value)) {
      const calculatedGrams = parseFloat(value) / goldRate;
      setGrams(calculatedGrams.toFixed(3));
    } else {
      setGrams("");
    }
  };

  const handleGramsChange = (value) => {
    setGrams(value);
    if (value && parseFloat(value) > 0) {
      const calculatedAmount = parseFloat(value) * goldRate;
      setAmount(calculatedAmount.toFixed(2));
      validateAmount(calculatedAmount);
    } else {
      setAmount("");
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const amountNum = parseFloat(amount);
    const gramsNum = parseFloat(grams);

    if (!validateAmount(amountNum)) return;

    onSubmit({
      amount: amountNum,
      grams: gramsNum,
    });
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
    }).format(value);
  };

  return (
    <div className="buy-gold-page page active">
      <nav className="navbar">
        <button className="btn-back" onClick={onBack}>
          ← Back
        </button>
        <span className="page-title">Digital Gold</span>
        <div className="nav-spacer"></div>
      </nav>

      <div className="form-container">
        <h2>Buy Digital Gold</h2>

        <div className="gold-rate-card">
          <div className="gold-icon">🥇</div>
          <div className="gold-info">
            <p className="gold-label">Current Gold Rate (24K)</p>
            <p className="gold-rate">{formatCurrency(goldRate)} / gram</p>
            <p className="gold-update">Last updated: Just now</p>
          </div>
        </div>

        <div className="gold-holdings">
          <p>
            Your Gold Holdings: <strong>{goldHoldings.toFixed(3)} grams</strong>
          </p>
          <p className="holdings-value">
            Value: {formatCurrency(goldHoldings * goldRate)}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="payment-form">
          <div className="buy-type-toggle">
            <button
              type="button"
              className={`toggle-btn ${buyType === "amount" ? "active" : ""}`}
              onClick={() => setBuyType("amount")}
            >
              Buy by Amount (₹)
            </button>
            <button
              type="button"
              className={`toggle-btn ${buyType === "grams" ? "active" : ""}`}
              onClick={() => setBuyType("grams")}
            >
              Buy by Grams
            </button>
          </div>

          {buyType === "amount" ? (
            <div className="form-group">
              <label htmlFor="gold-amount">Amount (₹)</label>
              <input
                type="number"
                id="gold-amount"
                value={amount}
                onChange={(e) => handleAmountChange(e.target.value)}
                placeholder="Enter amount"
                min="1"
                required
              />
              {error && <span className="input-hint error">{error}</span>}
              {grams && !error && (
                <p className="conversion-hint">
                  You will get: <strong>{grams} grams</strong>
                </p>
              )}
            </div>
          ) : (
            <div className="form-group">
              <label htmlFor="gold-grams">Grams</label>
              <input
                type="number"
                id="gold-grams"
                value={grams}
                onChange={(e) => handleGramsChange(e.target.value)}
                placeholder="Enter grams"
                min="0.001"
                step="0.001"
                required
              />
              {amount && !error && (
                <p className="conversion-hint">
                  You will pay:{" "}
                  <strong>{formatCurrency(parseFloat(amount))}</strong>
                </p>
              )}
            </div>
          )}

          {amount && !error && (
            <div className="payment-summary">
              <h3>Purchase Summary</h3>
              <div className="summary-row">
                <span>Gold Rate:</span>
                <span>{formatCurrency(goldRate)} / gram</span>
              </div>
              <div className="summary-row">
                <span>Quantity:</span>
                <span>{grams} grams</span>
              </div>
              <div className="summary-row total">
                <span>Total Amount:</span>
                <span>{formatCurrency(parseFloat(amount) || 0)}</span>
              </div>
            </div>
          )}

          <button
            type="submit"
            className="btn btn-primary btn-block"
            disabled={!!error || !amount}
          >
            Buy Gold
          </button>
        </form>
      </div>
    </div>
  );
}

export default BuyGold;
