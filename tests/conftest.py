"""
Pytest Configuration and Fixtures
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def project_root():
    """Get project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables for testing"""
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")
    monkeypatch.setenv("AI_PROVIDER", "gemini")
    monkeypatch.setenv("BANK_URL", "http://localhost:8080")
    monkeypatch.setenv("HEADLESS", "true")


@pytest.fixture
def sample_commands():
    """Sample user commands for testing"""
    return {
        "pay_bill": [
            "pay electricity bill of 1500",
            "pay gas bill Rs 500 to Adani",
            "pay mobile bill ₹999",
        ],
        "fund_transfer": [
            "transfer 5000 to Mom",
            "send money 10000 rupees to Rahul",
            "transfer ₹25000 to friend",
        ],
        "buy_gold": [
            "buy gold worth 10000",
            "buy 5 grams of gold",
            "invest in digital gold Rs 5000",
        ],
        "login": [
            "login to bank",
            "sign in to my account",
        ],
        "check_balance": [
            "check my balance",
            "how much money do I have",
            "show account balance",
        ],
    }


@pytest.fixture
def mock_screenshot():
    """Mock base64 encoded screenshot"""
    # Minimal valid PNG
    import base64
    # 1x1 transparent PNG
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    return base64.b64encode(png_data).decode()
