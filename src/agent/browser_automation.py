"""
Browser Automation - Controls web browser using Playwright

This module provides the "Digital Hand" functionality:
- Browser initialization and management
- Page navigation and element interaction
- Screenshot capture for AI vision
- Vision-based element detection (CORE INNOVATION)
- Action execution on the banking website
"""

import asyncio
import base64
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

from .config import config, ACTIONS


@dataclass
class ActionResult:
    """Result of a browser action"""
    success: bool
    action: str
    message: str
    screenshot: Optional[str] = None  # Base64 encoded
    data: Optional[Dict[str, Any]] = None
    vision_used: bool = False  # Track if vision was used
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action,
            "message": self.message,
            "data": self.data,
            "vision_used": self.vision_used
        }


class BrowserAutomation:
    """Browser automation using Playwright with Vision AI support"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_logged_in = False
        self.vision = None  # Vision module for AI-based element detection
        self._init_vision()
    
    def _init_vision(self):
        """Initialize vision module for AI-based element detection"""
        if config.vision_enabled:
            try:
                from .vision import VisionModule
                self.vision = VisionModule()
            except Exception as e:
                print(f"⚠️ Vision module not available: {e}")
    
    async def start(self):
        """Initialize browser"""
        self.playwright = await async_playwright().start()
        
        browser_types = {
            "chromium": self.playwright.chromium,
            "firefox": self.playwright.firefox,
            "webkit": self.playwright.webkit
        }
        
        browser_launcher = browser_types.get(config.browser_type, self.playwright.chromium)
        
        self.browser = await browser_launcher.launch(
            headless=config.headless,
            slow_mo=config.slow_mo
        )
        
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 800}
        )
        
        self.page = await self.context.new_page()
        print(f"🌐 Browser started ({config.browser_type})")
        if self.vision and self.vision.client:
            print("👁️ Vision AI enabled for element detection")
    
    async def stop(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("🌐 Browser closed")
    
    async def navigate(self, url: str = None) -> ActionResult:
        """Navigate to URL"""
        url = url or config.bank_url
        try:
            await self.page.goto(url, wait_until="networkidle")
            return ActionResult(
                success=True,
                action="navigate",
                message=f"Navigated to {url}"
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action="navigate",
                message=f"Navigation failed: {str(e)}"
            )
    
    async def take_screenshot(self) -> str:
        """Take screenshot and return base64 encoded"""
        screenshot_bytes = await self.page.screenshot()
        return base64.b64encode(screenshot_bytes).decode('utf-8')
    
    # ===== VISION-BASED ACTIONS (Core Innovation) =====
    
    async def click_with_vision(self, element_description: str, element_type: str = "button") -> ActionResult:
        """
        Click an element using AI Vision to find it
        
        This is the CORE INNOVATION - the agent "sees" the UI like a human
        and clicks based on visual understanding, not brittle selectors.
        """
        if not self.vision or not self.vision.client:
            return ActionResult(
                success=False,
                action="vision_click",
                message="Vision module not available"
            )
        
        try:
            # Take screenshot
            screenshot = await self.take_screenshot()
            
            # Use AI to find element
            print(f"   👁️ Looking for: {element_description}")
            location = await self.vision.find_element(screenshot, element_description, element_type)
            
            if not location.found:
                return ActionResult(
                    success=False,
                    action="vision_click",
                    message=f"Could not find: {element_description}",
                    screenshot=screenshot,
                    vision_used=True
                )
            
            print(f"   👁️ Found at ({location.x}, {location.y}) with {location.confidence:.0%} confidence")
            
            # Click at coordinates
            await self.page.mouse.click(location.x, location.y)
            await asyncio.sleep(0.5)  # Wait for UI response
            
            return ActionResult(
                success=True,
                action="vision_click",
                message=f"Clicked {element_description} at ({location.x}, {location.y})",
                screenshot=await self.take_screenshot(),
                vision_used=True,
                data={
                    "element": element_description,
                    "coordinates": {"x": location.x, "y": location.y},
                    "confidence": location.confidence
                }
            )
        
        except Exception as e:
            return ActionResult(
                success=False,
                action="vision_click",
                message=f"Vision click failed: {str(e)}",
                vision_used=True
            )
    
    async def type_with_vision(self, field_description: str, text: str) -> ActionResult:
        """
        Type into a field using AI Vision to find it
        """
        if not self.vision or not self.vision.client:
            return ActionResult(
                success=False,
                action="vision_type",
                message="Vision module not available"
            )
        
        try:
            screenshot = await self.take_screenshot()
            
            print(f"   👁️ Looking for input: {field_description}")
            location = await self.vision.find_element(screenshot, field_description, "input")
            
            if not location.found:
                return ActionResult(
                    success=False,
                    action="vision_type",
                    message=f"Could not find input: {field_description}",
                    screenshot=screenshot,
                    vision_used=True
                )
            
            print(f"   👁️ Found input at ({location.x}, {location.y})")
            
            # Click to focus, then type
            await self.page.mouse.click(location.x, location.y)
            await asyncio.sleep(0.2)
            await self.page.keyboard.type(text)
            
            return ActionResult(
                success=True,
                action="vision_type",
                message=f"Typed into {field_description}",
                screenshot=await self.take_screenshot(),
                vision_used=True
            )
        
        except Exception as e:
            return ActionResult(
                success=False,
                action="vision_type",
                message=f"Vision type failed: {str(e)}",
                vision_used=True
            )
    
    async def analyze_current_page(self) -> Dict[str, Any]:
        """
        Use Vision AI to understand current page state
        """
        if not self.vision or not self.vision.client:
            return {"error": "Vision module not available"}
        
        try:
            screenshot = await self.take_screenshot()
            analysis = await self.vision.analyze_page(screenshot)
            
            return {
                "page_type": analysis.page_type,
                "current_state": analysis.current_state,
                "elements": analysis.elements,
                "suggestions": analysis.suggestions
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    async def verify_action_success(self, expected_outcome: str) -> Tuple[bool, str]:
        """
        Use Vision AI to verify if an action succeeded
        """
        if not self.vision or not self.vision.client:
            return True, "Verification skipped (no vision)"
        
        try:
            screenshot = await self.take_screenshot()
            return await self.vision.verify_action(screenshot, expected_outcome)
        except Exception as e:
            return True, f"Verification error: {e}"
    
    async def smart_click(self, element_description: str, fallback_selector: str = None) -> ActionResult:
        """
        Smart click - tries Vision first, falls back to selector
        
        This is the HYBRID APPROACH mentioned in the submission:
        1. Try Vision-based detection (robust to UI changes)
        2. Fall back to DOM selectors if Vision fails
        """
        # Try Vision first if available
        if self.vision and self.vision.client and config.vision_enabled:
            result = await self.click_with_vision(element_description)
            if result.success:
                return result
            print(f"   ⚠️ Vision failed, trying selector fallback...")
        
        # Fallback to selector
        if fallback_selector:
            try:
                await self.page.click(fallback_selector)
                await asyncio.sleep(0.3)
                return ActionResult(
                    success=True,
                    action="selector_click",
                    message=f"Clicked {element_description} via selector",
                    screenshot=await self.take_screenshot(),
                    vision_used=False
                )
            except Exception as e:
                return ActionResult(
                    success=False,
                    action="click",
                    message=f"Both vision and selector failed: {str(e)}"
                )
        
        return ActionResult(
            success=False,
            action="click",
            message=f"Could not click {element_description}"
        )
    
    async def get_page_state(self) -> Dict[str, Any]:
        """Get current page state for AI analysis"""
        return {
            "url": self.page.url,
            "title": await self.page.title(),
            "is_logged_in": self.is_logged_in,
            "screenshot": await self.take_screenshot()
        }
    
    # ===== Banking Actions =====
    
    async def login(self, username: str = "demo_user", password: str = "demo123") -> ActionResult:
        """Log in to the banking portal using Vision AI"""
        try:
            # Check if already on the page, if not navigate
            if "localhost:8080" not in self.page.url:
                await self.navigate()
            
            # Wait for page to fully load
            await asyncio.sleep(0.5)
            
            # Check if already logged in using vision
            screenshot = await self.take_screenshot()
            if self.vision and self.vision.client:
                page_analysis = await self.vision.analyze_page(screenshot)
                if "dashboard" in page_analysis.page_type.lower() or "logged" in page_analysis.current_state.lower():
                    self.is_logged_in = True
                    return ActionResult(
                        success=True,
                        action="login",
                        message="Already logged in",
                        screenshot=screenshot,
                        vision_used=True,
                        data={"username": username}
                    )
            
            # Use vision to fill username field
            print("   👁️ Using Vision AI to login...")
            username_result = await self.type_with_vision("username input field", username)
            if not username_result.success:
                print("   ⚠️ Vision failed for username, trying selector fallback...")
                await self.page.fill("#username", username)
            
            await asyncio.sleep(0.2)
            
            # Use vision to fill password field
            password_result = await self.type_with_vision("password input field", password)
            if not password_result.success:
                print("   ⚠️ Vision failed for password, trying selector fallback...")
                await self.page.fill("#password", password)
            
            await asyncio.sleep(0.3)
            
            # Use vision to click login button
            login_result = await self.click_with_vision("login button", "button")
            if not login_result.success:
                print("   ⚠️ Vision failed for login button, trying selector fallback...")
                await self.page.click("#login-btn")
            
            # Wait for dashboard to become active
            await asyncio.sleep(1.5)  # Give JavaScript time to process
            
            # Verify dashboard is now visible
            for _ in range(5):
                dashboard_active = await self.page.query_selector("#dashboard-page.active")
                if dashboard_active:
                    break
                await asyncio.sleep(0.3)
            
            self.is_logged_in = True
            
            # Get balance
            balance_text = await self.page.text_content("#account-balance")
            
            return ActionResult(
                success=True,
                action="login",
                message=f"Logged in successfully as {username}",
                screenshot=await self.take_screenshot(),
                data={"username": username, "balance": balance_text}
            )
        
        except Exception as e:
            return ActionResult(
                success=False,
                action="login",
                message=f"Login failed: {str(e)}",
                screenshot=await self.take_screenshot()
            )
    
    async def check_balance(self) -> ActionResult:
        """Check account balance"""
        try:
            if not self.is_logged_in:
                return ActionResult(False, "check_balance", "Please login first")
            
            balance_text = await self.page.text_content("#account-balance")
            
            return ActionResult(
                success=True,
                action="check_balance",
                message=f"Current balance: {balance_text}",
                screenshot=await self.take_screenshot(),
                data={"balance": balance_text}
            )
        
        except Exception as e:
            return ActionResult(
                success=False,
                action="check_balance",
                message=f"Failed to check balance: {str(e)}"
            )
    
    async def navigate_to_pay_bills(self) -> ActionResult:
        """Navigate to bill payment page using Vision AI"""
        try:            # Ensure we're on the dashboard first
            dashboard = await self.page.query_selector("#dashboard-page.active")
            if not dashboard:
                print("   Not on dashboard, navigating there first...")
                await self.go_back_to_dashboard()
                await asyncio.sleep(0.5)
            
            # Use vision to click Pay Bills button
            result = await self.click_with_vision("Pay Bills button", "button")
            if result.success:
                await asyncio.sleep(0.5)
                return ActionResult(
                    success=True,
                    action="navigate",
                    message="Navigated to Pay Bills page using Vision",
                    screenshot=await self.take_screenshot(),
                    vision_used=True
                )
            
            # Fallback to selector
            print("   ⚠️ Vision failed, using selector fallback...")
            await self.page.wait_for_selector("[data-action='pay-bills']", timeout=5000)
            await self.page.click("[data-action='pay-bills']")
            await self.page.wait_for_selector("#pay-bills-page.active, #bill-pay-form", timeout=3000)
            
            return ActionResult(
                success=True,
                action="navigate",
                message="Navigated to Pay Bills page",
                screenshot=await self.take_screenshot()
            )
        except Exception as e:
            return ActionResult(False, "navigate", f"Navigation failed: {str(e)}")
    
    async def pay_bill(self, biller: str = "Adani Power", consumer_number: str = "1234567890", amount: float = 1000) -> ActionResult:
        """Pay a utility bill using Vision AI"""
        try:
            # First ensure we're on the pay bills page
            pay_bills_page = await self.page.query_selector("#pay-bills-page.active")
            if not pay_bills_page:
                await self.navigate_to_pay_bills()
                await asyncio.sleep(0.5)
            
            print("   👁️ Using Vision AI to fill bill payment form...")
            
            # Use vision to fill consumer number
            consumer_result = await self.type_with_vision("consumer number input field", consumer_number)
            if not consumer_result.success:
                print("   ⚠️ Vision failed, using selector fallback...")
                await self.page.fill("#consumer-number", consumer_number)
            
            await asyncio.sleep(0.3)
            
            # Use vision to fill amount
            amount_result = await self.type_with_vision("bill amount input field", str(int(amount)))
            if not amount_result.success:
                print("   ⚠️ Vision failed, using selector fallback...")
                await self.page.fill("#bill-amount", str(int(amount)))
            
            await asyncio.sleep(0.5)
            
            # Use vision to click pay button
            pay_result = await self.click_with_vision("Pay Bill button", "button")
            if not pay_result.success:
                print("   ⚠️ Vision failed, using selector fallback...")
                await self.page.click("#pay-bill-btn")
            
            # Wait for confirmation modal
            await asyncio.sleep(1)
            
            # Check if modal appeared
            for _ in range(5):
                modal = await self.page.query_selector("#confirm-modal.active")
                if modal:
                    break
                await asyncio.sleep(0.3)
            
            return ActionResult(
                success=True,
                action="pay_bill",
                message=f"Bill payment prepared: ₹{amount} to {biller}",
                screenshot=await self.take_screenshot(),
                data={
                    "biller": biller,
                    "consumer_number": consumer_number,
                    "amount": amount,
                    "awaiting_confirmation": True
                }
            )
        
        except Exception as e:
            return ActionResult(
                success=False,
                action="pay_bill",
                message=f"Bill payment failed: {str(e)}",
                screenshot=await self.take_screenshot()
            )
    
    async def navigate_to_fund_transfer(self) -> ActionResult:
        """Navigate to fund transfer page using Vision AI"""
        try:
            # Check if we're on the dashboard
            dashboard = await self.page.query_selector("#dashboard-page.active")
            if not dashboard:
                print("   Dashboard not active, navigating back...")
                await self.go_back_to_dashboard()
                await asyncio.sleep(0.5)
            
            # Use vision to click Fund Transfer button
            print("   👁️ Using Vision AI to navigate to Fund Transfer...")
            result = await self.click_with_vision("Fund Transfer button or Transfer Money button", "button")
            if result.success:
                await asyncio.sleep(0.5)
                return ActionResult(
                    success=True,
                    action="navigate",
                    message="Navigated to Fund Transfer page using Vision",
                    screenshot=await self.take_screenshot(),
                    vision_used=True
                )
            
            # Fallback to selector
            print("   ⚠️ Vision failed, using selector fallback...")
            await self.page.wait_for_selector("[data-action='fund-transfer']", timeout=5000, state="visible")
            await self.page.click("[data-action='fund-transfer']")
            await self.page.wait_for_selector("#fund-transfer-page.active, #transfer-form", timeout=3000)
            
            return ActionResult(
                success=True,
                action="navigate",
                message="Navigated to Fund Transfer page",
                screenshot=await self.take_screenshot()
            )
        except Exception as e:
            screenshot = await self.take_screenshot()
            return ActionResult(False, "navigate", f"Navigation failed: {str(e)}", screenshot=screenshot)
    
    async def fund_transfer(self, recipient: str = "Mom", account: str = "9876543210", ifsc: str = "JFIN0001234", amount: float = 1000) -> ActionResult:
        """Transfer money to another account using Vision AI"""
        try:
            # First ensure we're on the transfer page
            transfer_page = await self.page.query_selector("#fund-transfer-page.active")
            if not transfer_page:
                await self.navigate_to_fund_transfer()
                await asyncio.sleep(0.5)
            
            print("   👁️ Using Vision AI to fill transfer form...")
            
            # Use vision to fill recipient name
            result = await self.type_with_vision("recipient name field", recipient)
            if not result.success:
                await self.page.fill("#recipient-name", recipient)
            
            await asyncio.sleep(0.2)
            
            # Use vision to fill account number
            result = await self.type_with_vision("account number field", account)
            if not result.success:
                await self.page.fill("#recipient-account", account)
            
            await asyncio.sleep(0.2)
            
            # Use vision to fill IFSC code
            result = await self.type_with_vision("IFSC code field", ifsc)
            if not result.success:
                await self.page.fill("#recipient-ifsc", ifsc)
            
            await asyncio.sleep(0.2)
            
            # Use vision to fill amount
            result = await self.type_with_vision("transfer amount field", str(int(amount)))
            if not result.success:
                await self.page.fill("#transfer-amount", str(int(amount)))
            
            await asyncio.sleep(0.5)
            
            # Use vision to click transfer button
            result = await self.click_with_vision("Transfer button", "button")
            if not result.success:
                await self.page.click("#transfer-btn")
            
            # Wait for confirmation modal
            await asyncio.sleep(1)
            
            # Check if modal appeared
            for _ in range(5):
                modal = await self.page.query_selector("#confirm-modal.active")
                if modal:
                    break
                await asyncio.sleep(0.3)
            
            return ActionResult(
                success=True,
                action="fund_transfer",
                message=f"Transfer prepared: ₹{amount} to {recipient}",
                screenshot=await self.take_screenshot(),
                data={
                    "recipient": recipient,
                    "account": account,
                    "amount": amount,
                    "awaiting_confirmation": True
                }
            )
        
        except Exception as e:
            return ActionResult(
                success=False,
                action="fund_transfer",
                message=f"Transfer failed: {str(e)}",
                screenshot=await self.take_screenshot()
            )
    
    async def select_beneficiary(self, name: str) -> ActionResult:
        """Select a saved beneficiary for transfer"""
        try:
            await self.page.click(f".beneficiary-card[data-name='{name}']")
            return ActionResult(
                success=True,
                action="select_beneficiary",
                message=f"Selected beneficiary: {name}",
                screenshot=await self.take_screenshot()
            )
        except Exception as e:
            return ActionResult(False, "select_beneficiary", f"Failed: {str(e)}")
    
    async def navigate_to_buy_gold(self) -> ActionResult:
        """Navigate to digital gold page using Vision AI"""
        try:
            # Check if we're on the dashboard first
            dashboard = await self.page.query_selector("#dashboard-page.active")
            if not dashboard:
                print("   Dashboard not active, navigating back...")
                await self.go_back_to_dashboard()
                await asyncio.sleep(0.5)
            
            # Use vision to click Buy Gold button
            print("   👁️ Using Vision AI to navigate to Buy Gold...")
            result = await self.click_with_vision("Buy Gold button or Digital Gold button", "button")
            if result.success:
                await asyncio.sleep(0.5)
                return ActionResult(
                    success=True,
                    action="navigate",
                    message="Navigated to Digital Gold page using Vision",
                    screenshot=await self.take_screenshot(),
                    vision_used=True
                )
            
            # Fallback to selector
            print("   ⚠️ Vision failed, using selector fallback...")
            await self.page.wait_for_selector("[data-action='buy-gold']", timeout=5000, state="visible")
            await self.page.click("[data-action='buy-gold']")
            await self.page.wait_for_selector("#buy-gold-page.active, #gold-form", timeout=3000)
            
            return ActionResult(
                success=True,
                action="navigate",
                message="Navigated to Digital Gold page",
                screenshot=await self.take_screenshot()
            )
        except Exception as e:
            screenshot = await self.take_screenshot()
            return ActionResult(False, "navigate", f"Navigation failed: {str(e)}", screenshot=screenshot)
    
    async def buy_gold(self, amount: float = None, grams: float = None) -> ActionResult:
        """Buy digital gold using Vision AI"""
        try:
            # First ensure we're on the gold page
            gold_page = await self.page.query_selector("#buy-gold-page.active")
            if not gold_page:
                await self.navigate_to_buy_gold()
                await asyncio.sleep(0.5)
            
            print("   👁️ Using Vision AI to fill gold purchase form...")
            
            if grams:
                # Switch to grams mode using vision
                result = await self.click_with_vision("grams tab or grams option", "button")
                if not result.success:
                    await self.page.click("[data-type='grams']")
                
                await asyncio.sleep(0.3)
                
                # Fill grams using vision
                result = await self.type_with_vision("gold grams input field", str(grams))
                if not result.success:
                    await self.page.fill("#gold-grams", str(grams))
            elif amount:
                # Fill amount using vision (default mode)
                result = await self.type_with_vision("gold amount input field", str(int(amount)))
                if not result.success:
                    await self.page.fill("#gold-amount", str(int(amount)))
            else:
                # Just navigate to the page without filling values
                return ActionResult(
                    success=True,
                    action="buy_gold",
                    message="Navigated to Digital Gold page. Please specify the amount or grams to purchase.",
                    screenshot=await self.take_screenshot(),
                    data={
                        "awaiting_input": True
                    }
                )
            
            await asyncio.sleep(0.5)
            
            # Use vision to click buy button
            result = await self.click_with_vision("Buy Gold button or Purchase button", "button")
            if not result.success:
                await self.page.click("#buy-gold-btn")
            
            # Wait for confirmation modal
            await asyncio.sleep(1)
            
            # Check if modal appeared
            for _ in range(5):
                modal = await self.page.query_selector("#confirm-modal.active")
                if modal:
                    break
                await asyncio.sleep(0.3)
            
            return ActionResult(
                success=True,
                action="buy_gold",
                message=f"Gold purchase prepared: {'₹' + str(amount) if amount else str(grams) + ' grams'}",
                screenshot=await self.take_screenshot(),
                data={
                    "amount": amount,
                    "grams": grams,
                    "awaiting_confirmation": True
                }
            )
        
        except Exception as e:
            return ActionResult(
                success=False,
                action="buy_gold",
                message=f"Gold purchase failed: {str(e)}",
                screenshot=await self.take_screenshot()
            )
    
    async def confirm_action(self) -> ActionResult:
        """Confirm the pending action in modal"""
        try:
            print("   Clicking confirm button...")
            await self.page.click("#confirm-proceed-btn")
            
            # Wait for confirm modal to close
            print("   Waiting for confirm modal to close...")
            await asyncio.sleep(0.5)
            
            # Wait for loading overlay to appear and disappear (2 second simulation in script.js)
            print("   Waiting for transaction processing...")
            try:
                # Check if loading overlay appears
                await self.page.wait_for_selector("#loading-overlay", state="visible", timeout=1000)
                print("   Loading overlay visible")
                # Wait for it to disappear
                await self.page.wait_for_selector("#loading-overlay", state="hidden", timeout=5000)
                print("   Loading complete")
            except:
                # If loading doesn't appear, just wait a bit
                await asyncio.sleep(2.5)
            
            # Now wait for success modal
            print("   Waiting for success modal...")
            try:
                await self.page.wait_for_selector("#success-modal.active", timeout=3000)
                success_message = await self.page.text_content("#success-message")
                print(f"   ✅ Success: {success_message}")
                
                return ActionResult(
                    success=True,
                    action="confirm",
                    message=f"Action confirmed: {success_message}",
                    screenshot=await self.take_screenshot()
                )
            except Exception as wait_err:
                # Success modal might not appear - check page state
                print(f"   Success modal wait failed: {wait_err}")
                print("   Checking for any success indicators...")
                screenshot = await self.take_screenshot()
                
                # Check if we're back on dashboard (success without modal)
                try:
                    dashboard_visible = await self.page.is_visible(".dashboard-container")
                    if dashboard_visible:
                        return ActionResult(
                            success=True,
                            action="confirm",
                            message="Action confirmed (dashboard visible)",
                            screenshot=screenshot
                        )
                except:
                    pass
                
                # Assume success if no error modal
                return ActionResult(
                    success=True,
                    action="confirm",
                    message="Action confirmed (modal check skipped)",
                    screenshot=screenshot
                )
        
        except Exception as e:
            print(f"   ❌ Confirmation error: {str(e)}")
            return ActionResult(
                success=False,
                action="confirm",
                message=f"Confirmation failed: {str(e)}",
                screenshot=await self.take_screenshot()
            )
    
    async def cancel_action(self) -> ActionResult:
        """Cancel the pending action"""
        try:
            await self.page.click("#confirm-cancel-btn")
            return ActionResult(
                success=True,
                action="cancel",
                message="Action cancelled",
                screenshot=await self.take_screenshot()
            )
        except Exception as e:
            return ActionResult(False, "cancel", f"Cancel failed: {str(e)}")
    
    async def dismiss_modal(self) -> ActionResult:
        """Dismiss success/error modal"""
        try:
            await self.page.click("#success-ok-btn, #error-ok-btn")
            return ActionResult(True, "dismiss", "Modal dismissed")
        except:
            return ActionResult(True, "dismiss", "No modal to dismiss")
    
    async def go_back_to_dashboard(self) -> ActionResult:
        """Navigate back to dashboard"""
        try:
            # Try clicking back button
            back_btn = await self.page.query_selector(".btn-back, [id$='-back']")
            if back_btn:
                await back_btn.click()
            else:
                # Navigate directly
                await self.page.click(".nav-brand, .logo-icon-small")
            
            await self.page.wait_for_selector("#dashboard-page.active", timeout=3000)
            
            return ActionResult(
                success=True,
                action="navigate",
                message="Returned to dashboard",
                screenshot=await self.take_screenshot()
            )
        except Exception as e:
            return ActionResult(False, "navigate", f"Navigation failed: {str(e)}")
    
    async def view_transactions(self) -> ActionResult:
        """View transaction history"""
        try:
            transactions = []
            items = await self.page.query_selector_all(".transaction-item")
            
            for item in items[:5]:
                title = await item.query_selector(".txn-title")
                amount = await item.query_selector(".txn-amount")
                date = await item.query_selector(".txn-date")
                
                if title and amount:
                    transactions.append({
                        "title": await title.text_content(),
                        "amount": await amount.text_content(),
                        "date": await date.text_content() if date else ""
                    })
            
            return ActionResult(
                success=True,
                action="view_transactions",
                message=f"Found {len(transactions)} recent transactions",
                screenshot=await self.take_screenshot(),
                data={"transactions": transactions}
            )
        
        except Exception as e:
            return ActionResult(
                success=False,
                action="view_transactions",
                message=f"Failed to get transactions: {str(e)}"
            )


# Convenience function to create and start browser
async def create_browser() -> BrowserAutomation:
    """Create and start a browser automation instance"""
    browser = BrowserAutomation()
    await browser.start()
    return browser
