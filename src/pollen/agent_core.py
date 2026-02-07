"""
Agent Core - Local LLM Integration for Autonomous Decision Making
Integrates with Ollama for local inference, guided by Sofie intelligence
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

import httpx
import ollama

from .config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class AgentDecision:
    """Represents a decision made by the agent"""
    action: str
    params: Dict[str, Any]
    confidence: float
    reasoning: str
    timestamp: str
    requires_consent: bool


class PollenAgent:
    """
    Core agent orchestrating all Pollen capabilities.
    Makes autonomous decisions using local LLM, guided by Sofie.
    """
    
    SYSTEM_PROMPT = """You are Pollen, a sovereign AI agent operating within the Terracare ecosystem.
Your purpose is to serve your user's wellness, creativity, and productivity while maintaining complete privacy.

CORE PRINCIPLES:
1. SOVEREIGNTY: All data is encrypted locally. Only zero-knowledge proofs leave the device.
2. WELLNESS FIRST: Prioritize activities that enhance user wellbeing.
3. CONSENT: When in doubt, ask for user approval before acting.
4. HIVE ALIGNMENT: Submit proof-of-work to Hive for consensus and rewards.
5. CONTINUOUS LEARNING: Improve from user feedback and Hive guidance.

CAPABILITIES:
- Wellness: Monitor biometrics, suggest protocols, track progress
- Creative: Generate content, code, designs, media
- Social: Manage social media presence autonomously
- Technical: Write code, manage IoT, automate tasks
- Administrative: Track rewards, manage schedule, prepare transactions

DECISION FORMAT:
Respond ONLY with valid JSON in this format:
{
    "action": "action_name",
    "params": {"key": "value"},
    "confidence": 0.95,
    "reasoning": "Brief explanation",
    "requires_consent": true/false
}

Available actions:
- wellness_check: Analyze biometrics, suggest intervention
- create_content: Generate media, code, or documents
- schedule_post: Queue social media content
- execute_code: Run technical task
- ask_user: Request clarification/consent
- submit_proof: Send proof to Hive for validation
"""
    
    def __init__(self):
        self.settings = get_settings()
        self.ollama_client = ollama.AsyncClient(host=self.settings.OLLAMA_HOST)
        self.sofie_client: Optional[httpx.AsyncClient] = None
        self.context_memory: List[Dict] = []
        self.decision_history: List[AgentDecision] = []
        
    async def initialize(self):
        """Initialize agent connections"""
        logger.info("🌸 Initializing Pollen Agent Core")
        
        # Initialize Sofie client
        self.sofie_client = httpx.AsyncClient(
            base_url=self.settings.SOFIE_URL,
            timeout=self.settings.SOFIE_TIMEOUT
        )
        
        # Verify Ollama connection
        try:
            await self.ollama_client.list()
            logger.info("✅ Ollama connection verified")
        except Exception as e:
            logger.error(f"❌ Ollama connection failed: {e}")
            raise
        
        logger.info("✅ Agent Core initialized")
    
    async def decide(
        self,
        context: str,
        available_actions: List[str],
        user_preferences: Optional[Dict] = None
    ) -> AgentDecision:
        """
        Make autonomous decision using local LLM
        
        Args:
            context: Current situation description
            available_actions: List of possible actions
            user_preferences: User's stated preferences
        """
        # Build prompt
        prompt = self._build_decision_prompt(context, available_actions, user_preferences)
        
        try:
            # Query local LLM
            response = await self.ollama_client.chat(
                model=self.settings.OLLAMA_MODEL,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                options={
                    "temperature": 0.7,
                    "num_predict": 500
                }
            )
            
            # Parse decision
            decision_text = response["message"]["content"]
            decision_data = self._parse_decision(decision_text)
            
            decision = AgentDecision(
                action=decision_data.get("action", "ask_user"),
                params=decision_data.get("params", {}),
                confidence=decision_data.get("confidence", 0.5),
                reasoning=decision_data.get("reasoning", "No reasoning provided"),
                timestamp=datetime.utcnow().isoformat(),
                requires_consent=decision_data.get("requires_consent", True)
            )
            
            self.decision_history.append(decision)
            
            logger.info(f"🧠 Decision: {decision.action} (confidence: {decision.confidence:.2f})")
            
            return decision
            
        except Exception as e:
            logger.error(f"❌ Decision failed: {e}")
            # Safe fallback
            return AgentDecision(
                action="ask_user",
                params={"message": f"I encountered an error: {e}. How should I proceed?"},
                confidence=0.0,
                reasoning="Error fallback",
                timestamp=datetime.utcnow().isoformat(),
                requires_consent=True
            )
    
    async def consult_sofie(
        self,
        query: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Consult Sofie AI for high-level guidance
        Used for complex decisions requiring Hive intelligence
        """
        if not self.sofie_client:
            raise RuntimeError("Sofie client not initialized")
        
        payload = {
            "message": query,
            "consent": True,
            "context": context or {}
        }
        
        try:
            response = await self.sofie_client.post("/check-in", json=payload)
            response.raise_for_status()
            
            sofie_response = response.json()
            logger.info(f"🔮 Sofie guidance received")
            
            return sofie_response
            
        except Exception as e:
            logger.error(f"❌ Sofie consultation failed: {e}")
            return {"response": "Sofie unavailable. Proceeding with local intelligence.", "error": str(e)}
    
    async def generate_content(
        self,
        content_type: str,
        prompt: str,
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate creative content using local LLM
        
        Args:
            content_type: Type of content (text, code, image_prompt, etc.)
            prompt: Generation prompt
            style: Optional style guidance
        """
        system_prompt = f"""You are a creative assistant generating {content_type}.
Style: {style or 'professional and engaging'}
Respond with the generated content directly, no preamble."""
        
        try:
            response = await self.ollama_client.generate(
                model=self.settings.OLLAMA_MODEL,
                prompt=prompt,
                system=system_prompt,
                options={"temperature": 0.8}
            )
            
            return {
                "content": response["response"],
                "content_type": content_type,
                "model": self.settings.OLLAMA_MODEL,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Content generation failed: {e}")
            raise
    
    async def analyze_biometrics(
        self,
        biometric_data: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Analyze biometric data and suggest interventions
        """
        prompt = f"""Analyze this biometric data and suggest wellness interventions:
{json.dumps(biometric_data, indent=2)}

Respond with JSON:
{{
    "status": "optimal|caution|alert",
    "insights": ["insight1", "insight2"],
    "recommendations": ["action1", "action2"],
    "priority": "low|medium|high"
}}"""
        
        try:
            response = await self.ollama_client.generate(
                model=self.settings.OLLAMA_MODEL,
                prompt=prompt,
                options={"temperature": 0.3}
            )
            
            analysis = json.loads(response["response"])
            logger.info(f"💚 Biometric analysis: {analysis.get('status')}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Biometric analysis failed: {e}")
            return {
                "status": "unknown",
                "insights": ["Analysis failed"],
                "recommendations": ["Manual review recommended"],
                "priority": "medium"
            }
    
    def _build_decision_prompt(
        self,
        context: str,
        available_actions: List[str],
        user_preferences: Optional[Dict]
    ) -> str:
        """Build decision prompt for LLM"""
        prefs = json.dumps(user_preferences, indent=2) if user_preferences else "None"
        
        return f"""Current Context:
{context}

Available Actions:
{', '.join(available_actions)}

User Preferences:
{prefs}

Decision History (last 3):
{json.dumps([d.__dict__ for d in self.decision_history[-3:]], indent=2)}

What action should I take? Respond with JSON decision format."""
    
    def _parse_decision(self, text: str) -> Dict:
        """Parse decision from LLM response"""
        # Try to extract JSON from response
        try:
            # Look for JSON block
            if "```json" in text:
                json_str = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                json_str = text.split("```")[1].split("```")[0].strip()
            else:
                json_str = text.strip()
            
            return json.loads(json_str)
        except (json.JSONDecodeError, IndexError):
            logger.warning(f"Failed to parse JSON, using fallback. Response: {text[:200]}")
            return {
                "action": "ask_user",
                "params": {"message": f"I need clarification. I was thinking: {text[:200]}"},
                "confidence": 0.3,
                "reasoning": "Parse failure fallback",
                "requires_consent": True
            }
    
    async def remember(self, key: str, value: Any):
        """Store in context memory"""
        self.context_memory.append({
            "key": key,
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep memory size manageable
        if len(self.context_memory) > 100:
            self.context_memory = self.context_memory[-50:]
    
    async def recall(self, key: str) -> Optional[Any]:
        """Recall from context memory"""
        for item in reversed(self.context_memory):
            if item["key"] == key:
                return item["value"]
        return None
    
    async def close(self):
        """Cleanup resources"""
        if self.sofie_client:
            await self.sofie_client.aclose()
            logger.info("🔌 Sofie client disconnected")
