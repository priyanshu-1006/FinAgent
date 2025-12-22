"""
Transaction Limits - Safety Controls for Financial Operations

Implements transaction limits for security:
- Single transaction limits
- Daily transaction limits
- Per-action limit configuration
- Real-time limit tracking
"""

from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class LimitType(Enum):
    """Types of transaction limits"""
    SINGLE = "single"       # Per-transaction limit
    DAILY = "daily"         # Daily cumulative limit
    WEEKLY = "weekly"       # Weekly cumulative limit
    MONTHLY = "monthly"     # Monthly cumulative limit


@dataclass
class LimitConfig:
    """Configuration for a transaction limit"""
    single_limit: float
    daily_limit: float
    weekly_limit: Optional[float] = None
    monthly_limit: Optional[float] = None
    requires_2fa_above: Optional[float] = None  # Threshold for 2FA
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "single_limit": self.single_limit,
            "daily_limit": self.daily_limit,
            "weekly_limit": self.weekly_limit,
            "monthly_limit": self.monthly_limit,
            "requires_2fa_above": self.requires_2fa_above
        }


@dataclass
class TransactionRecord:
    """Record of a completed transaction"""
    action: str
    amount: float
    timestamp: datetime
    success: bool
    
    
@dataclass
class LimitCheckResult:
    """Result of a limit check"""
    allowed: bool
    reason: Optional[str] = None
    limit_type: Optional[LimitType] = None
    limit_value: Optional[float] = None
    current_usage: Optional[float] = None
    remaining: Optional[float] = None
    requires_2fa: bool = False


class TransactionLimits:
    """
    Transaction limit enforcement
    
    Features:
    - Configurable per-action limits
    - Daily/weekly/monthly tracking
    - 2FA threshold support
    - Real-time usage tracking
    """
    
    # Default limits per action type (in INR)
    DEFAULT_LIMITS: Dict[str, LimitConfig] = {
        "pay_bill": LimitConfig(
            single_limit=50000,
            daily_limit=200000,
            weekly_limit=500000,
            monthly_limit=1000000,
            requires_2fa_above=25000
        ),
        "fund_transfer": LimitConfig(
            single_limit=100000,
            daily_limit=500000,
            weekly_limit=1000000,
            monthly_limit=2000000,
            requires_2fa_above=50000
        ),
        "buy_gold": LimitConfig(
            single_limit=100000,
            daily_limit=200000,
            weekly_limit=500000,
            monthly_limit=1000000,
            requires_2fa_above=25000
        ),
        "update_profile": LimitConfig(
            single_limit=0,  # No monetary limit
            daily_limit=0,
            requires_2fa_above=0  # Always require approval
        )
    }
    
    def __init__(self, custom_limits: Optional[Dict[str, LimitConfig]] = None):
        """
        Initialize transaction limits
        
        Args:
            custom_limits: Override default limits with custom configuration
        """
        self.limits = {**self.DEFAULT_LIMITS}
        if custom_limits:
            self.limits.update(custom_limits)
        
        # Transaction history for tracking usage
        self.transactions: List[TransactionRecord] = []
    
    def check_limit(self, action: str, amount: float) -> LimitCheckResult:
        """
        Check if a transaction is within limits
        
        Args:
            action: Type of action (pay_bill, fund_transfer, etc.)
            amount: Transaction amount
            
        Returns:
            LimitCheckResult with allowed status and details
        """
        if action not in self.limits:
            # No limits configured for this action
            return LimitCheckResult(allowed=True)
        
        config = self.limits[action]
        
        # Check single transaction limit
        if config.single_limit > 0 and amount > config.single_limit:
            return LimitCheckResult(
                allowed=False,
                reason=f"Amount ₹{amount:,.2f} exceeds single transaction limit of ₹{config.single_limit:,.2f}",
                limit_type=LimitType.SINGLE,
                limit_value=config.single_limit,
                current_usage=amount,
                remaining=0
            )
        
        # Check daily limit
        if config.daily_limit > 0:
            daily_usage = self._get_usage(action, "daily")
            if daily_usage + amount > config.daily_limit:
                return LimitCheckResult(
                    allowed=False,
                    reason=f"Daily limit would be exceeded. Used: ₹{daily_usage:,.2f}, Limit: ₹{config.daily_limit:,.2f}",
                    limit_type=LimitType.DAILY,
                    limit_value=config.daily_limit,
                    current_usage=daily_usage,
                    remaining=max(0, config.daily_limit - daily_usage)
                )
        
        # Check weekly limit
        if config.weekly_limit and config.weekly_limit > 0:
            weekly_usage = self._get_usage(action, "weekly")
            if weekly_usage + amount > config.weekly_limit:
                return LimitCheckResult(
                    allowed=False,
                    reason=f"Weekly limit would be exceeded. Used: ₹{weekly_usage:,.2f}, Limit: ₹{config.weekly_limit:,.2f}",
                    limit_type=LimitType.WEEKLY,
                    limit_value=config.weekly_limit,
                    current_usage=weekly_usage,
                    remaining=max(0, config.weekly_limit - weekly_usage)
                )
        
        # Check monthly limit
        if config.monthly_limit and config.monthly_limit > 0:
            monthly_usage = self._get_usage(action, "monthly")
            if monthly_usage + amount > config.monthly_limit:
                return LimitCheckResult(
                    allowed=False,
                    reason=f"Monthly limit would be exceeded. Used: ₹{monthly_usage:,.2f}, Limit: ₹{config.monthly_limit:,.2f}",
                    limit_type=LimitType.MONTHLY,
                    limit_value=config.monthly_limit,
                    current_usage=monthly_usage,
                    remaining=max(0, config.monthly_limit - monthly_usage)
                )
        
        # Check if 2FA is required
        requires_2fa = False
        if config.requires_2fa_above is not None and amount > config.requires_2fa_above:
            requires_2fa = True
        
        # Calculate remaining limits
        daily_remaining = config.daily_limit - self._get_usage(action, "daily") if config.daily_limit > 0 else None
        
        return LimitCheckResult(
            allowed=True,
            limit_type=LimitType.SINGLE,
            limit_value=config.single_limit,
            current_usage=self._get_usage(action, "daily"),
            remaining=daily_remaining,
            requires_2fa=requires_2fa
        )
    
    def _get_usage(self, action: str, period: str) -> float:
        """Get total usage for an action within a period"""
        now = datetime.now()
        today = now.date()
        
        total = 0.0
        for tx in self.transactions:
            if tx.action != action or not tx.success:
                continue
            
            tx_date = tx.timestamp.date()
            
            if period == "daily" and tx_date == today:
                total += tx.amount
            elif period == "weekly":
                # Check if within current week (Monday to Sunday)
                week_start = today - timedelta(days=today.weekday())
                if tx_date >= week_start:
                    total += tx.amount
            elif period == "monthly":
                if tx_date.year == today.year and tx_date.month == today.month:
                    total += tx.amount
        
        return total
    
    def record_transaction(self, action: str, amount: float, success: bool = True):
        """Record a completed transaction"""
        self.transactions.append(TransactionRecord(
            action=action,
            amount=amount,
            timestamp=datetime.now(),
            success=success
        ))
        
        # Keep only last 1000 transactions
        if len(self.transactions) > 1000:
            self.transactions = self.transactions[-1000:]
    
    def get_remaining_limits(self, action: str) -> Dict[str, float]:
        """Get remaining limits for an action"""
        if action not in self.limits:
            return {}
        
        config = self.limits[action]
        
        return {
            "single": config.single_limit,
            "daily_remaining": max(0, config.daily_limit - self._get_usage(action, "daily")) if config.daily_limit > 0 else None,
            "weekly_remaining": max(0, config.weekly_limit - self._get_usage(action, "weekly")) if config.weekly_limit else None,
            "monthly_remaining": max(0, config.monthly_limit - self._get_usage(action, "monthly")) if config.monthly_limit else None
        }
    
    def get_usage_summary(self, action: str) -> Dict[str, Any]:
        """Get usage summary for an action"""
        if action not in self.limits:
            return {}
        
        config = self.limits[action]
        daily_usage = self._get_usage(action, "daily")
        weekly_usage = self._get_usage(action, "weekly")
        monthly_usage = self._get_usage(action, "monthly")
        
        return {
            "action": action,
            "limits": config.to_dict(),
            "usage": {
                "daily": daily_usage,
                "weekly": weekly_usage,
                "monthly": monthly_usage
            },
            "remaining": {
                "daily": max(0, config.daily_limit - daily_usage) if config.daily_limit > 0 else None,
                "weekly": max(0, config.weekly_limit - weekly_usage) if config.weekly_limit else None,
                "monthly": max(0, config.monthly_limit - monthly_usage) if config.monthly_limit else None
            },
            "utilization": {
                "daily": (daily_usage / config.daily_limit * 100) if config.daily_limit > 0 else 0,
                "weekly": (weekly_usage / config.weekly_limit * 100) if config.weekly_limit else 0,
                "monthly": (monthly_usage / config.monthly_limit * 100) if config.monthly_limit else 0
            }
        }
    
    def format_limit_message(self, result: LimitCheckResult) -> str:
        """Format limit check result for display"""
        if result.allowed:
            if result.requires_2fa:
                return f"✅ Transaction allowed (₹{result.remaining:,.2f} remaining today). ⚠️ 2FA required for this amount."
            return f"✅ Transaction allowed. Remaining daily limit: ₹{result.remaining:,.2f}"
        else:
            return f"❌ {result.reason}"
    
    def set_custom_limit(self, action: str, config: LimitConfig):
        """Set custom limit for an action"""
        self.limits[action] = config
    
    def reset_daily_usage(self, action: Optional[str] = None):
        """Reset daily usage (for testing or manual reset)"""
        today = datetime.now().date()
        
        self.transactions = [
            tx for tx in self.transactions
            if tx.timestamp.date() != today or (action and tx.action != action)
        ]


# Import timedelta for usage calculation
from datetime import timedelta


# Global transaction limits instance
_transaction_limits: Optional[TransactionLimits] = None


def get_transaction_limits() -> TransactionLimits:
    """Get or create global transaction limits"""
    global _transaction_limits
    if _transaction_limits is None:
        _transaction_limits = TransactionLimits()
    return _transaction_limits


def check_transaction_limit(action: str, amount: float) -> LimitCheckResult:
    """Check if transaction is within limits"""
    return get_transaction_limits().check_limit(action, amount)


def record_transaction(action: str, amount: float, success: bool = True):
    """Record a completed transaction"""
    get_transaction_limits().record_transaction(action, amount, success)
