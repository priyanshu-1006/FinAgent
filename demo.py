"""
FinAgent Demo Script

A guided demo showcasing all features:
1. Voice/Text command input
2. Vision-based UI navigation
3. Conscious Pause for approvals
4. Error recovery
5. Real-time dashboard updates

Run: python demo.py
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
load_dotenv()

from src.agent.agent import FinAgent
from src.agent.config import config


DEMO_SCENARIOS = [
    {
        "name": "🔐 Login",
        "command": "login to my account",
        "description": "Agent navigates to bank and logs in automatically",
        "approval_needed": False
    },
    {
        "name": "💰 Check Balance",
        "command": "check my account balance",
        "description": "Agent reads balance from dashboard using Vision AI",
        "approval_needed": False
    },
    {
        "name": "💡 Pay Electricity Bill",
        "command": "pay electricity bill of 1250 rupees to Adani Power",
        "description": "Agent fills payment form and pauses for approval",
        "approval_needed": True
    },
    {
        "name": "🥇 Buy Digital Gold",
        "command": "buy gold worth 1000 rupees",
        "description": "Agent navigates to gold section and prepares purchase",
        "approval_needed": True
    },
    {
        "name": "💸 Fund Transfer",
        "command": "transfer 2000 rupees to Mom",
        "description": "Agent selects beneficiary and prepares transfer",
        "approval_needed": True
    },
]


def print_header():
    """Print demo header"""
    print("\n" + "="*70)
    print("   🤖 FinAgent - AI-Powered Financial Automation Demo")
    print("   IIT Bombay Techfest × Jio Financial Services")
    print("="*70)
    print()
    print("   👁️  Vision AI:     Gemini 1.5 Flash (FREE)")
    print("   🌐 Browser:       Playwright")
    print("   🛡️  Safety:        Conscious Pause Mechanism")
    print("   🎤 Voice:         Web Speech API (FREE)")
    print()
    print("="*70)


def print_scenario(scenario: dict, index: int):
    """Print scenario details"""
    print(f"\n{'='*70}")
    print(f"   Demo {index + 1}: {scenario['name']}")
    print(f"{'='*70}")
    print(f"\n   📝 Command: \"{scenario['command']}\"")
    print(f"   📖 {scenario['description']}")
    if scenario['approval_needed']:
        print(f"   ⚠️  This action requires APPROVAL")
    print()


async def run_interactive_demo():
    """Run interactive demo"""
    print_header()
    
    print("📋 Available Demo Scenarios:")
    print("-" * 40)
    for i, scenario in enumerate(DEMO_SCENARIOS):
        approval = "⚠️" if scenario['approval_needed'] else "✅"
        print(f"   {i+1}. {scenario['name']} {approval}")
    print()
    print("   0. Run all demos")
    print("   q. Quit")
    print("-" * 40)
    
    agent = FinAgent()
    
    try:
        print("\n🚀 Starting FinAgent...")
        await agent.start()
        print("✅ Agent ready!")
        
        while True:
            choice = input("\n🎯 Enter scenario number (or 'q' to quit): ").strip()
            
            if choice.lower() == 'q':
                break
            
            if choice == '0':
                # Run all demos
                for i, scenario in enumerate(DEMO_SCENARIOS):
                    print_scenario(scenario, i)
                    
                    input("   Press ENTER to execute...")
                    
                    result = await agent.execute(scenario['command'])
                    
                    print(f"\n   📊 Result: {result['status']}")
                    print(f"   📈 Steps completed: {result['steps_completed']}/{result['total_steps']}")
                    
                    await asyncio.sleep(1)
            
            elif choice.isdigit() and 1 <= int(choice) <= len(DEMO_SCENARIOS):
                scenario = DEMO_SCENARIOS[int(choice) - 1]
                print_scenario(scenario, int(choice) - 1)
                
                input("   Press ENTER to execute...")
                
                result = await agent.execute(scenario['command'])
                
                print(f"\n   📊 Result: {result['status']}")
                print(f"   📈 Steps completed: {result['steps_completed']}/{result['total_steps']}")
            
            else:
                print("   ⚠️ Invalid choice. Enter a number 0-5 or 'q'.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    
    finally:
        print("\n🛑 Stopping agent...")
        await agent.stop()
        print("👋 Demo completed!")


async def run_quick_demo():
    """Run quick automated demo"""
    print_header()
    print("\n🎬 Running Quick Demo (Automated)")
    print("-" * 40)
    
    agent = FinAgent()
    
    try:
        await agent.start()
        
        # Quick demo commands
        demo_commands = [
            ("Login", "login to my account"),
            ("Balance", "check my balance"),
            ("Bill Pay", "pay electricity bill of 500 rupees"),
        ]
        
        for name, command in demo_commands:
            print(f"\n▶️  {name}: {command}")
            result = await agent.execute(command)
            
            status_emoji = "✅" if result['status'] == 'completed' else "⚠️"
            print(f"   {status_emoji} {result['status']}")
            
            await asyncio.sleep(1)
        
        print("\n" + "="*70)
        print("   ✅ Quick demo completed!")
        print("="*70)
    
    finally:
        await agent.stop()


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        asyncio.run(run_quick_demo())
    else:
        asyncio.run(run_interactive_demo())


if __name__ == "__main__":
    main()
