# FinAgent - AI-Powered Financial Automation Agent
# IIT Bombay Techfest Hackathon - Jio Financial Services

# This package provides the core agent functionality:
# - Intent parsing from natural language
# - Browser automation with Playwright
# - Vision AI for UI element detection (CORE INNOVATION)
# - Conscious Pause mechanism for high-risk actions
# - Multi-step task orchestration
# - Session persistence & recovery
# - Comprehensive audit logging
# - Performance metrics tracking
# - Transaction limits & safety controls

__version__ = "1.1.0"
__author__ = "FinAgent Team"

# Core components
from .config import config, Config, ACTIONS, calculate_backoff_delay
from .vision import VisionModule, find_element, analyze_page, verify_action
from .intent_parser import IntentParser, ParsedIntent
from .browser_automation import BrowserAutomation, ActionResult
from .conscious_pause import ConciousPause, ApprovalRequest, ApprovalStatus
from .orchestrator import TaskOrchestrator, Task, TaskStep, TaskStatus
from .agent import FinAgent

# New improvement modules
from .audit_logger import AuditLogger, get_audit_logger, init_audit_logger
from .session_manager import SessionManager, get_session_manager, init_session_manager
from .element_cache import ElementCache, get_element_cache, init_element_cache
from .user_errors import UserFriendlyErrors, translate_error, format_error, is_recoverable
from .transaction_limits import TransactionLimits, get_transaction_limits, check_transaction_limit
from .metrics import PerformanceMetrics, get_metrics, reset_metrics

__all__ = [
    # Config
    "config", "Config", "ACTIONS", "calculate_backoff_delay",
    
    # Core Agent
    "FinAgent",
    "VisionModule", "find_element", "analyze_page", "verify_action",
    "IntentParser", "ParsedIntent",
    "BrowserAutomation", "ActionResult",
    "ConciousPause", "ApprovalRequest", "ApprovalStatus",
    "TaskOrchestrator", "Task", "TaskStep", "TaskStatus",
    
    # Improvement Modules
    "AuditLogger", "get_audit_logger", "init_audit_logger",
    "SessionManager", "get_session_manager", "init_session_manager",
    "ElementCache", "get_element_cache", "init_element_cache",
    "UserFriendlyErrors", "translate_error", "format_error", "is_recoverable",
    "TransactionLimits", "get_transaction_limits", "check_transaction_limit",
    "PerformanceMetrics", "get_metrics", "reset_metrics",
]
