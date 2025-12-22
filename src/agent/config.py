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
    ai_provider: str = os.getenv("AI_PROVIDER", "gemini")  # Default to free tier
    openai_model: str = "gpt-4o-mini"  # Cheaper option
    gemini_model: str = "gemini-1.5-flash"  # Free tier
    
    # Vision Model Settings (for UI element detection)
    vision_enabled: bool = True
    vision_model: str = os.getenv("VISION_MODEL", "gemini-1.5-flash")
    
    # Browser Settings
    browser_type: str = os.getenv("BROWSER_TYPE", "chromium")
    headless: bool = os.getenv("HEADLESS", "false").lower() == "true"
    slow_mo: int = int(os.getenv("SLOW_MO", "100"))
    
    # Target Banking Website
    bank_url: str = os.getenv("BANK_URL", "http://localhost:8080")
    
    # Conscious Pause Settings
    require_approval_for: list = None  # High-risk actions requiring approval
    approval_timeout: int = int(os.getenv("APPROVAL_TIMEOUT", "60"))
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "logs/agent.log")
    
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
