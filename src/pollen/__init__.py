"""
Pollen AI Agent - Sovereign AI Agent within Terracare Ecosystem
Version: v1.0.0-production-ready

Pollen operates as the user's sovereign AI agent, spawned via Hive Consciousness,
guided by Sofie AI intelligence. All activities are rewarded via Hive consensus.

Core Capabilities:
- Wellness Agent: Biometric harvesting, wellness protocols
- Creative Agent: Content generation (web, apps, media, docs)
- Social Agent: Autonomous social media management
- Technical Agent: Code generation, IoT management
- Administrative Agent: Shadow wallet, graduation triggers
"""

__version__ = "v1.0.0-production-ready"
__author__ = "Adrian Sortino (The Dude)"
__license__ = "MIT"

from .agent_core import PollenAgent
from .spawner import HiveSpawner

__all__ = ["PollenAgent", "HiveSpawner", "__version__"]
