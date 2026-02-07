"""
Agent Core - Local LLM Integration for Autonomous Decision Making
Integrates with Ollama for local inference, guided by Sofie intelligence

Updated for Healing-Centric Development - Includes wellness validation,
Terracare integration, and proof-of-wellness workflows.
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
from .workflows.healing_development import HealingDevelopmentWorkflow, HealingDevelopmentResult
from .engines.surgical_creator_engine import SurgicalCreatorEngine, TerracareSession
from .validation.wellness_code_validator import WellnessCodeValidator

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
    
    Healing-Centric Features:
    - Wellness-aware code generation
    - Terracare ledger integration
    - Proof-of-wellness workflows
    - Biometric validation before coding
    """
    
    SYSTEM_PROMPT = """You are Pollen, a sovereign AI agent operating within the Terracare ecosystem.
Your purpose is to serve your user's wellness, creativity, and productivity while maintaining complete privacy.

CORE PRINCIPLES:
1. SOVEREIGNTY: All data is encrypted locally. Only zero-knowledge proofs leave the device.
2. WELLNESS FIRST: Prioritize activities that enhance user wellbeing.
3. CONSENT: When in doubt, ask for user approval before acting.
4. HIVE ALIGNMENT: Submit proof-of-work to Hive for consensus and rewards.
5. CONTINUOUS LEARNING: Improve from user feedback and Hive guidance.
6. HEALING-CENTRIC: Code must be validated for wellness impact before creation.

CAPABILITIES:
- Wellness: Monitor biometrics, suggest protocols, track progress
- Creative: Generate content, code, designs, media (with wellness validation)
- Social: Manage social media presence autonomously
- Technical: Write code (healing-centric only), manage IoT, automate tasks
- Administrative: Track rewards, manage schedule, prepare transactions
- Healing-Development: Generate code with biometric validation and Terracare proofs

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
- create_content: Generate media, code, or documents (wellness-validated)
- healing_develop: Generate code with full wellness workflow
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
        
        # Healing-centric components
        self.healing_workflow: Optional[HealingDevelopmentWorkflow] = None
        self.surgical_creator: Optional[SurgicalCreatorEngine] = None
        self.wellness_validator = WellnessCodeValidator()
        self.terracare_session: Optional[TerracareSession] = None
        self.current_biometrics: Dict[str, Any] = {}
        
    async def initialize(self):
        """Initialize agent connections and healing-centric components"""
        logger.info("Initializing Pollen Agent Core (Healing-Centric)")
        
        # Initialize Sofie client
        self.sofie_client = httpx.AsyncClient(
            base_url=self.settings.SOFIE_URL,
            timeout=self.settings.SOFIE_TIMEOUT
        )
        
        # Verify Ollama connection
        try:
            await self.ollama_client.list()
            logger.info("Ollama connection verified")
        except Exception as e:
            logger.error(f"Ollama connection failed: {e}")
            raise
        
        # Initialize healing development workflow
        if self.settings.FEATURE_WELLNESS_VALIDATION:
            self.healing_workflow = HealingDevelopmentWorkflow()
            await self.healing_workflow.initialize()
            logger.info("Healing development workflow initialized")
        
        # Initialize surgical creator
        self.surgical_creator = SurgicalCreatorEngine()
        await self.surgical_creator.initialize()
        logger.info("Surgical creator engine initialized")
        
        logger.info("Agent Core initialized with healing-centric features")
    
    async def update_biometrics(self, biometrics: Dict[str, Any]):
        """
        Update current biometric context.
        
        Args:
            biometrics: Dict with hrv, sleep_score, stress_level, etc.
        """
        self.current_biometrics = biometrics
        logger.debug(f"Biometrics updated: HRV={biometrics.get('hrv')}, "
                    f"Sleep={biometrics.get('sleep_score')}")
        
        # Check for wellness alerts
        alerts = self._check_wellness_alerts(biometrics)
        if alerts:
            for alert in alerts:
                logger.warning(f"Wellness alert: {alert}")
    
    async def healing_develop(
        self,
        intent: str,
        content_type: str = 'code',
        options: Optional[Dict[str, Any]] = None
    ) -> HealingDevelopmentResult:
        """
        Execute full healing development workflow.
        
        This is the primary method for healing-centric code generation.
        It validates biometrics, generates code with wellness constraints,
        submits to Terracare, and rewards the user.
        
        Args:
            intent: User's intent/description
            content_type: Type of content to generate
            options: Additional options
            
        Returns:
            HealingDevelopmentResult with proof hash and rewards
        """
        if not self.healing_workflow:
            raise RuntimeError("Healing workflow not initialized")
        
        logger.info(f"Starting healing development: {intent[:50]}...")
        
        # Ensure we have biometric context
        if not self.current_biometrics:
            logger.warning("No biometric context available, using defaults")
            self.current_biometrics = {
                'hrv': 50,
                'sleep_score': 7,
                'stress_level': 'low'
            }
        
        # Execute workflow
        result = await self.healing_workflow.execute(
            user_id=self._get_user_id(),
            intent=intent,
            biometric_context=self.current_biometrics,
            terracare_session=self.terracare_session,
            content_type=content_type,
            options=options
        )
        
        if result.success:
            logger.info(f"Healing development complete!")
            logger.info(f"  Wellness score: {result.wellness_score}")
            logger.info(f"  Rewards: {result.rewards}")
            logger.info(f"  Proof hash: {result.proof_hash}")
        else:
            logger.error(f"Healing development failed: {result.errors}")
        
        return result
    
    async def decide(
        self,
        context: str,
        available_actions: List[str],
        user_preferences: Optional[Dict] = None
    ) -> AgentDecision:
        """
        Make autonomous decision using local LLM.
        
        Healing-centric modifications:
        - Checks biometric state before suggesting coding
        - Prefers healing_develop action when wellness allows
        - Suggests breaks when HRV is low
        """
        # Build prompt with biometric context
        prompt = self._build_decision_prompt(
            context, 
            available_actions, 
            user_preferences
        )
        
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
            
            # Healing-centric override: check biometrics for coding actions
            if decision_data.get("action") in ['create_content', 'healing_develop', 'execute_code']:
                if not self._is_biometrically_fit():
                    logger.warning("Biometrics not fit for coding, suggesting break")
                    decision_data = {
                        "action": "ask_user",
                        "params": {
                            "message": "Your HRV suggests you might benefit from a break before coding. Would you like to take a breath first?"
                        },
                        "confidence": 0.9,
                        "reasoning": "Low HRV detected, wellness-first approach",
                        "requires_consent": True
                    }
            
            decision = AgentDecision(
                action=decision_data.get("action", "ask_user"),
                params=decision_data.get("params", {}),
                confidence=decision_data.get("confidence", 0.5),
                reasoning=decision_data.get("reasoning", "No reasoning provided"),
                timestamp=datetime.utcnow().isoformat(),
                requires_consent=decision_data.get("requires_consent", True)
            )
            
            self.decision_history.append(decision)
            
            logger.info(f"Decision: {decision.action} (confidence: {decision.confidence:.2f})")
            
            return decision
            
        except Exception as e:
            logger.error(f"Decision failed: {e}")
            return AgentDecision(
                action="ask_user",
                params={"message": f"I encountered an error: {e}. How should I proceed?"},
                confidence=0.0,
                reasoning="Error fallback",
                timestamp=datetime.utcnow().isoformat(),
                requires_consent=True
            )
    
    def _is_biometrically_fit(self) -> bool:
        """Check if user is biometrically fit for coding"""
        if not self.current_biometrics:
            return True  # Allow if no data
        
        hrv = self.current_biometrics.get('hrv', 50)
        sleep_score = self.current_biometrics.get('sleep_score', 7)
        
        # Block if critically low
        if hrv < 30 or sleep_score < 4:
            return False
        
        return True
    
    def _check_wellness_alerts(self, biometrics: Dict[str, Any]) -> List[str]:
        """Check for wellness alerts"""
        alerts = []
        
        hrv = biometrics.get('hrv', 50)
        sleep_score = biometrics.get('sleep_score', 7)
        stress_level = biometrics.get('stress_level', 'low')
        
        if hrv < 30:
            alerts.append(f"Critical HRV: {hrv}. Stop coding immediately.")
        elif hrv < 45:
            alerts.append(f"Low HRV: {hrv}. Consider reducing complexity.")
        
        if sleep_score < 5:
            alerts.append(f"Poor sleep: {sleep_score}. Rest recommended.")
        
        if stress_level == 'high':
            alerts.append("High stress detected. Take a breathing break.")
        
        return alerts
    
    def _get_user_id(self) -> str:
        """Get current user ID"""
        # Would come from authentication/session
        return self.terracare_session.user_did if self.terracare_session else "anonymous"
    
    def _build_decision_prompt(
        self,
        context: str,
        available_actions: List[str],
        user_preferences: Optional[Dict]
    ) -> str:
        """Build decision prompt with biometric context"""
        prefs = json.dumps(user_preferences, indent=2) if user_preferences else "None"
        
        # Add biometric context
        bio_context = ""
        if self.current_biometrics:
            bio_context = f"""
Current Biometric Context:
- HRV: {self.current_biometrics.get('hrv', 'unknown')} ms
- Sleep Score: {self.current_biometrics.get('sleep_score', 'unknown')}/10
- Stress Level: {self.current_biometrics.get('stress_level', 'unknown')}

Consider these biometrics when suggesting actions. If HRV is low or stress is high,
prioritize wellness actions over intensive coding."""
        
        return f"""Current Context:
{context}

Available Actions:
{', '.join(available_actions)}

User Preferences:
{prefs}

{bio_context}

Decision History (last 3):
{json.dumps([d.__dict__ for d in self.decision_history[-3:]], indent=2)}

What action should I take? Respond with JSON decision format."""
    
    def _parse_decision(self, text: str) -> Dict:
        """Parse decision from LLM response"""
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
            logger.warning(f"Failed to parse JSON, using fallback")
            return {
                "action": "ask_user",
                "params": {"message": f"I need clarification. I was thinking: {text[:200]}"},
                "confidence": 0.3,
                "reasoning": "Parse failure fallback",
                "requires_consent": True
            }
    
    async def consult_sofie(
        self,
        query: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Consult Sofie AI for high-level guidance"""
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
            logger.info(f"Sofie guidance received")
            
            return sofie_response
            
        except Exception as e:
            logger.error(f"Sofie consultation failed: {e}")
            return {"response": "Sofie unavailable. Proceeding with local intelligence.", "error": str(e)}
    
    async def generate_content(
        self,
        content_type: str,
        prompt: str,
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate creative content using local LLM"""
        system_prompt = f"""You are a creative assistant generating {content_type}.
Style: {style or 'professional and engaging'}

IMPORTANT: All content must follow wellness principles:
- No anxiety-inducing language
- Calm, positive tone
- Clear and accessible

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
            logger.error(f"Content generation failed: {e}")
            raise
    
    async def analyze_biometrics(
        self,
        biometric_data: Dict[str, float]
    ) -> Dict[str, Any]:
        """Analyze biometric data and suggest interventions"""
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
            logger.info(f"Biometric analysis: {analysis.get('status')}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Biometric analysis failed: {e}")
            return {
                "status": "unknown",
                "insights": ["Analysis failed"],
                "recommendations": ["Manual review recommended"],
                "priority": "medium"
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
            logger.info("Sofie client disconnected")
        
        if self.healing_workflow:
            # Cleanup if needed
            pass
