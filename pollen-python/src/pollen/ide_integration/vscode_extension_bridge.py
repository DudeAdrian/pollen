"""
VSCode Extension Bridge - Biometric Data Streaming

Provides API for VSCode extension to stream biometric data from Heartware
and receive real-time wellness feedback during coding sessions.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict

import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from ..validation.wellness_code_validator import WellnessCodeValidator

logger = logging.getLogger(__name__)


@dataclass
class BiometricDataPoint:
    """Single biometric data point from wearable"""
    timestamp: str
    hrv: float  # RMSSD in ms
    heart_rate: float
    stress_level: str  # 'low', 'medium', 'high'
    sleep_score: Optional[float]  # 0-10
    activity_level: str  # 'sedentary', 'light', 'moderate', 'intense'
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CodingSession:
    """Active coding session with biometric context"""
    session_id: str
    user_id: str
    started_at: str
    file_path: Optional[str]
    language: Optional[str]
    initial_hrv: float
    current_hrv: float
    hrv_trend: List[float]
    alerts_sent: int


class VSCodeExtensionBridge:
    """
    Bridge between VSCode extension and Pollen wellness system.
    
    Features:
    - WebSocket server for real-time biometric streaming
    - HTTP API for session management
    - Real-time wellness feedback during coding
    - Break suggestions based on HRV trends
    - Code complexity warnings based on biometric state
    
    Usage:
        bridge = VSCodeExtensionBridge()
        await bridge.start()
        
        # From VSCode extension:
        # Connect to ws://localhost:9001/biometrics
        # Stream HRV data every 30 seconds
    """
    
    def __init__(self, host: str = 'localhost', port: int = 9001):
        self.host = host
        self.port = port
        self.app = FastAPI(title="Pollen VSCode Bridge")
        self.validator = WellnessCodeValidator()
        
        # Active connections
        self.active_sessions: Dict[str, CodingSession] = {}
        self.websocket_connections: Dict[str, WebSocket] = {}
        
        # Callbacks for wellness events
        self.on_break_suggested: Optional[Callable] = None
        self.on_complexity_warning: Optional[Callable] = None
        
        # Current biometric state
        self.current_biometrics: Dict[str, BiometricDataPoint] = {}
        
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @self.app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "active_sessions": len(self.active_sessions),
                "websocket_connections": len(self.websocket_connections)
            }
        
        @self.app.post("/session/start")
        async def start_session(request: Dict[str, Any]):
            """Start a new coding session"""
            session_id = f"session_{datetime.utcnow().timestamp()}"
            
            session = CodingSession(
                session_id=session_id,
                user_id=request.get('user_id', 'anonymous'),
                started_at=datetime.utcnow().isoformat(),
                file_path=request.get('file_path'),
                language=request.get('language'),
                initial_hrv=request.get('initial_hrv', 50),
                current_hrv=request.get('initial_hrv', 50),
                hrv_trend=[],
                alerts_sent=0
            )
            
            self.active_sessions[session_id] = session
            
            logger.info(f"Started session: {session_id}")
            
            return {
                "session_id": session_id,
                "wellness_baseline": {
                    "hrv": session.initial_hrv,
                    "status": "optimal" if session.initial_hrv > 50 else "caution"
                }
            }
        
        @self.app.post("/session/{session_id}/end")
        async def end_session(session_id: str):
            """End a coding session and calculate impact"""
            if session_id not in self.active_sessions:
                return {"error": "Session not found"}
            
            session = self.active_sessions.pop(session_id)
            
            # Calculate session impact
            hrv_change = session.current_hrv - session.initial_hrv
            duration_minutes = self._calculate_duration(session.started_at)
            
            return {
                "session_id": session_id,
                "duration_minutes": duration_minutes,
                "hrv_change": hrv_change,
                "hrv_trend": session.hrv_trend,
                "impact": "positive" if hrv_change > 0 else "negative" if hrv_change < -5 else "neutral",
                "alerts_sent": session.alerts_sent
            }
        
        @self.app.post("/biometrics/update")
        async def update_biometrics(data: Dict[str, Any]):
            """Receive biometric update from Heartware"""
            user_id = data.get('user_id', 'anonymous')
            
            biometric = BiometricDataPoint(
                timestamp=datetime.utcnow().isoformat(),
                hrv=data.get('hrv', 50),
                heart_rate=data.get('heart_rate', 70),
                stress_level=data.get('stress_level', 'low'),
                sleep_score=data.get('sleep_score'),
                activity_level=data.get('activity_level', 'sedentary')
            )
            
            self.current_biometrics[user_id] = biometric
            
            # Check for alerts
            alerts = self._check_wellness_alerts(user_id, biometric)
            
            return {
                "received": True,
                "alerts": alerts,
                "biometric_state": biometric.to_dict()
            }
        
        @self.app.get("/wellness/status/{user_id}")
        async def get_wellness_status(user_id: str):
            """Get current wellness status for user"""
            biometrics = self.current_biometrics.get(user_id)
            
            if not biometrics:
                return {
                    "status": "unknown",
                    "message": "No biometric data available"
                }
            
            # Determine coding recommendation
            recommendation = self._get_coding_recommendation(biometrics)
            
            return {
                "status": recommendation['status'],
                "hrv": biometrics.hrv,
                "stress_level": biometrics.stress_level,
                "can_code": recommendation['can_code'],
                "recommended_complexity": recommendation['complexity'],
                "message": recommendation['message']
            }
        
        @self.app.websocket("/biometrics/{user_id}")
        async def biometric_websocket(websocket: WebSocket, user_id: str):
            """WebSocket for real-time biometric streaming"""
            await websocket.accept()
            self.websocket_connections[user_id] = websocket
            
            logger.info(f"WebSocket connected: {user_id}")
            
            try:
                while True:
                    # Receive biometric data from VSCode extension
                    data = await websocket.receive_json()
                    
                    # Process data
                    biometric = BiometricDataPoint(
                        timestamp=datetime.utcnow().isoformat(),
                        hrv=data.get('hrv', 50),
                        heart_rate=data.get('heart_rate', 70),
                        stress_level=data.get('stress_level', 'low'),
                        sleep_score=data.get('sleep_score'),
                        activity_level=data.get('activity_level', 'sedentary')
                    )
                    
                    self.current_biometrics[user_id] = biometric
                    
                    # Check for wellness issues
                    alerts = self._check_wellness_alerts(user_id, biometric)
                    
                    # Send feedback
                    await websocket.send_json({
                        "type": "wellness_feedback",
                        "alerts": alerts,
                        "coding_recommendation": self._get_coding_recommendation(biometric),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: {user_id}")
                del self.websocket_connections[user_id]
    
    async def start(self):
        """Start the bridge server"""
        import uvicorn
        
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        
        logger.info(f"Starting VSCode Bridge on {self.host}:{self.port}")
        
        await server.serve()
    
    def _check_wellness_alerts(
        self, 
        user_id: str, 
        biometrics: BiometricDataPoint
    ) -> List[Dict[str, Any]]:
        """Check for wellness alerts based on biometric data"""
        alerts = []
        
        # HRV alerts
        if biometrics.hrv < 30:
            alerts.append({
                "type": "critical_hrv",
                "severity": "high",
                "message": "HRV critically low. Recommend stopping coding session.",
                "hrv": biometrics.hrv,
                "action": "stop_coding"
            })
        elif biometrics.hrv < 45:
            alerts.append({
                "type": "low_hrv",
                "severity": "medium",
                "message": "HRV below optimal. Consider a break.",
                "hrv": biometrics.hrv,
                "action": "suggest_break"
            })
        
        # Stress alerts
        if biometrics.stress_level == 'high':
            alerts.append({
                "type": "high_stress",
                "severity": "medium",
                "message": "High stress detected. Take a breath before continuing.",
                "action": "breathing_exercise"
            })
        
        # Heart rate alerts during sedentary activity
        if biometrics.activity_level == 'sedentary' and biometrics.heart_rate > 100:
            alerts.append({
                "type": "elevated_hr",
                "severity": "low",
                "message": "Heart rate elevated while coding. Consider a walk.",
                "action": "movement_break"
            })
        
        # Update session
        if user_id in self.active_sessions:
            session = self.active_sessions[user_id]
            session.current_hrv = biometrics.hrv
            session.hrv_trend.append(biometrics.hrv)
            
            if alerts:
                session.alerts_sent += len(alerts)
        
        return alerts
    
    def _get_coding_recommendation(
        self, 
        biometrics: BiometricDataPoint
    ) -> Dict[str, Any]:
        """Get coding recommendation based on biometric state"""
        hrv = biometrics.hrv
        stress = biometrics.stress_level
        sleep = biometrics.sleep_score or 7
        
        # Determine status
        if hrv < 30 or sleep < 4:
            return {
                "status": "critical",
                "can_code": False,
                "complexity": "none",
                "message": "Biometrics indicate you need rest. Coding not recommended."
            }
        
        if hrv < 45 or stress == 'high' or sleep < 6:
            return {
                "status": "caution",
                "can_code": True,
                "complexity": "minimal",
                "message": "Low complexity tasks only. Take breaks every 20 minutes."
            }
        
        if hrv < 55 or sleep < 7:
            return {
                "status": "moderate",
                "can_code": True,
                "complexity": "balanced",
                "message": "Good to code. Complexity balanced recommended."
            }
        
        return {
            "status": "optimal",
            "can_code": True,
            "complexity": "full",
            "message": "Optimal state for coding. Full complexity available."
        }
    
    def _calculate_duration(self, started_at: str) -> int:
        """Calculate session duration in minutes"""
        start = datetime.fromisoformat(started_at)
        return int((datetime.utcnow() - start).total_seconds() / 60)
    
    async def send_to_vscode(self, user_id: str, message: Dict[str, Any]):
        """Send message to VSCode extension via WebSocket"""
        if user_id in self.websocket_connections:
            websocket = self.websocket_connections[user_id]
            await websocket.send_json(message)
