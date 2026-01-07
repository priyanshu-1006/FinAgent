"""
FinAgent Backend Server

FastAPI server providing:
- REST API for agent control
- WebSocket for real-time updates
- Serves the user dashboard
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.agent.agent import FinAgent
from src.agent.conscious_pause import ApprovalRequest


# ===== Pydantic Models =====

class CommandRequest(BaseModel):
    command: str

class ApprovalResponse(BaseModel):
    request_id: str
    approved: bool

class StatusResponse(BaseModel):
    is_running: bool
    session_start: Optional[str]
    commands_executed: int
    is_logged_in: bool
    current_url: str
    pending_approvals: list
    recent_history: list


# ===== WebSocket Manager =====

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Send message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                self.disconnect(connection)
    
    async def send_status(self, status: str):
        await self.broadcast({"type": "status", "message": status, "timestamp": datetime.now().isoformat()})
    
    async def send_screenshot(self, screenshot: str):
        await self.broadcast({"type": "screenshot", "data": screenshot})
    
    async def send_approval_request(self, request: ApprovalRequest):
        await self.broadcast({
            "type": "approval_request",
            "data": request.to_dict()
        })
    
    async def send_task_update(self, task):
        await self.broadcast({
            "type": "task_update",
            "data": task.to_dict()
        })


# ===== Global State =====

manager = ConnectionManager()
agent: Optional[FinAgent] = None
pending_approval_events: Dict[str, asyncio.Event] = {}
approval_results: Dict[str, bool] = {}


# ===== Agent Callbacks =====

async def on_status_update(status: str):
    await manager.send_status(status)

async def on_screenshot(screenshot: str):
    await manager.send_screenshot(screenshot)

async def on_approval_request(request: ApprovalRequest) -> bool:
    """Handle approval request from agent"""
    
    # Send to UI
    await manager.send_approval_request(request)
    
    # Create event to wait for approval
    event = asyncio.Event()
    pending_approval_events[request.id] = event
    
    # Wait for approval (with timeout)
    try:
        await asyncio.wait_for(event.wait(), timeout=60)
        return approval_results.get(request.id, False)
    except asyncio.TimeoutError:
        return False
    finally:
        pending_approval_events.pop(request.id, None)
        approval_results.pop(request.id, None)

async def on_task_update(task):
    await manager.send_task_update(task)


# ===== App Lifecycle =====

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global agent
    
    # Startup
    print("🚀 Starting FinAgent Server...")
    agent = FinAgent()
    
    # Set callbacks
    agent.on_status_update = on_status_update
    agent.on_screenshot = on_screenshot
    agent.on_approval_request = on_approval_request
    agent.on_task_update = on_task_update
    
    yield
    
    # Shutdown
    if agent and agent.is_running:
        await agent.stop()
    print("👋 Server stopped")


# ===== FastAPI App =====

app = FastAPI(
    title="FinAgent API",
    description="AI-powered Financial Automation Agent",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== REST Endpoints =====

@app.get("/")
async def root():
    """Serve dashboard"""
    dashboard_path = os.path.join(
        os.path.dirname(__file__), 
        "..", "frontend", "index.html"
    )
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return {"message": "FinAgent API", "docs": "/docs"}


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and container orchestration"""
    import platform
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "checks": {
            "agent_initialized": agent is not None,
            "agent_running": agent.is_running if agent else False,
            "browser_connected": agent.browser.page is not None if agent and agent.is_running else False,
        },
        "system": {
            "python_version": platform.python_version(),
            "platform": platform.system(),
        }
    }
    
    # Determine overall health
    if not agent:
        health_status["status"] = "degraded"
        health_status["message"] = "Agent not initialized"
    
    return health_status


@app.get("/ready")
async def readiness_check():
    """Readiness probe - checks if the service is ready to accept traffic"""
    if agent and agent.is_running:
        return {"ready": True}
    return {"ready": False, "reason": "Agent not running"}


@app.post("/api/start")
async def start_agent():
    """Start the agent"""
    global agent
    
    if agent.is_running:
        return {"status": "already_running"}
    
    await agent.start()
    return {"status": "started"}


@app.post("/api/stop")
async def stop_agent():
    """Stop the agent"""
    global agent
    
    if not agent.is_running:
        return {"status": "not_running"}
    
    await agent.stop()
    return {"status": "stopped"}


@app.get("/api/status")
async def get_status():
    """Get agent status"""
    global agent
    
    if not agent:
        return {"is_running": False}
    
    return await agent.get_status()


@app.post("/api/execute")
async def execute_command(request: CommandRequest):
    """Execute a natural language command"""
    global agent
    
    if not agent or not agent.is_running:
        # Auto-start agent
        await agent.start()
    
    result = await agent.execute(request.command)
    return result


@app.post("/api/approve")
async def approve_action(response: ApprovalResponse):
    """Approve or reject a pending action"""
    global pending_approval_events, approval_results
    
    request_id = response.request_id
    
    if request_id not in pending_approval_events:
        raise HTTPException(status_code=404, detail="No pending approval with this ID")
    
    approval_results[request_id] = response.approved
    pending_approval_events[request_id].set()
    
    return {"status": "processed", "approved": response.approved}


@app.get("/api/screenshot")
async def get_screenshot():
    """Get current browser screenshot"""
    global agent
    
    if not agent or not agent.is_running:
        raise HTTPException(status_code=400, detail="Agent not running")
    
    screenshot = await agent.get_screenshot()
    return {"screenshot": screenshot}


@app.get("/api/tasks")
async def get_tasks():
    """Get all tasks"""
    global agent
    
    if not agent or not agent.orchestrator:
        return {"tasks": []}
    
    return {"tasks": agent.orchestrator.get_all_tasks()}


@app.get("/api/history")
async def get_history():
    """Get command history"""
    global agent
    
    if not agent:
        return {"history": []}
    
    return {"history": agent.command_history}


# ===== WebSocket Endpoint =====

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    
    await manager.connect(websocket)
    
    try:
        # Send initial status
        if agent:
            status = await agent.get_status()
            await websocket.send_json({
                "type": "initial_status",
                "data": status
            })
        
        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle WebSocket commands
            if message.get("type") == "execute":
                command = message.get("command")
                if command and agent:
                    # Auto-start agent if not running
                    if not agent.is_running:
                        await agent.start()
                    result = await agent.execute(command)
                    # Send result back through WebSocket
                    await websocket.send_json({
                        "type": "execute_result",
                        "data": result
                    })
            
            elif message.get("type") == "approve":
                request_id = message.get("request_id")
                approved = message.get("approved", False)
                if request_id in pending_approval_events:
                    approval_results[request_id] = approved
                    pending_approval_events[request_id].set()
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ===== Static Files =====

# Serve frontend assets
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
