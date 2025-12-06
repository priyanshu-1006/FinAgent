"""
FinAgent - Main Entry Point

Run with: python main.py [mode]

Modes:
  cli      - Interactive command-line interface
  server   - Start FastAPI server for dashboard
  demo     - Run demo sequence
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agent.agent import FinAgent, run_cli


async def run_demo():
    """Run a demo sequence"""
    
    print("="*60)
    print("🎯 FinAgent Demo - IIT Bombay Techfest Hackathon")
    print("="*60)
    
    agent = FinAgent()
    
    try:
        await agent.start()
        
        # Demo commands
        demo_commands = [
            "login to my account",
            "check my account balance",
            "pay electricity bill of 1250 rupees to Adani",
            # "transfer 2000 rupees to Mom",
            # "buy gold worth 1000 rupees"
        ]
        
        for cmd in demo_commands:
            print(f"\n{'='*60}")
            print(f"📝 Demo Command: {cmd}")
            print("="*60)
            
            result = await agent.execute(cmd)
            
            print(f"\n📊 Status: {result['status']}")
            print(f"   Steps: {result['steps_completed']}/{result['total_steps']}")
            
            # Wait between commands
            await asyncio.sleep(2)
        
        print("\n" + "="*60)
        print("✅ Demo completed!")
        print("="*60)
        
    finally:
        await agent.stop()


async def run_server():
    """Start the FastAPI server"""
    
    try:
        import uvicorn
        from src.backend.server import app
        
        print("🌐 Starting FinAgent Server...")
        print("   Dashboard: http://localhost:8000")
        print("   API Docs:  http://localhost:8000/docs")
        
        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
        
    except ImportError:
        print("❌ Server dependencies not installed.")
        print("   Run: pip install fastapi uvicorn")


def main():
    """Main entry point"""
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "cli"
    
    print(f"\n🤖 FinAgent - Mode: {mode.upper()}\n")
    
    if mode == "cli":
        asyncio.run(run_cli())
    
    elif mode == "demo":
        asyncio.run(run_demo())
    
    elif mode == "server":
        asyncio.run(run_server())
    
    else:
        print(f"Unknown mode: {mode}")
        print("Available modes: cli, server, demo")
        sys.exit(1)


if __name__ == "__main__":
    main()
