import { useState, useEffect } from "react";
import "./App.css";
import LoginPage from "./components/LoginPage";
import Dashboard from "./components/Dashboard";
import PayBills from "./components/PayBills";
import FundTransfer from "./components/FundTransfer";
import BuyGold from "./components/BuyGold";
import Profile from "./components/Profile";
import Modal from "./components/Modal";
import LoadingOverlay from "./components/LoadingOverlay";

function App() {
  const [currentPage, setCurrentPage] = useState("login");
  const [user, setUser] = useState(null);
  const [balance, setBalance] = useState(45678.5);
  const [goldHoldings, setGoldHoldings] = useState(0.275);
  const [transactions, setTransactions] = useState([
    {
      title: "Salary Credit",
      amount: 50000,
      isDebit: false,
      date: "Dec 01, 2025",
    },
    {
      title: "Electricity Bill - Adani",
      amount: 1250,
      isDebit: true,
      date: "Nov 28, 2025",
    },
    {
      title: "Digital Gold Purchase",
      amount: 2000,
      isDebit: true,
      date: "Nov 25, 2025",
    },
  ]);
  const [modalState, setModalState] = useState({ type: null, data: {} });
  const [loading, setLoading] = useState(false);
  const [currentAction, setCurrentAction] = useState(null);

  const goldRate = 7250.0;

  useEffect(() => {
    // Create particles background
    createParticles();
  }, []);

  const createParticles = () => {
    const particlesContainer = document.getElementById("particles");
    if (!particlesContainer) return;

    const colors = [
      "rgba(0, 102, 255, 0.5)",
      "rgba(0, 212, 255, 0.4)",
      "rgba(255, 107, 53, 0.3)",
    ];

    for (let i = 0; i < 30; i++) {
      const particle = document.createElement("div");
      particle.className = "particle";
      particle.style.left = Math.random() * 100 + "%";
      particle.style.animationDelay = Math.random() * 15 + "s";
      particle.style.animationDuration = 15 + Math.random() * 20 + "s";
      particle.style.background =
        colors[Math.floor(Math.random() * colors.length)];
      particle.style.width = 2 + Math.random() * 4 + "px";
      particle.style.height = particle.style.width;
      particlesContainer.appendChild(particle);
    }
  };

  const handleLogin = async (username) => {
    setLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setLoading(false);
    setUser(username);
    setCurrentPage("dashboard");
  };

  const handleLogout = () => {
    setUser(null);
    setCurrentPage("login");
  };

  const navigateTo = (page) => {
    setCurrentPage(page);
  };

  const updateBalance = (amount, isDebit = true) => {
    setBalance((prev) => (isDebit ? prev - amount : prev + amount));
  };

  const addTransaction = (title, amount, isDebit = true) => {
    const newTxn = {
      title,
      amount,
      isDebit,
      date: new Date().toLocaleDateString("en-US", {
        month: "short",
        day: "2-digit",
        year: "numeric",
      }),
    };
    setTransactions((prev) => [newTxn, ...prev]);
  };

  const showModal = (type, data) => {
    setModalState({ type, data });
  };

  const hideModal = () => {
    setModalState({ type: null, data: {} });
  };

  const handleConfirmAction = async () => {
    if (!currentAction) return;

    hideModal();
    setLoading(true);

    // Simulate 2 second loading (matching dummy bank)
    await new Promise((resolve) => setTimeout(resolve, 2000));

    setLoading(false);

    const { type, amount } = currentAction;

    updateBalance(amount, true);

    let successMessage = "";
    let successTitle = "";

    switch (type) {
      case "bill-payment":
        addTransaction(`Bill Payment - ${currentAction.biller}`, amount, true);
        successTitle = "Bill Paid Successfully!";
        successMessage = `Your ${currentAction.biller} bill has been paid.`;
        break;
      case "fund-transfer":
        addTransaction(`Transfer to ${currentAction.recipient}`, amount, true);
        successTitle = "Transfer Successful!";
        successMessage = `₹${amount.toFixed(2)} transferred to ${
          currentAction.recipient
        }`;
        break;
      case "buy-gold":
        const grams = currentAction.grams;
        setGoldHoldings((prev) => prev + grams);
        addTransaction("Digital Gold Purchase", amount, true);
        successTitle = "Gold Purchase Successful!";
        successMessage = `You bought ${grams.toFixed(3)} grams of gold`;
        break;
    }

    showModal("success", { title: successTitle, message: successMessage });
    setCurrentAction(null);
  };

  const renderPage = () => {
    switch (currentPage) {
      case "login":
        return <LoginPage onLogin={handleLogin} />;
      case "dashboard":
        return (
          <Dashboard
            user={user}
            balance={balance}
            transactions={transactions}
            onLogout={handleLogout}
            onNavigate={navigateTo}
          />
        );
      case "payBills":
        return (
          <PayBills
            balance={balance}
            onBack={() => navigateTo("dashboard")}
            onSubmit={(data) => {
              setCurrentAction({ ...data, type: "bill-payment" });
              showModal("confirm", {
                title: "Confirm Bill Payment",
                message: "Please review the details before proceeding:",
                details: [
                  { label: "Biller", value: data.biller },
                  { label: "Consumer No", value: data.consumerNo },
                  { label: "Amount", value: `₹${data.amount.toFixed(2)}` },
                ],
              });
            }}
          />
        );
      case "fundTransfer":
        return (
          <FundTransfer
            balance={balance}
            onBack={() => navigateTo("dashboard")}
            onSubmit={(data) => {
              setCurrentAction({ ...data, type: "fund-transfer" });
              showModal("confirm", {
                title: "Confirm Fund Transfer",
                message: "Please review the details before proceeding:",
                details: [
                  { label: "To", value: data.recipient },
                  { label: "Account", value: data.account },
                  { label: "Amount", value: `₹${data.amount.toFixed(2)}` },
                ],
              });
            }}
          />
        );
      case "buyGold":
        return (
          <BuyGold
            balance={balance}
            goldRate={goldRate}
            goldHoldings={goldHoldings}
            onBack={() => navigateTo("dashboard")}
            onSubmit={(data) => {
              setCurrentAction({ ...data, type: "buy-gold" });
              showModal("confirm", {
                title: "Confirm Gold Purchase",
                message: "Please review the details before proceeding:",
                details: [
                  { label: "Gold Rate", value: `₹${goldRate.toFixed(2)}/gram` },
                  {
                    label: "Quantity",
                    value: `${data.grams.toFixed(3)} grams`,
                  },
                  {
                    label: "Total Amount",
                    value: `₹${data.amount.toFixed(2)}`,
                  },
                ],
              });
            }}
          />
        );
      case "profile":
        return (
          <Profile
            user={user}
            onBack={() => navigateTo("dashboard")}
            onSubmit={(data) => {
              showModal("success", {
                title: "Profile Updated!",
                message: "Your profile has been updated successfully.",
              });
            }}
          />
        );
      default:
        return <LoginPage onLogin={handleLogin} />;
    }
  };

  return (
    <div className="app">
      <div className="particles" id="particles"></div>
      {renderPage()}
      {modalState.type && (
        <Modal
          type={modalState.type}
          data={modalState.data}
          onClose={hideModal}
          onConfirm={handleConfirmAction}
        />
      )}
      {loading && <LoadingOverlay />}
    </div>
  );
}

export default App;
