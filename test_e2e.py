"""
FinAgent End-to-End Test Script

Tests the complete workflow:
1. Start dummy bank server
2. Start FinAgent backend
3. Execute test commands
4. Verify results

Usage:
    python test_e2e.py
"""

import asyncio
import subprocess
import time
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agent.agent import FinAgent
from src.agent.config import config


async def test_vision_module():
    """Test if vision module initializes correctly"""
    print("\n" + "="*60)
    print("🧪 Test 1: Vision Module Initialization")
    print("="*60)
    
    try:
        from src.agent.vision import VisionModule
        vision = VisionModule()
        
        if vision.model:
            print("✅ Vision module initialized with Gemini")
            return True
        else:
            print("⚠️ Vision module initialized but no API key")
            print("   Set GEMINI_API_KEY in .env file")
            print("   Get free key at: https://aistudio.google.com/app/apikey")
            return False
    except Exception as e:
        print(f"❌ Vision module failed: {e}")
        return False


async def test_browser_automation():
    """Test browser automation"""
    print("\n" + "="*60)
    print("🧪 Test 2: Browser Automation")
    print("="*60)
    
    try:
        from src.agent.browser_automation import BrowserAutomation
        
        browser = BrowserAutomation()
        await browser.start()
        
        # Navigate to bank
        result = await browser.navigate(config.bank_url)
        
        if result.success:
            print(f"✅ Browser navigated to {config.bank_url}")
            
            # Take screenshot
            screenshot = await browser.take_screenshot()
            print(f"✅ Screenshot captured ({len(screenshot)} chars)")
            
            # Test vision click if available
            if browser.vision and browser.vision.model:
                print("   Testing vision-based click...")
                # This is just a test, won't actually click
                analysis = await browser.analyze_current_page()
                print(f"   👁️ Page analysis: {analysis.get('page_type', 'unknown')}")
        else:
            print(f"⚠️ Navigation issue: {result.message}")
            print("   Make sure dummy bank is running: python -m http.server 8080")
        
        await browser.stop()
        return result.success
        
    except Exception as e:
        print(f"❌ Browser automation failed: {e}")
        return False


async def test_intent_parser():
    """Test intent parsing"""
    print("\n" + "="*60)
    print("🧪 Test 3: Intent Parser")
    print("="*60)
    
    try:
        from src.agent.intent_parser import IntentParser
        
        parser = IntentParser(use_ai=True)
        
        test_commands = [
            ("check my balance", "check_balance"),
            ("pay electricity bill of 1500 rupees", "pay_bill"),
            ("transfer 5000 to Mom", "fund_transfer"),
            ("buy gold worth 2000", "buy_gold"),
            ("login to my account", "login"),
        ]
        
        all_passed = True
        for command, expected_action in test_commands:
            intent = parser.parse(command)
            passed = intent.action == expected_action
            status = "✅" if passed else "❌"
            print(f"   {status} '{command}' → {intent.action} (expected: {expected_action})")
            if not passed:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Intent parser failed: {e}")
        return False


async def test_conscious_pause():
    """Test conscious pause mechanism"""
    print("\n" + "="*60)
    print("🧪 Test 4: Conscious Pause Mechanism")
    print("="*60)
    
    try:
        from src.agent.conscious_pause import ConciousPause, ApprovalStatus
        
        pause = ConciousPause()
        
        # Test that high-risk actions require approval
        high_risk = ["pay_bill", "fund_transfer", "buy_gold"]
        low_risk = ["login", "check_balance", "view_transactions"]
        
        all_passed = True
        
        for action in high_risk:
            if pause.requires_approval(action):
                print(f"   ✅ {action} requires approval (correct)")
            else:
                print(f"   ❌ {action} should require approval")
                all_passed = False
        
        for action in low_risk:
            if not pause.requires_approval(action):
                print(f"   ✅ {action} does not require approval (correct)")
            else:
                print(f"   ⚠️ {action} unexpectedly requires approval")
        
        # Test approval request creation
        request = await pause.request_approval(
            action="buy_gold",
            parameters={"amount": 1000}
        )
        
        if request.id and request.risk_level:
            print(f"   ✅ Approval request created: {request.id}")
        else:
            print("   ❌ Approval request creation failed")
            all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Conscious pause test failed: {e}")
        return False


async def test_full_agent():
    """Test full agent workflow"""
    print("\n" + "="*60)
    print("🧪 Test 5: Full Agent Workflow")
    print("="*60)
    
    try:
        agent = FinAgent()
        
        print("   Starting agent...")
        await agent.start()
        
        if agent.is_running:
            print("   ✅ Agent started successfully")
        else:
            print("   ❌ Agent failed to start")
            return False
        
        # Test simple command (balance check - no approval needed)
        print("   Executing: 'check my balance'...")
        result = await agent.execute("check my balance")
        
        print(f"   Status: {result.get('status')}")
        print(f"   Steps: {result.get('steps_completed')}/{result.get('total_steps')}")
        
        # Stop agent
        await agent.stop()
        print("   ✅ Agent stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Full agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 FinAgent End-to-End Test Suite")
    print("="*60)
    print(f"   Bank URL: {config.bank_url}")
    print(f"   AI Provider: {config.ai_provider}")
    print(f"   Vision Enabled: {config.vision_enabled}")
    print("="*60)
    
    results = {}
    
    # Run tests
    results["vision"] = await test_vision_module()
    results["intent"] = await test_intent_parser()
    results["pause"] = await test_conscious_pause()
    results["browser"] = await test_browser_automation()
    results["agent"] = await test_full_agent()
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test}: {status}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All tests passed! Ready for demo.")
    else:
        print("\n⚠️ Some tests failed. Check configuration.")
        print("\nTroubleshooting:")
        print("1. Create .env file from .env.example")
        print("2. Set GEMINI_API_KEY (free at https://aistudio.google.com/app/apikey)")
        print("3. Start dummy bank: cd src/dummy-bank && python -m http.server 8080")
        print("4. Install Playwright browsers: playwright install chromium")


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(run_all_tests())
