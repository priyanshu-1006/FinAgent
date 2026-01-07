"""
Configuration settings for FinAgent
"""

import os
import random
from dataclasses import dataclass, field
from typing import Optional, List
from pathlib import Path

# Load .env file
from dotenv import load_dotenv

# Find and load .env from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)


def get_gemini_api_keys() -> List[str]:
    """Get all configured Gemini API keys (primary + fallbacks)"""
    keys = []
    
    # Primary key
    primary = os.getenv("GEMINI_API_KEY")
    if primary:
        keys.append(primary)
    
    # Fallback keys
    for i in range(1, 10):
        fallback = os.getenv(f"GEMINI_API_KEY_FALLBACK_{i}")
        if fallback:
            keys.append(fallback)
    
    return keys


def calculate_backoff_delay(attempt: int, base_delay: float = 2.0, max_delay: float = 60.0) -> float:
    """
    Calculate exponential backoff delay with jitter
    
    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay cap in seconds
    
    Returns:
        Delay in seconds with jitter
    """
    # Exponential backoff: 2^attempt * base_delay
    delay = min(base_delay * (2 ** attempt), max_delay)
    
    # Add jitter (±25% randomization)
    jitter = delay * random.uniform(-0.25, 0.25)
    
    return delay + jitter


@dataclass
class Config:
    """Agent configuration settings"""
    
    # AI Model Settings
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    gemini_api_keys: List[str] = field(default_factory=list)
    current_key_index: int = 0
    
    # Which AI model to use: "openai" or "gemini"
    ai_provider: str = "gemini"
    openai_model: str = "gpt-4o-mini"
    gemini_model: str = "gemini-3-flash-preview"
    
    # Vision Model Settings (for UI element detection)
    vision_enabled: bool = True
    vision_model: str = "gemini-3-flash-preview"
    
    # Browser Settings
    browser_type: str = "chromium"
    headless: bool = False
    slow_mo: int = 100
    
    # Target Banking Website
    bank_url: str = "http://localhost:8080"
    
    # Conscious Pause Settings
    require_approval_for: list = None
    approval_timeout: int = 60
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/agent.log"
    
    def __post_init__(self):
        # Load from environment
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_api_keys = get_gemini_api_keys()
        
        self.ai_provider = os.getenv("AI_PROVIDER", "gemini")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
        self.vision_model = os.getenv("VISION_MODEL", "gemini-3-flash-preview")
        
        self.browser_type = os.getenv("BROWSER_TYPE", "chromium")
        self.headless = os.getenv("HEADLESS", "false").lower() == "true"
        self.slow_mo = int(os.getenv("SLOW_MO", "100"))
        
        self.bank_url = os.getenv("BANK_URL", "http://localhost:8080")
        self.approval_timeout = int(os.getenv("APPROVAL_TIMEOUT", "60"))
        
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "logs/agent.log")
        
        if self.require_approval_for is None:
            self.require_approval_for = [
                "pay_bill",
                "fund_transfer",
                "buy_gold",
                "update_profile"
            ]
    
    def get_next_api_key(self) -> Optional[str]:
        """Get next API key when current one hits rate limit"""
        if not self.gemini_api_keys:
            return None
        
        self.current_key_index = (self.current_key_index + 1) % len(self.gemini_api_keys)
        new_key = self.gemini_api_keys[self.current_key_index]
        self.gemini_api_key = new_key
        print(f"🔄 Switching to API key #{self.current_key_index + 1}")
        return new_key
    
    def get_current_api_key(self) -> Optional[str]:
        """Get the current active API key"""
        if self.gemini_api_keys:
            return self.gemini_api_keys[self.current_key_index]
        return self.gemini_api_key


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
