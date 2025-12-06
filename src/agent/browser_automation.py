"""
Browser Automation - Controls web browser using Playwright

This module provides the "Digital Hand" functionality:
- Browser initialization and management
- Page navigation and element interaction
- Screenshot capture for AI vision
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
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action,
            "message": self.message,
            "data": self.data
        }


class BrowserAutomation:
    """Browser automation using Playwright"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_logged_in = False
    
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
        """Log in to the banking portal"""
        try:
            # Navigate to bank
            await self.navigate()
            
            # Wait for login form
            await self.page.wait_for_selector("#login-form", timeout=5000)
            
            # Fill credentials
            await self.page.fill("#username", username)
            await self.page.fill("#password", password)
            
            # Click login button
            await self.page.click("#login-btn, button[type='submit']")
            
            # Wait for dashboard
            await self.page.wait_for_selector("#dashboard-page.active, .dashboard-container", timeout=5000)
            
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
        """Navigate to bill payment page"""
        try:
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
    
    async def pay_bill(self, biller: str, consumer_number: str, amount: float) -> ActionResult:
        """Pay a utility bill"""
        try:
            # Navigate to pay bills if not already there
            if "pay-bills" not in await self.page.text_content("body"):
                await self.navigate_to_pay_bills()
            
            # Select biller
            await self.page.select_option("#biller-select", label=biller)
            
            # Fill consumer number
            await self.page.fill("#consumer-number", consumer_number)
            
            # Fill amount
            await self.page.fill("#bill-amount", str(amount))
            
            # Click pay button
            await self.page.click("#pay-bill-btn, button[type='submit']")
            
            # Wait for confirmation modal
            await self.page.wait_for_selector("#confirm-modal.active, .modal.confirm", timeout=3000)
            
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
        """Navigate to fund transfer page"""
        try:
            await self.page.click("[data-action='fund-transfer']")
            await self.page.wait_for_selector("#fund-transfer-page.active, #transfer-form", timeout=3000)
            
            return ActionResult(
                success=True,
                action="navigate",
                message="Navigated to Fund Transfer page",
                screenshot=await self.take_screenshot()
            )
        except Exception as e:
            return ActionResult(False, "navigate", f"Navigation failed: {str(e)}")
    
    async def fund_transfer(self, recipient: str, account: str, ifsc: str, amount: float) -> ActionResult:
        """Transfer money to another account"""
        try:
            # Navigate if needed
            await self.navigate_to_fund_transfer()
            
            # Fill transfer form
            await self.page.fill("#recipient-name", recipient)
            await self.page.fill("#recipient-account", account)
            await self.page.fill("#recipient-ifsc", ifsc)
            await self.page.fill("#transfer-amount", str(amount))
            
            # Click transfer button
            await self.page.click("#transfer-btn, button[type='submit']")
            
            # Wait for confirmation
            await self.page.wait_for_selector("#confirm-modal.active, .modal.confirm", timeout=3000)
            
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
        """Navigate to digital gold page"""
        try:
            await self.page.click("[data-action='buy-gold']")
            await self.page.wait_for_selector("#buy-gold-page.active, #gold-form", timeout=3000)
            
            return ActionResult(
                success=True,
                action="navigate",
                message="Navigated to Digital Gold page",
                screenshot=await self.take_screenshot()
            )
        except Exception as e:
            return ActionResult(False, "navigate", f"Navigation failed: {str(e)}")
    
    async def buy_gold(self, amount: float = None, grams: float = None) -> ActionResult:
        """Buy digital gold"""
        try:
            await self.navigate_to_buy_gold()
            
            if grams:
                # Switch to grams mode
                await self.page.click("[data-type='grams']")
                await self.page.fill("#gold-grams", str(grams))
            else:
                # Amount mode (default)
                await self.page.fill("#gold-amount", str(amount))
            
            # Click buy button
            await self.page.click("#buy-gold-btn, button[type='submit']")
            
            # Wait for confirmation
            await self.page.wait_for_selector("#confirm-modal.active, .modal.confirm", timeout=3000)
            
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
            await self.page.click("#confirm-proceed-btn")
            
            # Wait for success modal
            await self.page.wait_for_selector("#success-modal.active, .modal.success", timeout=10000)
            
            success_message = await self.page.text_content("#success-message, .modal.success p")
            
            return ActionResult(
                success=True,
                action="confirm",
                message=f"Action confirmed: {success_message}",
                screenshot=await self.take_screenshot()
            )
        
        except Exception as e:
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
