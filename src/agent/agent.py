"""
FinAgent - Main Agent Class

The central coordinator that brings together:
- Intent parsing (Action Brain)
- Browser automation (Digital Hand)
- Conscious pause (Safety mechanism)
- Task orchestration (Multi-step planning)
"""

import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable
from datetime import datetime

from .config import config, Config
from .intent_parser import IntentParser, ParsedIntent
from .browser_automation import BrowserAutomation, ActionResult
from .conscious_pause import ConciousPause, ApprovalRequest, ApprovalStatus
from .orchestrator import TaskOrchestrator, Task, TaskStatus


class FinAgent:
    """
    AI-powered Financial Automation Agent
    
    Features:
    - Natural language command processing
    - Automated browser interactions
    - Human-in-the-loop approval for risky actions
    - Multi-step task orchestration
    """
    
    def __init__(self, custom_config: Config = None):
        self.config = custom_config or config
        
        # Core components
        self.intent_parser = IntentParser(use_ai=True)
        self.browser = BrowserAutomation()
        self.conscious_pause = ConciousPause()
        self.orchestrator = None
        
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
        
        # Start browser
        await self.browser.start()
        
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
        await self.browser.navigate()
        
        self.is_running = True
        self.session_start = datetime.now()
        
        print("✅ FinAgent ready!")
        print(f"🌐 Connected to: {self.config.bank_url}")
        
        return self
    
    async def stop(self):
        """Stop the agent and cleanup"""
        
        print("\n🛑 Stopping FinAgent...")
        
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
        
        # Store in history
        self.command_history.append({
            "command": command,
            "timestamp": datetime.now().isoformat()
        })
        
        # Process through orchestrator
        task = await self.orchestrator.process_command(command)
        
        return {
            "task_id": task.id,
            "status": task.status.value,
            "command": command,
            "steps_completed": sum(1 for s in task.steps if s.status == TaskStatus.COMPLETED),
            "total_steps": len(task.steps),
            "result": task.to_dict()
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        
        page_state = await self.browser.get_page_state() if self.is_running else {}
        
        return {
            "is_running": self.is_running,
            "session_start": self.session_start.isoformat() if self.session_start else None,
            "commands_executed": len(self.command_history),
            "is_logged_in": self.browser.is_logged_in if self.is_running else False,
            "current_url": page_state.get("url", ""),
            "pending_approvals": self.conscious_pause.get_pending_requests(),
            "recent_history": self.command_history[-5:]
        }
    
    async def approve(self, request_id: str) -> bool:
        """Approve a pending action"""
        return self.conscious_pause.approve(request_id)
    
    async def reject(self, request_id: str) -> bool:
        """Reject a pending action"""
        return self.conscious_pause.reject(request_id)
    
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
