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
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Running the Agent

#### 1. Start the Dummy Bank (required)
```bash
cd src/dummy-bank
python -m http.server 8080
```

#### 2. Run in CLI Mode
```bash
python main.py cli
```

#### 3. Run with Dashboard (Recommended)
```bash
python main.py server
# Open http://localhost:8000 in your browser
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
"buy gold worth 2000 rupees"
"purchase 0.5 grams of digital gold"
```

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
- Bill Payments
- Fund Transfers
- Gold Purchases
- Profile Updates

## 📁 Project Structure

```
FinAgent-AI/
├── src/
│   ├── agent/                 # Core AI Agent
│   │   ├── __init__.py
│   │   ├── agent.py           # Main agent class
│   │   ├── config.py          # Configuration
│   │   ├── intent_parser.py   # NLP intent extraction
│   │   ├── browser_automation.py  # Playwright controller
│   │   ├── conscious_pause.py # Human approval system
│   │   └── orchestrator.py    # Multi-step task planning
│   │
│   ├── backend/               # FastAPI Server
│   │   ├── __init__.py
│   │   └── server.py          # REST API & WebSocket
│   │
│   ├── frontend/              # User Dashboard
│   │   └── index.html         # Dashboard UI
│   │
│   └── dummy-bank/            # Target Banking Website
│       ├── index.html         # Bank pages
│       ├── styles.css         # Styling
│       └── script.js          # Bank functionality
│
├── docs/                      # Documentation
├── tests/                     # Test suite
├── main.py                    # Entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
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

| Criteria | Implementation |
|----------|---------------|
| **Feasibility** | Uses proven technologies (Playwright, GPT-4o, FastAPI) |
| **Technical Approach** | Modular architecture with clear separation of concerns |
| **Innovation** | Conscious Pause mechanism for safe financial automation |
| **Presentation** | Clean dashboard UI with real-time updates |

## 🛠️ Tech Stack

- **AI/NLP**: OpenAI GPT-4o / Google Gemini 1.5 Pro
- **Browser Automation**: Playwright
- **Backend**: Python, FastAPI, WebSockets
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Architecture**: Event-driven, async/await

## 👥 Team

- **Team Name**: FinAgent
- **Hackathon**: IIT Bombay Techfest + Jio Financial Services

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built with ❤️ for IIT Bombay Techfest Hackathon
</p>
