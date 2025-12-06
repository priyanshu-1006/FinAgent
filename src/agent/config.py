"""
Configuration settings for FinAgent
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Agent configuration settings"""
    
    # AI Model Settings
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # Which AI model to use: "openai" or "gemini"
    ai_provider: str = "openai"
    openai_model: str = "gpt-4o"
    gemini_model: str = "gemini-1.5-pro"
    
    # Browser Settings
    browser_type: str = "chromium"  # chromium, firefox, webkit
    headless: bool = False  # Set to True for production
    slow_mo: int = 100  # Milliseconds between actions (for visibility)
    
    # Target Banking Website
    bank_url: str = "http://localhost:8080"
    
    # Conscious Pause Settings
    require_approval_for: list = None  # High-risk actions requiring approval
    approval_timeout: int = 60  # Seconds to wait for approval
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/agent.log"
    
    def __post_init__(self):
        if self.require_approval_for is None:
            self.require_approval_for = [
                "pay_bill",
                "fund_transfer",
                "buy_gold",
                "update_profile"
            ]


# Default configuration instance
config = Config()


# Action definitions with risk levels
ACTIONS = {
    "login": {
        "description": "Log in to the banking portal",
        "risk_level": "low",
        "requires_approval": False
    },
    "check_balance": {
        "description": "Check account balance",
        "risk_level": "low",
        "requires_approval": False
    },
    "pay_bill": {
        "description": "Pay a utility bill",
        "risk_level": "high",
        "requires_approval": True
    },
    "fund_transfer": {
        "description": "Transfer money to another account",
        "risk_level": "high",
        "requires_approval": True
    },
    "buy_gold": {
        "description": "Purchase digital gold",
        "risk_level": "high",
        "requires_approval": True
    },
    "view_profile": {
        "description": "View profile information",
        "risk_level": "low",
        "requires_approval": False
    },
    "update_profile": {
        "description": "Update profile information",
        "risk_level": "medium",
        "requires_approval": True
    },
    "view_transactions": {
        "description": "View transaction history",
        "risk_level": "low",
        "requires_approval": False
    }
}


# Intent keywords mapping
INTENT_KEYWORDS = {
    "login": ["login", "sign in", "log in", "authenticate", "enter"],
    "check_balance": ["balance", "how much", "account", "money", "funds"],
    "pay_bill": ["pay bill", "electricity", "gas", "water", "mobile", "broadband", "utility"],
    "fund_transfer": ["transfer", "send money", "pay", "remit", "wire"],
    "buy_gold": ["gold", "buy gold", "digital gold", "invest gold"],
    "view_profile": ["profile", "my details", "account info", "personal"],
    "update_profile": ["update profile", "change email", "change phone", "edit profile"],
    "view_transactions": ["transactions", "history", "statement", "recent"]
}
