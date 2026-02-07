"""
Pollen Python Agent - Healing-Centric Development

A sovereign AI agent for wellness-aware code generation and creative content,
integrated with the Terracare ecosystem.

Key Components:
- HealingDevelopmentWorkflow: Full proof-of-wellness code generation
- SurgicalCreatorEngine: AST-aware code generation with wellness constraints
- WellnessCodeValidator: Validates code against stress thresholds
- TerracareBridge: Blockchain integration for proof submission
"""

__version__ = "1.1.0-healing"

from .agent_core import PollenAgent, AgentDecision
from .workflows.healing_development import (
    HealingDevelopmentWorkflow,
    HealingDevelopmentResult,
    WorkflowStage
)
from .engines.surgical_creator_engine import (
    SurgicalCreatorEngine,
    WellnessConstrainedCreation,
    TerracareSession
)
from .validation.wellness_code_validator import (
    WellnessCodeValidator,
    WellnessViolation,
    CognitiveLoadReport,
    ViolationType
)
from .integration.terracare_bridge import (
    TerracareBridge,
    submit_code_proof,
    validate_build_token,
    log_biometric_impact
)
from .config import get_settings

__all__ = [
    # Core
    'PollenAgent',
    'AgentDecision',
    
    # Workflows
    'HealingDevelopmentWorkflow',
    'HealingDevelopmentResult',
    'WorkflowStage',
    
    # Engines
    'SurgicalCreatorEngine',
    'WellnessConstrainedCreation',
    'TerracareSession',
    
    # Validation
    'WellnessCodeValidator',
    'WellnessViolation',
    'CognitiveLoadReport',
    'ViolationType',
    
    # Integration
    'TerracareBridge',
    'submit_code_proof',
    'validate_build_token',
    'log_biometric_impact',
    
    # Config
    'get_settings',
]
