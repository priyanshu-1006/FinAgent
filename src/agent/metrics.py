"""
Performance Metrics - Agent Performance Tracking

Tracks and reports performance metrics for FinAgent:
- Command success/failure rates
- Execution times
- API call statistics
- Vision accuracy metrics
- Session analytics
"""

import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from contextlib import contextmanager
from collections import defaultdict


@dataclass
class TimingMetric:
    """Single timing measurement"""
    operation: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def complete(self, success: bool = True):
        """Mark timing as complete"""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        self.success = success


@dataclass
class CommandMetric:
    """Metrics for a single command execution"""
    command: str
    action: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[float] = None
    success: bool = False
    error: Optional[str] = None
    steps_count: int = 0
    api_calls: int = 0
    vision_calls: int = 0
    approval_required: bool = False
    approval_granted: Optional[bool] = None


class PerformanceMetrics:
    """
    Comprehensive performance tracking for FinAgent
    
    Features:
    - Command success/failure tracking
    - Execution time measurement
    - API usage statistics
    - Vision accuracy tracking
    - Real-time dashboard data
    """
    
    def __init__(self):
        self.started_at = datetime.now()
        
        # Command metrics
        self.commands: List[CommandMetric] = []
        self.current_command: Optional[CommandMetric] = None
        
        # Timing metrics
        self.timings: List[TimingMetric] = []
        
        # Counters
        self.counters = defaultdict(int)
        
        # API call tracking
        self.api_calls: List[Dict[str, Any]] = []
        
        # Vision call tracking
        self.vision_calls: List[Dict[str, Any]] = []
        
        # Error tracking
        self.errors: List[Dict[str, Any]] = []
        
        print("📊 Performance Metrics initialized")
    
    # Command Tracking
    def start_command(self, command: str, action: str, approval_required: bool = False):
        """Start tracking a command execution"""
        self.current_command = CommandMetric(
            command=command,
            action=action,
            started_at=datetime.now(),
            approval_required=approval_required
        )
        self.counters["total_commands"] += 1
    
    def complete_command(self, success: bool = True, error: Optional[str] = None):
        """Complete current command tracking"""
        if self.current_command:
            self.current_command.completed_at = datetime.now()
            self.current_command.duration_ms = (
                self.current_command.completed_at - self.current_command.started_at
            ).total_seconds() * 1000
            self.current_command.success = success
            self.current_command.error = error
            
            self.commands.append(self.current_command)
            
            if success:
                self.counters["successful_commands"] += 1
            else:
                self.counters["failed_commands"] += 1
            
            self.current_command = None
    
    def increment_step(self):
        """Increment step counter for current command"""
        if self.current_command:
            self.current_command.steps_count += 1
    
    def set_approval_granted(self, granted: bool):
        """Record approval decision"""
        if self.current_command:
            self.current_command.approval_granted = granted
        
        self.counters["approvals_requested"] += 1
        if granted:
            self.counters["approvals_granted"] += 1
        else:
            self.counters["approvals_denied"] += 1
    
    # Timing Tracking
    @contextmanager
    def measure(self, operation: str, metadata: Optional[Dict] = None):
        """Context manager for timing operations"""
        timing = TimingMetric(
            operation=operation,
            start_time=time.time(),
            metadata=metadata or {}
        )
        
        try:
            yield timing
            timing.complete(success=True)
        except Exception as e:
            timing.complete(success=False)
            timing.metadata["error"] = str(e)
            raise
        finally:
            self.timings.append(timing)
    
    def start_timing(self, operation: str, metadata: Optional[Dict] = None) -> TimingMetric:
        """Start a timing measurement"""
        timing = TimingMetric(
            operation=operation,
            start_time=time.time(),
            metadata=metadata or {}
        )
        return timing
    
    def complete_timing(self, timing: TimingMetric, success: bool = True):
        """Complete a timing measurement"""
        timing.complete(success)
        self.timings.append(timing)
    
    # API Call Tracking
    def record_api_call(
        self,
        provider: str,
        model: str,
        duration_ms: float,
        success: bool = True,
        error: Optional[str] = None
    ):
        """Record an AI API call"""
        self.api_calls.append({
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "duration_ms": duration_ms,
            "success": success,
            "error": error
        })
        
        self.counters["api_calls"] += 1
        if success:
            self.counters["api_calls_success"] += 1
        else:
            self.counters["api_calls_failed"] += 1
        
        if self.current_command:
            self.current_command.api_calls += 1
    
    # Vision Call Tracking
    def record_vision_call(
        self,
        operation: str,
        duration_ms: float,
        element_found: bool = True,
        confidence: float = 0.0
    ):
        """Record a vision AI call"""
        self.vision_calls.append({
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "duration_ms": duration_ms,
            "element_found": element_found,
            "confidence": confidence
        })
        
        self.counters["vision_calls"] += 1
        if element_found:
            self.counters["vision_elements_found"] += 1
        else:
            self.counters["vision_elements_missed"] += 1
        
        if self.current_command:
            self.current_command.vision_calls += 1
    
    # Error Tracking
    def record_error(self, error_type: str, message: str, recoverable: bool = True):
        """Record an error"""
        self.errors.append({
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": message,
            "recoverable": recoverable
        })
        
        self.counters["errors"] += 1
        if recoverable:
            self.counters["recoverable_errors"] += 1
        else:
            self.counters["fatal_errors"] += 1
    
    # Statistics & Reporting
    def get_success_rate(self) -> float:
        """Calculate command success rate"""
        total = self.counters["total_commands"]
        if total == 0:
            return 0.0
        return self.counters["successful_commands"] / total
    
    def get_average_execution_time(self) -> float:
        """Calculate average command execution time in ms"""
        completed = [c for c in self.commands if c.duration_ms is not None]
        if not completed:
            return 0.0
        return sum(c.duration_ms for c in completed) / len(completed)
    
    def get_api_success_rate(self) -> float:
        """Calculate API call success rate"""
        total = self.counters["api_calls"]
        if total == 0:
            return 0.0
        return self.counters["api_calls_success"] / total
    
    def get_vision_accuracy(self) -> float:
        """Calculate vision element detection accuracy"""
        total = self.counters["vision_calls"]
        if total == 0:
            return 0.0
        return self.counters["vision_elements_found"] / total
    
    def get_session_duration(self) -> timedelta:
        """Get current session duration"""
        return datetime.now() - self.started_at
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        session_duration = self.get_session_duration()
        
        return {
            "session": {
                "started_at": self.started_at.isoformat(),
                "duration_seconds": session_duration.total_seconds(),
                "duration_formatted": str(session_duration).split('.')[0]
            },
            "commands": {
                "total": self.counters["total_commands"],
                "successful": self.counters["successful_commands"],
                "failed": self.counters["failed_commands"],
                "success_rate": round(self.get_success_rate() * 100, 2),
                "avg_execution_time_ms": round(self.get_average_execution_time(), 2)
            },
            "approvals": {
                "requested": self.counters["approvals_requested"],
                "granted": self.counters["approvals_granted"],
                "denied": self.counters["approvals_denied"]
            },
            "api": {
                "total_calls": self.counters["api_calls"],
                "successful": self.counters["api_calls_success"],
                "failed": self.counters["api_calls_failed"],
                "success_rate": round(self.get_api_success_rate() * 100, 2)
            },
            "vision": {
                "total_calls": self.counters["vision_calls"],
                "elements_found": self.counters["vision_elements_found"],
                "elements_missed": self.counters["vision_elements_missed"],
                "accuracy": round(self.get_vision_accuracy() * 100, 2)
            },
            "errors": {
                "total": self.counters["errors"],
                "recoverable": self.counters["recoverable_errors"],
                "fatal": self.counters["fatal_errors"]
            }
        }
    
    def get_recent_commands(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent command executions"""
        recent = self.commands[-limit:]
        return [
            {
                "command": c.command,
                "action": c.action,
                "started_at": c.started_at.isoformat(),
                "duration_ms": c.duration_ms,
                "success": c.success,
                "error": c.error,
                "steps": c.steps_count,
                "api_calls": c.api_calls,
                "vision_calls": c.vision_calls
            }
            for c in reversed(recent)
        ]
    
    def get_timing_stats(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get timing statistics for operations"""
        filtered = [t for t in self.timings if t.duration_ms is not None]
        if operation:
            filtered = [t for t in filtered if t.operation == operation]
        
        if not filtered:
            return {}
        
        durations = [t.duration_ms for t in filtered]
        
        return {
            "operation": operation or "all",
            "count": len(durations),
            "min_ms": round(min(durations), 2),
            "max_ms": round(max(durations), 2),
            "avg_ms": round(sum(durations) / len(durations), 2),
            "success_rate": round(sum(1 for t in filtered if t.success) / len(filtered) * 100, 2)
        }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data formatted for dashboard display"""
        return {
            "summary": self.get_summary(),
            "recent_commands": self.get_recent_commands(5),
            "recent_errors": self.errors[-5:] if self.errors else [],
            "timing_stats": {
                "vision": self.get_timing_stats("vision"),
                "api": self.get_timing_stats("api"),
                "browser": self.get_timing_stats("browser")
            }
        }
    
    def reset(self):
        """Reset all metrics"""
        self.__init__()


# Global metrics instance
_metrics: Optional[PerformanceMetrics] = None


def get_metrics() -> PerformanceMetrics:
    """Get or create global metrics instance"""
    global _metrics
    if _metrics is None:
        _metrics = PerformanceMetrics()
    return _metrics


def reset_metrics():
    """Reset global metrics"""
    global _metrics
    _metrics = PerformanceMetrics()
