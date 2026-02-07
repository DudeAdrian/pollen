"""
Pollen Configuration Settings

Environment-based configuration with sensible defaults
for healing-centric development.
"""

import os
from typing import List, Optional
from functools import lru_cache

from pydantic import BaseSettings, Field


class PollenConfig(BaseSettings):
    """
    Pollen Configuration
    
    All settings can be overridden via environment variables
    or a .env file.
    """
    
    # ═══════════════════════════════════════════════════════════════════════
    # CORE SETTINGS
    # ═══════════════════════════════════════════════════════════════════════
    
    APP_NAME: str = "Pollen - Healing-Centric Development"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="POLLEN_DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="POLLEN_LOG_LEVEL")
    
    # ═══════════════════════════════════════════════════════════════════════
    # TERRACARE LEDGER CONFIGURATION
    # ═══════════════════════════════════════════════════════════════════════
    
    TERRACARE_LEDGER_URL: str = Field(
        default="http://localhost:3000",
        env="TERRACARE_LEDGER_URL",
        description="URL of the Terracare Hive ledger"
    )
    
    TERRACARE_API_KEY: Optional[str] = Field(
        default=None,
        env="TERRACARE_API_KEY",
        description="API key for Terracare authentication"
    )
    
    TERRACARE_VALIDATION_ENABLED: bool = Field(
        default=True,
        env="TERRACARE_VALIDATION_ENABLED",
        description="Enable Terracare ledger validation"
    )
    
    TERRACARE_REQUIRED_TOKENS_PER_GENERATION: float = Field(
        default=1.0,
        env="TERRACARE_REQUIRED_TOKENS_PER_GENERATION",
        description="WELL tokens required per code generation"
    )
    
    # ═══════════════════════════════════════════════════════════════════════
    # WELLNESS CONSTRAINTS
    # ═══════════════════════════════════════════════════════════════════════
    
    WELLNESS_MAX_COGNITIVE_LOAD: float = Field(
        default=7.0,
        env="WELLNESS_MAX_COGNITIVE_LOAD",
        description="Maximum allowed cognitive load (1-10 scale)"
    )
    
    WELLNESS_REQUIRED_SLEEP_SCORE: float = Field(
        default=6.0,
        env="WELLNESS_REQUIRED_SLEEP_SCORE",
        description="Minimum sleep score required for complex coding"
    )
    
    WELLNESS_HRV_THRESHOLD: float = Field(
        default=45.0,
        env="WELLNESS_HRV_THRESHOLD",
        description="Minimum HRV (ms) for coding authorization"
    )
    
    WELLNESS_BANNED_PATTERNS: List[str] = Field(
        default=[
            "infinite_scroll",
            "deceptive_dark_patterns",
            "anxiety_notifications",
            "attention_extraction"
        ],
        env="WELLNESS_BANNED_PATTERNS",
        description="Patterns banned from generated code"
    )
    
    # ═══════════════════════════════════════════════════════════════════════
    # HEALING DEFAULTS - UI/UX PREFERENCES
    # ═══════════════════════════════════════════════════════════════════════
    
    HEALING_UI_ANIMATION_SPEED: str = Field(
        default="calming",
        env="HEALING_UI_ANIMATION_SPEED",
        description="UI animation style: calming, gentle, or standard"
    )
    
    HEALING_NOTIFICATION_BATCHING: str = Field(
        default="mindful_moments",
        env="HEALING_NOTIFICATION_BATCHING",
        description="Notification delivery mode"
    )
    
    HEALING_PAGINATION_STYLE: str = Field(
        default="intentional_breaks",
        env="HEALING_PAGINATION_STYLE",
        description="Pagination approach for lists"
    )
    
    HEALING_PROGRESS_CELEBRATION: str = Field(
        default="includes_rest",
        env="HEALING_PROGRESS_CELEBRATION",
        description="How to celebrate milestones"
    )
    
    # ═══════════════════════════════════════════════════════════════════════
    # OLLAMA / LLM SETTINGS
    # ═══════════════════════════════════════════════════════════════════════
    
    OLLAMA_HOST: str = Field(
        default="http://localhost:11434",
        env="OLLAMA_HOST",
        description="Ollama server URL"
    )
    
    OLLAMA_MODEL: str = Field(
        default="llama3.1:8b",
        env="OLLAMA_MODEL",
        description="Default Ollama model for inference"
    )
    
    OLLAMA_TIMEOUT: int = Field(
        default=120,
        env="OLLAMA_TIMEOUT",
        description="Ollama request timeout in seconds"
    )
    
    # ═══════════════════════════════════════════════════════════════════════
    # SOFIE INTEGRATION
    # ═══════════════════════════════════════════════════════════════════════
    
    SOFIE_URL: str = Field(
        default="http://localhost:8000",
        env="SOFIE_URL",
        description="Sofie-LLaMA backend URL"
    )
    
    SOFIE_TIMEOUT: int = Field(
        default=30,
        env="SOFIE_TIMEOUT",
        description="Sofie API timeout"
    )
    
    # ═══════════════════════════════════════════════════════════════════════
    # IDE INTEGRATION
    # ═══════════════════════════════════════════════════════════════════════
    
    IDE_BRIDGE_HOST: str = Field(
        default="localhost",
        env="IDE_BRIDGE_HOST",
        description="IDE bridge WebSocket host"
    )
    
    IDE_BRIDGE_PORT: int = Field(
        default=9001,
        env="IDE_BRIDGE_PORT",
        description="IDE bridge WebSocket port"
    )
    
    IDE_PRECOMMIT_BLOCK_ON_CRITICAL: bool = Field(
        default=True,
        env="IDE_PRECOMMIT_BLOCK_ON_CRITICAL",
        description="Block git commits with critical wellness violations"
    )
    
    IDE_PRECOMMIT_MIN_WELLNESS_SCORE: float = Field(
        default=6.0,
        env="IDE_PRECOMMIT_MIN_WELLNESS_SCORE",
        description="Minimum wellness score for commits"
    )
    
    # ═══════════════════════════════════════════════════════════════════════
    # VAULT & SECURITY
    # ═══════════════════════════════════════════════════════════════════════
    
    VAULT_PATH: str = Field(
        default="./vault",
        env="VAULT_PATH",
        description="Path to encrypted creation vault"
    )
    
    ENCRYPTION_KEY_PATH: Optional[str] = Field(
        default=None,
        env="ENCRYPTION_KEY_PATH",
        description="Path to encryption key file"
    )
    
    # ═══════════════════════════════════════════════════════════════════════
    # DATABASE
    # ═══════════════════════════════════════════════════════════════════════
    
    DATABASE_URL: str = Field(
        default="sqlite:///./pollen.db",
        env="DATABASE_URL",
        description="Database connection URL"
    )
    
    REDIS_URL: Optional[str] = Field(
        default=None,
        env="REDIS_URL",
        description="Redis connection URL for caching"
    )
    
    # ═══════════════════════════════════════════════════════════════════════
    # EXTERNAL SERVICES
    # ═══════════════════════════════════════════════════════════════════════
    
    HEARTWARE_URL: Optional[str] = Field(
        default=None,
        env="HEARTWARE_URL",
        description="Heartware biometric data service URL"
    )
    
    STABLE_DIFFUSION_URL: Optional[str] = Field(
        default=None,
        env="STABLE_DIFFUSION_URL",
        description="Stable Diffusion API URL for image generation"
    )
    
    # ═══════════════════════════════════════════════════════════════════════
    # FEATURE FLAGS
    # ═══════════════════════════════════════════════════════════════════════
    
    FEATURE_WELLNESS_VALIDATION: bool = Field(
        default=True,
        env="FEATURE_WELLNESS_VALIDATION",
        description="Enable wellness code validation"
    )
    
    FEATURE_TERRACARE_SUBMISSION: bool = Field(
        default=True,
        env="FEATURE_TERRACARE_SUBMISSION",
        description="Enable automatic Terracare submission"
    )
    
    FEATURE_TOKEN_REWARDS: bool = Field(
        default=True,
        env="FEATURE_TOKEN_REWARDS",
        description="Enable MINE/WELL token rewards"
    )
    
    FEATURE_BIOMETRIC_MONITORING: bool = Field(
        default=True,
        env="FEATURE_BIOMETRIC_MONITORING",
        description="Enable biometric monitoring during coding"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> PollenConfig:
    """
    Get cached settings instance.
    
    Returns:
        PollenConfig with loaded settings
    """
    return PollenConfig()


# YAML Configuration Template for User Customization
CONFIG_YAML_TEMPLATE = """
# Pollen Configuration File
# Place at ~/.pollen/config.yaml or ./pollen.config.yaml

terracare:
  ledger_url: http://localhost:3000
  validation_enabled: true
  required_tokens_per_generation: 1.0  # WELL
  
wellness_constraints:
  max_cognitive_load: 7           # 1-10 scale
  required_sleep_score: 6         # 0-10 scale
  hrv_threshold: 45               # milliseconds
  banned_patterns:
    - infinite_scroll
    - deceptive_dark_patterns
    - anxiety_notifications
    - attention_extraction
    
healing_defaults:
  ui_animation_speed: calming     # calming | gentle | standard
  notification_batching: mindful_moments  # mindful_moments | batched | immediate
  pagination: intentional_breaks  # intentional_breaks | standard
  progress_celebration: includes_rest     # includes_rest | standard | minimal
  
# Biometric thresholds
coding_authorization:
  # HRV thresholds
  hrv_critical: 30     # Block coding below this
  hrv_caution: 45      # Minimal complexity only
  hrv_optimal: 60      # Full complexity allowed
  
  # Sleep score thresholds
  sleep_critical: 4    # Block coding
  sleep_caution: 6     # Minimal complexity
  sleep_optimal: 8     # Full complexity
  
  # Session limits based on state
  session_limits:
    low_hrv: 20        # minutes
    poor_sleep: 30     # minutes
    optimal: 90        # minutes

# IDE integration
ide:
  precommit:
    block_on_critical: true
    min_wellness_score: 6.0
    warn_on_warnings: true
  
  realtime_linter:
    enabled: true
    severity_threshold: warning  # error | warning | info
    
# Token economics
tokens:
  base_mine_reward: 20.0
  base_well_reward: 0.2
  
  # Multipliers
  zero_violation_bonus: 1.5
  high_hrv_bonus: 1.2
  good_sleep_bonus: 1.1
  
  # Costs
  generation_costs:
    minimal: 0.5   # WELL
    balanced: 1.0  # WELL
    full: 2.0      # WELL

# Notifications
notifications:
  breath_prompt_interval: 10      # minutes
  session_reminder_interval: 30   # minutes
  quiet_hours:
    start: 22  # 10 PM
    end: 8     # 8 AM
"""


def generate_config_yaml() -> str:
    """Generate a default configuration YAML file"""
    return CONFIG_YAML_TEMPLATE
