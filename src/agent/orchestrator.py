"""
Task Orchestrator - Multi-step task planning and execution

Uses LangGraph-style orchestration for complex tasks:
- Breaks down commands into atomic steps
- Manages execution flow
- Handles errors and retries
- Coordinates between Intent Parser, Browser, and Conscious Pause
"""

import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from .config import config, ACTIONS
from .intent_parser import IntentParser, ParsedIntent
from .browser_automation import BrowserAutomation, ActionResult
from .conscious_pause import ConciousPause, ApprovalStatus


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskStep:
    """Single step in a task"""
    id: int
    action: str
    parameters: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[ActionResult] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "action": self.action,
            "parameters": self.parameters,
            "status": self.status.value,
            "result": self.result.to_dict() if self.result else None,
            "error": self.error
        }


@dataclass
class Task:
    """Complete task with multiple steps"""
    id: str
    original_command: str
    steps: List[TaskStep] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    current_step: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "command": self.original_command,
            "status": self.status.value,
            "current_step": self.current_step,
            "total_steps": len(self.steps),
            "steps": [s.to_dict() for s in self.steps],
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class TaskOrchestrator:
    """Orchestrates multi-step financial tasks"""
    
    def __init__(
        self,
        browser: BrowserAutomation,
        intent_parser: IntentParser = None,
        conscious_pause: ConciousPause = None
    ):
        self.browser = browser
        self.intent_parser = intent_parser or IntentParser(use_ai=True)
        self.conscious_pause = conscious_pause or ConciousPause()
        
        self.tasks: Dict[str, Task] = {}
        self._task_counter = 0
        
        # Event handlers
        self.on_step_start = None
        self.on_step_complete = None
        self.on_approval_needed = None
        self.on_task_complete = None
    
    async def process_command(self, command: str) -> Task:
        """Process a natural language command"""
        
        # Parse intent
        intent = self.intent_parser.parse(command)
        
        if intent.action == "unknown":
            return self._create_failed_task(
                command,
                "Could not understand the command. Please try rephrasing."
            )
        
        # Create task
        task = self._create_task(command, intent)
        
        # Execute task
        await self._execute_task(task)
        
        return task
    
    def _create_task(self, command: str, intent: ParsedIntent) -> Task:
        """Create a task from parsed intent"""
        
        self._task_counter += 1
        task_id = f"TASK-{self._task_counter:04d}"
        
        task = Task(
            id=task_id,
            original_command=command
        )
        
        # Build steps based on action type
        steps = self._build_steps(intent)
        task.steps = steps
        
        self.tasks[task_id] = task
        
        print(f"\n📋 Created {task_id} with {len(steps)} steps")
        for step in steps:
            print(f"   {step.id}. {step.action}")
        
        return task
    
    def _build_steps(self, intent: ParsedIntent) -> List[TaskStep]:
        """Build execution steps for an intent"""
        
        steps = []
        step_id = 0
        
        action = intent.action
        params = intent.parameters
        
        # Check if login is needed first
        if not self.browser.is_logged_in and action != "login":
            step_id += 1
            steps.append(TaskStep(
                id=step_id,
                action="login",
                parameters={"username": "demo_user", "password": "demo123"}
            ))
        
        # Main action steps
        if action == "login":
            step_id += 1
            steps.append(TaskStep(
                id=step_id,
                action="login",
                parameters=params
            ))
        
        elif action == "check_balance":
            step_id += 1
            steps.append(TaskStep(
                id=step_id,
                action="check_balance",
                parameters={}
            ))
        
        elif action == "pay_bill":
            # Navigate to pay bills
            step_id += 1
            steps.append(TaskStep(
                id=step_id,
                action="navigate_to_pay_bills",
                parameters={}
            ))
            
            # Fill and submit bill payment
            step_id += 1
            steps.append(TaskStep(
                id=step_id,
                action="pay_bill",
                parameters={
                    "biller": params.get("biller_name", "Adani Power"),
                    "consumer_number": params.get("consumer_number", "100234567890"),
                    "amount": params.get("amount", 1000)
                }
            ))
            
            # Confirm action (with approval)
            step_id += 1
            steps.append(TaskStep(
                id=step_id,
                action="confirm_with_approval",
                parameters={"parent_action": "pay_bill", **params}
            ))
        
        elif action == "fund_transfer":
            # Navigate
            step_id += 1
            steps.append(TaskStep(
                id=step_id,
                action="navigate_to_fund_transfer",
                parameters={}
            ))
            
            # Check if beneficiary is known
            if params.get("recipient", "").lower() in ["mom", "dad", "friend"]:
                step_id += 1
                steps.append(TaskStep(
                    id=step_id,
                    action="select_beneficiary",
                    parameters={"name": params["recipient"].capitalize()}
                ))
            
            # Fill transfer form
            step_id += 1
            steps.append(TaskStep(
                id=step_id,
                action="fund_transfer",
                parameters={
                    "recipient": params.get("recipient", ""),
                    "account": params.get("account", "9876543210"),
                    "ifsc": params.get("ifsc", "JFIN0001234"),
                    "amount": params.get("amount", 0)
                }
            ))
            
            # Confirm with approval
            step_id += 1
            steps.append(TaskStep(
                id=step_id,
                action="confirm_with_approval",
                parameters={"parent_action": "fund_transfer", **params}
            ))
        
        elif action == "buy_gold":
            # Navigate
            step_id += 1
            steps.append(TaskStep(
                id=step_id,
                action="navigate_to_buy_gold",
                parameters={}
            ))
            
            # Buy gold
            step_id += 1
            steps.append(TaskStep(
                id=step_id,
                action="buy_gold",
                parameters={
                    "amount": params.get("amount"),
                    "grams": params.get("grams")
                }
            ))
            
            # Confirm with approval
            step_id += 1
            steps.append(TaskStep(
                id=step_id,
                action="confirm_with_approval",
                parameters={"parent_action": "buy_gold", **params}
            ))
        
        elif action == "view_transactions":
            step_id += 1
            steps.append(TaskStep(
                id=step_id,
                action="view_transactions",
                parameters={}
            ))
        
        else:
            # Generic action
            step_id += 1
            steps.append(TaskStep(
                id=step_id,
                action=action,
                parameters=params
            ))
        
        return steps
    
    async def _execute_task(self, task: Task):
        """Execute all steps in a task"""
        
        task.status = TaskStatus.IN_PROGRESS
        
        for i, step in enumerate(task.steps):
            task.current_step = i + 1
            
            print(f"\n▶️  Step {step.id}/{len(task.steps)}: {step.action}")
            
            if self.on_step_start:
                await self.on_step_start(task, step)
            
            step.status = TaskStatus.IN_PROGRESS
            
            try:
                result = await self._execute_step(step)
                step.result = result
                
                if result.success:
                    step.status = TaskStatus.COMPLETED
                    print(f"   ✅ {result.message}")
                else:
                    step.status = TaskStatus.FAILED
                    step.error = result.message
                    print(f"   ❌ {result.message}")
                    
                    # Stop on failure
                    task.status = TaskStatus.FAILED
                    break
                
                if self.on_step_complete:
                    await self.on_step_complete(task, step)
            
            except Exception as e:
                step.status = TaskStatus.FAILED
                step.error = str(e)
                task.status = TaskStatus.FAILED
                print(f"   ❌ Error: {e}")
                break
            
            # Small delay between steps for visibility
            await asyncio.sleep(0.5)
        
        # Task completed
        if task.status == TaskStatus.IN_PROGRESS:
            task.status = TaskStatus.COMPLETED
        
        task.completed_at = datetime.now()
        
        if self.on_task_complete:
            await self.on_task_complete(task)
        
        status_emoji = "✅" if task.status == TaskStatus.COMPLETED else "❌"
        print(f"\n{status_emoji} Task {task.id} {task.status.value}")
    
    async def _execute_step(self, step: TaskStep) -> ActionResult:
        """Execute a single step"""
        
        action = step.action
        params = step.parameters
        
        # Special handling for approval steps
        if action == "confirm_with_approval":
            return await self._handle_approval_step(step)
        
        # Map action to browser method
        action_map = {
            "login": lambda: self.browser.login(
                params.get("username", "demo_user"),
                params.get("password", "demo123")
            ),
            "check_balance": self.browser.check_balance,
            "navigate_to_pay_bills": self.browser.navigate_to_pay_bills,
            "pay_bill": lambda: self.browser.pay_bill(
                params.get("biller"),
                params.get("consumer_number"),
                params.get("amount")
            ),
            "navigate_to_fund_transfer": self.browser.navigate_to_fund_transfer,
            "select_beneficiary": lambda: self.browser.select_beneficiary(params.get("name")),
            "fund_transfer": lambda: self.browser.fund_transfer(
                params.get("recipient"),
                params.get("account"),
                params.get("ifsc"),
                params.get("amount")
            ),
            "navigate_to_buy_gold": self.browser.navigate_to_buy_gold,
            "buy_gold": lambda: self.browser.buy_gold(
                params.get("amount"),
                params.get("grams")
            ),
            "view_transactions": self.browser.view_transactions,
            "confirm_action": self.browser.confirm_action,
            "cancel_action": self.browser.cancel_action,
            "go_back": self.browser.go_back_to_dashboard,
            "dismiss_modal": self.browser.dismiss_modal
        }
        
        if action in action_map:
            return await action_map[action]()
        
        return ActionResult(
            success=False,
            action=action,
            message=f"Unknown action: {action}"
        )
    
    async def _handle_approval_step(self, step: TaskStep) -> ActionResult:
        """Handle step that requires user approval"""
        
        parent_action = step.parameters.get("parent_action", "unknown")
        
        # Get screenshot for approval
        screenshot = await self.browser.take_screenshot()
        
        # Request approval
        request = await self.conscious_pause.request_approval(
            action=parent_action,
            parameters=step.parameters,
            screenshot=screenshot
        )
        
        step.status = TaskStatus.AWAITING_APPROVAL
        
        if self.on_approval_needed:
            await self.on_approval_needed(request)
        
        # Wait for approval
        status = await self.conscious_pause.wait_for_approval(request)
        
        if status == ApprovalStatus.APPROVED:
            # Proceed with confirmation
            return await self.browser.confirm_action()
        
        elif status == ApprovalStatus.REJECTED:
            await self.browser.cancel_action()
            return ActionResult(
                success=False,
                action="confirm_with_approval",
                message="Action rejected by user"
            )
        
        else:  # TIMEOUT
            await self.browser.cancel_action()
            return ActionResult(
                success=False,
                action="confirm_with_approval",
                message="Approval timeout - action cancelled for safety"
            )
    
    def _create_failed_task(self, command: str, error: str) -> Task:
        """Create a failed task for error reporting"""
        
        self._task_counter += 1
        task = Task(
            id=f"TASK-{self._task_counter:04d}",
            original_command=command,
            status=TaskStatus.FAILED
        )
        task.steps = [TaskStep(
            id=1,
            action="error",
            parameters={},
            status=TaskStatus.FAILED,
            error=error
        )]
        self.tasks[task.id] = task
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks"""
        return [t.to_dict() for t in self.tasks.values()]
