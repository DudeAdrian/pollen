"""
Consensus Client - Hive Consensus Submission
Submits proofs to Hive, receives validation, triggers Ledger rewards
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import httpx
import websockets

from .config import get_settings
from .utils.encryptor import DataEncryptor

logger = logging.getLogger(__name__)


class ProofStatus(Enum):
    PENDING = "pending"
    VALIDATING = "validating"
    APPROVED = "approved"
    REJECTED = "rejected"
    REWARDED = "rewarded"


@dataclass
class ProofSubmission:
    """Proof submitted to Hive"""
    proof_id: str
    agent_id: str
    activity_type: str
    proof_hash: str
    metadata: Dict[str, Any]
    submitted_at: str
    status: ProofStatus
    consensus_result: Optional[Dict] = None
    reward_tx_hash: Optional[str] = None


class ConsensusClient:
    """
    Manages proof submission to Hive Consciousness.
    Receives validation and triggers Ledger rewards.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.encryptor = DataEncryptor()
        self.http_client: Optional[httpx.AsyncClient] = None
        self.ws_connection: Optional[websockets.WebSocketClientProtocol] = None
        self.pending_proofs: Dict[str, ProofSubmission] = {}
        self.validation_callbacks: List[callable] = []
        self.reward_callbacks: List[callable] = []
        self._listener_task: Optional[asyncio.Task] = None
        
    async def initialize(self):
        """Initialize consensus client"""
        logger.info("🐝 Initializing Consensus Client")
        
        self.http_client = httpx.AsyncClient(
            base_url=self.settings.HIVE_URL,
            headers={"X-Hive-API-Key": self.settings.HIVE_API_KEY},
            timeout=30.0
        )
        
        # Start validation listener
        self._listener_task = asyncio.create_task(self._validation_listener())
        
        logger.info("✅ Consensus Client initialized")
    
    async def submit_proof(
        self,
        activity_type: str,
        proof_hash: str,
        value_score: float,
        metadata: Optional[Dict] = None
    ) -> ProofSubmission:
        """
        Submit proof-of-work to Hive for consensus validation
        
        Args:
            activity_type: Type of activity (wellness, creative, etc.)
            proof_hash: Zero-knowledge proof hash
            value_score: Calculated value of the activity
            metadata: Additional context
        """
        proof = ProofSubmission(
            proof_id=f"proof_{datetime.utcnow().timestamp()}",
            agent_id=self.settings.POLLEN_AGENT_NAME,
            activity_type=activity_type,
            proof_hash=proof_hash,
            metadata=metadata or {},
            submitted_at=datetime.utcnow().isoformat(),
            status=ProofStatus.PENDING
        )
        
        payload = {
            "type": "proof_submission",
            "proof_id": proof.proof_id,
            "agent_id": proof.agent_id,
            "activity_type": activity_type,
            "proof_hash": proof_hash,
            "value_score": value_score,
            "metadata": metadata,
            "timestamp": proof.submitted_at
        }
        
        try:
            response = await self.http_client.post(
                "/consensus/submit",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("accepted"):
                proof.status = ProofStatus.VALIDATING
                logger.info(f"📤 Proof submitted: {proof.proof_id}")
                logger.info(f"   Activity: {activity_type}")
                logger.info(f"   Value: {value_score} Honey")
            else:
                proof.status = ProofStatus.REJECTED
                logger.warning(f"⚠️  Proof rejected: {result.get('reason')}")
            
            self.pending_proofs[proof.proof_id] = proof
            
            return proof
            
        except Exception as e:
            logger.error(f"❌ Proof submission failed: {e}")
            proof.status = ProofStatus.REJECTED
            raise
    
    async def _validation_listener(self):
        """Listen for validation results from Hive"""
        while True:
            try:
                # Connect to Hive WebSocket for consensus updates
                ws_url = f"{self.settings.HIVE_WS_URL}/consensus"
                
                async with websockets.connect(ws_url) as ws:
                    logger.info("🔗 Connected to Hive consensus stream")
                    
                    async for message in ws:
                        try:
                            data = json.loads(message)
                            msg_type = data.get("type")
                            
                            if msg_type == "consensus_result":
                                await self._handle_consensus_result(data)
                            elif msg_type == "reward_confirmed":
                                await self._handle_reward_confirmation(data)
                                
                        except json.JSONDecodeError:
                            logger.warning("Invalid JSON in consensus stream")
                            
            except websockets.exceptions.ConnectionClosed:
                logger.warning("Consensus stream disconnected, reconnecting...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Consensus listener error: {e}")
                await asyncio.sleep(10)
    
    async def _handle_consensus_result(self, data: Dict):
        """Handle consensus validation result"""
        proof_id = data.get("proof_id")
        result = data.get("result")
        
        if proof_id not in self.pending_proofs:
            logger.warning(f"Unknown proof ID: {proof_id}")
            return
        
        proof = self.pending_proofs[proof_id]
        proof.consensus_result = data
        
        if result == "approved":
            proof.status = ProofStatus.APPROVED
            logger.info(f"✅ Proof approved by consensus: {proof_id}")
            logger.info(f"   Confidence: {data.get('confidence', 0):.2f}")
            logger.info(f"   Validating nodes: {data.get('validator_count', 0)}")
            
            # Notify callbacks
            for callback in self.validation_callbacks:
                try:
                    await callback(proof)
                except Exception as e:
                    logger.error(f"Validation callback error: {e}")
            
            # Trigger reward (if auto-reward enabled)
            await self._request_reward(proof)
            
        else:
            proof.status = ProofStatus.REJECTED
            logger.warning(f"❌ Proof rejected: {proof_id}")
            logger.warning(f"   Reason: {data.get('reason', 'unknown')}")
    
    async def _request_reward(self, proof: ProofSubmission):
        """Request Honey reward via Ledger"""
        logger.info(f"💰 Requesting reward for: {proof.proof_id}")
        
        payload = {
            "type": "reward_request",
            "proof_id": proof.proof_id,
            "agent_id": proof.agent_id,
            "activity_type": proof.activity_type,
            "value_score": proof.metadata.get("value_score", 0),
            "consensus_proof": proof.consensus_result
        }
        
        try:
            response = await self.http_client.post(
                "/ledger/reward",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("tx_hash"):
                proof.reward_tx_hash = result["tx_hash"]
                proof.status = ProofStatus.REWARDED
                logger.info(f"🎉 Reward confirmed! TX: {result['tx_hash'][:20]}...")
                
                # Notify reward callbacks
                for callback in self.reward_callbacks:
                    try:
                        await callback(proof, result)
                    except Exception as e:
                        logger.error(f"Reward callback error: {e}")
            
        except Exception as e:
            logger.error(f"Reward request failed: {e}")
    
    async def _handle_reward_confirmation(self, data: Dict):
        """Handle on-chain reward confirmation"""
        proof_id = data.get("proof_id")
        tx_hash = data.get("tx_hash")
        honey_amount = data.get("honey_amount")
        
        if proof_id in self.pending_proofs:
            proof = self.pending_proofs[proof_id]
            proof.reward_tx_hash = tx_hash
            proof.status = ProofStatus.REWARDED
            
            logger.info(f"⛓️  On-chain reward confirmed: {proof_id}")
            logger.info(f"   TX: {tx_hash}")
            logger.info(f"   Honey: {honey_amount}")
    
    async def check_consensus_status(self, proof_id: str) -> Optional[Dict]:
        """Check status of a proof in consensus"""
        if proof_id in self.pending_proofs:
            proof = self.pending_proofs[proof_id]
            return {
                "proof_id": proof.proof_id,
                "status": proof.status.value,
                "submitted_at": proof.submitted_at,
                "consensus_result": proof.consensus_result,
                "reward_tx_hash": proof.reward_tx_hash
            }
        
        # Try to fetch from Hive
        try:
            response = await self.http_client.get(f"/consensus/status/{proof_id}")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Status check failed: {e}")
        
        return None
    
    async def get_consensus_stats(self) -> Dict[str, Any]:
        """Get consensus participation statistics"""
        total = len(self.pending_proofs)
        
        by_status = {}
        for proof in self.pending_proofs.values():
            status = proof.status.value
            by_status[status] = by_status.get(status, 0) + 1
        
        total_rewards = sum(
            1 for p in self.pending_proofs.values()
            if p.reward_tx_hash
        )
        
        return {
            "total_proofs_submitted": total,
            "by_status": by_status,
            "total_rewards_confirmed": total_rewards,
            "success_rate": round((total_rewards / max(total, 1)) * 100, 1)
        }
    
    def on_validation(self, callback: callable):
        """Register callback for when proof is validated"""
        self.validation_callbacks.append(callback)
    
    def on_reward(self, callback: callable):
        """Register callback for when reward is confirmed"""
        self.reward_callbacks.append(callback)
    
    async def batch_submit_proofs(
        self,
        proofs: List[Dict[str, Any]]
    ) -> List[ProofSubmission]:
        """Submit multiple proofs in batch"""
        results = []
        
        for proof_data in proofs:
            try:
                proof = await self.submit_proof(
                    activity_type=proof_data["activity_type"],
                    proof_hash=proof_data["proof_hash"],
                    value_score=proof_data.get("value_score", 0),
                    metadata=proof_data.get("metadata", {})
                )
                results.append(proof)
            except Exception as e:
                logger.error(f"Batch proof submission failed: {e}")
        
        return results
    
    async def verify_on_chain(self, tx_hash: str) -> Dict[str, Any]:
        """Verify a reward transaction on-chain"""
        try:
            # Query Ledger for transaction
            response = await self.http_client.get(
                f"/ledger/tx/{tx_hash}"
            )
            response.raise_for_status()
            
            tx_data = response.json()
            
            return {
                "verified": True,
                "tx_hash": tx_hash,
                "block_number": tx_data.get("block_number"),
                "confirmations": tx_data.get("confirmations"),
                "honey_amount": tx_data.get("value"),
                "timestamp": tx_data.get("timestamp")
            }
            
        except Exception as e:
            logger.error(f"On-chain verification failed: {e}")
            return {
                "verified": False,
                "tx_hash": tx_hash,
                "error": str(e)
            }
    
    async def close(self):
        """Cleanup resources"""
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
        
        if self.http_client:
            await self.http_client.aclose()
        
        logger.info("🐝 Consensus Client shut down")
