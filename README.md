# FinAgent - AI-Powered Financial Automation Agent

## IIT Bombay Techfest Hackathon | Jio Financial Services

![Status](https://img.shields.io/badge/Status-Prototype-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

<p align="center">
  <img src="docs/architecture.png" alt="FinAgent Architecture" width="600">
</p>

## 🎯 Overview

FinAgent is an intelligent browser automation agent that executes complex financial tasks through natural language commands. It interprets user intent, navigates a banking website autonomously, and critically - **pauses before any high-risk action** to ensure human oversight.

### Key Features

- 🧠 **Natural Language Understanding** - Powered by GPT-4o/Gemini for intent parsing
- 🤖 **Autonomous Browser Control** - Playwright-based web automation
- ⚠️ **Conscious Pause Mechanism** - Human-in-the-loop approval for risky actions
- 🔄 **Multi-Step Orchestration** - Complex task breakdown and execution
- 📊 **Real-Time Dashboard** - Monitor and control the agent

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER DASHBOARD                               │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────────┐ │
│  │ Command Input │  │ Live Preview │  │    Approval Interface     │ │
│  └──────┬───────┘  └──────────────┘  └─────────────┬──────────────┘ │
└─────────┼──────────────────────────────────────────┼────────────────┘
          │                                          │
          ▼                                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         FINAGENT CORE                                │
│  ┌────────────────┐    ┌────────────────┐    ┌───────────────────┐  │
│  │  ACTION BRAIN  │───▶│  ORCHESTRATOR  │───▶│  CONSCIOUS PAUSE  │  │
│  │ (Intent Parse) │    │  (Task Plan)   │    │  (Human Review)   │  │
│  └────────────────┘    └───────┬────────┘    └───────────────────┘  │
│                                │                                     │
│                                ▼                                     │
│                    ┌────────────────────┐                           │
│                    │    DIGITAL HAND    │                           │
│                    │ (Browser Control)  │                           │
│                    └─────────┬──────────┘                           │
└──────────────────────────────┼──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DUMMY BANKING WEBSITE                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐ │
│  │  Login   │  │ Pay Bills │  │ Transfer │  │    Digital Gold     │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js (optional, for additional tooling)
- OpenAI API key or Google Gemini API key

### Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/finagent.git
cd finagent

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Set up environment variables
# Create a .env file and add your API keys:
# OPENAI_API_KEY=your_openai_key
# Or GEMINI_API_KEY=your_gemini_key
```

### Running the Agent

#### 1. Start the Dummy Bank (Terminal 1)

```bash
cd src/dummy-bank
npm install
npm run dev
# Bank will run on http://localhost:8080
```

#### 2. Run FinAgent Server (Terminal 2)

```bash
python main.py server
# Dashboard: http://localhost:8000
# FinAgent UI: http://localhost:8000/static/index.html
```

#### 3. Alternative: CLI Mode

```bash
python main.py cli
```

#### 4. Run Demo

```bash
python main.py demo
```

## 💻 Usage Examples

### Natural Language Commands

```python
# Login
"login to my account"
"sign in with my credentials"

# Check Balance
"what is my current balance"
"show me my account balance"

# Pay Bills
"pay electricity bill of 1500 rupees to Adani"
"pay my Tata Power bill for 2000"

# Fund Transfer
"transfer 5000 rupees to Mom"
"send 10000 to account number 9876543210"

# Buy Gold
"invest in gold"  # Opens gold page without filling amount
"buy gold worth 2000 rupees"
"purchase 0.5 grams of digital gold"

# Profile
"show my profile"
"view my account details"
```

### Web Dashboard Usage

1. Open http://localhost:8000/static/index.html
2. Wait for "Connected" status (green indicator)
3. Type commands in the Command Center
4. View live browser preview and activity log
5. Approve/reject transactions when prompted

### Demo Credentials

- **Username**: demo_user
- **Password**: demo123

### Programmatic Usage

```python
from src.agent.agent import FinAgent
import asyncio

async def main():
    agent = FinAgent()
    await agent.start()

    # Execute commands
    result = await agent.execute("pay electricity bill of 1500 to Adani")
    print(result)

    await agent.stop()

asyncio.run(main())
```

## 🔐 Conscious Pause - Safety Mechanism

For all high-risk financial actions, FinAgent implements a **Conscious Pause**:

1. **Action Preparation** - Agent fills out forms and prepares the action
2. **Review Display** - Shows complete action details to the user
3. **Explicit Approval** - Waits for user to approve or reject
4. **Timeout Protection** - Auto-cancels if no response within 60 seconds

### High-Risk Actions Requiring Approval:

- ✓ Bill Payments
- ✓ Fund Transfers
- ✓ Gold Purchases
- ✓ Profile Updates

### Safety Features:

- Transaction amount limits
- Daily transaction caps
- Audit logging of all actions
- Session-based tracking
- Error recovery mechanisms

## 🔄 Workflow

1. **User Input** → Natural language command
2. **Intent Parsing** → AI extracts action and parameters
3. **Task Planning** → Orchestrator breaks down into steps
4. **Browser Control** → Playwright executes automation
5. **Conscious Pause** → Human approval for risky actions
6. **Confirmation** → Final execution with user consent
7. **Logging** → Complete audit trail

## 📁 Project Structure

```
FinAgent-AI/
├── src/
│   ├── agent/                 # Core AI Agent
│   │   ├── __init__.py
│   │   ├── agent.py           # Main agent class
│   │   ├── config.py          # Configuration management
│   │   ├── intent_parser.py   # NLP intent extraction (AI-powered)
│   │   ├── browser_automation.py  # Playwright browser controller
│   │   ├── conscious_pause.py # Human approval system
│   │   ├── orchestrator.py    # Multi-step task planning
│   │   ├── session_manager.py # Session state management
│   │   ├── audit_logger.py    # Action logging & audit trail
│   │   ├── vision.py          # Visual element detection
│   │   ├── error_recovery.py  # Error handling & retry logic
│   │   ├── transaction_limits.py  # Safety limits
│   │   └── user_errors.py     # Custom exceptions
│   │
│   ├── backend/               # FastAPI Server
│   │   ├── __init__.py
│   │   └── server.py          # REST API & WebSocket server
│   │
│   └── dummy-bank/            # Demo Banking Website (React)
│       ├── src/
│       │   ├── App.jsx        # Main app component
│       │   ├── App.css        # Global styles (fully responsive)
│       │   └── components/    # UI components
│       │       ├── Dashboard.jsx    # Account overview
│       │       ├── LoginPage.jsx    # Login interface
│       │       ├── PayBills.jsx     # Bill payment
│       │       ├── FundTransfer.jsx # Money transfer
│       │       ├── BuyGold.jsx      # Gold investment
│       │       ├── Profile.jsx      # User profile
│       │       └── Modal.jsx        # Confirmation modals
│       ├── index.html         # Entry point
│       ├── package.json       # NPM dependencies
│       └── vite.config.js     # Vite configuration
│
├── tests/                     # Test suite
│   ├── test_intent_parser.py
│   ├── test_transaction_limits.py
│   └── test_user_errors.py
│
├── logs/                      # Execution logs
├── sessions/                  # Session data
├── main.py                    # Entry point
├── demo.py                    # Demo script
├── test_e2e.py               # End-to-end tests
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests/test_intent_parser.py
```

## 🎥 Demo Video

[Watch the Demo Video](https://youtube.com/watch?v=your-video-id)

## 📊 Evaluation Criteria

| Criteria               | Implementation                                          |
| ---------------------- | ------------------------------------------------------- |
| **Feasibility**        | Uses proven technologies (Playwright, GPT-4o, FastAPI)  |
| **Technical Approach** | Modular architecture with clear separation of concerns  |
| **Innovation**         | Conscious Pause mechanism for safe financial automation |
| **Presentation**       | Clean dashboard UI with real-time updates               |

## 🛠️ Tech Stack

### Backend & AI

- **AI/NLP**: OpenAI GPT-4o / Google Gemini 1.5 Pro
- **Browser Automation**: Playwright (Chromium)
- **Backend**: Python 3.10+, FastAPI, WebSockets
- **Architecture**: Event-driven, async/await

### Frontend & UI

- **Bank Website**: React 18, Vite, Modern CSS
- **Dashboard**: HTML5, CSS3, Vanilla JavaScript
- **Design**: Glassmorphism, Fully Responsive (Mobile-first)

### Features

- ✅ Natural Language Processing for intent extraction
- ✅ Multi-step task orchestration
- ✅ Real-time browser preview via WebSocket
- ✅ Session management & audit logging
- ✅ Transaction limits & safety checks
- ✅ Error recovery & retry logic
- ✅ Fully responsive UI (360px - 2560px+)
- ✅ Conscious Pause for human oversight

## 🎨 UI Features

The dummy bank website is **fully responsive** with:

- **Desktop** (1920px+): Full feature layout
- **Tablet** (768px-1024px): Optimized grid layouts
- **Mobile** (360px-767px): Touch-friendly, stacked layout
- Modern glassmorphism design
- Smooth animations and transitions
- Touch-optimized controls

## 👥 Team

- **Team Name**: FinAgent
- **Hackathon**: IIT Bombay Techfest + Jio Financial Services

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built with ❤️ for IIT Bombay Techfest Hackathon
</p>
