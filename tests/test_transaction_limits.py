"""
Unit Tests for Transaction Limits

Tests transaction limit enforcement functionality
"""

import pytest
from datetime import datetime, timedelta
from src.agent.transaction_limits import (
    TransactionLimits,
    LimitConfig,
    LimitCheckResult,
    LimitType,
    check_transaction_limit,
    record_transaction
)


class TestTransactionLimits:
    """Test suite for TransactionLimits"""
    
    @pytest.fixture
    def limits(self):
        """Create fresh TransactionLimits instance"""
        return TransactionLimits()
    
    # ============ Single Transaction Limit Tests ============
    
    def test_single_limit_allowed(self, limits):
        """Test transaction within single limit"""
        result = limits.check_limit("pay_bill", 10000)
        
        assert result.allowed == True
        assert result.limit_type == LimitType.SINGLE
    
    def test_single_limit_exceeded(self, limits):
        """Test transaction exceeding single limit"""
        result = limits.check_limit("pay_bill", 100000)  # Limit is 50000
        
        assert result.allowed == False
        assert result.limit_type == LimitType.SINGLE
        assert "exceeds single transaction limit" in result.reason
    
    def test_single_limit_exact(self, limits):
        """Test transaction at exact limit"""
        result = limits.check_limit("pay_bill", 50000)  # Exact limit
        
        assert result.allowed == True
    
    # ============ Daily Limit Tests ============
    
    def test_daily_limit_tracking(self, limits):
        """Test daily limit accumulation"""
        # First transaction (within single limit of 50000)
        limits.record_transaction("pay_bill", 50000, success=True)
        limits.record_transaction("pay_bill", 50000, success=True)
        limits.record_transaction("pay_bill", 50000, success=True)
        
        # Used 150000 of 200000 daily limit, next 50000 still allowed
        result = limits.check_limit("pay_bill", 50000)
        assert result.allowed == True
        
        # But exceed daily limit
        limits.record_transaction("pay_bill", 50000, success=True)  # Now at 200000
        result = limits.check_limit("pay_bill", 10000)
        
        assert result.allowed == False
        assert result.limit_type == LimitType.DAILY
    
    def test_daily_limit_multiple_transactions(self, limits):
        """Test multiple transactions within daily limit"""
        limits.record_transaction("pay_bill", 40000, success=True)
        limits.record_transaction("pay_bill", 40000, success=True)
        limits.record_transaction("pay_bill", 40000, success=True)
        
        # Should have used 120000 of 200000 daily limit
        result = limits.check_limit("pay_bill", 40000)
        
        assert result.allowed == True
    
    def test_daily_limit_exceeded_cumulative(self, limits):
        """Test cumulative daily limit exceeded"""
        limits.record_transaction("pay_bill", 40000, success=True)
        limits.record_transaction("pay_bill", 40000, success=True)
        limits.record_transaction("pay_bill", 40000, success=True)
        limits.record_transaction("pay_bill", 40000, success=True)
        limits.record_transaction("pay_bill", 40000, success=True)
        
        # Used 200000, at limit
        result = limits.check_limit("pay_bill", 10000)
        
        assert result.allowed == False
        assert result.limit_type == LimitType.DAILY
    
    # ============ Failed Transactions ============
    
    def test_failed_transactions_not_counted(self, limits):
        """Test that failed transactions don't count toward limits"""
        limits.record_transaction("pay_bill", 190000, success=False)
        
        # This should still be allowed since previous failed
        result = limits.check_limit("pay_bill", 40000)
        
        assert result.allowed == True
    
    # ============ 2FA Threshold Tests ============
    
    def test_2fa_not_required_below_threshold(self, limits):
        """Test 2FA not required for small amounts"""
        result = limits.check_limit("pay_bill", 10000)  # Below 25000 threshold
        
        assert result.allowed == True
        assert result.requires_2fa == False
    
    def test_2fa_required_above_threshold(self, limits):
        """Test 2FA required for large amounts"""
        result = limits.check_limit("pay_bill", 30000)  # Above 25000 threshold
        
        assert result.allowed == True
        assert result.requires_2fa == True
    
    # ============ Unknown Action Tests ============
    
    def test_unknown_action_allowed(self, limits):
        """Test unknown action has no limits"""
        result = limits.check_limit("unknown_action", 1000000)
        
        assert result.allowed == True
    
    # ============ Remaining Limits Tests ============
    
    def test_get_remaining_limits(self, limits):
        """Test remaining limits calculation"""
        limits.record_transaction("pay_bill", 50000, success=True)
        
        remaining = limits.get_remaining_limits("pay_bill")
        
        assert remaining["daily_remaining"] == 150000  # 200000 - 50000
        assert remaining["single"] == 50000  # Single limit unchanged
    
    def test_get_usage_summary(self, limits):
        """Test usage summary"""
        limits.record_transaction("pay_bill", 50000, success=True)
        
        summary = limits.get_usage_summary("pay_bill")
        
        assert summary["usage"]["daily"] == 50000
        assert summary["remaining"]["daily"] == 150000
        assert summary["utilization"]["daily"] == 25.0
    
    # ============ Custom Limits Tests ============
    
    def test_custom_limit_config(self, limits):
        """Test custom limit configuration"""
        custom_config = LimitConfig(
            single_limit=5000,
            daily_limit=20000,
            requires_2fa_above=2000
        )
        limits.set_custom_limit("custom_action", custom_config)
        
        result = limits.check_limit("custom_action", 6000)
        
        assert result.allowed == False
        assert "exceeds single transaction limit" in result.reason
    
    # ============ Format Message Tests ============
    
    def test_format_allowed_message(self, limits):
        """Test formatting allowed transaction message"""
        result = limits.check_limit("pay_bill", 10000)
        message = limits.format_limit_message(result)
        
        assert "✅" in message
        assert "allowed" in message.lower()
    
    def test_format_denied_message(self, limits):
        """Test formatting denied transaction message"""
        result = limits.check_limit("pay_bill", 100000)
        message = limits.format_limit_message(result)
        
        assert "❌" in message
    
    def test_format_2fa_message(self, limits):
        """Test 2FA warning in message"""
        result = limits.check_limit("pay_bill", 30000)
        message = limits.format_limit_message(result)
        
        assert "2FA" in message
    
    # ============ Reset Tests ============
    
    def test_reset_daily_usage(self, limits):
        """Test resetting daily usage"""
        limits.record_transaction("pay_bill", 50000, success=True)
        limits.record_transaction("pay_bill", 50000, success=True)
        limits.record_transaction("pay_bill", 50000, success=True)
        limits.record_transaction("pay_bill", 50000, success=True)  # At 200000 daily limit
        
        # Verify limit reached
        result = limits.check_limit("pay_bill", 10000)
        assert result.allowed == False
        
        # Reset daily usage
        limits.reset_daily_usage("pay_bill")
        
        # Now should be allowed again
        result = limits.check_limit("pay_bill", 50000)
        
        assert result.allowed == True


class TestFundTransferLimits:
    """Test fund transfer specific limits"""
    
    @pytest.fixture
    def limits(self):
        return TransactionLimits()
    
    def test_fund_transfer_single_limit(self, limits):
        """Test fund transfer has higher single limit"""
        result = limits.check_limit("fund_transfer", 80000)  # Limit is 100000
        
        assert result.allowed == True
    
    def test_fund_transfer_2fa_threshold(self, limits):
        """Test fund transfer 2FA threshold is 50000"""
        result_below = limits.check_limit("fund_transfer", 40000)
        result_above = limits.check_limit("fund_transfer", 60000)
        
        assert result_below.requires_2fa == False
        assert result_above.requires_2fa == True


class TestBuyGoldLimits:
    """Test gold purchase specific limits"""
    
    @pytest.fixture
    def limits(self):
        return TransactionLimits()
    
    def test_buy_gold_limits(self, limits):
        """Test gold purchase limits"""
        result = limits.check_limit("buy_gold", 80000)  # Limit is 100000
        
        assert result.allowed == True
    
    def test_buy_gold_exceed(self, limits):
        """Test gold purchase exceeds limit"""
        result = limits.check_limit("buy_gold", 150000)  # Above 100000 limit
        
        assert result.allowed == False


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
