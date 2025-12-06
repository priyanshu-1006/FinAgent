// ===== DOM Elements =====
const pages = {
    login: document.getElementById('login-page'),
    dashboard: document.getElementById('dashboard-page'),
    payBills: document.getElementById('pay-bills-page'),
    fundTransfer: document.getElementById('fund-transfer-page'),
    buyGold: document.getElementById('buy-gold-page'),
    profile: document.getElementById('profile-page')
};

const modals = {
    success: document.getElementById('success-modal'),
    error: document.getElementById('error-modal'),
    confirm: document.getElementById('confirm-modal')
};

const loadingOverlay = document.getElementById('loading-overlay');

// ===== State Management =====
let appState = {
    user: null,
    balance: 45678.50,
    goldHoldings: 0.275,
    goldRate: 7250.00,
    transactions: [],
    currentAction: null
};

// ===== Utility Functions =====
function showPage(pageId) {
    Object.values(pages).forEach(page => page.classList.remove('active'));
    pages[pageId].classList.add('active');
}

function showModal(modalId) {
    modals[modalId].classList.add('active');
}

function hideModal(modalId) {
    modals[modalId].classList.remove('active');
}

function hideAllModals() {
    Object.values(modals).forEach(modal => modal.classList.remove('active'));
}

function showLoading() {
    loadingOverlay.classList.add('active');
}

function hideLoading() {
    loadingOverlay.classList.remove('active');
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 2
    }).format(amount);
}

function simulateDelay(ms = 1500) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function updateBalance(amount, isDebit = true) {
    if (isDebit) {
        appState.balance -= amount;
    } else {
        appState.balance += amount;
    }
    document.getElementById('account-balance').textContent = formatCurrency(appState.balance);
}

function addTransaction(title, amount, isDebit = true) {
    const txn = {
        title,
        amount,
        isDebit,
        date: new Date().toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' })
    };
    appState.transactions.unshift(txn);
    renderTransactions();
}

function renderTransactions() {
    const list = document.getElementById('transaction-list');
    const html = appState.transactions.slice(0, 5).map(txn => `
        <div class="transaction-item">
            <div class="txn-icon ${txn.isDebit ? 'debit' : 'credit'}">${txn.isDebit ? '↑' : '↓'}</div>
            <div class="txn-details">
                <p class="txn-title">${txn.title}</p>
                <p class="txn-date">${txn.date}</p>
            </div>
            <p class="txn-amount ${txn.isDebit ? 'debit' : 'credit'}">
                ${txn.isDebit ? '-' : '+'} ${formatCurrency(txn.amount)}
            </p>
        </div>
    `).join('');
    
    if (html) {
        list.innerHTML = html;
    }
}

function validateAmount(amount, fieldId) {
    const errorSpan = document.getElementById(fieldId);
    if (amount <= 0) {
        if (errorSpan) errorSpan.textContent = 'Amount must be greater than zero';
        return false;
    }
    if (amount > appState.balance) {
        if (errorSpan) errorSpan.textContent = 'Insufficient balance';
        return false;
    }
    if (errorSpan) errorSpan.textContent = '';
    return true;
}

// ===== Login Handler =====
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    
    showLoading();
    await simulateDelay(1000);
    hideLoading();
    
    appState.user = username;
    document.getElementById('user-greeting').textContent = `Welcome, ${username}`;
    showPage('dashboard');
});

document.getElementById('logout-btn').addEventListener('click', () => {
    appState.user = null;
    showPage('login');
    document.getElementById('login-form').reset();
});

// ===== Navigation =====
document.querySelectorAll('.action-card').forEach(card => {
    card.addEventListener('click', () => {
        const action = card.dataset.action;
        switch(action) {
            case 'pay-bills':
                showPage('payBills');
                break;
            case 'fund-transfer':
                showPage('fundTransfer');
                break;
            case 'buy-gold':
            case 'investments':
                showPage('buyGold');
                break;
            case 'profile':
                showPage('profile');
                break;
            case 'history':
                alert('Transaction History - Coming Soon!');
                break;
        }
    });
});

// Back buttons
document.getElementById('bills-back').addEventListener('click', () => showPage('dashboard'));
document.getElementById('transfer-back').addEventListener('click', () => showPage('dashboard'));
document.getElementById('gold-back').addEventListener('click', () => showPage('dashboard'));
document.getElementById('profile-back').addEventListener('click', () => showPage('dashboard'));

// ===== Bill Payment =====
const billForm = document.getElementById('bill-pay-form');
const billAmount = document.getElementById('bill-amount');
const billSummary = document.getElementById('bill-summary');

billAmount.addEventListener('input', () => {
    const amount = parseFloat(billAmount.value) || 0;
    validateAmount(amount, 'bill-amount-error');
    
    if (amount > 0) {
        document.getElementById('summary-biller').textContent = 
            document.getElementById('biller-select').options[document.getElementById('biller-select').selectedIndex].text;
        document.getElementById('summary-consumer').textContent = 
            document.getElementById('consumer-number').value || '-';
        document.getElementById('summary-amount').textContent = formatCurrency(amount);
        billSummary.style.display = 'block';
    } else {
        billSummary.style.display = 'none';
    }
});

billForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const amount = parseFloat(billAmount.value);
    if (!validateAmount(amount, 'bill-amount-error')) return;
    
    const biller = document.getElementById('biller-select').options[document.getElementById('biller-select').selectedIndex].text;
    const consumerNo = document.getElementById('consumer-number').value;
    
    // Show confirmation modal
    document.getElementById('confirm-title').textContent = 'Confirm Bill Payment';
    document.getElementById('confirm-message').textContent = 'Please review the details before proceeding:';
    document.getElementById('confirm-details').innerHTML = `
        <p><strong>Biller:</strong> ${biller}</p>
        <p><strong>Consumer No:</strong> ${consumerNo}</p>
        <p><strong>Amount:</strong> ${formatCurrency(amount)}</p>
    `;
    
    appState.currentAction = {
        type: 'bill-payment',
        biller,
        consumerNo,
        amount
    };
    
    showModal('confirm');
});

// ===== Fund Transfer =====
const transferForm = document.getElementById('transfer-form');
const transferAmount = document.getElementById('transfer-amount');
const transferSummary = document.getElementById('transfer-summary');

// Beneficiary selection
document.querySelectorAll('.beneficiary-card').forEach(card => {
    card.addEventListener('click', () => {
        document.querySelectorAll('.beneficiary-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        
        document.getElementById('recipient-name').value = card.dataset.name;
        document.getElementById('recipient-account').value = card.dataset.account;
        document.getElementById('recipient-ifsc').value = 'JFIN0001234';
    });
});

transferAmount.addEventListener('input', () => {
    const amount = parseFloat(transferAmount.value) || 0;
    validateAmount(amount, 'transfer-amount-error');
    
    if (amount > 0) {
        document.getElementById('transfer-to').textContent = 
            document.getElementById('recipient-name').value || '-';
        document.getElementById('transfer-account-display').textContent = 
            document.getElementById('recipient-account').value || '-';
        document.getElementById('transfer-amount-display').textContent = formatCurrency(amount);
        transferSummary.style.display = 'block';
    } else {
        transferSummary.style.display = 'none';
    }
});

transferForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const amount = parseFloat(transferAmount.value);
    if (!validateAmount(amount, 'transfer-amount-error')) return;
    
    const recipient = document.getElementById('recipient-name').value;
    const account = document.getElementById('recipient-account').value;
    
    // Show confirmation modal
    document.getElementById('confirm-title').textContent = 'Confirm Fund Transfer';
    document.getElementById('confirm-message').textContent = 'Please review the details before proceeding:';
    document.getElementById('confirm-details').innerHTML = `
        <p><strong>To:</strong> ${recipient}</p>
        <p><strong>Account:</strong> ${account}</p>
        <p><strong>Amount:</strong> ${formatCurrency(amount)}</p>
    `;
    
    appState.currentAction = {
        type: 'fund-transfer',
        recipient,
        account,
        amount
    };
    
    showModal('confirm');
});

// ===== Buy Gold =====
const goldForm = document.getElementById('gold-form');
const goldAmount = document.getElementById('gold-amount');
const goldGrams = document.getElementById('gold-grams');
const goldSummary = document.getElementById('gold-summary');

// Toggle between amount and grams
document.querySelectorAll('.toggle-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        if (btn.dataset.type === 'amount') {
            document.getElementById('amount-input-group').style.display = 'block';
            document.getElementById('grams-input-group').style.display = 'none';
        } else {
            document.getElementById('amount-input-group').style.display = 'none';
            document.getElementById('grams-input-group').style.display = 'block';
        }
    });
});

goldAmount.addEventListener('input', () => {
    const amount = parseFloat(goldAmount.value) || 0;
    validateAmount(amount, 'gold-amount-error');
    
    const grams = amount / appState.goldRate;
    document.querySelector('#grams-hint strong').textContent = grams.toFixed(3) + ' grams';
    
    if (amount > 0) {
        document.getElementById('gold-quantity').textContent = grams.toFixed(3) + ' grams';
        document.getElementById('gold-total').textContent = formatCurrency(amount);
        goldSummary.style.display = 'block';
    } else {
        goldSummary.style.display = 'none';
    }
});

goldGrams.addEventListener('input', () => {
    const grams = parseFloat(goldGrams.value) || 0;
    const amount = grams * appState.goldRate;
    
    document.querySelector('#amount-hint strong').textContent = formatCurrency(amount);
    
    if (grams > 0 && amount <= appState.balance) {
        document.getElementById('gold-quantity').textContent = grams.toFixed(3) + ' grams';
        document.getElementById('gold-total').textContent = formatCurrency(amount);
        goldSummary.style.display = 'block';
    } else {
        goldSummary.style.display = 'none';
    }
});

goldForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    let amount, grams;
    
    if (document.querySelector('.toggle-btn.active').dataset.type === 'amount') {
        amount = parseFloat(goldAmount.value);
        grams = amount / appState.goldRate;
    } else {
        grams = parseFloat(goldGrams.value);
        amount = grams * appState.goldRate;
    }
    
    if (!validateAmount(amount, 'gold-amount-error')) return;
    
    // Show confirmation modal
    document.getElementById('confirm-title').textContent = 'Confirm Gold Purchase';
    document.getElementById('confirm-message').textContent = 'Please review the details before proceeding:';
    document.getElementById('confirm-details').innerHTML = `
        <p><strong>Gold Rate:</strong> ${formatCurrency(appState.goldRate)} / gram</p>
        <p><strong>Quantity:</strong> ${grams.toFixed(3)} grams</p>
        <p><strong>Total Amount:</strong> ${formatCurrency(amount)}</p>
    `;
    
    appState.currentAction = {
        type: 'buy-gold',
        grams,
        amount
    };
    
    showModal('confirm');
});

// ===== Profile Update =====
document.getElementById('profile-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    document.getElementById('confirm-title').textContent = 'Confirm Profile Update';
    document.getElementById('confirm-message').textContent = 'Are you sure you want to update your profile?';
    document.getElementById('confirm-details').innerHTML = `
        <p><strong>Name:</strong> ${document.getElementById('profile-fullname').value}</p>
        <p><strong>Email:</strong> ${document.getElementById('profile-email').value}</p>
        <p><strong>Phone:</strong> ${document.getElementById('profile-phone').value}</p>
    `;
    
    appState.currentAction = {
        type: 'profile-update',
        name: document.getElementById('profile-fullname').value,
        email: document.getElementById('profile-email').value,
        phone: document.getElementById('profile-phone').value
    };
    
    showModal('confirm');
});

// ===== Confirmation Modal Handlers =====
document.getElementById('confirm-cancel-btn').addEventListener('click', () => {
    hideModal('confirm');
    appState.currentAction = null;
});

document.getElementById('confirm-proceed-btn').addEventListener('click', async () => {
    hideModal('confirm');
    showLoading();
    
    await simulateDelay(2000);
    
    hideLoading();
    
    const action = appState.currentAction;
    
    if (!action) return;
    
    switch(action.type) {
        case 'bill-payment':
            updateBalance(action.amount, true);
            addTransaction(`Bill Payment - ${action.biller}`, action.amount, true);
            document.getElementById('success-title').textContent = 'Bill Paid Successfully!';
            document.getElementById('success-message').textContent = 'Your bill has been paid.';
            document.getElementById('success-details').innerHTML = `
                <p><strong>Biller:</strong> ${action.biller}</p>
                <p><strong>Amount:</strong> ${formatCurrency(action.amount)}</p>
                <p><strong>Reference:</strong> TXN${Date.now()}</p>
            `;
            billForm.reset();
            billSummary.style.display = 'none';
            break;
            
        case 'fund-transfer':
            updateBalance(action.amount, true);
            addTransaction(`Transfer to ${action.recipient}`, action.amount, true);
            document.getElementById('success-title').textContent = 'Transfer Successful!';
            document.getElementById('success-message').textContent = 'Money has been transferred.';
            document.getElementById('success-details').innerHTML = `
                <p><strong>To:</strong> ${action.recipient}</p>
                <p><strong>Amount:</strong> ${formatCurrency(action.amount)}</p>
                <p><strong>Reference:</strong> TXN${Date.now()}</p>
            `;
            transferForm.reset();
            transferSummary.style.display = 'none';
            document.querySelectorAll('.beneficiary-card').forEach(c => c.classList.remove('selected'));
            break;
            
        case 'buy-gold':
            updateBalance(action.amount, true);
            appState.goldHoldings += action.grams;
            document.getElementById('gold-holdings').textContent = appState.goldHoldings.toFixed(3) + ' grams';
            addTransaction('Digital Gold Purchase', action.amount, true);
            document.getElementById('success-title').textContent = 'Gold Purchased!';
            document.getElementById('success-message').textContent = 'Gold has been added to your holdings.';
            document.getElementById('success-details').innerHTML = `
                <p><strong>Quantity:</strong> ${action.grams.toFixed(3)} grams</p>
                <p><strong>Amount:</strong> ${formatCurrency(action.amount)}</p>
                <p><strong>Total Holdings:</strong> ${appState.goldHoldings.toFixed(3)} grams</p>
            `;
            goldForm.reset();
            goldSummary.style.display = 'none';
            break;
            
        case 'profile-update':
            document.getElementById('profile-name').textContent = action.name;
            document.getElementById('success-title').textContent = 'Profile Updated!';
            document.getElementById('success-message').textContent = 'Your profile has been updated successfully.';
            document.getElementById('success-details').innerHTML = '';
            break;
    }
    
    appState.currentAction = null;
    showModal('success');
});

// ===== Success/Error Modal Close =====
document.getElementById('success-ok-btn').addEventListener('click', () => {
    hideModal('success');
    showPage('dashboard');
});

document.getElementById('error-ok-btn').addEventListener('click', () => {
    hideModal('error');
});

// ===== Initialize =====
function init() {
    // Add initial transactions
    appState.transactions = [
        { title: 'Salary Credit', amount: 50000, isDebit: false, date: 'Dec 01, 2025' },
        { title: 'Electricity Bill - Adani', amount: 1250, isDebit: true, date: 'Nov 28, 2025' },
        { title: 'Digital Gold Purchase', amount: 2000, isDebit: true, date: 'Nov 25, 2025' }
    ];
    
    document.getElementById('account-balance').textContent = formatCurrency(appState.balance);
    document.getElementById('gold-rate').textContent = formatCurrency(appState.goldRate) + ' / gram';
    
    console.log('🏦 JioFinance Dummy Bank initialized');
    console.log('📋 Available pages:', Object.keys(pages));
}

// Close modals on outside click
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
});

// Initialize on load
document.addEventListener('DOMContentLoaded', init);
