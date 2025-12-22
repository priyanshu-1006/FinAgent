"""
User-Friendly Errors - Error Translation Module

Translates technical errors into user-friendly messages.
Improves user experience by showing clear, actionable error messages.
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ErrorCategory(Enum):
    """Error categories for classification"""
    NETWORK = "network"
    TIMEOUT = "timeout"
    ELEMENT_NOT_FOUND = "element_not_found"
    API_QUOTA = "api_quota"
    API_ERROR = "api_error"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    TRANSACTION = "transaction"
    BROWSER = "browser"
    SYSTEM = "system"
    UNKNOWN = "unknown"


@dataclass
class UserError:
    """User-friendly error representation"""
    category: ErrorCategory
    message: str
    suggestion: str
    technical_details: Optional[str] = None
    recoverable: bool = True
    retry_allowed: bool = True


class UserFriendlyErrors:
    """
    Translates technical errors to user-friendly messages
    
    Features:
    - Pattern-based error detection
    - Actionable suggestions
    - Recovery guidance
    - Severity classification
    """
    
    # Error patterns and their user-friendly translations
    ERROR_PATTERNS: Dict[str, Tuple[ErrorCategory, str, str]] = {
        # Network errors
        "timeout": (
            ErrorCategory.TIMEOUT,
            "The page took too long to load.",
            "Please check your internet connection and try again."
        ),
        "net::err": (
            ErrorCategory.NETWORK,
            "Unable to connect to the server.",
            "Please check your internet connection."
        ),
        "connection refused": (
            ErrorCategory.NETWORK,
            "The server is not responding.",
            "Please make sure the banking server is running."
        ),
        "network": (
            ErrorCategory.NETWORK,
            "Network connection lost.",
            "Please check your internet and try again."
        ),
        
        # API errors
        "quota": (
            ErrorCategory.API_QUOTA,
            "Service temporarily unavailable.",
            "Please wait a moment and try again."
        ),
        "rate limit": (
            ErrorCategory.API_QUOTA,
            "Too many requests. Please slow down.",
            "Wait a few seconds before trying again."
        ),
        "429": (
            ErrorCategory.API_QUOTA,
            "Service is busy.",
            "Please try again in a few seconds."
        ),
        "api key": (
            ErrorCategory.API_ERROR,
            "Authentication with AI service failed.",
            "Please check your API key configuration."
        ),
        "invalid api": (
            ErrorCategory.API_ERROR,
            "API configuration issue.",
            "Please verify your API settings."
        ),
        
        # Element detection errors
        "element not found": (
            ErrorCategory.ELEMENT_NOT_FOUND,
            "Could not find the required button or field.",
            "The page may have changed. Try refreshing."
        ),
        "selector": (
            ErrorCategory.ELEMENT_NOT_FOUND,
            "Unable to locate the element.",
            "The page layout may have changed."
        ),
        "no such element": (
            ErrorCategory.ELEMENT_NOT_FOUND,
            "The requested element doesn't exist.",
            "Please navigate to the correct page first."
        ),
        
        # Authentication errors
        "login failed": (
            ErrorCategory.AUTHENTICATION,
            "Login was unsuccessful.",
            "Please check your username and password."
        ),
        "session expired": (
            ErrorCategory.AUTHENTICATION,
            "Your session has expired.",
            "Please log in again."
        ),
        "unauthorized": (
            ErrorCategory.AUTHORIZATION,
            "You don't have permission for this action.",
            "Please check your account permissions."
        ),
        "403": (
            ErrorCategory.AUTHORIZATION,
            "Access denied.",
            "You may not have permission for this action."
        ),
        
        # Transaction errors
        "insufficient": (
            ErrorCategory.TRANSACTION,
            "Insufficient balance for this transaction.",
            "Please add funds or reduce the amount."
        ),
        "limit exceeded": (
            ErrorCategory.TRANSACTION,
            "Transaction limit exceeded.",
            "Try a smaller amount or wait for limit reset."
        ),
        "invalid amount": (
            ErrorCategory.VALIDATION,
            "The entered amount is invalid.",
            "Please enter a valid positive amount."
        ),
        "minimum amount": (
            ErrorCategory.VALIDATION,
            "Amount is below the minimum required.",
            "Please enter a higher amount."
        ),
        "maximum amount": (
            ErrorCategory.VALIDATION,
            "Amount exceeds the maximum allowed.",
            "Please enter a smaller amount."
        ),
        
        # Browser errors
        "browser": (
            ErrorCategory.BROWSER,
            "Browser encountered an issue.",
            "Try refreshing the page."
        ),
        "playwright": (
            ErrorCategory.BROWSER,
            "Browser automation error.",
            "The browser may need to be restarted."
        ),
        "page crash": (
            ErrorCategory.BROWSER,
            "The page crashed.",
            "Please refresh and try again."
        ),
        
        # Vision/AI errors
        "vision": (
            ErrorCategory.API_ERROR,
            "Visual recognition encountered an issue.",
            "The AI may need more time. Please try again."
        ),
        "model not found": (
            ErrorCategory.API_ERROR,
            "AI model is temporarily unavailable.",
            "Switching to alternative model..."
        ),
        
        # Validation errors
        "validation": (
            ErrorCategory.VALIDATION,
            "The input provided is invalid.",
            "Please check your input and try again."
        ),
        "required field": (
            ErrorCategory.VALIDATION,
            "Required information is missing.",
            "Please fill in all required fields."
        ),
    }
    
    # Non-recoverable error patterns
    FATAL_PATTERNS = [
        "fatal",
        "critical",
        "cannot recover",
        "system failure",
        "database error"
    ]
    
    @classmethod
    def translate(cls, technical_error: str) -> UserError:
        """
        Translate a technical error to user-friendly format
        
        Args:
            technical_error: The technical error message
            
        Returns:
            UserError with friendly message and suggestions
        """
        error_lower = technical_error.lower()
        
        # Check for fatal errors first
        is_fatal = any(pattern in error_lower for pattern in cls.FATAL_PATTERNS)
        
        # Find matching pattern
        for pattern, (category, message, suggestion) in cls.ERROR_PATTERNS.items():
            if pattern in error_lower:
                return UserError(
                    category=category,
                    message=message,
                    suggestion=suggestion,
                    technical_details=technical_error,
                    recoverable=not is_fatal,
                    retry_allowed=category not in [ErrorCategory.AUTHORIZATION, ErrorCategory.VALIDATION]
                )
        
        # Default unknown error
        return UserError(
            category=ErrorCategory.UNKNOWN,
            message="Something went wrong.",
            suggestion="Please try again or contact support if the issue persists.",
            technical_details=technical_error,
            recoverable=not is_fatal,
            retry_allowed=True
        )
    
    @classmethod
    def format_for_display(cls, error: UserError, show_technical: bool = False) -> str:
        """
        Format error for user display
        
        Args:
            error: The UserError to format
            show_technical: Whether to include technical details
            
        Returns:
            Formatted error string for display
        """
        lines = [f"❌ {error.message}"]
        lines.append(f"💡 {error.suggestion}")
        
        if error.retry_allowed:
            lines.append("🔄 You can try again.")
        
        if show_technical and error.technical_details:
            lines.append(f"\n📋 Technical: {error.technical_details}")
        
        return "\n".join(lines)
    
    @classmethod
    def get_retry_message(cls, error: UserError, attempt: int, max_attempts: int) -> str:
        """Get retry status message"""
        if error.retry_allowed and attempt < max_attempts:
            return f"🔄 Retrying... (attempt {attempt + 1}/{max_attempts})"
        elif not error.retry_allowed:
            return "❌ This error cannot be automatically retried."
        else:
            return "❌ Maximum retry attempts reached."
    
    @classmethod
    def is_recoverable(cls, technical_error: str) -> bool:
        """Check if an error is potentially recoverable"""
        error = cls.translate(technical_error)
        return error.recoverable
    
    @classmethod
    def should_retry(cls, technical_error: str) -> bool:
        """Check if an error should trigger a retry"""
        error = cls.translate(technical_error)
        return error.retry_allowed
    
    @classmethod
    def get_category(cls, technical_error: str) -> ErrorCategory:
        """Get error category for classification"""
        error = cls.translate(technical_error)
        return error.category


# Convenience functions
def translate_error(technical_error: str) -> UserError:
    """Translate technical error to user-friendly format"""
    return UserFriendlyErrors.translate(technical_error)


def format_error(technical_error: str, show_technical: bool = False) -> str:
    """Format error for user display"""
    error = UserFriendlyErrors.translate(technical_error)
    return UserFriendlyErrors.format_for_display(error, show_technical)


def is_recoverable(technical_error: str) -> bool:
    """Check if error is recoverable"""
    return UserFriendlyErrors.is_recoverable(technical_error)


def should_retry(technical_error: str) -> bool:
    """Check if error should trigger retry"""
    return UserFriendlyErrors.should_retry(technical_error)
