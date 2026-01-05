<div align="center">

# 🏦 FinAgent

### AI-Powered Financial Automation Agent

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev)

_Execute complex financial tasks through natural language with human-in-the-loop safety_

**IIT Bombay Techfest Hackathon × Jio Financial Services**

---

[Features](#-features) • [Quick Start](#-quick-start) • [Usage](#-usage) • [Architecture](#-architecture) • [Tech Stack](#-tech-stack)

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🧠 Natural Language Understanding

Powered by **GPT-4o/Gemini** for intelligent intent parsing. Just speak naturally:

- _"Pay my electricity bill of ₹1500"_
- _"Transfer 5000 to Mom"_
- _"Buy gold worth 2000 rupees"_

</td>
<td width="50%">

### 🛡️ Conscious Pause™

**Human-in-the-loop safety** for all risky actions:

- ⏸️ Pauses before executing
- 👁️ Shows full action preview
- ✅ Requires explicit approval
- ⏱️ Auto-cancels on timeout

</td>
</tr>
<tr>
<td width="50%">

### 🤖 Autonomous Browser Control

**Playwright-powered** web automation:

- Smart element detection
- Form auto-filling
- Navigation handling
- Error recovery

</td>
<td width="50%">

### 📊 Real-Time Dashboard

**Live monitoring & control**:

- Browser preview stream
- Activity logging
- Approval interface
- WebSocket updates

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites

```
✓ Python 3.10+
✓ Node.js 18+
✓ OpenAI or Gemini API key
```

### Installation

```bash
# Clone & setup
git clone https://github.com/your-repo/finagent.git
cd finagent

# Python environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt
playwright install chromium
```

### Environment Setup

Create a `.env` file:

```env
# Choose one AI provider
OPENAI_API_KEY=sk-your-key-here
# OR
GEMINI_API_KEY=your-gemini-key
```

### Run

<table>
<tr>
<td>

**Terminal 1 - Bank Website**

```bash
cd src/dummy-bank
npm install
npm run dev
```

→ http://localhost:8080

</td>
<td>

**Terminal 2 - FinAgent**

```bash
python main.py server
```

→ http://localhost:8000

</td>
</tr>
</table>

---

## 💻 Usage

### Natural Language Commands

| Category         | Example Commands                          |
| ---------------- | ----------------------------------------- |
| 🔐 **Login**     | `"login to my account"` `"sign in"`       |
| 💰 **Balance**   | `"what's my balance"` `"show balance"`    |
| 💡 **Pay Bills** | `"pay electricity bill of 1500 to Adani"` |
| 💸 **Transfer**  | `"transfer 5000 rupees to Mom"`           |
| 🥇 **Gold**      | `"invest in gold"` `"buy 0.5 grams gold"` |
| 👤 **Profile**   | `"show my profile"`                       |

### Demo Credentials

```
👤 Username: demo_user
🔑 Password: demo123
```

### Programmatic Usage

```python
from src.agent.agent import FinAgent
import asyncio

async def main():
    agent = FinAgent()
    await agent.start()

    result = await agent.execute("pay electricity bill of 1500 to Adani")
    print(result)

    await agent.stop()

asyncio.run(main())
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    📱 USER DASHBOARD                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Command   │  │    Live     │  │      Approval       │  │
│  │    Input    │  │   Preview   │  │     Interface       │  │
│  └──────┬──────┘  └─────────────┘  └──────────┬──────────┘  │
└─────────┼──────────────────────────────────────┼────────────┘
          │                                      │
          ▼                                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    🤖 FINAGENT CORE                          │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │ 🧠 Intent    │───▶│ 📋 Task      │───▶│ ⏸️ Conscious  │   │
│  │    Parser    │    │ Orchestrator │    │    Pause     │   │
│  └──────────────┘    └──────┬───────┘    └──────────────┘   │
│                             │                                │
│                             ▼                                │
│                    ┌──────────────┐                         │
│                    │ 🖐️ Browser   │                         │
│                    │   Control    │                         │
│                    └──────┬───────┘                         │
└───────────────────────────┼─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    🏦 JIOFINANCE BANK                        │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐ │
│  │ Login  │  │  Pay   │  │Transfer│  │  Gold  │  │Profile │ │
│  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 Conscious Pause™ - Safety First

> **Every high-risk action requires explicit human approval**

```
┌────────────────────────────────────────┐
│         ⚠️ APPROVAL REQUIRED           │
├────────────────────────────────────────┤
│                                        │
│  Action: Fund Transfer                 │
│  Amount: ₹5,000.00                     │
│  To: Mom (A/C: XXXX1234)              │
│                                        │
│  ┌──────────┐      ┌──────────┐       │
│  │ ✅ Approve│      │ ❌ Reject │       │
│  └──────────┘      └──────────┘       │
│                                        │
│        ⏱️ Auto-cancel in 60s           │
└────────────────────────────────────────┘
```

### Protected Actions

- ✓ Bill Payments
- ✓ Fund Transfers
- ✓ Gold Purchases
- ✓ Profile Updates

---

## 📁 Project Structure

```
finagent/
├── 📂 src/
│   ├── 📂 agent/              # 🤖 Core AI Agent
│   │   ├── agent.py           # Main agent class
│   │   ├── intent_parser.py   # NLP processing
│   │   ├── browser_automation.py
│   │   ├── conscious_pause.py # Safety mechanism
│   │   ├── orchestrator.py    # Task planning
│   │   └── ...
│   │
│   ├── 📂 backend/            # ⚡ FastAPI Server
│   │   └── server.py          # REST + WebSocket
│   │
│   └── 📂 dummy-bank/         # 🏦 React Bank App
│       ├── src/components/    # UI Components
│       └── ...
│
├── 📂 tests/                  # 🧪 Test Suite
├── main.py                    # 🚀 Entry Point
├── demo.py                    # 🎬 Demo Script
└── requirements.txt           # 📦 Dependencies
```

---

## 🛠️ Tech Stack

<table>
<tr>
<td align="center" width="20%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="40"/>
<br><b>Python</b>
<br><sub>Backend</sub>
</td>
<td align="center" width="20%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg" width="40"/>
<br><b>React</b>
<br><sub>Bank UI</sub>
</td>
<td align="center" width="20%">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg" width="40"/>
<br><b>FastAPI</b>
<br><sub>API Server</sub>
</td>
<td align="center" width="20%">
<img src="https://playwright.dev/img/playwright-logo.svg" width="40"/>
<br><b>Playwright</b>
<br><sub>Automation</sub>
</td>
<td align="center" width="20%">
<img src="https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg" width="40"/>
<br><b>GPT-4o</b>
<br><sub>AI/NLP</sub>
</td>
</tr>
</table>

### Key Technologies

| Layer        | Technologies                              |
| ------------ | ----------------------------------------- |
| **AI/NLP**   | OpenAI GPT-4o, Google Gemini 1.5 Pro      |
| **Browser**  | Playwright (Chromium)                     |
| **Backend**  | Python 3.10+, FastAPI, WebSockets         |
| **Frontend** | React 18, Vite, Modern CSS                |
| **Design**   | Glassmorphism, Responsive (360px-2560px+) |

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src

# Specific test
pytest tests/test_intent_parser.py
```

---

## 🎯 Hackathon Criteria

| Criteria            | Our Approach                                    |
| ------------------- | ----------------------------------------------- |
| 🎯 **Feasibility**  | Battle-tested tech: Playwright, GPT-4o, FastAPI |
| 🔧 **Technical**    | Clean modular architecture, async/await         |
| 💡 **Innovation**   | Conscious Pause™ for safe financial AI          |
| 🎨 **Presentation** | Modern glassmorphism UI, real-time updates      |

---

<div align="center">

### Built with ❤️ for IIT Bombay Techfest × Jio Financial Services

[![GitHub](https://img.shields.io/badge/View_on-GitHub-181717?style=for-the-badge&logo=github)](https://github.com/your-repo/finagent)

**MIT License**

</div>
