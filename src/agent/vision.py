"""
Vision Module - AI-powered UI Element Detection

This module implements the core innovation of FinAgent:
- Uses Gemini 1.5 Flash Vision (FREE TIER) to analyze screenshots
- Finds UI elements like buttons, inputs, and links
- Returns coordinates for clicking/interacting
- Provides human-like understanding of web interfaces
"""

import json
import re
import base64
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass

from .config import config


@dataclass
class ElementLocation:
    """Detected UI element location"""
    found: bool
    element_type: str
    description: str
    x: int = 0
    y: int = 0
    confidence: float = 0.0
    selector_hint: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "found": self.found,
            "element_type": self.element_type,
            "description": self.description,
            "x": self.x,
            "y": self.y,
            "confidence": self.confidence,
            "selector_hint": self.selector_hint
        }


@dataclass
class PageAnalysis:
    """Complete page analysis result"""
    page_type: str  # login, dashboard, payment, etc.
    elements: List[Dict[str, Any]]
    current_state: str
    suggestions: List[str]


class VisionModule:
    """
    AI Vision for understanding web UI
    
    Uses Gemini 1.5 Flash (free tier) for:
    - Element detection from screenshots
    - Page state analysis
    - Visual verification of actions
    """
    
    def __init__(self):
        self.model = None
        self._init_model()
    
    def _init_model(self):
        """Initialize Gemini model for vision"""
        try:
            import google.generativeai as genai
            
            if config.gemini_api_key:
                genai.configure(api_key=config.gemini_api_key)
                self.model = genai.GenerativeModel(config.vision_model)
                print(f"✅ Vision Module initialized with {config.vision_model}")
            else:
                print("⚠️ No Gemini API key found. Vision features disabled.")
                print("   Get free key at: https://aistudio.google.com/app/apikey")
        except ImportError:
            print("⚠️ google-generativeai not installed. Run: pip install google-generativeai")
        except Exception as e:
            print(f"⚠️ Vision module init error: {e}")
    
    async def find_element(
        self,
        screenshot_base64: str,
        element_description: str,
        element_type: str = "button"
    ) -> ElementLocation:
        """
        Find a UI element in a screenshot
        
        Args:
            screenshot_base64: Base64 encoded screenshot
            element_description: What to find (e.g., "Login button", "Amount input field")
            element_type: Type of element (button, input, link, text)
        
        Returns:
            ElementLocation with coordinates and confidence
        """
        if not self.model:
            return ElementLocation(
                found=False,
                element_type=element_type,
                description=element_description,
                confidence=0.0
            )
        
        prompt = f"""Analyze this banking website screenshot and find the UI element described below.

TASK: Find the "{element_description}" {element_type}

INSTRUCTIONS:
1. Look carefully at the screenshot
2. Find the element that matches the description
3. Estimate the CENTER coordinates (x, y) of the element
4. The image is approximately 1280x800 pixels

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "found": true or false,
    "element_type": "{element_type}",
    "description": "what you found",
    "x": center_x_coordinate,
    "y": center_y_coordinate,
    "confidence": 0.0 to 1.0,
    "selector_hint": "CSS selector if visible (like #login-btn or .action-card)"
}}

If element is NOT found, set found=false and x,y to 0.
ONLY return the JSON, no other text."""

        try:
            import google.generativeai as genai
            
            # Decode base64 to bytes
            image_bytes = base64.b64decode(screenshot_base64)
            
            # Create image part
            image_part = {
                "mime_type": "image/png",
                "data": image_bytes
            }
            
            response = self.model.generate_content([prompt, image_part])
            
            # Parse JSON from response
            result = self._parse_json_response(response.text)
            
            if result:
                return ElementLocation(
                    found=result.get("found", False),
                    element_type=result.get("element_type", element_type),
                    description=result.get("description", element_description),
                    x=result.get("x", 0),
                    y=result.get("y", 0),
                    confidence=result.get("confidence", 0.0),
                    selector_hint=result.get("selector_hint")
                )
        
        except Exception as e:
            print(f"⚠️ Vision find_element error: {e}")
        
        return ElementLocation(
            found=False,
            element_type=element_type,
            description=element_description,
            confidence=0.0
        )
    
    async def analyze_page(self, screenshot_base64: str) -> PageAnalysis:
        """
        Analyze the current page state and available elements
        
        Useful for:
        - Understanding what page we're on
        - Finding all interactive elements
        - Verifying successful navigation
        """
        if not self.model:
            return PageAnalysis(
                page_type="unknown",
                elements=[],
                current_state="Vision module not available",
                suggestions=[]
            )
        
        prompt = """Analyze this banking website screenshot and describe:

1. PAGE TYPE: What type of page is this? (login, dashboard, payment, transfer, gold_purchase, profile, etc.)

2. CURRENT STATE: What is the current state? (logged_out, logged_in, form_empty, form_filled, modal_open, success_shown, error_shown)

3. KEY ELEMENTS: List all interactive elements visible with their approximate positions:
   - Buttons (with text labels)
   - Input fields (with labels)
   - Links/Navigation items
   - Modals or popups

4. SUGGESTIONS: What actions can be taken on this page?

RESPOND IN THIS EXACT JSON FORMAT:
{
    "page_type": "type_here",
    "current_state": "state_here",
    "elements": [
        {"type": "button", "label": "Login", "x": 640, "y": 400},
        {"type": "input", "label": "Username", "x": 640, "y": 300}
    ],
    "suggestions": ["Click Login button", "Enter username"]
}

ONLY return the JSON, no other text."""

        try:
            import google.generativeai as genai
            
            image_bytes = base64.b64decode(screenshot_base64)
            image_part = {"mime_type": "image/png", "data": image_bytes}
            
            response = self.model.generate_content([prompt, image_part])
            result = self._parse_json_response(response.text)
            
            if result:
                return PageAnalysis(
                    page_type=result.get("page_type", "unknown"),
                    elements=result.get("elements", []),
                    current_state=result.get("current_state", "unknown"),
                    suggestions=result.get("suggestions", [])
                )
        
        except Exception as e:
            print(f"⚠️ Vision analyze_page error: {e}")
        
        return PageAnalysis(
            page_type="unknown",
            elements=[],
            current_state="Analysis failed",
            suggestions=[]
        )
    
    async def verify_action(
        self,
        screenshot_base64: str,
        expected_outcome: str
    ) -> Tuple[bool, str]:
        """
        Verify if an action was successful
        
        Args:
            screenshot_base64: Screenshot after action
            expected_outcome: What should have happened (e.g., "Login successful", "Dashboard visible")
        
        Returns:
            (success: bool, description: str)
        """
        if not self.model:
            return True, "Vision verification skipped"
        
        prompt = f"""Analyze this screenshot and verify if the expected outcome occurred.

EXPECTED OUTCOME: {expected_outcome}

Look for:
1. Success indicators (green messages, checkmarks, correct page loaded)
2. Error indicators (red messages, error modals, wrong page)
3. Loading states (spinners, processing)

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "success": true or false,
    "description": "what you see on the screen",
    "indicators": ["list", "of", "visual", "clues"]
}}

ONLY return the JSON, no other text."""

        try:
            import google.generativeai as genai
            
            image_bytes = base64.b64decode(screenshot_base64)
            image_part = {"mime_type": "image/png", "data": image_bytes}
            
            response = self.model.generate_content([prompt, image_part])
            result = self._parse_json_response(response.text)
            
            if result:
                return result.get("success", False), result.get("description", "Unknown")
        
        except Exception as e:
            print(f"⚠️ Vision verify_action error: {e}")
        
        return True, "Verification skipped due to error"
    
    async def extract_text(
        self,
        screenshot_base64: str,
        region_description: str
    ) -> Optional[str]:
        """
        Extract text from a specific region of the screenshot
        
        Useful for reading:
        - Account balances
        - Transaction amounts
        - Error messages
        - Success confirmations
        """
        if not self.model:
            return None
        
        prompt = f"""Look at this banking screenshot and extract the text from: {region_description}

Examples:
- "account balance" → "₹ 45,678.50"
- "error message" → "Insufficient balance"
- "success message" → "Transaction successful"

RESPOND with ONLY the extracted text, nothing else.
If text is not found, respond with "NOT_FOUND"."""

        try:
            import google.generativeai as genai
            
            image_bytes = base64.b64decode(screenshot_base64)
            image_part = {"mime_type": "image/png", "data": image_bytes}
            
            response = self.model.generate_content([prompt, image_part])
            text = response.text.strip()
            
            if text and text != "NOT_FOUND":
                return text
        
        except Exception as e:
            print(f"⚠️ Vision extract_text error: {e}")
        
        return None
    
    def _parse_json_response(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from model response"""
        try:
            # Try direct parse first
            return json.loads(text)
        except:
            pass
        
        try:
            # Find JSON in response
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return None


# Singleton instance
vision = VisionModule()


# Convenience functions
async def find_element(screenshot: str, description: str, element_type: str = "button") -> ElementLocation:
    """Find a UI element in screenshot"""
    return await vision.find_element(screenshot, description, element_type)


async def analyze_page(screenshot: str) -> PageAnalysis:
    """Analyze page state"""
    return await vision.analyze_page(screenshot)


async def verify_action(screenshot: str, expected: str) -> Tuple[bool, str]:
    """Verify action outcome"""
    return await vision.verify_action(screenshot, expected)


async def extract_text(screenshot: str, region: str) -> Optional[str]:
    """Extract text from region"""
    return await vision.extract_text(screenshot, region)
