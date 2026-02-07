"""
Hive Spawner - Pollen Agent Initialization
Handles WebSocket connection to sandironratio-node (Hive HQ)
"""

import asyncio
import json
import logging
from typing import Optional, Callable
import websockets
import httpx
from datetime import datetime

from .config import get_settings

logger = logging.getLogger(__name__)


class HiveSpawner:
    """
    Manages Pollen agent lifecycle within Hive Consciousness.
    Handles spawn, heartbeat, and task receipt from Hive.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.agent_id: Optional[str] = None
        self.is_connected: bool = False
        self.reconnect_attempts: int = 0
        self.task_handlers: list[Callable] = []
        self._shutdown: bool = False
        
    async def spawn(self) -> dict:
        """
        Initialize Pollen agent via Hive POST /spawn
        Returns spawn confirmation with agent credentials
        """
        logger.info(f"🌸 Spawning Pollen agent: {self.settings.POLLEN_AGENT_NAME}")
        
        spawn_payload = {
            "agent_type": "pollen",
            "agent_name": self.settings.POLLEN_AGENT_NAME,
            "capabilities": {
                "wellness": self.settings.ENABLE_WELLNESS_AGENT,
                "creative": self.settings.ENABLE_CREATIVE_AGENT,
                "social": self.settings.ENABLE_SOCIAL_AGENT,
                "technical": self.settings.ENABLE_TECHNICAL_AGENT,
                "admin": self.settings.ENABLE_ADMIN_AGENT
            },
            "timestamp": datetime.utcnow().isoformat(),
            "version": "v1.0.0-production-ready"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.settings.HIVE_URL}/spawn",
                    json=spawn_payload,
                    headers={"X-Hive-API-Key": self.settings.HIVE_API_KEY},
                    timeout=30.0
                )
                response.raise_for_status()
                
                spawn_data = response.json()
                self.agent_id = spawn_data.get("agent_id")
                
                logger.info(f"✅ Spawned successfully as agent: {self.agent_id}")
                logger.info(f"🐝 Assigned bee role: {spawn_data.get('bee_role', 'worker')}")
                
                return spawn_data
                
        except Exception as e:
            logger.error(f"❌ Spawn failed: {e}")
            raise
    
    async def connect_websocket(self):
        """Establish persistent WebSocket connection to Hive"""
        if not self.agent_id:
            raise RuntimeError("Must spawn before connecting WebSocket")
        
        ws_url = f"{self.settings.HIVE_WS_URL}/{self.agent_id}"
        
        while not self._shutdown and self.reconnect_attempts < self.settings.HIVE_MAX_RECONNECT_ATTEMPTS:
            try:
                logger.info(f"🔗 Connecting to Hive WebSocket: {ws_url}")
                
                self.ws = await websockets.connect(
                    ws_url,
                    extra_headers={"X-Agent-ID": self.agent_id}
                )
                
                self.is_connected = True
                self.reconnect_attempts = 0
                
                logger.info("✅ Connected to Hive Consciousness")
                
                # Start message handler
                await self._handle_messages()
                
            except websockets.exceptions.ConnectionClosed:
                logger.warning("🔌 Hive connection closed, reconnecting...")
                self.is_connected = False
                
            except Exception as e:
                logger.error(f"❌ WebSocket error: {e}")
                self.is_connected = False
            
            if not self._shutdown:
                self.reconnect_attempts += 1
                wait_time = min(self.settings.HIVE_RECONNECT_INTERVAL * self.reconnect_attempts, 60)
                logger.info(f"⏳ Reconnecting in {wait_time}s (attempt {self.reconnect_attempts})")
                await asyncio.sleep(wait_time)
        
        if self.reconnect_attempts >= self.settings.HIVE_MAX_RECONNECT_ATTEMPTS:
            logger.error("❌ Max reconnection attempts reached")
            raise ConnectionError("Failed to maintain Hive connection")
    
    async def _handle_messages(self):
        """Handle incoming WebSocket messages from Hive"""
        try:
            async for message in self.ws:
                try:
                    data = json.loads(message)
                    msg_type = data.get("type")
                    
                    if msg_type == "task":
                        logger.info(f"📋 Received task from Hive: {data.get('task_type')}")
                        await self._handle_task(data)
                        
                    elif msg_type == "heartbeat":
                        await self._send_heartbeat_response()
                        
                    elif msg_type == "consensus":
                        logger.info(f"✅ Consensus received: {data.get('result')}")
                        await self._handle_consensus(data)
                        
                    elif msg_type == "graduation":
                        logger.info("🎓 Graduation signal received!")
                        await self._handle_graduation(data)
                        
                    else:
                        logger.debug(f"📨 Received: {msg_type}")
                        
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received: {message}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Message handler connection closed")
    
    async def _handle_task(self, data: dict):
        """Process task from Hive"""
        task = {
            "id": data.get("task_id"),
            "type": data.get("task_type"),
            "payload": data.get("payload"),
            "priority": data.get("priority", "normal"),
            "source": "hive"
        }
        
        # Notify all registered handlers
        for handler in self.task_handlers:
            try:
                await handler(task)
            except Exception as e:
                logger.error(f"Task handler error: {e}")
        
        # Acknowledge receipt
        await self._send_ack(task["id"])
    
    async def _send_heartbeat_response(self):
        """Respond to Hive heartbeat"""
        if self.ws and self.is_connected:
            await self.ws.send(json.dumps({
                "type": "heartbeat_ack",
                "agent_id": self.agent_id,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "healthy"
            }))
    
    async def _send_ack(self, task_id: str):
        """Acknowledge task receipt"""
        if self.ws and self.is_connected:
            await self.ws.send(json.dumps({
                "type": "task_ack",
                "agent_id": self.agent_id,
                "task_id": task_id,
                "timestamp": datetime.utcnow().isoformat()
            }))
    
    async def _handle_consensus(self, data: dict):
        """Handle consensus validation from Hive"""
        logger.info(f"Consensus for task {data.get('task_id')}: {data.get('result')}")
        # Forward to consensus client for reward processing
        
    async def _handle_graduation(self, data: dict):
        """Handle graduation ceremony trigger"""
        logger.info(f"Graduation to Level {data.get('new_level')}!")
        # Trigger wallet creation ceremony
        
    async def submit_proof(self, task_id: str, proof: dict) -> dict:
        """Submit proof-of-work to Hive for consensus validation"""
        payload = {
            "type": "proof",
            "agent_id": self.agent_id,
            "task_id": task_id,
            "proof": proof,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.settings.HIVE_URL}/consensus/proof",
                    json=payload,
                    headers={"X-Hive-API-Key": self.settings.HIVE_API_KEY},
                    timeout=30.0
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"✅ Proof submitted: {result.get('consensus_status')}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Proof submission failed: {e}")
            raise
    
    def on_task(self, handler: Callable):
        """Register task handler callback"""
        self.task_handlers.append(handler)
        return handler
    
    async def disconnect(self):
        """Gracefully disconnect from Hive"""
        self._shutdown = True
        self.is_connected = False
        
        if self.ws:
            await self.ws.close()
            logger.info("🔌 Disconnected from Hive")
    
    async def __aenter__(self):
        await self.spawn()
        asyncio.create_task(self.connect_websocket())
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
