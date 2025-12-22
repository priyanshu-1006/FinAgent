"""
Unit Tests for User-Friendly Errors

Tests error translation functionality
"""

import pytest
from src.agent.user_errors import (
    UserFriendlyErrors,
    UserError,
    ErrorCategory,
    translate_error,
    format_error,
    is_recoverable,
    should_retry
)


class TestUserFriendlyErrors:
    """Test suite for UserFriendlyErrors"""
    
    # ============ Timeout Errors ============
    
    def test_timeout_error(self):
        """Test timeout error translation"""
        error = translate_error("Page.wait_for_selector: Timeout 3000ms exceeded")
        
        assert error.category == ErrorCategory.TIMEOUT
        assert "took too long" in error.message
        assert error.recoverable == True
        assert error.retry_allowed == True
    
    # ============ Network Errors ============
    
    def test_network_error(self):
        """Test network error translation"""
        error = translate_error("net::ERR_CONNECTION_REFUSED")
        
        assert error.category == ErrorCategory.NETWORK
        assert "connect" in error.message.lower() or "server" in error.message.lower()
    
    def test_connection_refused(self):
        """Test connection refused error"""
        error = translate_error("Connection refused to localhost:8080")
        
        assert error.category == ErrorCategory.NETWORK
        assert error.recoverable == True
    
    # ============ API Quota Errors ============
    
    def test_quota_error(self):
        """Test API quota error"""
        error = translate_error("Resource exhausted: Quota exceeded for gemini-1.5-flash")
        
        assert error.category == ErrorCategory.API_QUOTA
        assert "temporarily" in error.message.lower() or "unavailable" in error.message.lower()
    
    def test_rate_limit_error(self):
        """Test rate limit error"""
        error = translate_error("Rate limit exceeded. Please slow down.")
        
        assert error.category == ErrorCategory.API_QUOTA
        assert error.retry_allowed == True
    
    def test_429_error(self):
        """Test HTTP 429 error"""
        error = translate_error("HTTP Error 429: Too Many Requests")
        
        assert error.category == ErrorCategory.API_QUOTA
    
    # ============ Element Not Found Errors ============
    
    def test_element_not_found(self):
        """Test element not found error"""
        error = translate_error("Element not found: #login-button")
        
        assert error.category == ErrorCategory.ELEMENT_NOT_FOUND
        assert "find" in error.message.lower() or "locate" in error.message.lower()
    
    def test_selector_error(self):
        """Test selector error"""
        error = translate_error("Selector '#pay-btn' not visible")
        
        assert error.category == ErrorCategory.ELEMENT_NOT_FOUND
    
    # ============ Authentication Errors ============
    
    def test_login_failed(self):
        """Test login failed error"""
        error = translate_error("Login failed: Invalid credentials")
        
        assert error.category == ErrorCategory.AUTHENTICATION
        assert "unsuccessful" in error.message.lower() or "login" in error.message.lower()
    
    def test_session_expired(self):
        """Test session expired error"""
        error = translate_error("Session expired. Please login again.")
        
        assert error.category == ErrorCategory.AUTHENTICATION
    
    def test_unauthorized_error(self):
        """Test unauthorized error"""
        error = translate_error("Unauthorized access to resource")
        
        assert error.category == ErrorCategory.AUTHORIZATION
        assert error.retry_allowed == False  # Auth errors shouldn't auto-retry
    
    def test_403_error(self):
        """Test HTTP 403 error"""
        error = translate_error("HTTP Error 403: Forbidden")
        
        assert error.category == ErrorCategory.AUTHORIZATION
    
    # ============ Transaction Errors ============
    
    def test_insufficient_balance(self):
        """Test insufficient balance error"""
        error = translate_error("Transaction failed: Insufficient balance")
        
        assert error.category == ErrorCategory.TRANSACTION
        assert "balance" in error.message.lower()
    
    def test_limit_exceeded(self):
        """Test limit exceeded error"""
        error = translate_error("Daily transaction limit exceeded")
        
        assert error.category == ErrorCategory.TRANSACTION
    
    # ============ Validation Errors ============
    
    def test_invalid_amount(self):
        """Test invalid amount error"""
        error = translate_error("Validation error: Invalid amount entered")
        
        assert error.category == ErrorCategory.VALIDATION
        assert error.retry_allowed == False  # Validation errors need user input
    
    def test_minimum_amount(self):
        """Test minimum amount error"""
        error = translate_error("Minimum amount required is Rs 100")
        
        assert error.category == ErrorCategory.VALIDATION
    
    # ============ Browser Errors ============
    
    def test_browser_error(self):
        """Test browser error"""
        error = translate_error("Browser instance crashed unexpectedly")
        
        assert error.category == ErrorCategory.BROWSER
    
    def test_playwright_error(self):
        """Test Playwright error"""
        error = translate_error("Playwright: Context closed")
        
        assert error.category == ErrorCategory.BROWSER
    
    # ============ Unknown Errors ============
    
    def test_unknown_error(self):
        """Test unknown error handling"""
        error = translate_error("Some random unexpected error xyz123")
        
        assert error.category == ErrorCategory.UNKNOWN
        assert "went wrong" in error.message.lower()
        assert error.recoverable == True
    
    # ============ Fatal Errors ============
    
    def test_fatal_error(self):
        """Test fatal error detection"""
        error = translate_error("Fatal system error: Database connection lost")
        
        assert error.recoverable == False
    
    def test_critical_error(self):
        """Test critical error detection"""
        error = translate_error("Critical failure in core module")
        
        assert error.recoverable == False
    
    # ============ Format Tests ============
    
    def test_format_for_display(self):
        """Test error formatting"""
        error = translate_error("Timeout exceeded")
        formatted = UserFriendlyErrors.format_for_display(error)
        
        assert "❌" in formatted
        assert "💡" in formatted
    
    def test_format_with_technical(self):
        """Test formatting with technical details"""
        error = translate_error("Timeout exceeded")
        formatted = UserFriendlyErrors.format_for_display(error, show_technical=True)
        
        assert "📋" in formatted
        assert "Timeout" in formatted
    
    def test_format_without_retry(self):
        """Test formatting for non-retryable error"""
        error = translate_error("Validation error: Invalid amount")
        formatted = UserFriendlyErrors.format_for_display(error)
        
        # Validation errors shouldn't show retry message
        assert "🔄 You can try again" not in formatted
    
    # ============ Retry Message Tests ============
    
    def test_retry_message(self):
        """Test retry status message"""
        error = translate_error("Timeout exceeded")
        message = UserFriendlyErrors.get_retry_message(error, attempt=1, max_attempts=3)
        
        assert "Retrying" in message
        assert "2/3" in message
    
    def test_retry_message_max_reached(self):
        """Test max retries message"""
        error = translate_error("Timeout exceeded")
        message = UserFriendlyErrors.get_retry_message(error, attempt=3, max_attempts=3)
        
        assert "Maximum" in message
    
    # ============ Convenience Function Tests ============
    
    def test_is_recoverable_function(self):
        """Test is_recoverable convenience function"""
        assert is_recoverable("Timeout exceeded") == True
        assert is_recoverable("Fatal system failure") == False
    
    def test_should_retry_function(self):
        """Test should_retry convenience function"""
        assert should_retry("Timeout exceeded") == True
        assert should_retry("Validation error") == False
    
    def test_format_error_function(self):
        """Test format_error convenience function"""
        formatted = format_error("Timeout exceeded")
        
        assert isinstance(formatted, str)
        assert len(formatted) > 0


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
