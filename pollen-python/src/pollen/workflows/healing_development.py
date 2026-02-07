"""
Healing Development Workflow - Proof-of-Wellness Implementation

This workflow orchestrates the entire healing-centric development process:
1. Ingest user intent through wellness lens
2. Check biometric eligibility
3. Generate with validation
4. Submit to Terracare ledger
5. Reward contribution with MINE/WELL tokens
"""

import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

from ..validation.wellness_code_validator import WellnessCodeValidator, WellnessViolation
from ..engines.surgical_creator_engine import SurgicalCreatorEngine, WellnessConstrainedCreation, TerracareSession
from ..integration.terracare_bridge import TerracareBridge
from ..config import get_settings

logger = logging.getLogger(__name__)


class WorkflowStage(Enum):
    """Stages of the healing development workflow"""
    IDLE = "idle"
    INGESTING = "ingesting"
    CHECKING_ELIGIBILITY = "checking_eligibility"
    GENERATING = "generating"
    VALIDATING = "validating"
    SUBMITTING = "submitting"
    REWARDING = "rewarding"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class WorkflowContext:
    """Context maintained throughout the workflow"""
    user_id: str
    original_intent: str
    wellness_intent: Optional[str] = None
    biometric_context: Dict[str, Any] = field(default_factory=dict)
    eligibility_check: Optional[Dict[str, Any]] = None
    constrained_creation: Optional[WellnessConstrainedCreation] = None
    terracare_tx_id: Optional[str] = None
    rewards_issued: Dict[str, float] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    stage: WorkflowStage = WorkflowStage.IDLE
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None


@dataclass
class HealingDevelopmentResult:
    """Result of the healing development workflow"""
    success: bool
    creation: Optional[WellnessConstrainedCreation]
    terracare_tx_id: Optional[str]
    rewards: Dict[str, float]
    wellness_score: float
    workflow_duration_seconds: float
    errors: List[str]
    proof_hash: str


class HealingDevelopmentWorkflow:
    """
    Proof-of-Wellness Development Workflow
    
    Orchestrates the entire healing-centric development process,
    ensuring all code is generated with wellness constraints and
    validated against Terracare principles.
    
    Usage:
        workflow = HealingDevelopmentWorkflow()
        await workflow.initialize()
        
        result = await workflow.execute(
            user_id="0x...",
            intent="Create a meditation timer app",
            biometric_context={"hrv": 65, "sleep_score": 8}
        )
    """
    
    def __init__(self):
        self.validator = WellnessCodeValidator()
        self.creator = SurgicalCreatorEngine()
        self.terracare: Optional[TerracareBridge] = None
        self.settings = get_settings()
        self._context: Optional[WorkflowContext] = None
        
    async def initialize(self, terracare_session: Optional[TerracareSession] = None):
        """Initialize the workflow with all components"""
        logger.info("Initializing Healing Development Workflow")
        
        # Initialize creator engine
        await self.creator.initialize()
        
        # Initialize Terracare bridge
        self.terracare = TerracareBridge(
            ledger_url=self.settings.TERRACARE_LEDGER_URL,
            api_key=self.settings.TERRACARE_API_KEY
        )
        
        if terracare_session:
            await self.terracare.connect(
                terracare_session.user_did,
                terracare_session.session_token
            )
        
        logger.info("Healing Development Workflow initialized")
        
    async def execute(
        self,
        user_id: str,
        intent: str,
        biometric_context: Dict[str, Any],
        terracare_session: Optional[TerracareSession] = None,
        content_type: str = 'code',
        options: Optional[Dict[str, Any]] = None
    ) -> HealingDevelopmentResult:
        """
        Execute the complete healing development workflow.
        
        Args:
            user_id: Unique user identifier
            intent: User's original intent/prompt
            biometric_context: Current HRV, sleep score, etc.
            terracare_session: Active Terracare session
            content_type: Type of content to generate
            options: Additional generation options
            
        Returns:
            HealingDevelopmentResult with all workflow outputs
        """
        start_time = datetime.utcnow()
        
        # Initialize context
        self._context = WorkflowContext(
            user_id=user_id,
            original_intent=intent,
            biometric_context=biometric_context
        )
        
        try:
            # Step 1: Ingest intent through wellness lens
            await self._ingest_intent(intent)
            
            # Step 2: Check biometric eligibility
            await self._check_biometric_eligibility()
            
            # Step 3: Generate with validation
            await self._generate_with_validation(
                biometric_context,
                terracare_session,
                content_type,
                options
            )
            
            # Step 4: Submit to ledger
            await self._submit_to_ledger(terracare_session)
            
            # Step 5: Reward contribution
            await self._reward_contribution()
            
            # Mark complete
            self._context.stage = WorkflowStage.COMPLETE
            self._context.completed_at = datetime.utcnow().isoformat()
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Generate proof hash
            proof_hash = self._generate_proof_hash()
            
            return HealingDevelopmentResult(
                success=True,
                creation=self._context.constrained_creation,
                terracare_tx_id=self._context.terracare_tx_id,
                rewards=self._context.rewards_issued,
                wellness_score=self._calculate_wellness_score(),
                workflow_duration_seconds=duration,
                errors=self._context.errors,
                proof_hash=proof_hash
            )
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            self._context.stage = WorkflowStage.ERROR
            self._context.errors.append(str(e))
            
            return HealingDevelopmentResult(
                success=False,
                creation=None,
                terracare_tx_id=None,
                rewards={},
                wellness_score=0.0,
                workflow_duration_seconds=(datetime.utcnow() - start_time).total_seconds(),
                errors=self._context.errors,
                proof_hash=""
            )
    
    async def _ingest_intent(self, intent: str):
        """
        Step 1: Ingest user intent through wellness lens.
        
        Transforms the original intent into a wellness-weighted version
        that prioritizes healing outcomes.
        """
        self._context.stage = WorkflowStage.INGESTING
        logger.info(f"Ingesting intent: {intent[:50]}...")
        
        # Analyze intent for wellness implications
        wellness_keywords = {
            'app': 'wellness_app',
            'website': 'wellness_website',
            'tool': 'wellness_tool',
            'game': 'mindful_game',
            'social': 'intentional_social',
        }
        
        wellness_intent = intent
        
        # Add wellness framing
        if 'app' in intent.lower():
            wellness_intent = f"Create a wellness-optimized app that respects user attention and promotes healthy engagement: {intent}"
        elif 'website' in intent.lower():
            wellness_intent = f"Create a calm, accessible website with intentional navigation and circadian-aware theming: {intent}"
        
        # Check for potential anti-patterns in intent
        anti_patterns = [
            ('viral', 'engagement-focused'),
            ('addictive', 'engaging'),
            ('sticky', 'valuable'),
            ('notification spam', 'mindful notifications'),
        ]
        
        for pattern, replacement in anti_patterns:
            if pattern in intent.lower():
                wellness_intent = wellness_intent.replace(pattern, replacement)
                logger.warning(f"Replaced anti-pattern '{pattern}' with '{replacement}'")
        
        self._context.wellness_intent = wellness_intent
        logger.info(f"Wellness intent: {wellness_intent[:50]}...")
    
    async def _check_biometric_eligibility(self):
        """
        Step 2: Check if user's biometric state permits coding.
        
        Blocks or adjusts complexity based on:
        - HRV (heart rate variability)
        - Sleep score
        - Current stress level
        """
        self._context.stage = WorkflowStage.CHECKING_ELIGIBILITY
        logger.info("Checking biometric eligibility")
        
        hrv = self._context.biometric_context.get('hrv', 50)
        sleep_score = self._context.biometric_context.get('sleep_score', 7)
        stress_level = self._context.biometric_context.get('stress_level', 'low')
        
        eligibility = {
            'eligible': True,
            'warnings': [],
            'recommended_complexity': 'full',
            'requires_approval': False,
        }
        
        # HRV checks
        if hrv < 30:
            eligibility['eligible'] = False
            eligibility['warnings'].append(f'Critical: HRV ({hrv}) too low for coding')
        elif hrv < 45:
            eligibility['warnings'].append(f'Warning: Low HRV ({hrv}), reducing complexity')
            eligibility['recommended_complexity'] = 'minimal'
            eligibility['requires_approval'] = True
        
        # Sleep checks
        if sleep_score < 5:
            eligibility['eligible'] = False
            eligibility['warnings'].append(f'Critical: Sleep score ({sleep_score}) too low')
        elif sleep_score < 6:
            eligibility['warnings'].append(f'Warning: Poor sleep ({sleep_score}), recommend rest')
            eligibility['recommended_complexity'] = 'minimal'
            eligibility['requires_approval'] = True
        
        # Stress checks
        if stress_level == 'high':
            eligibility['warnings'].append('Warning: High stress detected')
            eligibility['recommended_complexity'] = 'minimal'
        
        self._context.eligibility_check = eligibility
        
        for warning in eligibility['warnings']:
            logger.warning(warning)
        
        if not eligibility['eligible']:
            raise BiometricEligibilityError(
                f"Not eligible for code generation due to biometric state: {eligibility['warnings']}"
            )
    
    async def _generate_with_validation(
        self,
        biometric_context: Dict[str, Any],
        terracare_session: Optional[TerracareSession],
        content_type: str,
        options: Optional[Dict[str, Any]]
    ):
        """
        Step 3: Generate code with wellness constraints.
        
        Uses SurgicalCreatorEngine to generate code that passes
        all wellness validations.
        """
        self._context.stage = WorkflowStage.GENERATING
        logger.info("Generating with wellness constraints")
        
        # Determine complexity from eligibility
        complexity = self._context.eligibility_check.get(
            'recommended_complexity', 
            options.get('complexity', 'balanced') if options else 'balanced'
        )
        
        # Map content type
        from ..engines.creator_engine import ContentType
        ct_map = {
            'code': ContentType.CODE,
            'website': ContentType.WEBSITE,
            'mobile_app': ContentType.MOBILE_APP,
        }
        ct = ct_map.get(content_type, ContentType.CODE)
        
        # Generate
        constrained_creation = await self.creator.generate_with_wellness_constraints(
            intent=self._context.wellness_intent,
            biometric_context=biometric_context,
            terracare_session=terracare_session,
            content_type=ct,
            complexity_preference=complexity
        )
        
        self._context.constrained_creation = constrained_creation
        self._context.stage = WorkflowStage.VALIDATING
        
        # Check for critical violations
        critical_violations = [
            v for v in constrained_creation.wellness_violations 
            if v.severity == 'critical'
        ]
        
        if critical_violations:
            logger.error(f"Critical violations detected: {len(critical_violations)}")
            for v in critical_violations:
                self._context.errors.append(f"Critical: {v.message}")
            raise WellnessValidationError("Critical wellness violations detected")
        
        logger.info(f"Generation complete with {len(constrained_creation.wellness_violations)} violations")
    
    async def _submit_to_ledger(self, terracare_session: Optional[TerracareSession]):
        """
        Step 4: Submit to Terracare ledger.
        
        Creates an immutable record of the code creation with wellness proof.
        """
        self._context.stage = WorkflowStage.SUBMITTING
        
        if not terracare_session or not self.terracare:
            logger.warning("No Terracare session, skipping ledger submission")
            return
        
        if not self._context.constrained_creation:
            logger.error("No creation to submit")
            return
        
        logger.info("Submitting to Terracare ledger")
        
        try:
            success, tx_id = await self.terracare.submit_code_proof(
                code_hash=self._context.constrained_creation.wellness_proof_hash,
                wellness_metrics=self._context.biometric_context,
                author_did=terracare_session.user_did
            )
            
            if success:
                self._context.terracare_tx_id = tx_id
                logger.info(f"Submitted to ledger: {tx_id}")
            else:
                logger.error("Failed to submit to ledger")
                
        except Exception as e:
            logger.error(f"Ledger submission error: {e}")
            self._context.errors.append(f"Ledger submission failed: {e}")
    
    async def _reward_contribution(self):
        """
        Step 5: Reward contribution with MINE/WELL tokens.
        
        Calculates and issues token rewards based on:
        - Code quality (violations)
        - Biometric state at creation
        - Wellness impact
        """
        self._context.stage = WorkflowStage.REWARDING
        logger.info("Calculating rewards")
        
        if not self._context.constrained_creation:
            return
        
        rewards = self._context.constrained_creation.token_reward_estimate
        
        # Bonus for zero violations
        if len(self._context.constrained_creation.wellness_violations) == 0:
            rewards['MINE'] = rewards.get('MINE', 0) + 10
            rewards['WELL'] = rewards.get('WELL', 0) + 0.1
            logger.info("Bonus reward for zero violations")
        
        # Bonus for good biometric state
        hrv = self._context.biometric_context.get('hrv', 50)
        if hrv > 60:
            rewards['MINE'] = rewards.get('MINE', 0) * 1.2
            logger.info("HRV bonus applied")
        
        # Round to reasonable precision
        rewards['MINE'] = round(rewards.get('MINE', 0), 2)
        rewards['WELL'] = round(rewards.get('WELL', 0), 3)
        
        self._context.rewards_issued = rewards
        
        logger.info(f"Rewards: {rewards}")
        
        # Attempt to issue on ledger if connected
        if self.terracare and self._context.terracare_tx_id:
            try:
                # This would call the actual reward API
                logger.info("Issuing rewards on ledger")
            except Exception as e:
                logger.error(f"Failed to issue rewards: {e}")
    
    def _calculate_wellness_score(self) -> float:
        """Calculate overall wellness score for this creation"""
        if not self._context.constrained_creation:
            return 0.0
        
        base_score = 10.0
        
        # Deduct for violations
        for violation in self._context.constrained_creation.wellness_violations:
            if violation.severity == 'critical':
                base_score -= 3
            elif violation.severity == 'warning':
                base_score -= 1
            else:
                base_score -= 0.5
        
        # Bonus for good cognitive load report
        if self._context.constrained_creation.cognitive_load_report:
            load = self._context.constrained_creation.cognitive_load_report.overall_score
            if load < 5:
                base_score += 1
        
        return max(0, min(10, base_score))
    
    def _generate_proof_hash(self) -> str:
        """Generate proof hash for this workflow execution"""
        if not self._context:
            return ""
        
        proof_data = {
            'user_id': self._context.user_id,
            'intent_hash': hashlib.sha256(
                self._context.original_intent.encode()
            ).hexdigest()[:16],
            'wellness_score': self._calculate_wellness_score(),
            'timestamp': self._context.started_at,
            'terracare_tx': self._context.terracare_tx_id,
        }
        
        return hashlib.sha256(
            json.dumps(proof_data, sort_keys=True).encode()
        ).hexdigest()[:32]
    
    def get_context(self) -> Optional[WorkflowContext]:
        """Get current workflow context"""
        return self._context


class BiometricEligibilityError(Exception):
    """Raised when user is not biometrically eligible for coding"""
    pass


class WellnessValidationError(Exception):
    """Raised when code fails wellness validation"""
    pass
