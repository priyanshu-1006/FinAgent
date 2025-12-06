"""
Conscious Pause - Human-in-the-loop approval mechanism

This module implements the critical safety feature:
- Pauses execution before high-risk actions
- Displays action details for user review
- Waits for explicit user approval or rejection
- Logs all approval decisions
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum

from .config import config, ACTIONS


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


@dataclass
class ApprovalRequest:
    """Request for user approval"""
    id: str
    action: str
    description: str
    parameters: Dict[str, Any]
    risk_level: str
    timestamp: datetime = field(default_factory=datetime.now)
    status: ApprovalStatus = ApprovalStatus.PENDING
    screenshot: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "action": self.action,
            "description": self.description,
            "parameters": self.parameters,
            "risk_level": self.risk_level,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value
        }


class ConciousPause:
    """Human-in-the-loop approval system"""
    
    def __init__(self):
        self.pending_requests: Dict[str, ApprovalRequest] = {}
        self.approval_history: list = []
        self.approval_callback: Optional[Callable[[ApprovalRequest], Awaitable[bool]]] = None
        self._request_counter = 0
    
    def set_approval_callback(self, callback: Callable[[ApprovalRequest], Awaitable[bool]]):
        """Set callback function for approval UI"""
        self.approval_callback = callback
    
    def requires_approval(self, action: str) -> bool:
        """Check if an action requires approval"""
        if action in ACTIONS:
            return ACTIONS[action].get("requires_approval", False)
        return action in config.require_approval_for
    
    async def request_approval(
        self,
        action: str,
        parameters: Dict[str, Any],
        screenshot: Optional[str] = None
    ) -> ApprovalRequest:
        """Create an approval request"""
        
        self._request_counter += 1
        request_id = f"APR-{self._request_counter:04d}"
        
        action_info = ACTIONS.get(action, {})
        
        request = ApprovalRequest(
            id=request_id,
            action=action,
            description=self._build_description(action, parameters),
            parameters=parameters,
            risk_level=action_info.get("risk_level", "high"),
            screenshot=screenshot
        )
        
        self.pending_requests[request_id] = request
        
        print(f"\n🔔 APPROVAL REQUIRED - {request_id}")
        print(f"   Action: {action}")
        print(f"   {request.description}")
        print(f"   Risk Level: {request.risk_level.upper()}")
        
        return request
    
    def _build_description(self, action: str, params: Dict[str, Any]) -> str:
        """Build human-readable description of the action"""
        
        if action == "pay_bill":
            biller = params.get("biller", "Unknown Biller")
            amount = params.get("amount", 0)
            return f"Pay ₹{amount:,.2f} to {biller}"
        
        elif action == "fund_transfer":
            recipient = params.get("recipient", "Unknown")
            amount = params.get("amount", 0)
            return f"Transfer ₹{amount:,.2f} to {recipient}"
        
        elif action == "buy_gold":
            if params.get("grams"):
                return f"Purchase {params['grams']:.3f} grams of Digital Gold"
            else:
                amount = params.get("amount", 0)
                return f"Purchase ₹{amount:,.2f} worth of Digital Gold"
        
        elif action == "update_profile":
            return "Update profile information"
        
        return f"Execute {action} action"
    
    async def wait_for_approval(
        self,
        request: ApprovalRequest,
        timeout: int = None
    ) -> ApprovalStatus:
        """Wait for user approval with timeout"""
        
        timeout = timeout or config.approval_timeout
        
        # If we have a UI callback, use it
        if self.approval_callback:
            try:
                approved = await asyncio.wait_for(
                    self.approval_callback(request),
                    timeout=timeout
                )
                request.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
            except asyncio.TimeoutError:
                request.status = ApprovalStatus.TIMEOUT
        else:
            # Console-based approval for testing
            request.status = await self._console_approval(request, timeout)
        
        # Move to history
        self.approval_history.append(request)
        if request.id in self.pending_requests:
            del self.pending_requests[request.id]
        
        # Log decision
        status_emoji = {
            ApprovalStatus.APPROVED: "✅",
            ApprovalStatus.REJECTED: "❌",
            ApprovalStatus.TIMEOUT: "⏰"
        }
        print(f"\n{status_emoji.get(request.status, '❓')} {request.id}: {request.status.value.upper()}")
        
        return request.status
    
    async def _console_approval(
        self,
        request: ApprovalRequest,
        timeout: int
    ) -> ApprovalStatus:
        """Console-based approval for testing"""
        
        print(f"\n{'='*50}")
        print(f"⚠️  CONSCIOUS PAUSE - ACTION REVIEW")
        print(f"{'='*50}")
        print(f"Request ID: {request.id}")
        print(f"Action: {request.action}")
        print(f"Details: {request.description}")
        print(f"Parameters: {request.parameters}")
        print(f"Risk Level: {request.risk_level.upper()}")
        print(f"{'='*50}")
        print(f"⏳ Waiting for approval (timeout: {timeout}s)...")
        print(f"   Type 'y' to APPROVE, 'n' to REJECT")
        
        # For automated testing, auto-approve after a delay
        # In production, this would be replaced by actual user input
        try:
            loop = asyncio.get_event_loop()
            
            # Try to read from stdin with timeout
            future = loop.run_in_executor(None, input, ">>> ")
            response = await asyncio.wait_for(future, timeout=timeout)
            
            if response.lower() in ['y', 'yes', 'approve', '1']:
                return ApprovalStatus.APPROVED
            elif response.lower() in ['n', 'no', 'reject', '0']:
                return ApprovalStatus.REJECTED
            else:
                print("Invalid response, defaulting to REJECT for safety")
                return ApprovalStatus.REJECTED
                
        except asyncio.TimeoutError:
            return ApprovalStatus.TIMEOUT
        except Exception as e:
            print(f"Approval error: {e}")
            return ApprovalStatus.REJECTED
    
    def approve(self, request_id: str) -> bool:
        """Manually approve a pending request"""
        if request_id in self.pending_requests:
            self.pending_requests[request_id].status = ApprovalStatus.APPROVED
            return True
        return False
    
    def reject(self, request_id: str) -> bool:
        """Manually reject a pending request"""
        if request_id in self.pending_requests:
            self.pending_requests[request_id].status = ApprovalStatus.REJECTED
            return True
        return False
    
    def get_pending_requests(self) -> list:
        """Get all pending approval requests"""
        return [r.to_dict() for r in self.pending_requests.values()]
    
    def get_approval_history(self, limit: int = 10) -> list:
        """Get recent approval history"""
        return [r.to_dict() for r in self.approval_history[-limit:]]


# Global instance
conscious_pause = ConciousPause()
