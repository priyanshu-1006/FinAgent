"""
Vision Module - AI-powered UI Element Detection

This module implements the core innovation of FinAgent:
- Uses Gemini 2.0 Flash Vision for analyzing screenshots
- Finds UI elements like buttons, inputs, and links
- Returns coordinates for clicking/interacting
- Provides human-like understanding of web interfaces
- Supports API key fallback for rate limit handling
- Implements element caching to reduce API calls
- Uses exponential backoff for rate limit recovery
"""

import json
import re
import base64
import asyncio
import random
import time
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass

from .config import config
from .element_cache import get_element_cache
from .metrics import get_metrics


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
    
    Uses Gemini 2.0 Flash (best vision model) for:
    - Element detection from screenshots
    - Page state analysis
    - Visual verification of actions
    - Supports automatic API key rotation on rate limits
    - Implements element caching to reduce API calls
    - Uses exponential backoff with jitter for retries
    """
    
    def __init__(self):
        self.client = None
        self.current_model_name = None
        self.cache = get_element_cache()
        self.metrics = get_metrics()
        self._init_model()
    
    def _init_model(self):
        """Initialize Gemini model for vision using new google.genai API"""
        try:
            from google import genai
            
            api_key = config.get_current_api_key()
            if api_key:
                self.client = genai.Client(api_key=api_key)
                self.current_model_name = config.vision_model
                print(f"✅ Vision Module initialized with {self.current_model_name}")
                if len(config.gemini_api_keys) > 1:
                    print(f"   📦 {len(config.gemini_api_keys)} API keys available for fallback")
            else:
                print("⚠️ No Gemini API key found. Vision features disabled.")
                print("   Get free key at: https://aistudio.google.com/app/apikey")
        except ImportError:
            print("⚠️ google-genai not installed. Run: pip install google-genai")
        except Exception as e:
            print(f"⚠️ Vision module init error: {e}")
    
    def _switch_api_key(self):
        """Switch to next API key on rate limit"""
        try:
            from google import genai
            new_key = config.get_next_api_key()
            if new_key:
                self.client = genai.Client(api_key=new_key)
                return True
        except Exception as e:
            print(f"⚠️ Failed to switch API key: {e}")
        return False
    
    async def _call_with_retry(self, prompt: str, image_bytes: bytes, max_retries: int = 3):
        """
        Call the model with automatic retry, exponential backoff, and key rotation
        
        Uses exponential backoff with jitter to avoid thundering herd problem
        """
        from google.genai import types
        
        last_error = None
        base_delay = 2  # Start with 2 seconds
        
        start_time = time.time()
        
        for attempt in range(max_retries):
            try:
                # Use the new google.genai API structure
                response = self.client.models.generate_content(
                    model=self.current_model_name,
                    contents=[
                        types.Content(
                            parts=[
                                types.Part.from_text(text=prompt),
                                types.Part.from_bytes(data=image_bytes, mime_type="image/png")
                            ]
                        )
                    ]
                )
                
                # Record successful API call
                duration_ms = (time.time() - start_time) * 1000
                self.metrics.record_api_call(
                    provider="gemini",
                    model=self.current_model_name,
                    duration_ms=duration_ms,
                    success=True
                )
                
                return response
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                # Check for rate limit or quota errors
                if "quota" in error_str or "rate" in error_str or "limit" in error_str or "429" in error_str:
                    # Calculate delay with exponential backoff and jitter
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"⚠️ API rate limit hit, waiting {delay:.1f}s before retry...")
                    await asyncio.sleep(delay)
                    
                    if self._switch_api_key():
                        continue
                
                # Check for model not found (fallback to stable model)
                if "not found" in error_str or "404" in error_str:
                    print(f"⚠️ Model {self.current_model_name} not available, falling back...")
                    fallback_models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
                    for fallback in fallback_models:
                        if fallback != self.current_model_name:
                            try:
                                self.current_model_name = fallback
                                print(f"   Switched to {fallback}")
                                break
                            except:
                                continue
                    continue
                
                print(f"⚠️ Vision API error (attempt {attempt + 1}): {e}")
        
        # Record failed API call
        duration_ms = (time.time() - start_time) * 1000
        self.metrics.record_api_call(
            provider="gemini",
            model=self.current_model_name,
            duration_ms=duration_ms,
            success=False,
            error=str(last_error)
        )
        
        raise last_error if last_error else Exception("Max retries exceeded")
    
    async def find_element(
        self,
        screenshot_base64: str,
        element_description: str,
        element_type: str = "button",
        page_url: str = ""
    ) -> ElementLocation:
        """
        Find a UI element in a screenshot
        
        Uses caching to avoid repeated API calls for same elements.
        
        Args:
            screenshot_base64: Base64 encoded screenshot
            element_description: What to find (e.g., "Login button", "Amount input field")
            element_type: Type of element (button, input, link, text)
            page_url: Current page URL for cache scoping
        
        Returns:
            ElementLocation with coordinates and confidence
        """
        if not self.client:
            return ElementLocation(
                found=False,
                element_type=element_type,
                description=element_description,
                confidence=0.0
            )
        
        # Check cache first
        if page_url:
            cached = self.cache.get(page_url, element_description, element_type)
            if cached:
                print(f"📦 Cache hit for '{element_description}'")
                return ElementLocation(
                    found=True,
                    element_type=cached.element_type,
                    description=cached.description,
                    x=cached.x,
                    y=cached.y,
                    confidence=cached.confidence,
                    selector_hint=cached.selector_hint
                )
        
        start_time = time.time()
        
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
            image_bytes = base64.b64decode(screenshot_base64)
            response = await self._call_with_retry(prompt, image_bytes)
            result = self._parse_json_response(response.text)
            
            if result:
                element_found = result.get("found", False)
                x = result.get("x", 0)
                y = result.get("y", 0)
                confidence = result.get("confidence", 0.0)
                selector_hint = result.get("selector_hint")
                
                # Cache the result if found
                if element_found and page_url and x > 0 and y > 0:
                    self.cache.set(
                        page_url=page_url,
                        element_desc=element_description,
                        element_type=element_type,
                        x=x,
                        y=y,
                        confidence=confidence,
                        selector_hint=selector_hint
                    )
                
                # Record vision call metrics
                duration_ms = (time.time() - start_time) * 1000
                self.metrics.record_vision_call(
                    operation="find_element",
                    duration_ms=duration_ms,
                    element_found=element_found,
                    confidence=confidence
                )
                
                return ElementLocation(
                    found=element_found,
                    element_type=result.get("element_type", element_type),
                    description=result.get("description", element_description),
                    x=x,
                    y=y,
                    confidence=confidence,
                    selector_hint=selector_hint
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
        if not self.client:
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
            image_bytes = base64.b64decode(screenshot_base64)
            response = await self._call_with_retry(prompt, image_bytes)
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
        if not self.client:
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
            image_bytes = base64.b64decode(screenshot_base64)
            response = await self._call_with_retry(prompt, image_bytes)
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
        if not self.client:
            return None
        
        prompt = f"""Look at this banking screenshot and extract the text from: {region_description}

Examples:
- "account balance" → "₹ 45,678.50"
- "error message" → "Insufficient balance"
- "success message" → "Transaction successful"

RESPOND with ONLY the extracted text, nothing else.
If text is not found, respond with "NOT_FOUND"."""

        try:
            image_bytes = base64.b64decode(screenshot_base64)
            response = await self._call_with_retry(prompt, image_bytes)
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
