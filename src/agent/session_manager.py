"""
Session Manager - Persistence & Recovery

Provides session state management for FinAgent:
- Save/restore session state
- Cookie persistence for login sessions
- Command history tracking
- Crash recovery
- Auto-save functionality
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict, field


@dataclass
class SessionState:
    """Complete session state"""
    session_id: str
    created_at: str
    updated_at: str
    is_logged_in: bool = False
    current_user: Optional[str] = None
    current_page: Optional[str] = None
    command_history: List[Dict[str, Any]] = field(default_factory=list)
    approval_history: List[Dict[str, Any]] = field(default_factory=list)
    cookies: List[Dict[str, Any]] = field(default_factory=list)
    browser_state: Dict[str, Any] = field(default_factory=dict)
    custom_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionState":
        return cls(**data)


class SessionManager:
    """
    Manages session persistence and recovery
    
    Features:
    - Automatic state saving
    - Cookie persistence for login sessions
    - Command history with timestamps
    - Crash recovery support
    - Session export/import
    """
    
    def __init__(
        self,
        session_dir: str = "sessions",
        session_id: Optional[str] = None,
        auto_save: bool = True,
        auto_save_interval: int = 30
    ):
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        self.auto_save = auto_save
        self.auto_save_interval = auto_save_interval
        self._auto_save_task: Optional[asyncio.Task] = None
        
        # Initialize or load session
        if session_id:
            self.state = self._load_session(session_id) or self._create_new_session(session_id)
        else:
            self.state = self._create_new_session()
        
        self.session_file = self.session_dir / f"session_{self.state.session_id}.json"
        
        print(f"📁 Session Manager initialized (ID: {self.state.session_id[:8]}...)")
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _create_new_session(self, session_id: Optional[str] = None) -> SessionState:
        """Create new session state"""
        now = datetime.now().isoformat()
        return SessionState(
            session_id=session_id or self._generate_session_id(),
            created_at=now,
            updated_at=now
        )
    
    def _load_session(self, session_id: str) -> Optional[SessionState]:
        """Load existing session from disk"""
        session_file = self.session_dir / f"session_{session_id}.json"
        
        if session_file.exists():
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"📂 Loaded existing session: {session_id[:8]}...")
                return SessionState.from_dict(data)
            except Exception as e:
                print(f"⚠️ Failed to load session: {e}")
        
        return None
    
    def save(self):
        """Save current session state to disk"""
        self.state.updated_at = datetime.now().isoformat()
        
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(self.state.to_dict(), f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save session: {e}")
    
    def load(self) -> bool:
        """Load session state from disk"""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.state = SessionState.from_dict(data)
                return True
            except Exception as e:
                print(f"⚠️ Failed to load session: {e}")
        return False
    
    # Login State Management
    def set_logged_in(self, username: str, cookies: Optional[List[Dict]] = None):
        """Mark session as logged in"""
        self.state.is_logged_in = True
        self.state.current_user = username
        if cookies:
            self.state.cookies = cookies
        self.save()
    
    def set_logged_out(self):
        """Mark session as logged out"""
        self.state.is_logged_in = False
        self.state.current_user = None
        self.state.cookies = []
        self.save()
    
    def is_logged_in(self) -> bool:
        """Check if session is logged in"""
        return self.state.is_logged_in
    
    # Cookie Management
    def save_cookies(self, cookies: List[Dict[str, Any]]):
        """Save browser cookies"""
        self.state.cookies = cookies
        self.save()
    
    def get_cookies(self) -> List[Dict[str, Any]]:
        """Get saved cookies"""
        return self.state.cookies
    
    async def save_cookies_from_browser(self, browser_context):
        """Save cookies from Playwright browser context"""
        try:
            cookies = await browser_context.cookies()
            self.save_cookies(cookies)
            return True
        except Exception as e:
            print(f"⚠️ Failed to save browser cookies: {e}")
            return False
    
    async def restore_cookies_to_browser(self, browser_context) -> bool:
        """Restore cookies to Playwright browser context"""
        if not self.state.cookies:
            return False
        
        try:
            await browser_context.add_cookies(self.state.cookies)
            print(f"🍪 Restored {len(self.state.cookies)} cookies")
            return True
        except Exception as e:
            print(f"⚠️ Failed to restore cookies: {e}")
            return False
    
    # Command History
    def add_command(self, command: str, intent: Optional[Dict] = None, result: Optional[str] = None):
        """Add command to history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "intent": intent,
            "result": result
        }
        self.state.command_history.append(entry)
        
        # Keep last 100 commands
        if len(self.state.command_history) > 100:
            self.state.command_history = self.state.command_history[-100:]
        
        self.save()
    
    def get_command_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent command history"""
        return self.state.command_history[-limit:]
    
    def get_last_command(self) -> Optional[Dict[str, Any]]:
        """Get the last executed command"""
        if self.state.command_history:
            return self.state.command_history[-1]
        return None
    
    # Approval History
    def add_approval(self, action: str, details: Dict, approved: bool, reason: Optional[str] = None):
        """Add approval decision to history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "approved": approved,
            "reason": reason
        }
        self.state.approval_history.append(entry)
        
        # Keep last 50 approvals
        if len(self.state.approval_history) > 50:
            self.state.approval_history = self.state.approval_history[-50:]
        
        self.save()
    
    def get_approval_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent approval history"""
        return self.state.approval_history[-limit:]
    
    # Page State
    def set_current_page(self, page_type: str):
        """Update current page state"""
        self.state.current_page = page_type
        self.save()
    
    def get_current_page(self) -> Optional[str]:
        """Get current page type"""
        return self.state.current_page
    
    # Browser State
    def save_browser_state(self, state: Dict[str, Any]):
        """Save browser state (URL, scroll position, etc.)"""
        self.state.browser_state = {
            "saved_at": datetime.now().isoformat(),
            **state
        }
        self.save()
    
    def get_browser_state(self) -> Dict[str, Any]:
        """Get saved browser state"""
        return self.state.browser_state
    
    # Custom Data Storage
    def set_data(self, key: str, value: Any):
        """Store custom data"""
        self.state.custom_data[key] = value
        self.save()
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """Get custom data"""
        return self.state.custom_data.get(key, default)
    
    # Auto-save
    async def start_auto_save(self):
        """Start auto-save background task"""
        if self.auto_save and self._auto_save_task is None:
            self._auto_save_task = asyncio.create_task(self._auto_save_loop())
    
    async def stop_auto_save(self):
        """Stop auto-save background task"""
        if self._auto_save_task:
            self._auto_save_task.cancel()
            try:
                await self._auto_save_task
            except asyncio.CancelledError:
                pass
            self._auto_save_task = None
    
    async def _auto_save_loop(self):
        """Background auto-save loop"""
        while True:
            await asyncio.sleep(self.auto_save_interval)
            self.save()
    
    # Session Management
    def clear_session(self):
        """Clear current session data"""
        session_id = self.state.session_id
        self.state = self._create_new_session(session_id)
        self.save()
    
    def delete_session(self):
        """Delete session file"""
        if self.session_file.exists():
            self.session_file.unlink()
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all saved sessions"""
        sessions = []
        
        for session_file in self.session_dir.glob("session_*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                sessions.append({
                    "session_id": data.get("session_id"),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "is_logged_in": data.get("is_logged_in", False),
                    "current_user": data.get("current_user"),
                    "command_count": len(data.get("command_history", []))
                })
            except:
                continue
        
        return sorted(sessions, key=lambda x: x.get("updated_at", ""), reverse=True)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        return {
            "session_id": self.state.session_id,
            "created_at": self.state.created_at,
            "updated_at": self.state.updated_at,
            "is_logged_in": self.state.is_logged_in,
            "current_user": self.state.current_user,
            "current_page": self.state.current_page,
            "command_count": len(self.state.command_history),
            "approval_count": len(self.state.approval_history),
            "has_cookies": len(self.state.cookies) > 0
        }
    
    def export_session(self, filepath: Optional[str] = None) -> str:
        """Export session to a file"""
        if filepath is None:
            filepath = self.session_dir / f"export_{self.state.session_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.state.to_dict(), f, indent=2)
        
        return str(filepath)
    
    def import_session(self, filepath: str) -> bool:
        """Import session from a file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.state = SessionState.from_dict(data)
            self.session_file = self.session_dir / f"session_{self.state.session_id}.json"
            self.save()
            return True
        except Exception as e:
            print(f"⚠️ Failed to import session: {e}")
            return False


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get or create global session manager"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


def init_session_manager(
    session_dir: str = "sessions",
    session_id: Optional[str] = None,
    auto_save: bool = True
) -> SessionManager:
    """Initialize global session manager with custom settings"""
    global _session_manager
    _session_manager = SessionManager(
        session_dir=session_dir,
        session_id=session_id,
        auto_save=auto_save
    )
    return _session_manager
