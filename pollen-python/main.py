"""
Pollen AI Agent - Main API Server
Port 9000 - Comprehensive sovereign AI agent
"""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import Pollen modules
from src.pollen.config import get_settings
from src.pollen.agent_core import PollenAgent
from src.pollen.spawner import HiveSpawner
from src.pollen.engines.wellness_engine import WellnessEngine, WellnessProof
from src.pollen.engines.creator_engine import CreatorEngine, ContentType
from src.pollen.engines.social_manager import SocialManager, Platform
from src.pollen.engines.shadow_accumulator import ShadowAccumulator, ActivityType
from src.pollen.consensus_client import ConsensusClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/pollen.log')
    ]
)
logger = logging.getLogger(__name__)

# Global instances
settings = get_settings()
agent: Optional[PollenAgent] = None
spawner: Optional[HiveSpawner] = None
wellness_engine: Optional[WellnessEngine] = None
creator_engine: Optional[CreatorEngine] = None
social_manager: Optional[SocialManager] = None
shadow_accumulator: Optional[ShadowAccumulator] = None
consensus_client: Optional[ConsensusClient] = None


# Pydantic models
class SpawnRequest(BaseModel):
    agent_name: str = Field(default="pollen-agent-001")
    capabilities: Dict[str, bool] = Field(default_factory=dict)


class TaskExecuteRequest(BaseModel):
    task_type: str = Field(..., description="Type of task to execute")
    payload: Dict[str, Any] = Field(default_factory=dict)
    require_consent: bool = Field(default=True)


class CreateRequest(BaseModel):
    content_type: str = Field(..., description="Type of content to create")
    prompt: str = Field(..., description="Creation prompt")
    style: Optional[str] = Field(default=None)
    options: Dict[str, Any] = Field(default_factory=dict)


class PublishRequest(BaseModel):
    creation_id: str = Field(..., description="ID of creation to publish")
    platform: Optional[str] = Field(default=None)


class ProofSubmitRequest(BaseModel):
    activity_type: str
    proof_hash: str
    value_score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global agent, spawner, wellness_engine, creator_engine
    global social_manager, shadow_accumulator, consensus_client
    
    logger.info("🌸 Starting Pollen AI Agent")
    
    # Initialize all components
    agent = PollenAgent()
    await agent.initialize()
    
    wellness_engine = WellnessEngine()
    await wellness_engine.initialize()
    
    creator_engine = CreatorEngine()
    await creator_engine.initialize()
    
    social_manager = SocialManager()
    await social_manager.initialize()
    
    shadow_accumulator = ShadowAccumulator()
    await shadow_accumulator.initialize()
    
    consensus_client = ConsensusClient()
    await consensus_client.initialize()
    
    # Connect to Hive
    spawner = HiveSpawner()
    await spawner.spawn()
    
    # Register task handler
    spawner.on_task(handle_hive_task)
    asyncio.create_task(spawner.connect_websocket())
    
    # Register consensus callbacks
    consensus_client.on_validation(on_proof_validated)
    consensus_client.on_reward(on_reward_confirmed)
    
    logger.info(f"✅ Pollen operational on port {settings.POLLEN_PORT}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Pollen")
    await agent.close()
    await wellness_engine.close()
    await creator_engine.close()
    await social_manager.close()
    await shadow_accumulator.close()
    await consensus_client.close()
    await spawner.disconnect()


app = FastAPI(
    title="Pollen AI Agent",
    description="Sovereign AI Agent within Terracare Ecosystem",
    version="v1.0.0-production-ready",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def handle_hive_task(task: Dict[str, Any]):
    """Handle tasks received from Hive"""
    logger.info(f"📋 Executing Hive task: {task['type']}")
    
    # Route to appropriate engine
    if task["type"] == "wellness_protocol":
        result = await wellness_engine.execute_protocol(
            task["payload"]["protocol_id"]
        )
    elif task["type"] == "create_content":
        result = await creator_engine.generate_website(
            task["payload"]["title"],
            task["payload"]["content"]
        )
    elif task["type"] == "social_post":
        result = await social_manager.create_post(
            task["payload"]["content_type"],
            task["payload"]["context"],
            Platform(task["payload"]["platform"])
        )
    else:
        result = {"status": "unknown_task", "task": task}
    
    # Submit proof
    proof_hash = result.get("proof_hash", "")
    if proof_hash:
        await consensus_client.submit_proof(
            activity_type=task["type"],
            proof_hash=proof_hash,
            value_score=result.get("value_score", 10),
            metadata={"task_id": task["id"]}
        )


async def on_proof_validated(proof):
    """Callback when proof is validated by Hive"""
    # Add to shadow accumulator
    await shadow_accumulator.add_entry(
        activity_type=ActivityType(proof.activity_type.split("_")[0]),
        description=f"Validated {proof.activity_type}",
        honey_value=proof.metadata.get("value_score", 0),
        proof_hash=proof.proof_hash
    )


async def on_reward_confirmed(proof, result):
    """Callback when reward is confirmed"""
    logger.info(f"🎉 Reward confirmed: {result.get('honey_amount')} Honey")


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "pollen-ai-agent",
        "version": "v1.0.0-production-ready",
        "timestamp": datetime.utcnow().isoformat(),
        "agent_id": spawner.agent_id if spawner else None,
        "hive_connected": spawner.is_connected if spawner else False,
        "components": {
            "agent": agent is not None,
            "wellness": wellness_engine is not None,
            "creator": creator_engine is not None,
            "social": social_manager is not None,
            "shadow": shadow_accumulator is not None,
            "consensus": consensus_client is not None
        }
    }


@app.post("/spawn")
async def spawn_agent(request: SpawnRequest):
    """
    POST /spawn - Hive initiation
    Initialize or respawn agent with Hive
    """
    global spawner
    
    try:
        if spawner:
            await spawner.disconnect()
        
        spawner = HiveSpawner()
        result = await spawner.spawn()
        
        # Start WebSocket connection
        asyncio.create_task(spawner.connect_websocket())
        
        return {
            "success": True,
            "agent_id": result.get("agent_id"),
            "bee_role": result.get("bee_role"),
            "hive_status": "connected",
            "capabilities": result.get("capabilities"),
            "message": "Pollen agent spawned successfully"
        }
        
    except Exception as e:
        logger.error(f"Spawn failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/task/execute")
async def execute_task(request: TaskExecuteRequest):
    """
    POST /task/execute - Execute task from Hive or Sofie
    Tasks: "build website", "post content", "analyze biometrics"
    """
    try:
        # Use agent to decide execution
        decision = await agent.decide(
            context=f"Execute task: {request.task_type} with payload: {request.payload}",
            available_actions=["create_content", "wellness_check", "social_post", "ask_user"],
            user_preferences={"auto_execute": settings.AUTO_EXECUTE_TASKS}
        )
        
        if decision.requires_consent and request.require_consent:
            return {
                "status": "consent_required",
                "decision": decision.__dict__,
                "message": "User consent required before execution"
            }
        
        # Execute based on decision
        result = {"action": decision.action, "status": "completed"}
        
        if decision.action == "create_content":
            creation = await creator_engine.generate_website(
                request.payload.get("title", "Untitled"),
                request.payload.get("content", "")
            )
            result["creation_id"] = creation.creation_id
            result["proof_hash"] = creation.proof_hash
            
        elif decision.action == "wellness_check":
            analysis = await wellness_engine.analyze_wellness_status()
            result["wellness_status"] = analysis
            
        elif decision.action == "social_post":
            post = await social_manager.create_post(
                request.payload.get("content_type", "wellness"),
                request.payload.get("context", {}),
                Platform(request.payload.get("platform", "twitter"))
            )
            result["post_id"] = post.post_id
        
        return {
            "success": True,
            "task_type": request.task_type,
            "decision": decision.__dict__,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Task execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/create")
async def create_content(request: CreateRequest):
    """
    POST /create - User direct creation request
    "Generate image of my wellness journey", etc.
    """
    try:
        creation = None
        
        if request.content_type == "website":
            creation = await creator_engine.generate_website(
                request.prompt,
                request.options.get("content", ""),
                request.options.get("template", "portfolio")
            )
        elif request.content_type == "mobile_app":
            creation = await creator_engine.generate_mobile_app(
                request.prompt,
                request.options.get("platform", "react_native")
            )
        elif request.content_type == "document":
            creation = await creator_engine.generate_document(
                request.prompt,
                request.options.get("content", ""),
                request.options.get("format", "markdown")
            )
        elif request.content_type == "image":
            creation = await creator_engine.generate_image(
                request.prompt,
                request.style or "photorealistic"
            )
        elif request.content_type == "code":
            creation = await creator_engine.generate_code(
                request.prompt,
                request.options.get("language", "python")
            )
        elif request.content_type == "audio":
            creation = await creator_engine.generate_frequency_composition(
                request.options.get("frequencies", [432, 528]),
                request.options.get("duration", 300)
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown content type: {request.content_type}")
        
        # Submit proof for reward
        if creation and creation.proof_hash:
            asyncio.create_task(consensus_client.submit_proof(
                activity_type=f"creative_{request.content_type}",
                proof_hash=creation.proof_hash,
                value_score=50,  # Base creative reward
                metadata={"creation_type": request.content_type}
            ))
        
        return {
            "success": True,
            "creation_id": creation.creation_id if creation else None,
            "content_type": request.content_type,
            "title": creation.title if creation else None,
            "proof_hash": creation.proof_hash if creation else None,
            "encrypted_path": creation.encrypted_path if creation else None,
            "message": f"{request.content_type} created and encrypted in vault"
        }
        
    except Exception as e:
        logger.error(f"Creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/publish")
async def publish_content(request: PublishRequest):
    """
    POST /publish - User approves release of encrypted content
    """
    try:
        # Get creation
        creation = await creator_engine.get_creation(request.creation_id)
        
        if not creation:
            raise HTTPException(status_code=404, detail="Creation not found")
        
        # Prepare for publish
        preview = await creator_engine.prepare_for_publish(request.creation_id)
        
        # If platform specified, publish there
        if request.platform:
            post = await social_manager.create_post(
                "creative",
                {"creation_type": creation.content_type.value, "title": creation.title},
                Platform(request.platform)
            )
            await social_manager.approve_post(post.post_id)
            preview["social_post_id"] = post.post_id
        
        return {
            "success": True,
            "creation_id": request.creation_id,
            "preview": preview,
            "published_to": request.platform,
            "message": "Content approved for publishing"
        }
        
    except Exception as e:
        logger.error(f"Publish failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    """
    GET /status - Shadow balance, pending tasks, creation queue
    """
    try:
        # Get shadow balance
        shadow = await shadow_accumulator.get_balance()
        
        # Get pending posts
        pending_posts = await social_manager.get_pending_posts()
        
        # Get creations
        creations = await creator_engine.list_creations()
        
        # Get wellness summary
        wellness = await wellness_engine.get_wellness_summary()
        
        # Get consensus stats
        consensus = await consensus_client.get_consensus_stats()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": spawner.agent_id if spawner else None,
            "shadow_balance": shadow,
            "pending_posts": pending_posts,
            "creation_queue": len(creations),
            "wellness_summary": wellness,
            "consensus_stats": consensus,
            "hive_connected": spawner.is_connected if spawner else False
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/wellness/status")
async def get_wellness_status():
    """Get detailed wellness status"""
    return await wellness_engine.get_wellness_summary()


@app.post("/wellness/protocol/{protocol_id}")
async def execute_wellness_protocol(protocol_id: str):
    """Execute a wellness protocol"""
    result = await wellness_engine.execute_protocol(protocol_id)
    
    # Submit proof
    if "proof" in result:
        await consensus_client.submit_proof(
            activity_type=f"wellness_{protocol_id}",
            proof_hash=result["proof"]["biometric_hash"],
            value_score=result["value_score"],
            metadata={"protocol": protocol_id}
        )
    
    return result


@app.get("/creations")
async def list_creations(content_type: Optional[str] = None):
    """List all creations"""
    ct = ContentType(content_type) if content_type else None
    return await creator_engine.list_creations(ct)


@app.get("/creations/{creation_id}")
async def get_creation(creation_id: str):
    """Get specific creation"""
    creation = await creator_engine.get_creation(creation_id)
    if not creation:
        raise HTTPException(status_code=404, detail="Creation not found")
    return {
        "creation_id": creation.creation_id,
        "content_type": creation.content_type.value,
        "title": creation.title,
        "metadata": creation.metadata,
        "created_at": creation.created_at,
        "proof_hash": creation.proof_hash
    }


@app.post("/consensus/proof")
async def submit_proof(request: ProofSubmitRequest):
    """Submit proof to Hive consensus"""
    proof = await consensus_client.submit_proof(
        activity_type=request.activity_type,
        proof_hash=request.proof_hash,
        value_score=request.value_score,
        metadata=request.metadata
    )
    
    return {
        "success": True,
        "proof_id": proof.proof_id,
        "status": proof.status.value,
        "submitted_at": proof.submitted_at
    }


@app.get("/consensus/proof/{proof_id}")
async def get_proof_status(proof_id: str):
    """Check proof status"""
    status = await consensus_client.check_consensus_status(proof_id)
    if not status:
        raise HTTPException(status_code=404, detail="Proof not found")
    return status


@app.post("/shadow/graduation")
async def trigger_graduation():
    """Manually trigger graduation ceremony"""
    try:
        result = await shadow_accumulator.trigger_graduation()
        return {
            "success": True,
            "ceremony": result,
            "message": "Graduation complete! Welcome to Level 2."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/shadow/history")
async def get_shadow_history(limit: int = 50):
    """Get shadow entry history"""
    return await shadow_accumulator.get_history(limit=limit)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    
    try:
        while True:
            # Send status updates every 30 seconds
            status = await get_status()
            await websocket.send_json({
                "type": "status_update",
                "data": status
            })
            await asyncio.sleep(30)
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.POLLEN_HOST,
        port=settings.POLLEN_PORT,
        log_level=settings.POLLEN_LOG_LEVEL,
        reload=settings.POLLEN_ENV == "development"
    )
