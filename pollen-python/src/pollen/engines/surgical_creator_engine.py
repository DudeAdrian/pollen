"""
Surgical Creator Engine - Healing-Centric Development

Extends CreatorEngine with AST parsing capabilities and wellness constraints.
Generates code templates filtered through WellnessCodeValidator and integrated
with Terracare ledger for proof-of-wellness.
"""

import ast
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import hashlib

import httpx

from .creator_engine import CreatorEngine, ContentType, Creation
from ..validation.wellness_code_validator import WellnessCodeValidator, CognitiveLoadReport
from ..config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class WellnessConstrainedCreation:
    """Extended creation with wellness proof and token estimates"""
    creation: Creation
    wellness_proof_hash: str
    token_reward_estimate: Dict[str, float]  # {'MINE': X, 'WELL': Y}
    wellness_violations: List[Any]
    cognitive_load_report: Optional[CognitiveLoadReport]
    terracare_tx_id: Optional[str]
    biometric_context_at_creation: Dict[str, Any]


@dataclass
class TerracareSession:
    """Active Terracare ledger session"""
    ledger_url: str
    user_did: str
    session_token: str
    wallet_address: str
    staked_mine: float
    available_well: float
    
    async def validate_spend(self, amount_well: float) -> bool:
        """Check if user has sufficient WELL tokens"""
        return self.available_well >= amount_well


class SurgicalCreatorEngine(CreatorEngine):
    """
    Surgical-precision creator engine with wellness constraints.
    
    This engine extends the base CreatorEngine with:
    - AST parsing for code validation
    - Biometric-aware generation constraints
    - Terracare ledger integration for proof-of-wellness
    - Token reward estimation
    """
    
    def __init__(self):
        super().__init__()
        self.validator = WellnessCodeValidator()
        self.settings = get_settings()
        self.terracare_client: Optional[httpx.AsyncClient] = None
        
    async def initialize(self):
        """Initialize surgical creator with Terracare connection"""
        await super().initialize()
        
        # Initialize Terracare client
        self.terracare_client = httpx.AsyncClient(
            base_url=self.settings.TERRACARE_LEDGER_URL,
            timeout=30.0
        )
        
        logger.info("Surgical Creator Engine initialized")
        logger.info("  - AST parsing: enabled")
        logger.info("  - Wellness validation: enabled")
        logger.info("  - Terracare integration: enabled")
    
    async def generate_with_wellness_constraints(
        self,
        intent: str,
        biometric_context: Dict[str, Any],
        terracare_session: Optional[TerracareSession] = None,
        content_type: ContentType = ContentType.CODE,
        complexity_preference: str = 'auto'
    ) -> WellnessConstrainedCreation:
        """
        Generate code with wellness constraints and Terracare validation.
        """
        logger.info(f"Generating with wellness constraints: {intent[:50]}...")
        
        # Step 1: Validate biometric eligibility
        hrv = biometric_context.get('hrv', 50)
        sleep_score = biometric_context.get('sleep_score', 7)
        
        if hrv < self.validator.hrv_threshold:
            logger.warning(f"Low HRV ({hrv}) - suggesting simpler implementation")
            complexity_preference = 'minimal'
        
        if sleep_score < 6:
            logger.warning(f"Poor sleep ({sleep_score}) - reducing cognitive load")
            complexity_preference = 'minimal'
        
        # Step 2: Check token balance if Terracare session provided
        if terracare_session:
            required_tokens = self._calculate_token_cost(intent, complexity_preference)
            has_funds = await terracare_session.validate_spend(required_tokens['WELL'])
            
            if not has_funds:
                raise InsufficientTokensError(
                    f"Insufficient WELL tokens. Required: {required_tokens['WELL']}, "
                    f"Available: {terracare_session.available_well}"
                )
        
        # Step 3: Generate based on content type
        if content_type == ContentType.WEBSITE:
            creation = await self._generate_wellness_website(intent, complexity_preference)
        elif content_type == ContentType.MOBILE_APP:
            creation = await self._generate_wellness_app(intent, complexity_preference)
        elif content_type == ContentType.CODE:
            creation = await self._generate_wellness_code(intent, complexity_preference)
        else:
            creation = await self.generate_document(intent, intent, format='markdown')
        
        # Step 4: Validate generated code
        code_to_validate = self._extract_code_from_creation(creation)
        is_valid, violations, validation_metadata = self.validator.validate_edit(
            code_to_validate,
            biometric_context
        )
        
        # Step 5: Generate wellness proof
        wellness_proof_hash = self._generate_wellness_proof(
            creation, violations, biometric_context
        )
        
        # Step 6: Calculate token rewards
        token_estimate = self._calculate_token_rewards(
            creation, violations, biometric_context
        )
        
        # Step 7: Submit to Terracare if session available
        terracare_tx_id = None
        if terracare_session and self.settings.TERRACARE_VALIDATION_ENABLED:
            terracare_tx_id = await self._submit_to_terracare(
                creation,
                wellness_proof_hash,
                biometric_context,
                terracare_session
            )
        
        # Step 8: Create constrained creation result
        constrained_creation = WellnessConstrainedCreation(
            creation=creation,
            wellness_proof_hash=wellness_proof_hash,
            token_reward_estimate=token_estimate,
            wellness_violations=violations,
            cognitive_load_report=validation_metadata.get('cognitive_load_report'),
            terracare_tx_id=terracare_tx_id,
            biometric_context_at_creation=biometric_context
        )
        
        logger.info(f"Wellness-constrained creation complete:")
        logger.info(f"  Proof hash: {wellness_proof_hash}")
        logger.info(f"  Token estimate: {token_estimate}")
        logger.info(f"  Violations: {len(violations)}")
        
        return constrained_creation
    
    async def _generate_wellness_website(self, intent: str, complexity: str) -> Creation:
        """Generate website with wellness patterns"""
        template = 'wellness_minimal' if complexity == 'minimal' else 'wellness_balanced'
        
        html = self._generate_wellness_html(intent, template)
        css = self._generate_wellness_css()
        js = self._generate_wellness_js()
        
        creation = Creation(
            creation_id=f"wellness_web_{datetime.utcnow().timestamp()}",
            content_type=ContentType.WEBSITE,
            title=f"Wellness Website: {intent[:40]}",
            content={
                'html': html,
                'css': css,
                'js': js,
                'template': template,
                'wellness_features': [
                    'no_infinite_scroll',
                    'circadian_aware_theme',
                    'mindful_animations'
                ]
            },
            metadata={
                'template': template,
                'complexity': complexity,
                'wellness_score': 9.0
            },
            created_at=datetime.utcnow().isoformat()
        )
        
        await self._store_creation(creation)
        return creation
    
    async def _generate_wellness_app(self, intent: str, complexity: str) -> Creation:
        """Generate mobile app with wellness patterns"""
        screens = ['Home', 'Wellness', 'Profile', 'Breathing', 'Sleep']
        
        content = self._generate_react_native_wellness_scaffold(intent, screens, complexity)
        
        creation = Creation(
            creation_id=f"wellness_app_{datetime.utcnow().timestamp()}",
            content_type=ContentType.MOBILE_APP,
            title=f"Wellness App: {intent[:40]}",
            content=content,
            metadata={
                'platform': 'react_native',
                'screens': screens,
                'complexity': complexity,
                'wellness_hooks': [
                    'useMindfulScroll',
                    'useBreathPause',
                    'useIntentionalNotification'
                ]
            },
            created_at=datetime.utcnow().isoformat()
        )
        
        await self._store_creation(creation)
        return creation
    
    async def _generate_wellness_code(self, intent: str, complexity: str) -> Creation:
        """Generate wellness-optimized code module"""
        if 'hook' in intent.lower():
            code = self._generate_wellness_hook(intent, complexity)
            language = 'typescript'
        else:
            code = self._generate_wellness_component(intent, complexity)
            language = 'typescript'
        
        creation = Creation(
            creation_id=f"wellness_code_{datetime.utcnow().timestamp()}",
            content_type=ContentType.CODE,
            title=f"Wellness Code: {intent[:40]}",
            content={
                'code': code,
                'language': language,
                'complexity': complexity,
                'wellness_impact': 'Reduces cognitive load through intentional design'
            },
            metadata={
                'language': language,
                'lines_of_code': len(code.split('\n')),
                'complexity': complexity
            },
            created_at=datetime.utcnow().isoformat()
        )
        
        await self._store_creation(creation)
        return creation
    
    def _generate_wellness_html(self, intent: str, template: str) -> str:
        """Generate wellness-optimized HTML"""
        return f"""<!DOCTYPE html>
<html lang="en" data-wellness-theme="calm">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="wellness-score" content="9.0">
    <title>{intent[:50]}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <nav class="intentional-nav">
        <a href="#home" class="nav-link">Home</a>
        <a href="#wellness" class="nav-link">Wellness</a>
        <a href="#about" class="nav-link">About</a>
    </nav>
    <main id="main-content">
        <section id="home" class="page-section">
            <h1>{intent[:50]}</h1>
            <p>Designed with wellness in mind.</p>
        </section>
    </main>
    <div id="breath-reminder" class="hidden">
        <p>Take a breath. You have been here for 10 minutes.</p>
    </div>
    <script src="app.js"></script>
</body>
</html>"""
    
    def _generate_wellness_css(self) -> str:
        """Generate wellness-optimized CSS"""
        return """/* Wellness-Optimized CSS */
:root {
    --color-primary: #5B8C85;
    --color-secondary: #8FB9A8;
    --color-background: #F7F4F0;
    --color-text: #2C3E50;
    --transition-speed: 0.3s;
    --line-height: 1.6;
}

.intentional-nav {
    display: flex;
    gap: 2rem;
    padding: 1rem;
    background: var(--color-background);
}

.nav-link {
    color: var(--color-primary);
    text-decoration: none;
    padding: 0.5rem 1rem;
}

.hidden { display: none; }
"""
    
    def _generate_wellness_js(self) -> str:
        """Generate wellness-optimized JavaScript"""
        return """// Wellness-Optimized JavaScript
(function() {
    let sessionStart = Date.now();
    let lastBreakPrompt = sessionStart;
    
    setInterval(() => {
        const now = Date.now();
        if (now - lastBreakPrompt > 10 * 60 * 1000) {
            showBreakReminder();
            lastBreakPrompt = now;
        }
    }, 60000);
    
    function showBreakReminder() {
        const reminder = document.getElementById('breath-reminder');
        if (reminder) reminder.classList.remove('hidden');
    }
    
    console.log('Wellness mode active');
})();
"""
    
    def _generate_react_native_wellness_scaffold(
        self, name: str, screens: List[str], complexity: str
    ) -> Dict[str, Any]:
        """Generate React Native app with wellness hooks"""
        return {
            'App.js': f"import React from 'react';\nexport default function App() {{ return null; }}",
            'package.json': json.dumps({
                'name': name.lower().replace(' ', '-'),
                'version': '1.0.0',
                'dependencies': {
                    'react': '^18.2.0',
                    'react-native': '^0.73.0'
                }
            })
        }
    
    def _generate_wellness_hook(self, intent: str, complexity: str) -> str:
        """Generate a wellness-optimized React hook"""
        hook_name = ''.join(word.capitalize() for word in intent.split()[:3])
        return f"""import {{ useState, useEffect, useCallback }} from 'react';

/**
 * use{hook_name} Hook
 * Complexity: {complexity}
 * Intent: {intent[:50]}
 */

export function use{hook_name}(options = {{
    const [state, setState] = useState(null);
    const [loading, setLoading] = useState(false);
    
    const execute = useCallback(async (params) => {{
        setLoading(true);
        try {{
            const result = await performAction(params);
            setState(result);
            return result;
        }} catch (err) {{
            console.warn('Action failed:', err.message);
        }} finally {{
            setLoading(false);
        }}
    }}, []);
    
    return {{ state, loading, execute }};
}}

async function performAction(params) {{
    return params;
}}
"""
    
    def _generate_wellness_component(self, intent: str, complexity: str) -> str:
        """Generate wellness-optimized UI component"""
        component_name = ''.join(word.capitalize() for word in intent.split()[:3])
        return f"""import React from 'react';
import {{ View, Text, StyleSheet }} from 'react-native';

export function {component_name}(props) {{
    return (
        <View style={{styles.container}}>
            <Text style={{styles.text}}>{{props.children}}</Text>
        </View>
    );
}}

const styles = StyleSheet.create({{
    container: {{
        padding: 16,
        borderRadius: 8,
    }},
    text: {{
        fontSize: 16,
        lineHeight: 24,
    }},
}});
"""
    
    def _extract_code_from_creation(self, creation: Creation) -> str:
        """Extract code string from creation for validation"""
        content = creation.content
        
        if isinstance(content, dict):
            parts = []
            if 'html' in content:
                parts.append(content['html'])
            if 'css' in content:
                parts.append(content['css'])
            if 'js' in content:
                parts.append(content['js'])
            if 'code' in content:
                parts.append(content['code'])
            return '\n'.join(parts)
        
        return str(content)
    
    def _generate_wellness_proof(
        self, creation: Creation, violations: List[Any], biometric_context: Dict[str, Any]
    ) -> str:
        """Generate a wellness proof hash for Terracare"""
        proof_data = {
            'creation_id': creation.creation_id,
            'violation_count': len(violations),
            'hrv_at_creation': biometric_context.get('hrv'),
            'timestamp': datetime.utcnow().isoformat(),
            'wellness_score': max(0, 10 - len(violations) * 2),
        }
        
        proof_string = json.dumps(proof_data, sort_keys=True)
        return hashlib.sha256(proof_string.encode()).hexdigest()[:32]
    
    def _calculate_token_rewards(
        self, creation: Creation, violations: List[Any], biometric_context: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate MINE/WELL token rewards"""
        base_mine = 20.0
        base_well = 0.2
        
        if len(violations) == 0:
            base_mine *= 1.5
            base_well *= 1.5
        
        if biometric_context.get('hrv', 0) > 60:
            base_mine *= 1.2
        
        return {
            'MINE': max(0, round(base_mine - len(violations) * 5, 2)),
            'WELL': max(0, round(base_well - len(violations) * 0.05, 3))
        }
    
    def _calculate_token_cost(self, intent: str, complexity: str) -> Dict[str, float]:
        """Calculate WELL token cost for generation"""
        base_cost = 0.5 if complexity == 'minimal' else (2.0 if complexity == 'full' else 1.0)
        return {'WELL': round(base_cost, 2), 'MINE': 0}
    
    async def _submit_to_terracare(
        self, creation: Creation, wellness_proof_hash: str,
        biometric_context: Dict[str, Any], session: TerracareSession
    ) -> Optional[str]:
        """Submit creation proof to Terracare ledger"""
        try:
            payload = {
                'type': 'CODE_CREATION',
                'creation_id': creation.creation_id,
                'wellness_proof_hash': wellness_proof_hash,
                'author_did': session.user_did,
                'hrv_at_creation': biometric_context.get('hrv'),
                'timestamp': datetime.utcnow().isoformat(),
            }
            
            response = await self.terracare_client.post(
                '/api/consensus/submit-proof',
                json=payload,
                headers={'Authorization': f'Bearer {session.session_token}'}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('tx_id')
            return None
        except Exception as e:
            logger.error(f"Terracare submission failed: {e}")
            return None


class InsufficientTokensError(Exception):
    """Raised when user lacks sufficient WELL tokens"""
    pass
