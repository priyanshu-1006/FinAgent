"""
FinAgent - Main Agent Class

The central coordinator that brings together:
- Intent parsing (Action Brain)
- Browser automation (Digital Hand)
- Conscious pause (Safety mechanism)
- Task orchestration (Multi-step planning)
- Audit logging (Compliance & debugging)
- Session management (Persistence & recovery)
- Performance metrics (Analytics & monitoring)
- Transaction limits (Safety controls)
"""

import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable
from datetime import datetime

from .config import config, Config
from .intent_parser import IntentParser, ParsedIntent
from .browser_automation import BrowserAutomation, ActionResult
from .conscious_pause import ConciousPause, ApprovalRequest, ApprovalStatus
from .orchestrator import TaskOrchestrator, Task, TaskStatus

# Import improvement modules
from .audit_logger import get_audit_logger, ActionType
from .session_manager import get_session_manager
from .metrics import get_metrics
from .transaction_limits import get_transaction_limits, check_transaction_limit
from .user_errors import translate_error, format_error


class FinAgent:
    """
    AI-powered Financial Automation Agent
    
    Features:
    - Natural language command processing
    - Automated browser interactions
    - Human-in-the-loop approval for risky actions
    - Multi-step task orchestration
    - Comprehensive audit logging
    - Session persistence & recovery
    - Performance metrics tracking
    - Transaction limit enforcement
    """
    
    def __init__(self, custom_config: Config = None):
        self.config = custom_config or config
        
        # Core components
        self.intent_parser = IntentParser(use_ai=True)
        self.browser = BrowserAutomation()
        self.conscious_pause = ConciousPause()
        self.orchestrator = None
        
        # Improvement modules
        self.audit_logger = get_audit_logger()
        self.session_manager = get_session_manager()
        self.metrics = get_metrics()
        self.transaction_limits = get_transaction_limits()
        
        # State
        self.is_running = False
        self.session_start = None
        self.command_history = []
        
        # Callbacks for UI integration
        self.on_status_update: Optional[Callable[[str], Awaitable[None]]] = None
        self.on_screenshot: Optional[Callable[[str], Awaitable[None]]] = None
        self.on_approval_request: Optional[Callable[[ApprovalRequest], Awaitable[bool]]] = None
        self.on_task_update: Optional[Callable[[Task], Awaitable[None]]] = None
    
    async def start(self):
        """Initialize and start the agent"""
        
        print("🚀 Starting FinAgent...")
        print(f"🌐 Target bank URL: {self.config.bank_url}")
        
        # Log session start
        self.audit_logger.log(
            action_type=ActionType.SESSION_START,
            details={"bank_url": self.config.bank_url},
            risk_level="low"
        )
        
        # Start browser
        await self.browser.start()
        
        # Try to restore session (cookies, login state)
        if self.session_manager.is_logged_in():
            print("📂 Found previous session, attempting to restore...")
            if self.browser.context:
                await self.session_manager.restore_cookies_to_browser(self.browser.context)
        
        # Initialize orchestrator
        self.orchestrator = TaskOrchestrator(
            browser=self.browser,
            intent_parser=self.intent_parser,
            conscious_pause=self.conscious_pause
        )
        
        # Wire up callbacks
        if self.on_approval_request:
            self.conscious_pause.set_approval_callback(self.on_approval_request)
        
        self.orchestrator.on_step_complete = self._on_step_complete
        self.orchestrator.on_approval_needed = self._on_approval_needed
        self.orchestrator.on_task_complete = self._on_task_complete
        
        # Navigate to bank
        print(f"🌐 Navigating to: {self.config.bank_url}")
        nav_result = await self.browser.navigate()
        print(f"📍 Navigation result: {nav_result.message}")
        
        # Send initial screenshot to UI
        if self.on_screenshot:
            try:
                screenshot = await self.browser.take_screenshot()
                await self.on_screenshot(screenshot)
                print("📸 Initial screenshot sent")
            except Exception as e:
                print(f"⚠️ Failed to send initial screenshot: {e}")
        
        # Start auto-save for session
        await self.session_manager.start_auto_save()
        
        self.is_running = True
        self.session_start = datetime.now()
        
        print("✅ FinAgent ready!")
        print(f"🌐 Connected to: {self.config.bank_url}")
        
        return self
    
    async def stop(self):
        """Stop the agent and cleanup"""
        
        print("\n🛑 Stopping FinAgent...")
        
        # Save session state before stopping
        if self.browser.context:
            await self.session_manager.save_cookies_from_browser(self.browser.context)
        
        # Stop auto-save
        await self.session_manager.stop_auto_save()
        
        # Log session end
        self.audit_logger.log(
            action_type=ActionType.SESSION_END,
            details={
                "commands_executed": len(self.command_history),
                "session_duration": str(datetime.now() - self.session_start) if self.session_start else "0"
            },
            risk_level="low"
        )
        
        # Export session log
        try:
            log_path = self.audit_logger.export_session_log()
            print(f"📝 Session log saved: {log_path}")
        except Exception as e:
            print(f"⚠️ Failed to export session log: {e}")
        
        await self.browser.stop()
        self.is_running = False
        
        print("👋 FinAgent stopped")
    
    async def execute(self, command: str) -> Dict[str, Any]:
        """
        Execute a natural language command
        
        Args:
            command: Natural language command like "Pay electricity bill of 1500 rupees"
        
        Returns:
            Task result dictionary
        """
        
        if not self.is_running:
            return {"error": "Agent not running. Call start() first."}
        
        print(f"\n📝 Command: {command}")
        
        # Start tracking metrics
        self.metrics.start_command(command, action="parsing")
        
        # Log command received
        self.audit_logger.log_command(command)
        
        # Parse intent first to check transaction limits
        intent = self.intent_parser.parse(command)
        
        # Check transaction limits if applicable
        amount = intent.parameters.get("amount", 0)
        if amount > 0 and intent.action in ["pay_bill", "fund_transfer", "buy_gold"]:
            limit_check = check_transaction_limit(intent.action, amount)
            
            if not limit_check.allowed:
                error_msg = self.transaction_limits.format_limit_message(limit_check)
                print(f"⚠️ {error_msg}")
                
                self.audit_logger.log_error(
                    error_type="transaction_limit",
                    message=limit_check.reason,
                    recoverable=True
                )
                
                self.metrics.complete_command(success=False, error="Transaction limit exceeded")
                
                return {
                    "status": "rejected",
                    "error": error_msg,
                    "limit_info": {
                        "type": limit_check.limit_type.value if limit_check.limit_type else None,
                        "limit": limit_check.limit_value,
                        "remaining": limit_check.remaining
                    }
                }
            
            # Warn about 2FA if required
            if limit_check.requires_2fa:
                print("⚠️ High-value transaction: Additional verification may be required")
        
        # Store in history
        self.command_history.append({
            "command": command,
            "timestamp": datetime.now().isoformat(),
            "intent": intent.to_dict()
        })
        
        # Save to session manager
        self.session_manager.add_command(command, intent.to_dict())
        
        try:
            # Process through orchestrator
            task = await self.orchestrator.process_command(command)
            
            # Record successful transaction if applicable
            if task.status == TaskStatus.COMPLETED and amount > 0:
                self.transaction_limits.record_transaction(intent.action, amount, success=True)
            
            # Complete metrics tracking
            self.metrics.complete_command(
                success=task.status == TaskStatus.COMPLETED,
                error=None if task.status == TaskStatus.COMPLETED else "Task failed"
            )
            
            return {
                "task_id": task.id,
                "status": task.status.value,
                "command": command,
                "steps_completed": sum(1 for s in task.steps if s.status == TaskStatus.COMPLETED),
                "total_steps": len(task.steps),
                "result": task.to_dict()
            }
            
        except Exception as e:
            # Translate error for user
            user_error = translate_error(str(e))
            error_message = format_error(str(e))
            
            self.audit_logger.log_error(
                error_type="execution",
                message=str(e),
                recoverable=user_error.recoverable
            )
            
            self.metrics.complete_command(success=False, error=str(e))
            
            return {
                "status": "error",
                "error": user_error.message,
                "suggestion": user_error.suggestion,
                "technical_details": str(e)
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status with comprehensive metrics"""
        
        page_state = await self.browser.get_page_state() if self.is_running else {}
        
        return {
            "is_running": self.is_running,
            "session_start": self.session_start.isoformat() if self.session_start else None,
            "commands_executed": len(self.command_history),
            "is_logged_in": self.browser.is_logged_in if self.is_running else False,
            "current_url": page_state.get("url", ""),
            "pending_approvals": self.conscious_pause.get_pending_requests(),
            "recent_history": self.command_history[-5:],
            
            # New metrics
            "performance": self.metrics.get_summary(),
            "session_info": self.session_manager.get_session_summary(),
            "transaction_limits": {
                "pay_bill": self.transaction_limits.get_remaining_limits("pay_bill"),
                "fund_transfer": self.transaction_limits.get_remaining_limits("fund_transfer"),
                "buy_gold": self.transaction_limits.get_remaining_limits("buy_gold"),
            }
        }
    
    async def approve(self, request_id: str) -> bool:
        """Approve a pending action"""
        result = self.conscious_pause.approve(request_id)
        
        # Log approval decision
        self.audit_logger.log_approval_decision(
            approved=True,
            action=request_id,
            reason="User approved"
        )
        
        # Track in metrics
        self.metrics.set_approval_granted(True)
        
        # Save to session
        self.session_manager.add_approval(
            action=request_id,
            details={},
            approved=True
        )
        
        return result
    
    async def reject(self, request_id: str) -> bool:
        """Reject a pending action"""
        result = self.conscious_pause.reject(request_id)
        
        # Log rejection
        self.audit_logger.log_approval_decision(
            approved=False,
            action=request_id,
            reason="User rejected"
        )
        
        # Track in metrics
        self.metrics.set_approval_granted(False)
        
        # Save to session
        self.session_manager.add_approval(
            action=request_id,
            details={},
            approved=False
        )
        
        return result
    
    async def get_screenshot(self) -> str:
        """Get current browser screenshot (base64)"""
        if self.is_running:
            return await self.browser.take_screenshot()
        return ""
    
    async def get_balance(self) -> str:
        """Quick command to check balance"""
        result = await self.execute("check my balance")
        if result.get("status") == "completed":
            return result.get("result", {}).get("steps", [{}])[-1].get("result", {}).get("data", {}).get("balance", "Unknown")
        return "Unable to fetch balance"
    
    # Internal callbacks
    
    async def _on_step_complete(self, task: Task, step):
        """Called when a step completes"""
        if self.on_status_update:
            await self.on_status_update(
                f"Step {step.id}/{len(task.steps)}: {step.result.message if step.result else 'Done'}"
            )
        
        if self.on_screenshot and step.result and step.result.screenshot:
            await self.on_screenshot(step.result.screenshot)
        
        if self.on_task_update:
            await self.on_task_update(task)
    
    async def _on_approval_needed(self, request: ApprovalRequest):
        """Called when approval is needed"""
        if self.on_status_update:
            await self.on_status_update(
                f"⚠️ Approval needed: {request.description}"
            )
    
    async def _on_task_complete(self, task: Task):
        """Called when task completes"""
        if self.on_status_update:
            status = "✅ Completed" if task.status == TaskStatus.COMPLETED else "❌ Failed"
            await self.on_status_update(f"Task {task.id}: {status}")
        
        if self.on_task_update:
            await self.on_task_update(task)


# ===== CLI Interface =====

async def run_cli():
    """Run agent in CLI mode for testing"""
    
    agent = FinAgent()
    
    try:
        await agent.start()
        
        print("\n" + "="*60)
        print("FinAgent CLI - Type commands or 'quit' to exit")
        print("="*60)
        print("Examples:")
        print("  - 'login'")
        print("  - 'check my balance'")
        print("  - 'pay electricity bill of 1500 rupees to Adani'")
        print("  - 'transfer 5000 to Mom'")
        print("  - 'buy gold worth 2000'")
        print("="*60 + "\n")
        
        while True:
            try:
                command = input("\n🤖 Enter command: ").strip()
                
                if not command:
                    continue
                
                if command.lower() in ['quit', 'exit', 'q']:
                    break
                
                result = await agent.execute(command)
                
                print(f"\n📊 Result: {result['status']}")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(run_cli())
