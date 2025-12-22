"""
Audit Logger - Comprehensive Logging & Audit Trail

Provides structured logging for all FinAgent operations:
- User commands
- AI responses
- Browser actions
- Approval decisions
- Errors and recoveries
- Performance metrics
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class LogLevel(Enum):
    """Log severity levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ActionType(Enum):
    """Types of auditable actions"""
    COMMAND_RECEIVED = "command_received"
    INTENT_PARSED = "intent_parsed"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_DENIED = "approval_denied"
    BROWSER_ACTION = "browser_action"
    VISION_ANALYSIS = "vision_analysis"
    API_CALL = "api_call"
    ERROR_OCCURRED = "error_occurred"
    ERROR_RECOVERED = "error_recovered"
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    TRANSACTION_START = "transaction_start"
    TRANSACTION_COMPLETE = "transaction_complete"
    TRANSACTION_FAILED = "transaction_failed"


@dataclass
class AuditEntry:
    """Single audit log entry"""
    timestamp: str
    action_type: str
    risk_level: str
    details: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    execution_time_ms: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class AuditLogger:
    """
    Centralized audit logging for FinAgent
    
    Features:
    - Structured JSON logging
    - File and console output
    - Session tracking
    - Performance timing
    - Risk level classification
    """
    
    def __init__(self, log_dir: str = "logs", session_id: Optional[str] = None):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_id = session_id or self._generate_session_id()
        
        # Setup loggers
        self._setup_audit_logger()
        self._setup_performance_logger()
        
        # In-memory log buffer for recent entries
        self.recent_entries: list[AuditEntry] = []
        self.max_recent = 1000
        
        print(f"📝 Audit Logger initialized (Session: {self.session_id[:8]}...)")
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _setup_audit_logger(self):
        """Setup main audit logger"""
        self.audit_logger = logging.getLogger("finagent.audit")
        self.audit_logger.setLevel(logging.INFO)
        self.audit_logger.handlers = []  # Clear existing handlers
        
        # File handler - JSON format
        audit_file = self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(audit_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(message)s'))
        self.audit_logger.addHandler(file_handler)
        
        # Console handler for important events
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        ))
        self.audit_logger.addHandler(console_handler)
    
    def _setup_performance_logger(self):
        """Setup performance metrics logger"""
        self.perf_logger = logging.getLogger("finagent.performance")
        self.perf_logger.setLevel(logging.INFO)
        self.perf_logger.handlers = []
        
        perf_file = self.log_dir / f"performance_{datetime.now().strftime('%Y%m%d')}.log"
        handler = logging.FileHandler(perf_file, encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.perf_logger.addHandler(handler)
    
    def log(
        self,
        action_type: ActionType,
        details: Dict[str, Any],
        risk_level: str = "low",
        success: bool = True,
        error_message: Optional[str] = None,
        execution_time_ms: Optional[float] = None,
        user_id: Optional[str] = None
    ) -> AuditEntry:
        """
        Log an auditable action
        
        Args:
            action_type: Type of action being logged
            details: Action-specific details
            risk_level: low, medium, high, critical
            success: Whether action succeeded
            error_message: Error details if failed
            execution_time_ms: Time taken in milliseconds
            user_id: User identifier if available
        """
        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            action_type=action_type.value,
            risk_level=risk_level,
            details=details,
            user_id=user_id,
            session_id=self.session_id,
            execution_time_ms=execution_time_ms,
            success=success,
            error_message=error_message
        )
        
        # Log to file
        self.audit_logger.info(entry.to_json())
        
        # Store in memory
        self.recent_entries.append(entry)
        if len(self.recent_entries) > self.max_recent:
            self.recent_entries.pop(0)
        
        return entry
    
    def log_command(self, command: str, user_id: Optional[str] = None):
        """Log a user command"""
        return self.log(
            action_type=ActionType.COMMAND_RECEIVED,
            details={"command": command},
            risk_level="low",
            user_id=user_id
        )
    
    def log_intent(self, intent: Dict[str, Any], confidence: float):
        """Log parsed intent"""
        risk = "high" if intent.get("requires_approval") else "low"
        return self.log(
            action_type=ActionType.INTENT_PARSED,
            details={"intent": intent, "confidence": confidence},
            risk_level=risk
        )
    
    def log_approval_request(self, action: str, details: Dict[str, Any]):
        """Log approval request"""
        return self.log(
            action_type=ActionType.APPROVAL_REQUESTED,
            details={"action": action, **details},
            risk_level="high"
        )
    
    def log_approval_decision(self, approved: bool, action: str, reason: Optional[str] = None):
        """Log approval decision"""
        return self.log(
            action_type=ActionType.APPROVAL_GRANTED if approved else ActionType.APPROVAL_DENIED,
            details={"action": action, "reason": reason},
            risk_level="high",
            success=approved
        )
    
    def log_browser_action(
        self,
        action: str,
        target: str,
        success: bool = True,
        execution_time_ms: Optional[float] = None
    ):
        """Log browser automation action"""
        return self.log(
            action_type=ActionType.BROWSER_ACTION,
            details={"action": action, "target": target},
            success=success,
            execution_time_ms=execution_time_ms
        )
    
    def log_vision_analysis(
        self,
        analysis_type: str,
        result: Dict[str, Any],
        execution_time_ms: Optional[float] = None
    ):
        """Log vision AI analysis"""
        return self.log(
            action_type=ActionType.VISION_ANALYSIS,
            details={"type": analysis_type, "result": result},
            execution_time_ms=execution_time_ms
        )
    
    def log_api_call(
        self,
        provider: str,
        model: str,
        success: bool = True,
        execution_time_ms: Optional[float] = None,
        error: Optional[str] = None
    ):
        """Log AI API call"""
        return self.log(
            action_type=ActionType.API_CALL,
            details={"provider": provider, "model": model},
            success=success,
            execution_time_ms=execution_time_ms,
            error_message=error
        )
    
    def log_error(
        self,
        error_type: str,
        message: str,
        recoverable: bool = True,
        context: Optional[Dict[str, Any]] = None
    ):
        """Log an error"""
        return self.log(
            action_type=ActionType.ERROR_OCCURRED,
            details={
                "error_type": error_type,
                "recoverable": recoverable,
                "context": context or {}
            },
            risk_level="high" if not recoverable else "medium",
            success=False,
            error_message=message
        )
    
    def log_transaction(
        self,
        transaction_type: str,
        amount: float,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log financial transaction"""
        action_type = (
            ActionType.TRANSACTION_COMPLETE if status == "success"
            else ActionType.TRANSACTION_FAILED if status == "failed"
            else ActionType.TRANSACTION_START
        )
        
        return self.log(
            action_type=action_type,
            details={
                "type": transaction_type,
                "amount": amount,
                "status": status,
                **(details or {})
            },
            risk_level="high",
            success=status == "success"
        )
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        if not self.recent_entries:
            return {"session_id": self.session_id, "entries": 0}
        
        success_count = sum(1 for e in self.recent_entries if e.success)
        error_count = len(self.recent_entries) - success_count
        
        action_counts = {}
        for entry in self.recent_entries:
            action_counts[entry.action_type] = action_counts.get(entry.action_type, 0) + 1
        
        return {
            "session_id": self.session_id,
            "total_entries": len(self.recent_entries),
            "success_count": success_count,
            "error_count": error_count,
            "success_rate": success_count / len(self.recent_entries) if self.recent_entries else 0,
            "action_breakdown": action_counts,
            "start_time": self.recent_entries[0].timestamp if self.recent_entries else None,
            "last_activity": self.recent_entries[-1].timestamp if self.recent_entries else None
        }
    
    def get_recent_errors(self, limit: int = 10) -> list[AuditEntry]:
        """Get recent errors"""
        errors = [e for e in self.recent_entries if not e.success]
        return errors[-limit:]
    
    def export_session_log(self, filepath: Optional[str] = None) -> str:
        """Export session log to JSON file"""
        if filepath is None:
            filepath = self.log_dir / f"session_{self.session_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "session_id": self.session_id,
            "export_time": datetime.now().isoformat(),
            "summary": self.get_session_summary(),
            "entries": [e.to_dict() for e in self.recent_entries]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        return str(filepath)


# Global logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get or create global audit logger"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def init_audit_logger(log_dir: str = "logs", session_id: Optional[str] = None) -> AuditLogger:
    """Initialize global audit logger with custom settings"""
    global _audit_logger
    _audit_logger = AuditLogger(log_dir=log_dir, session_id=session_id)
    return _audit_logger
