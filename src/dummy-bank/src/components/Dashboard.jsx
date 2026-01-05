import "./Dashboard.css";

function Dashboard({ user, balance, transactions, onLogout, onNavigate }) {
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 2,
    }).format(amount);
  };

  const actions = [
    { id: "pay-bills", icon: "💡", label: "Pay Bills", page: "payBills" },
    {
      id: "fund-transfer",
      icon: "💸",
      label: "Fund Transfer",
      page: "fundTransfer",
    },
    { id: "buy-gold", icon: "🥇", label: "Digital Gold", page: "buyGold" },
    { id: "investments", icon: "📈", label: "Investments", page: "buyGold" },
    { id: "profile", icon: "👤", label: "My Profile", page: "profile" },
    { id: "history", icon: "📋", label: "Transaction History", page: null },
  ];

  const handleActionClick = (action) => {
    if (action.page) {
      onNavigate(action.page);
    } else {
      alert("Transaction History - Coming Soon!");
    }
  };

  return (
    <div id="dashboard-page" className="dashboard-page page active">
      <nav className="navbar">
        <div className="nav-brand">
          <span className="logo-icon-small">🏦</span>
          <span>JioFinance Bank</span>
        </div>
        <div className="nav-user">
          <span className="user-greeting">Welcome, {user}</span>
          <button className="btn btn-outline" onClick={onLogout}>
            Logout
          </button>
        </div>
      </nav>

      <div className="dashboard-container">
        <div className="account-card">
          <div className="account-info">
            <h3>Savings Account</h3>
            <p className="account-number">A/C: XXXX XXXX 1234</p>
          </div>
          <div className="balance-info">
            <p className="balance-label">Available Balance</p>
            <p className="balance-amount" id="account-balance">
              {formatCurrency(balance)}
            </p>
          </div>
        </div>

        <div className="quick-actions">
          <h2>Quick Actions</h2>
          <div className="actions-grid">
            {actions.map((action) => (
              <button
                key={action.id}
                className="action-card"
                data-action={action.id}
                onClick={() => handleActionClick(action)}
              >
                <span className="action-icon">{action.icon}</span>
                <span className="action-label">{action.label}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="recent-transactions">
          <h2>Recent Transactions</h2>
          <div className="transaction-list">
            {transactions.slice(0, 5).map((txn, index) => (
              <div key={index} className="transaction-item">
                <div className={`txn-icon ${txn.isDebit ? "debit" : "credit"}`}>
                  {txn.isDebit ? "↑" : "↓"}
                </div>
                <div className="txn-details">
                  <p className="txn-title">{txn.title}</p>
                  <p className="txn-date">{txn.date}</p>
                </div>
                <p className={`txn-amount ${txn.isDebit ? "debit" : "credit"}`}>
                  {txn.isDebit ? "-" : "+"} {formatCurrency(txn.amount)}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
