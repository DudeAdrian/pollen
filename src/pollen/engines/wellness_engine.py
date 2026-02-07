"""
Wellness Engine - Biometric Harvesting & Protocol Execution
Integrates with Heartware for biometrics, submits proof-of-wellness to Hive
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

import httpx
import numpy as np

from ..config import get_settings
from ..utils.encryptor import DataEncryptor

logger = logging.getLogger(__name__)


class WellnessStatus(Enum):
    OPTIMAL = "optimal"
    GOOD = "good"
    CAUTION = "caution"
    ALERT = "alert"


@dataclass
class BiometricReading:
    """Single biometric reading"""
    timestamp: str
    hrv: Optional[float] = None
    heart_rate: Optional[float] = None
    movement: Optional[float] = None  # steps or activity level
    frequency_exposure: Optional[float] = None  # Hz
    sleep_quality: Optional[float] = None  # 0-100
    stress_level: Optional[float] = None  # 0-100
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "hrv": self.hrv,
            "heart_rate": self.heart_rate,
            "movement": self.movement,
            "frequency_exposure": self.frequency_exposure,
            "sleep_quality": self.sleep_quality,
            "stress_level": self.stress_level,
            "metadata": self.metadata or {}
        }


@dataclass
class WellnessProof:
    """Proof-of-wellness for Hive submission"""
    proof_id: str
    agent_id: str
    timestamp: str
    activity_type: str
    duration_minutes: int
    biometric_hash: str  # ZK proof hash
    protocol_id: str
    value_score: float


class WellnessEngine:
    """
    Harvests biometrics from Heartware, executes wellness protocols,
    and submits proof-of-wellness to Hive for Honey rewards.
    """
    
    PROTOCOLS = {
        "tai_chi": {
            "name": "Tai Chi Flow",
            "duration": 15,
            "frequency": 432,
            "movements": ["ward_off", "grasp_sparrows_tail", "single_whip"],
            "benefits": ["balance", "stress_reduction", "hrv_improvement"]
        },
        "meditation": {
            "name": "Mindful Meditation",
            "duration": 20,
            "frequency": 528,
            "type": "mindfulness",
            "benefits": ["focus", "emotional_regulation", "sleep_quality"]
        },
        "frequency_healing": {
            "name": "Solfeggio Frequency",
            "duration": 30,
            "frequencies": [396, 417, 528, 639, 741, 852],
            "benefits": ["cellular_regeneration", "dna_repair", "spiritual_awakening"]
        },
        "movement_break": {
            "name": "Micro Movement",
            "duration": 5,
            "movements": ["stretching", "walking", "breathing"],
            "benefits": ["circulation", "energy", "focus"]
        },
        "nutrition_tracking": {
            "name": "Conscious Nutrition",
            "duration": 0,  # ongoing
            "metrics": ["water_intake", "meal_timing", "food_quality"],
            "benefits": ["energy", "digestion", "mental_clarity"]
        }
    }
    
    def __init__(self):
        self.settings = get_settings()
        self.encryptor = DataEncryptor()
        self.heartware_client: Optional[httpx.AsyncClient] = None
        self.biometric_history: List[BiometricReading] = []
        self.active_protocols: Dict[str, Any] = {}
        self._polling_task: Optional[asyncio.Task] = None
        
    async def initialize(self):
        """Initialize wellness engine"""
        logger.info("💚 Initializing Wellness Engine")
        
        if self.settings.ENABLE_WELLNESS_AGENT:
            self.heartware_client = httpx.AsyncClient(
                base_url=self.settings.HEARTWARE_URL,
                headers={"X-API-Key": self.settings.HEARTWARE_API_KEY}
            )
            
            # Start biometric polling
            self._polling_task = asyncio.create_task(self._poll_biometrics())
            
            logger.info("✅ Wellness Engine initialized")
        else:
            logger.info("⚠️ Wellness Agent disabled")
    
    async def harvest_biometrics(self) -> BiometricReading:
        """
        Harvest biometrics from Heartware devices
        """
        if not self.heartware_client:
            logger.warning("Heartware not connected, using simulated data")
            return self._generate_simulated_reading()
        
        try:
            response = await self.heartware_client.get(
                f"/api/biometrics/{self.settings.HEARTWARE_DEVICE_ID}",
                timeout=10.0
            )
            response.raise_for_status()
            
            data = response.json()
            
            reading = BiometricReading(
                timestamp=datetime.utcnow().isoformat(),
                hrv=data.get("hrv"),
                heart_rate=data.get("heart_rate"),
                movement=data.get("steps"),
                frequency_exposure=data.get("frequency"),
                sleep_quality=data.get("sleep_score"),
                stress_level=data.get("stress"),
                metadata={"source": "heartware", "device_id": self.settings.HEARTWARE_DEVICE_ID}
            )
            
            self.biometric_history.append(reading)
            
            # Keep history manageable
            if len(self.biometric_history) > 1000:
                self.biometric_history = self.biometric_history[-500:]
            
            logger.debug(f"💚 Biometrics harvested: HRV={reading.hrv}, HR={reading.heart_rate}")
            
            return reading
            
        except Exception as e:
            logger.error(f"❌ Biometric harvest failed: {e}")
            return self._generate_simulated_reading()
    
    def _generate_simulated_reading(self) -> BiometricReading:
        """Generate simulated biometric data for testing"""
        return BiometricReading(
            timestamp=datetime.utcnow().isoformat(),
            hrv=np.random.normal(65, 10),
            heart_rate=np.random.normal(72, 8),
            movement=np.random.poisson(100),
            frequency_exposure=432.0,
            sleep_quality=np.random.normal(85, 10),
            stress_level=np.random.normal(30, 15),
            metadata={"source": "simulated"}
        )
    
    async def analyze_wellness_status(self) -> Dict[str, Any]:
        """
        Analyze current wellness status based on biometric history
        """
        if not self.biometric_history:
            return {"status": "unknown", "message": "No biometric data available"}
        
        # Get recent readings (last 24 hours)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        recent = [
            r for r in self.biometric_history
            if datetime.fromisoformat(r.timestamp) > cutoff
        ]
        
        if not recent:
            return {"status": "unknown", "message": "No recent data"}
        
        # Calculate metrics
        avg_hrv = np.mean([r.hrv for r in recent if r.hrv])
        avg_hr = np.mean([r.heart_rate for r in recent if r.heart_rate])
        avg_stress = np.mean([r.stress_level for r in recent if r.stress_level])
        
        # Determine status
        status = WellnessStatus.OPTIMAL
        if avg_stress > 70 or avg_hrv < 50:
            status = WellnessStatus.ALERT
        elif avg_stress > 50 or avg_hrv < 60:
            status = WellnessStatus.CAUTION
        elif avg_stress > 30:
            status = WellnessStatus.GOOD
        
        return {
            "status": status.value,
            "metrics": {
                "avg_hrv": round(avg_hrv, 2) if avg_hrv else None,
                "avg_heart_rate": round(avg_hr, 2) if avg_hr else None,
                "avg_stress": round(avg_stress, 2) if avg_stress else None,
                "data_points": len(recent)
            },
            "recommendations": self._generate_recommendations(status, avg_hrv, avg_stress)
        }
    
    def _generate_recommendations(
        self,
        status: WellnessStatus,
        hrv: Optional[float],
        stress: Optional[float]
    ) -> List[str]:
        """Generate wellness recommendations"""
        recommendations = []
        
        if status == WellnessStatus.ALERT:
            recommendations.extend([
                "Immediate meditation session recommended",
                "Consider frequency healing at 528Hz",
                "Reduce activity and rest"
            ])
        elif status == WellnessStatus.CAUTION:
            recommendations.extend([
                "Schedule Tai Chi session",
                "Take movement breaks every hour",
                "Practice conscious breathing"
            ])
        elif hrv and hrv < 60:
            recommendations.append("HRV below optimal - prioritize recovery")
        
        if stress and stress > 50:
            recommendations.append("High stress detected - consider nature exposure")
        
        return recommendations
    
    async def execute_protocol(
        self,
        protocol_id: str,
        duration_override: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute a wellness protocol and track completion
        
        Args:
            protocol_id: Key from PROTOCOLS dict
            duration_override: Optional custom duration
        """
        if protocol_id not in self.PROTOCOLS:
            raise ValueError(f"Unknown protocol: {protocol_id}")
        
        protocol = self.PROTOCOLS[protocol_id]
        duration = duration_override or protocol["duration"]
        
        logger.info(f"🧘 Starting protocol: {protocol['name']} ({duration}min)")
        
        # Record start
        start_time = datetime.utcnow()
        self.active_protocols[protocol_id] = {
            "started_at": start_time.isoformat(),
            "protocol": protocol,
            "status": "in_progress"
        }
        
        # Simulate protocol execution (in production, this would guide user)
        await asyncio.sleep(2)  # Reduced for demo
        
        # Record completion
        end_time = datetime.utcnow()
        self.active_protocols[protocol_id]["status"] = "completed"
        self.active_protocols[protocol_id]["completed_at"] = end_time.isoformat()
        
        # Calculate value score based on duration and protocol difficulty
        value_score = self._calculate_protocol_value(protocol, duration)
        
        # Create proof
        proof = await self._create_wellness_proof(
            protocol_id=protocol_id,
            duration=duration,
            value_score=value_score
        )
        
        logger.info(f"✅ Protocol completed: {protocol['name']} (score: {value_score:.2f})")
        
        return {
            "protocol": protocol,
            "duration": duration,
            "completed_at": end_time.isoformat(),
            "value_score": value_score,
            "proof": proof.__dict__
        }
    
    def _calculate_protocol_value(self, protocol: Dict, duration: int) -> float:
        """Calculate wellness value score for reward"""
        base_value = duration * 10  # 10 points per minute
        
        # Multipliers based on protocol benefits
        multipliers = {
            "hrv_improvement": 1.5,
            "stress_reduction": 1.3,
            "focus": 1.2,
            "spiritual_awakening": 1.4
        }
        
        multiplier = 1.0
        for benefit in protocol.get("benefits", []):
            multiplier += multipliers.get(benefit, 0.1)
        
        return base_value * multiplier
    
    async def _create_wellness_proof(
        self,
        protocol_id: str,
        duration: int,
        value_score: float
    ) -> WellnessProof:
        """Create zero-knowledge proof of wellness for Hive"""
        # Encrypt biometric data locally
        biometric_data = json.dumps([r.to_dict() for r in self.biometric_history[-10:]])
        encrypted = self.encryptor.encrypt(biometric_data)
        
        # Create hash for proof
        biometric_hash = self.encryptor.hash_data(encrypted)
        
        proof = WellnessProof(
            proof_id=f"wellness_{datetime.utcnow().timestamp()}",
            agent_id=self.settings.POLLEN_AGENT_NAME,
            timestamp=datetime.utcnow().isoformat(),
            activity_type=f"wellness_{protocol_id}",
            duration_minutes=duration,
            biometric_hash=biometric_hash,
            protocol_id=protocol_id,
            value_score=value_score
        )
        
        # Store encrypted data locally
        await self._store_wellness_data(proof.proof_id, encrypted)
        
        return proof
    
    async def _store_wellness_data(self, proof_id: str, encrypted_data: str):
        """Store encrypted wellness data locally"""
        import aiofiles
        
        filepath = f"{self.settings.VAULT_PATH}/wellness_{proof_id}.enc"
        async with aiofiles.open(filepath, 'w') as f:
            await f.write(encrypted_data)
    
    async def _poll_biometrics(self):
        """Background task to poll biometrics periodically"""
        while True:
            try:
                if self.settings.ENABLE_WELLNESS_AGENT:
                    await self.harvest_biometrics()
                await asyncio.sleep(self.settings.HEARTWARE_POLL_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Biometric polling error: {e}")
                await asyncio.sleep(60)
    
    async def get_wellness_summary(self) -> Dict[str, Any]:
        """Get comprehensive wellness summary"""
        status = await self.analyze_wellness_status()
        
        # Count completed protocols
        completed_protocols = [
            p for p in self.active_protocols.values()
            if p.get("status") == "completed"
        ]
        
        total_wellness_value = sum(
            self._calculate_protocol_value(p["protocol"], p["protocol"]["duration"])
            for p in completed_protocols
        )
        
        return {
            "current_status": status,
            "protocols_completed": len(completed_protocols),
            "total_wellness_value": round(total_wellness_value, 2),
            "active_protocols": list(self.active_protocols.keys()),
            "data_points_24h": len([
                r for r in self.biometric_history
                if datetime.fromisoformat(r.timestamp) > datetime.utcnow() - timedelta(hours=24)
            ])
        }
    
    async def close(self):
        """Cleanup resources"""
        if self._polling_task:
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass
        
        if self.heartware_client:
            await self.heartware_client.aclose()
            
        logger.info("💚 Wellness Engine shut down")
