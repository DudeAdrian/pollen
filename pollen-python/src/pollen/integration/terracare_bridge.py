"""
Terracare Bridge - Healing-Centric Development Integration

Provides integration with Terracare Ledger for:
- Code proof submission
- Token validation
- Biometric impact logging
"""

import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

import httpx

from ..config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class CodeProofSubmission:
    """Represents a code proof submission to the ledger"""
    code_hash: str
    wellness_metrics: Dict[str, Any]
    author_did: str
    timestamp: str
    proof_type: str = 'CODE_CREATION'


@dataclass
class BiometricImpactLog:
    """Represents biometric impact of code changes"""
    code_id: str
    pre_hrv: float
    post_hrv: float
    pre_stress: str
    post_stress: str
    duration_minutes: int
    impact_assessment: str


class TerracareBridge:
    """
    Bridge to Terracare Ledger for healing-centric development.
    
    Handles all interactions with the Terracare blockchain including:
    - Proof submission for code creations
    - Token balance validation
    - Biometric impact tracking
    - Consensus participation
    """
    
    def __init__(
        self,
        ledger_url: str = "http://localhost:3000",
        api_key: Optional[str] = None,
        wallet_private_key: Optional[str] = None
    ):
        self.ledger_url = ledger_url.rstrip('/')
        self.api_key = api_key
        self.wallet_private_key = wallet_private_key
        self.client = httpx.AsyncClient(
            base_url=self.ledger_url,
            timeout=30.0,
            headers={'Content-Type': 'application/json'}
        )
        self._session_token: Optional[str] = None
        
    async def connect(self, did: str, signature: str) -> bool:
        """
        Authenticate with Terracare ledger.
        
        Args:
            did: Decentralized Identifier
            signature: Signed authentication challenge
            
        Returns:
            True if authenticated successfully
        """
        try:
            response = await self.client.post(
                '/api/auth/verify',
                json={
                    'did': did,
                    'signature': signature,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self._session_token = data.get('session_token')
                self.client.headers['Authorization'] = f'Bearer {self._session_token}'
                logger.info(f"Connected to Terracare as {did}")
                return True
            else:
                logger.error(f"Terracare auth failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Terracare connection failed: {e}")
            return False
    
    async def submit_code_proof(
        self,
        code_hash: str,
        wellness_metrics: Dict[str, Any],
        author_did: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Submit code proof to Hive ledger.
        
        Args:
            code_hash: SHA256 hash of the code
            wellness_metrics: Dict with hrv, sleep_score, stress_level, etc.
            author_did: Author's decentralized identifier
            metadata: Optional additional metadata
            
        Returns:
            Tuple of (success, tx_id, response_data)
        """
        if not self._session_token:
            logger.error("Not authenticated with Terracare")
            return False, None, None
        
        proof = CodeProofSubmission(
            code_hash=code_hash,
            wellness_metrics=wellness_metrics,
            author_did=author_did,
            timestamp=datetime.utcnow().isoformat()
        )
        
        payload = {
            'type': 'CODE_PROOF',
            'code_hash': proof.code_hash,
            'wellness_metrics': proof.wellness_metrics,
            'author_did': proof.author_did,
            'timestamp': proof.timestamp,
            'wellness_score': self._calculate_wellness_score(wellness_metrics),
            'metadata': metadata or {}
        }
        
        try:
            response = await self.client.post(
                '/api/consensus/submit-proof',
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                tx_id = data.get('tx_id')
                logger.info(f"Code proof submitted: {tx_id}")
                return True, tx_id, data
            else:
                logger.error(f"Proof submission failed: {response.text}")
                return False, None, None
                
        except Exception as e:
            logger.error(f"Failed to submit code proof: {e}")
            return False, None, None
    
    async def validate_build_token(
        self,
        intent_complexity: str,
        user_did: Optional[str] = None
    ) -> Tuple[bool, Dict[str, float], Optional[str]]:
        """
        Check if user has sufficient WELL tokens for generation.
        
        Args:
            intent_complexity: 'minimal', 'balanced', or 'full'
            user_did: User's DID (optional if already authenticated)
            
        Returns:
            Tuple of (has_sufficient, required_amounts, error_message)
        """
        # Calculate required tokens based on complexity
        token_costs = {
            'minimal': {'WELL': 0.5, 'MINE': 0},
            'balanced': {'WELL': 1.0, 'MINE': 0},
            'full': {'WELL': 2.0, 'MINE': 0}
        }
        
        required = token_costs.get(intent_complexity, token_costs['balanced'])
        
        try:
            # Query user's token balance
            response = await self.client.get(
                f'/api/economics/balance',
                params={'did': user_did or 'self'}
            )
            
            if response.status_code != 200:
                return False, required, "Failed to query balance"
            
            balance = response.json()
            available_well = balance.get('WELL', 0)
            
            if available_well < required['WELL']:
                return (
                    False,
                    required,
                    f"Insufficient WELL. Required: {required['WELL']}, Available: {available_well}"
                )
            
            return True, required, None
            
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return False, required, str(e)
    
    async def log_biometric_impact(
        self,
        code_id: str,
        pre_hrv: float,
        post_hrv: float,
        pre_stress: str = 'unknown',
        post_stress: str = 'unknown',
        duration_minutes: int = 0
    ) -> Tuple[bool, Optional[str]]:
        """
        Track physiological impact of code changes.
        
        Args:
            code_id: Identifier of the code worked on
            pre_hrv: HRV before coding session
            post_hrv: HRV after coding session
            pre_stress: Stress level before ('low', 'medium', 'high')
            post_stress: Stress level after
            duration_minutes: Length of coding session
            
        Returns:
            Tuple of (success, tx_id)
        """
        if not self._session_token:
            logger.error("Not authenticated with Terracare")
            return False, None
        
        # Calculate impact
        hrv_change = post_hrv - pre_hrv
        
        if hrv_change > 5:
            impact = 'positive'
        elif hrv_change > -5:
            impact = 'neutral'
        else:
            impact = 'negative'
        
        log = BiometricImpactLog(
            code_id=code_id,
            pre_hrv=pre_hrv,
            post_hrv=post_hrv,
            pre_stress=pre_stress,
            post_stress=post_stress,
            duration_minutes=duration_minutes,
            impact_assessment=impact
        )
        
        payload = {
            'type': 'BIOMETRIC_IMPACT',
            'code_id': log.code_id,
            'pre_hrv': log.pre_hrv,
            'post_hrv': log.post_hrv,
            'hrv_change': hrv_change,
            'pre_stress': log.pre_stress,
            'post_stress': log.post_stress,
            'duration_minutes': log.duration_minutes,
            'impact_assessment': log.impact_assessment,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            response = await self.client.post(
                '/api/wellness/log-impact',
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                tx_id = data.get('tx_id')
                
                # Reward MINE for positive impact
                if impact == 'positive':
                    await self._reward_positive_impact(code_id, hrv_change)
                
                logger.info(f"Biometric impact logged: {tx_id} ({impact})")
                return True, tx_id
            else:
                logger.error(f"Impact logging failed: {response.text}")
                return False, None
                
        except Exception as e:
            logger.error(f"Failed to log biometric impact: {e}")
            return False, None
    
    async def get_code_wellness_history(
        self,
        code_id: Optional[str] = None,
        author_did: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve wellness history for code or author.
        
        Args:
            code_id: Specific code ID (optional)
            author_did: Specific author (optional)
            
        Returns:
            Dict with wellness history data
        """
        params = {}
        if code_id:
            params['code_id'] = code_id
        if author_did:
            params['author_did'] = author_did
        
        try:
            response = await self.client.get(
                '/api/wellness/code-history',
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': response.text}
                
        except Exception as e:
            logger.error(f"Failed to get wellness history: {e}")
            return {'error': str(e)}
    
    async def get_wellness_leaderboard(
        self,
        timeframe: str = 'week'
    ) -> List[Dict[str, Any]]:
        """
        Get leaderboard of most wellness-positive developers.
        
        Args:
            timeframe: 'day', 'week', 'month'
            
        Returns:
            List of top wellness contributors
        """
        try:
            response = await self.client.get(
                '/api/wellness/leaderboard',
                params={'timeframe': timeframe}
            )
            
            if response.status_code == 200:
                return response.json().get('leaders', [])
            else:
                return []
                
        except Exception as e:
            logger.error(f"Failed to get leaderboard: {e}")
            return []
    
    def _calculate_wellness_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall wellness score from metrics"""
        hrv = metrics.get('hrv', 50)
        sleep_score = metrics.get('sleep_score', 7)
        stress_level = metrics.get('stress_level', 'low')
        
        # HRV component (0-40 points)
        hrv_score = min(40, max(0, (hrv / 100) * 40))
        
        # Sleep component (0-30 points)
        sleep_component = min(30, (sleep_score / 10) * 30)
        
        # Stress component (0-30 points)
        stress_scores = {'low': 30, 'medium': 20, 'high': 10, 'unknown': 15}
        stress_component = stress_scores.get(stress_level, 15)
        
        return round(hrv_score + sleep_component + stress_component, 2)
    
    async def _reward_positive_impact(
        self,
        code_id: str,
        hrv_improvement: float
    ):
        """Reward MINE tokens for positive biometric impact"""
        try:
            reward_amount = min(50, hrv_improvement * 2)  # Cap at 50 MINE
            
            await self.client.post(
                '/api/economics/reward',
                json={
                    'type': 'POSITIVE_BIOMETRIC_IMPACT',
                    'code_id': code_id,
                    'amount': reward_amount,
                    'reason': f'HRV improved by {hrv_improvement:.1f}ms'
                }
            )
            
            logger.info(f"Rewarded {reward_amount} MINE for positive impact")
            
        except Exception as e:
            logger.error(f"Failed to reward positive impact: {e}")
    
    async def close(self):
        """Close the Terracare connection"""
        await self.client.aclose()


# Convenience functions for direct use

async def submit_code_proof(
    ledger_url: str,
    code_hash: str,
    wellness_metrics: Dict[str, Any],
    author_did: str,
    session_token: str
) -> Tuple[bool, Optional[str]]:
    """
    Convenience function to submit code proof without creating bridge instance.
    
    Returns:
        Tuple of (success, tx_id)
    """
    bridge = TerracareBridge(ledger_url)
    bridge._session_token = session_token
    bridge.client.headers['Authorization'] = f'Bearer {session_token}'
    
    success, tx_id, _ = await bridge.submit_code_proof(
        code_hash, wellness_metrics, author_did
    )
    
    await bridge.close()
    return success, tx_id


async def validate_build_token(
    ledger_url: str,
    intent_complexity: str,
    user_did: str
) -> Tuple[bool, str]:
    """
    Convenience function to validate token balance.
    
    Returns:
        Tuple of (has_sufficient, message)
    """
    bridge = TerracareBridge(ledger_url)
    
    has_sufficient, required, error = await bridge.validate_build_token(
        intent_complexity, user_did
    )
    
    await bridge.close()
    
    if error:
        return False, error
    
    return True, f"Sufficient tokens. Cost: {required['WELL']} WELL"


async def log_biometric_impact(
    ledger_url: str,
    code_id: str,
    pre_hrv: float,
    post_hrv: float,
    session_token: str,
    **kwargs
) -> Tuple[bool, Optional[str]]:
    """
    Convenience function to log biometric impact.
    
    Returns:
        Tuple of (success, tx_id)
    """
    bridge = TerracareBridge(ledger_url)
    bridge._session_token = session_token
    bridge.client.headers['Authorization'] = f'Bearer {session_token}'
    
    success, tx_id = await bridge.log_biometric_impact(
        code_id=code_id,
        pre_hrv=pre_hrv,
        post_hrv=post_hrv,
        **kwargs
    )
    
    await bridge.close()
    return success, tx_id
