# FinAgent - AI-Powered Financial Automation Agent
# IIT Bombay Techfest Hackathon - Jio Financial Services

# This package provides the core agent functionality:
# - Intent parsing from natural language
# - Browser automation with Playwright
# - Vision AI for UI element detection (CORE INNOVATION)
# - Conscious Pause mechanism for high-risk actions
# - Multi-step task orchestration

__version__ = "1.0.0"
__author__ = "FinAgent Team"

# Core components
from .config import config, Config, ACTIONS
from .vision import VisionModule, find_element, analyze_page, verify_action
from .intent_parser import IntentParser, ParsedIntent
from .browser_automation import BrowserAutomation, ActionResult
from .conscious_pause import ConciousPause, ApprovalRequest, ApprovalStatus
from .orchestrator import TaskOrchestrator, Task, TaskStep, TaskStatus
from .agent import FinAgent

__all__ = [
    "config", "Config", "ACTIONS",
    "VisionModule", "find_element", "analyze_page", "verify_action",
    "IntentParser", "ParsedIntent",
    "BrowserAutomation", "ActionResult",
    "ConciousPause", "ApprovalRequest", "ApprovalStatus",
    "TaskOrchestrator", "Task", "TaskStep", "TaskStatus",
    "FinAgent"
]
