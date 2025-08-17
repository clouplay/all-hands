from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import logging
from typing import Dict, List
import os

from core.agent_manager import AgentManager
from core.session_manager import SessionManager
from api.routes import router
from api.websocket_handler import WebSocketHandler

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Aieditor API",
    description="AI-powered code editor backend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global managers
agent_manager = AgentManager()
session_manager = SessionManager()
websocket_handler = WebSocketHandler(agent_manager, session_manager)

# Inject managers into routes
import api.routes as routes_module
routes_module.agent_manager = agent_manager
routes_module.session_manager = session_manager

# API routes
app.include_router(router, prefix="/api/v1")

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time communication"""
    await websocket_handler.handle_connection(websocket, session_id)

@app.get("/")
async def root():
    return {"message": "Aieditor API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)