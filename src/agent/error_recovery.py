"""
Error Recovery System - Intelligent retry and recovery mechanisms

Implements the 3-tier error handling strategy:
- Tier 1: Automatic Recovery (retry, re-screenshot, wait)
- Tier 2: User Intervention (invalid input, CAPTCHA, OTP)
- Tier 3: Graceful Abort (unrecoverable errors)
"""

import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class ErrorTier(Enum):
    TIER_1_AUTO = "auto_recovery"
    TIER_2_USER = "user_intervention"
    TIER_3_ABORT = "graceful_abort"


class ErrorType(Enum):
    # Tier 1 - Auto-recoverable
    SLOW_LOAD = "slow_load"
    ELEMENT_NOT_FOUND = "element_not_found"
    POPUP_INTERRUPT = "popup_interrupt"
    SESSION_TIMEOUT = "session_timeout"
    NETWORK_ERROR = "network_error"
    
    # Tier 2 - Needs user
    INVALID_AMOUNT = "invalid_amount"
    INSUFFICIENT_BALANCE = "insufficient_balance"
    CAPTCHA_REQUIRED = "captcha_required"
    OTP_REQUIRED = "otp_required"
    VERIFICATION_NEEDED = "verification_needed"
    
    # Tier 3 - Must abort
    ACCOUNT_LOCKED = "account_locked"
    SECURITY_BLOCK = "security_block"
    CRITICAL_FAILURE = "critical_failure"
    MAX_RETRIES_EXCEEDED = "max_retries_exceeded"


@dataclass
class RecoveryAttempt:
    """Track recovery attempts"""
    error_type: ErrorType
    attempt_number: int
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = False
    message: str = ""


@dataclass 
class ErrorContext:
    """Context for error handling"""
    error_type: ErrorType
    tier: ErrorTier
    message: str
    action: str
    screenshot: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    can_recover: bool = True
    user_message: Optional[str] = None


class ErrorRecovery:
    """
    Intelligent error recovery system
    
    Uses vision AI to understand errors and determine best recovery strategy
    """
    
    def __init__(self, browser=None, vision=None):
        self.browser = browser
        self.vision = vision
        self.recovery_history: list[RecoveryAttempt] = []
        self.on_user_intervention: Optional[Callable[[str], Awaitable[str]]] = None
        
        # Error classification rules
        self.error_keywords = {
            ErrorType.SLOW_LOAD: ["timeout", "loading", "slow", "network"],
            ErrorType.ELEMENT_NOT_FOUND: ["not found", "element", "selector", "locate"],
            ErrorType.POPUP_INTERRUPT: ["popup", "modal", "dialog", "overlay"],
            ErrorType.SESSION_TIMEOUT: ["session", "expired", "login", "authenticate"],
            ErrorType.INVALID_AMOUNT: ["invalid", "amount", "format", "number"],
            ErrorType.INSUFFICIENT_BALANCE: ["insufficient", "balance", "funds", "low"],
            ErrorType.CAPTCHA_REQUIRED: ["captcha", "verify", "robot", "human"],
            ErrorType.OTP_REQUIRED: ["otp", "verification code", "sms", "2fa"],
            ErrorType.ACCOUNT_LOCKED: ["locked", "blocked", "suspended", "disabled"],
            ErrorType.SECURITY_BLOCK: ["security", "fraud", "suspicious", "unusual"],
        }
        
        # Tier mappings
        self.error_tiers = {
            ErrorType.SLOW_LOAD: ErrorTier.TIER_1_AUTO,
            ErrorType.ELEMENT_NOT_FOUND: ErrorTier.TIER_1_AUTO,
            ErrorType.POPUP_INTERRUPT: ErrorTier.TIER_1_AUTO,
            ErrorType.SESSION_TIMEOUT: ErrorTier.TIER_1_AUTO,
            ErrorType.NETWORK_ERROR: ErrorTier.TIER_1_AUTO,
            ErrorType.INVALID_AMOUNT: ErrorTier.TIER_2_USER,
            ErrorType.INSUFFICIENT_BALANCE: ErrorTier.TIER_2_USER,
            ErrorType.CAPTCHA_REQUIRED: ErrorTier.TIER_2_USER,
            ErrorType.OTP_REQUIRED: ErrorTier.TIER_2_USER,
            ErrorType.VERIFICATION_NEEDED: ErrorTier.TIER_2_USER,
            ErrorType.ACCOUNT_LOCKED: ErrorTier.TIER_3_ABORT,
            ErrorType.SECURITY_BLOCK: ErrorTier.TIER_3_ABORT,
            ErrorType.CRITICAL_FAILURE: ErrorTier.TIER_3_ABORT,
            ErrorType.MAX_RETRIES_EXCEEDED: ErrorTier.TIER_3_ABORT,
        }
    
    def classify_error(self, error_message: str, action: str = "") -> ErrorContext:
        """Classify an error and determine recovery strategy"""
        
        error_lower = error_message.lower()
        
        # Find matching error type
        detected_type = ErrorType.CRITICAL_FAILURE
        max_matches = 0
        
        for error_type, keywords in self.error_keywords.items():
            matches = sum(1 for kw in keywords if kw in error_lower)
            if matches > max_matches:
                max_matches = matches
                detected_type = error_type
        
        tier = self.error_tiers.get(detected_type, ErrorTier.TIER_3_ABORT)
        
        return ErrorContext(
            error_type=detected_type,
            tier=tier,
            message=error_message,
            action=action,
            can_recover=tier != ErrorTier.TIER_3_ABORT
        )
    
    async def attempt_recovery(
        self,
        context: ErrorContext,
        retry_action: Callable[[], Awaitable[Any]]
    ) -> tuple[bool, Any]:
        """
        Attempt to recover from an error
        
        Args:
            context: Error context with classification
            retry_action: Async function to retry
            
        Returns:
            (success: bool, result: Any)
        """
        
        print(f"\n🔧 Error Recovery: {context.error_type.value}")
        print(f"   Tier: {context.tier.value}")
        print(f"   Attempt: {context.retry_count + 1}/{context.max_retries}")
        
        if context.tier == ErrorTier.TIER_3_ABORT:
            print("   ❌ Unrecoverable error - aborting")
            return False, None
        
        if context.retry_count >= context.max_retries:
            print("   ❌ Max retries exceeded")
            context.error_type = ErrorType.MAX_RETRIES_EXCEEDED
            context.tier = ErrorTier.TIER_3_ABORT
            return False, None
        
        # Tier 1: Automatic recovery
        if context.tier == ErrorTier.TIER_1_AUTO:
            return await self._tier1_recovery(context, retry_action)
        
        # Tier 2: User intervention needed
        if context.tier == ErrorTier.TIER_2_USER:
            return await self._tier2_recovery(context, retry_action)
        
        return False, None
    
    async def _tier1_recovery(
        self,
        context: ErrorContext,
        retry_action: Callable
    ) -> tuple[bool, Any]:
        """Tier 1: Automatic recovery strategies"""
        
        error_type = context.error_type
        
        if error_type == ErrorType.SLOW_LOAD:
            print("   🔄 Waiting for page to load...")
            await asyncio.sleep(3)
        
        elif error_type == ErrorType.ELEMENT_NOT_FOUND:
            print("   🔄 Re-analyzing page with vision...")
            await asyncio.sleep(1)
            
            # Use vision to find alternative element
            if self.vision and self.browser:
                screenshot = await self.browser.take_screenshot()
                analysis = await self.vision.analyze_page(screenshot)
                print(f"   👁️ Page type: {analysis.page_type}")
                print(f"   👁️ Found elements: {len(analysis.elements)}")
        
        elif error_type == ErrorType.POPUP_INTERRUPT:
            print("   🔄 Attempting to dismiss popup...")
            if self.browser:
                try:
                    # Try common dismiss actions
                    await self.browser.dismiss_modal()
                except:
                    pass
        
        elif error_type == ErrorType.SESSION_TIMEOUT:
            print("   🔄 Session expired, re-authenticating...")
            if self.browser:
                try:
                    await self.browser.login()
                except:
                    pass
        
        elif error_type == ErrorType.NETWORK_ERROR:
            print("   🔄 Network issue, waiting and retrying...")
            await asyncio.sleep(5)
        
        # Attempt retry
        try:
            context.retry_count += 1
            result = await retry_action()
            
            self.recovery_history.append(RecoveryAttempt(
                error_type=error_type,
                attempt_number=context.retry_count,
                success=True,
                message="Recovery successful"
            ))
            
            print("   ✅ Recovery successful!")
            return True, result
        
        except Exception as e:
            self.recovery_history.append(RecoveryAttempt(
                error_type=error_type,
                attempt_number=context.retry_count,
                success=False,
                message=str(e)
            ))
            print(f"   ⚠️ Retry failed: {e}")
            return False, None
    
    async def _tier2_recovery(
        self,
        context: ErrorContext,
        retry_action: Callable
    ) -> tuple[bool, Any]:
        """Tier 2: User intervention required"""
        
        error_type = context.error_type
        
        # Generate user-friendly message
        user_messages = {
            ErrorType.INVALID_AMOUNT: "Please enter a valid amount",
            ErrorType.INSUFFICIENT_BALANCE: "Insufficient balance. Would you like to proceed with a smaller amount?",
            ErrorType.CAPTCHA_REQUIRED: "Please solve the CAPTCHA shown on screen",
            ErrorType.OTP_REQUIRED: "Please enter the OTP sent to your phone",
            ErrorType.VERIFICATION_NEEDED: "Additional verification required. Please check the screen.",
        }
        
        context.user_message = user_messages.get(
            error_type, 
            f"User intervention needed: {context.message}"
        )
        
        print(f"   👤 {context.user_message}")
        
        # Request user input if callback is set
        if self.on_user_intervention:
            try:
                user_response = await self.on_user_intervention(context.user_message)
                
                if user_response:
                    print(f"   👤 User response received")
                    # Retry with user input
                    context.retry_count += 1
                    result = await retry_action()
                    return True, result
            except Exception as e:
                print(f"   ❌ User intervention failed: {e}")
        
        return False, None
    
    async def with_recovery(
        self,
        action: Callable[[], Awaitable[Any]],
        action_name: str = "action",
        max_retries: int = 3
    ) -> tuple[bool, Any]:
        """
        Execute an action with automatic error recovery
        
        Usage:
            success, result = await recovery.with_recovery(
                lambda: browser.click_button("Submit"),
                "submit_form"
            )
        """
        
        retry_count = 0
        last_error = None
        
        while retry_count <= max_retries:
            try:
                result = await action()
                return True, result
            
            except Exception as e:
                last_error = str(e)
                context = self.classify_error(last_error, action_name)
                context.retry_count = retry_count
                context.max_retries = max_retries
                
                success, recovered_result = await self.attempt_recovery(
                    context,
                    action
                )
                
                if success:
                    return True, recovered_result
                
                if context.tier == ErrorTier.TIER_3_ABORT:
                    break
                
                retry_count += 1
        
        print(f"   ❌ All recovery attempts failed: {last_error}")
        return False, None
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """Get recovery statistics"""
        
        total = len(self.recovery_history)
        successful = sum(1 for r in self.recovery_history if r.success)
        
        by_type = {}
        for r in self.recovery_history:
            key = r.error_type.value
            if key not in by_type:
                by_type[key] = {"total": 0, "success": 0}
            by_type[key]["total"] += 1
            if r.success:
                by_type[key]["success"] += 1
        
        return {
            "total_attempts": total,
            "successful": successful,
            "success_rate": successful / total if total > 0 else 0,
            "by_error_type": by_type
        }


# Singleton instance
error_recovery = ErrorRecovery()


# Convenience decorator
def with_error_recovery(max_retries: int = 3):
    """Decorator for adding error recovery to async functions"""
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await error_recovery.with_recovery(
                lambda: func(*args, **kwargs),
                action_name=func.__name__,
                max_retries=max_retries
            )
        return wrapper
    return decorator
