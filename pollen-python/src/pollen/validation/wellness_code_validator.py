"""
Wellness Code Validator - Healing-Centric Development Architecture

Validates code against stress/cognitive load thresholds and detects
anti-patterns that harm user wellbeing.
"""

import ast
import hashlib
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ViolationType(Enum):
    """Types of wellness violations"""
    INFINITE_SCROLL = "infinite_scroll"
    DARK_PATTERN = "dark_pattern"
    NOTIFICATION_SPAM = "notification_spam"
    COGNITIVE_OVERLOAD = "cognitive_overload"
    ANXIETY_INDUCING = "anxiety_inducing"
    SLEEP_DISRUPTING = "sleep_disrupting"
    ATTENTION_EXTRACTION = "attention_extraction"
    HIGH_COGNITIVE_LOAD = "high_cognitive_load"


@dataclass
class WellnessViolation:
    """Represents a wellness violation in code"""
    type: ViolationType
    severity: str  # 'critical', 'warning', 'info'
    location: str  # file:line:column
    message: str
    suggested_fix: str
    wellness_impact: str  # Description of health impact
    cognitive_load_increase: float  # 0.0 - 10.0


@dataclass
class CognitiveLoadReport:
    """Cognitive load analysis for code segment"""
    overall_score: float  # 0.0 - 10.0
    cyclomatic_complexity: int
    nesting_depth: int
    function_count: int
    average_function_length: float
    hrv_impact_estimate: str  # 'low', 'moderate', 'high', 'severe'
    stress_indicators: List[str]


class WellnessCodeValidator:
    """
    Validates code against wellness and stress thresholds.
    
    Integrates with Terracare ledger to ensure all code changes
    are aligned with healing principles and user biometric state.
    """
    
    # Anti-patterns that induce stress or addiction
    ANTI_PATTERNS = {
        ViolationType.INFINITE_SCROLL: {
            'patterns': [
                r'scroll.*infinite|infinite.*scroll|loadMore|onScrollToBottom',
                r'pagination.*auto|auto.*load|scroll.*trigger',
                r'PullToRefresh.*continuous|continuous.*scroll',
            ],
            'impact': 'Induces dopamine loops, reduces intentional engagement',
            'cognitive_load': 2.5,
        },
        ViolationType.DARK_PATTERN: {
            'patterns': [
                r'confirm.*tricky|tricky.*confirm|dark.*pattern',
                r'optOut.*hidden|hidden.*opt|preselected.*true','                r'roach motel|hard to cancel|forced continuity',
            ],
            'impact': 'Erodes trust, increases decision fatigue',
            'cognitive_load': 3.0,
        },
        ViolationType.NOTIFICATION_SPAM: {
            'patterns': [
                r'notification.*batch.*false|frequent.*notification',
                r'push.*aggressive|aggressive.*push|notify.*all',
                r'BadgeNumber.*increment|increment.*badge',
            ],
            'impact': 'Triggers anxiety, interrupts flow states',
            'cognitive_load': 2.0,
        },
        ViolationType.ANXIETY_INDUCING: {
            'patterns': [
                r'urgent|hurry|limited.*time|countdown.*small',
                r'fomo|fear.*missing|only.*left|others.*viewing',
                r'read.*receipt|typing.*indicator.*force',
            ],
            'impact': 'Activates stress response, elevates cortisol',
            'cognitive_load': 2.8,
        },
        ViolationType.SLEEP_DISRUPTING: {
            'patterns': [
                r'blue.*light|screen.*night|suppress.*melatonin',
                r'notification.*night|alert.*sleep|wake.*user',
                r'autoPlay.*sound|sound.*auto|video.*unmute',
            ],
            'impact': 'Disrupts circadian rhythm, reduces sleep quality',
            'cognitive_load': 1.5,
        },
        ViolationType.ATTENTION_EXTRACTION: {
            'patterns': [
                r'engagement.*maximize|maximize.*time.*spent',
                r'autoplay.*next|next.*auto| binge.*watch',
                r'sticky|addictive|hook.*model|variable.*reward',
            ],
            'impact': 'Hijacks attention, reduces agency',
            'cognitive_load': 3.5,
        },
    }
    
    # Wellness-positive alternatives
    HEALING_ALTERNATIVES = {
        ViolationType.INFINITE_SCROLL: {
            'pattern': 'Intentional pagination with mindful breaks',
            'implementation': 'useIntentionalPagination() with breath prompts every 10 items',
            'wellness_gain': 'Restores user agency, reduces doom-scrolling',
        },
        ViolationType.DARK_PATTERN: {
            'pattern': 'Transparent consent with clear options',
            'implementation': 'useTransparentConsent() with equal visual weight',
            'wellness_gain': 'Builds trust, reduces decision fatigue',
        },
        ViolationType.NOTIFICATION_SPAM: {
            'pattern': 'Mindful moment batching',
            'implementation': 'useMindfulNotifications() with circadian awareness',
            'wellness_gain': 'Respects attention, reduces anxiety',
        },
        ViolationType.ANXIETY_INDUCING: {
            'pattern': 'Calm urgency with breath integration',
            'implementation': 'useCalmUrgency() with HRV-responsive pacing',
            'wellness_gain': 'Maintains urgency without stress activation',
        },
        ViolationType.SLEEP_DISRUPTING: {
            'pattern': 'Circadian-aware UI with auto-dim',
            'implementation': 'useCircadianUI() with melatonin-friendly palettes',
            'wellness_gain': 'Protects sleep hygiene',
        },
        ViolationType.ATTENTION_EXTRACTION: {
            'pattern': 'Intentional engagement with exit prompts',
            'implementation': 'useIntentionalEngagement() with periodic check-ins',
            'wellness_gain': 'Respects user time, builds healthy habits',
        },
        ViolationType.HIGH_COGNITIVE_LOAD: {
            'pattern': 'Progressive disclosure with focus mode',
            'implementation': 'useProgressiveDisclosure() with complexity warnings',
            'wellness_gain': 'Reduces mental fatigue',
        },
    }
    
    def __init__(self, max_cognitive_load: float = 7.0, hrv_threshold: float = 45.0):
        self.max_cognitive_load = max_cognitive_load
        self.hrv_threshold = hrv_threshold
        self.violation_history: List[WellnessViolation] = []
        
    def validate_edit(
        self, 
        file_diff: str, 
        biometric_context: Dict[str, Any]
    ) -> Tuple[bool, List[WellnessViolation], Dict[str, Any]]:
        """
        Validates a code edit against wellness thresholds.
        
        Args:
            file_diff: The code diff to validate
            biometric_context: Current HRV, sleep score, stress level
            
        Returns:
            Tuple of (is_valid, violations, metadata)
        """
        violations = []
        
        # Check if user is in fit state to code
        current_hrv = biometric_context.get('hrv', 50)
        sleep_score = biometric_context.get('sleep_score', 7)
        stress_level = biometric_context.get('stress_level', 'low')
        
        # Block high-complexity edits during low HRV
        if current_hrv < self.hrv_threshold:
            complexity = self._estimate_diff_complexity(file_diff)
            if complexity > 5:
                violations.append(WellnessViolation(
                    type=ViolationType.HIGH_COGNITIVE_LOAD,
                    severity='critical',
                    location='diff:global',
                    message=f'Low HRV ({current_hrv}) suggests stress. Complex edits not recommended.',
                    suggested_fix='Take a breathing break, try again when HRV > 45',
                    wellness_impact='Coding during stress impairs decision-making and increases error rates',
                    cognitive_load_increase=complexity * 0.5
                ))
        
        # Parse and analyze the code
        try:
            tree = ast.parse(file_diff)
            violations.extend(self.detect_anti_patterns(tree))
            
            # Calculate cognitive load
            load_report = self.calculate_cognitive_load(file_diff)
            
            # Flag high cognitive load during poor sleep
            if sleep_score < 6 and load_report.overall_score > 6:
                violations.append(WellnessViolation(
                    type=ViolationType.HIGH_COGNITIVE_LOAD,
                    severity='warning',
                    location='diff:global',
                    message=f'High cognitive load code ({load_report.overall_score:.1f}) during poor sleep ({sleep_score})',
                    suggested_fix='Simplify logic or wait for better rest',
                    wellness_impact='Sleep-deprived coding increases technical debt',
                    cognitive_load_increase=load_report.overall_score - 6
                ))
            
            metadata = {
                'cognitive_load_report': load_report,
                'hrv_at_validation': current_hrv,
                'sleep_score_at_validation': sleep_score,
                'validation_hash': self._generate_validation_hash(file_diff, biometric_context)
            }
            
            is_valid = not any(v.severity == 'critical' for v in violations)
            
            self.violation_history.extend(violations)
            
            return is_valid, violations, metadata
            
        except SyntaxError as e:
            logger.error(f"Failed to parse code: {e}")
            return False, [], {'error': str(e)}
    
    def detect_anti_patterns(self, ast_tree: ast.AST) -> List[WellnessViolation]:
        """
        Detects addiction-inducing and stress-inducing patterns in code.
        
        Args:
            ast_tree: Parsed AST of the code
            
        Returns:
            List of wellness violations
        """
        violations = []
        source = ast.unparse(ast_tree) if hasattr(ast, 'unparse') else ""
        
        for violation_type, config in self.ANTI_PATTERNS.items():
            for pattern in config['patterns']:
                matches = re.finditer(pattern, source, re.IGNORECASE)
                for match in matches:
                    line_num = source[:match.start()].count('\n') + 1
                    
                    violations.append(WellnessViolation(
                        type=violation_type,
                        severity='warning',
                        location=f'diff:{line_num}:0',
                        message=f'Detected {violation_type.value}: {match.group()[:50]}...',
                        suggested_fix=self.suggest_healing_alternative(violation_type),
                        wellness_impact=config['impact'],
                        cognitive_load_increase=config['cognitive_load']
                    ))
        
        # AST-based analysis
        violations.extend(self._analyze_ast_wellness(ast_tree))
        
        return violations
    
    def calculate_cognitive_load(self, code_segment: str) -> CognitiveLoadReport:
        """
        Calculates cognitive load score weighted by estimated HRV impact.
        
        Uses cyclomatic complexity, nesting depth, and function metrics
        to estimate mental effort required to understand the code.
        
        Args:
            code_segment: The code to analyze
            
        Returns:
            CognitiveLoadReport with detailed metrics
        """
        try:
            tree = ast.parse(code_segment)
        except SyntaxError:
            return CognitiveLoadReport(
                overall_score=10.0,
                cyclomatic_complexity=999,
                nesting_depth=999,
                function_count=0,
                average_function_length=0,
                hrv_impact_estimate='severe',
                stress_indicators=['syntax_error']
            )
        
        # Calculate metrics
        complexity = self._calculate_cyclomatic_complexity(tree)
        nesting = self._calculate_nesting_depth(tree)
        func_metrics = self._analyze_functions(tree)
        
        # Calculate overall score (0-10)
        score = min(10.0, (
            (complexity / 10) * 3 +  # 30% weight
            (nesting / 5) * 2 +      # 20% weight
            (func_metrics['avg_length'] / 50) * 2 +  # 20% weight
            (func_metrics['count'] / 10) * 1.5 +     # 15% weight
            (1 if complexity > 15 else 0) * 1.5      # 15% bonus for high complexity
        ))
        
        # Determine HRV impact
        if score < 4:
            hrv_impact = 'low'
        elif score < 6:
            hrv_impact = 'moderate'
        elif score < 8:
            hrv_impact = 'high'
        else:
            hrv_impact = 'severe'
        
        # Identify stress indicators
        stress_indicators = []
        if complexity > 15:
            stress_indicators.append('high_cyclomatic_complexity')
        if nesting > 4:
            stress_indicators.append('deep_nesting')
        if func_metrics['avg_length'] > 50:
            stress_indicators.append('long_functions')
        if func_metrics['count'] > 10:
            stress_indicators.append('too_many_functions')
            
        return CognitiveLoadReport(
            overall_score=round(score, 2),
            cyclomatic_complexity=complexity,
            nesting_depth=nesting,
            function_count=func_metrics['count'],
            average_function_length=round(func_metrics['avg_length'], 2),
            hrv_impact_estimate=hrv_impact,
            stress_indicators=stress_indicators
        )
    
    def suggest_healing_alternative(self, violation_type: ViolationType) -> str:
        """
        Returns a wellness-positive code pattern to replace the violation.
        
        Args:
            violation_type: The type of violation detected
            
        Returns:
            Suggested healing pattern with implementation guidance
        """
        if violation_type not in self.HEALING_ALTERNATIVES:
            return "Review code for wellness impact"
        
        alt = self.HEALING_ALTERNATIVES[violation_type]
        return (
            f"Replace with: {alt['pattern']}\n"
            f"Implementation: {alt['implementation']}\n"
            f"Wellness gain: {alt['wellness_gain']}"
        )
    
    def _analyze_ast_wellness(self, tree: ast.AST) -> List[WellnessViolation]:
        """Additional AST-based wellness analysis"""
        violations = []
        
        for node in ast.walk(tree):
            # Detect tight loops that might cause UI freezing
            if isinstance(node, ast.For) or isinstance(node, ast.While):
                # Check if loop has any yield or sleep
                has_yield = any(
                    isinstance(n, (ast.Yield, ast.YieldFrom))
                    for n in ast.walk(node)
                )
                if not has_yield and self._is_tight_loop(node):
                    violations.append(WellnessViolation(
                        type=ViolationType.ANXIETY_INDUCING,
                        severity='info',
                        location=f'diff:{getattr(node, "lineno", 0)}:0',
                        message='Tight loop detected - may cause UI freezing',
                        suggested_fix='Add yield points or use async patterns',
                        wellness_impact='UI freezing causes user frustration',
                        cognitive_load_increase=1.0
                    ))
        
        return violations
    
    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """Calculate McCabe cyclomatic complexity"""
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, 
                                 ast.ExceptHandler, ast.With,
                                 ast.comprehension)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity
    
    def _calculate_nesting_depth(self, tree: ast.AST) -> int:
        """Calculate maximum nesting depth"""
        max_depth = 0
        
        def visit_node(node, depth=0):
            nonlocal max_depth
            if isinstance(node, (ast.If, ast.For, ast.While, 
                                 ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef, ast.With, ast.Try)):
                depth += 1
                max_depth = max(max_depth, depth)
            
            for child in ast.iter_child_nodes(node):
                visit_node(child, depth)
        
        visit_node(tree)
        return max_depth
    
    def _analyze_functions(self, tree: ast.AST) -> Dict[str, float]:
        """Analyze function metrics"""
        functions = [
            node for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        
        if not functions:
            return {'count': 0, 'avg_length': 0}
        
        lengths = []
        for func in functions:
            # Count lines in function
            if hasattr(func, 'end_lineno') and hasattr(func, 'lineno'):
                lengths.append(func.end_lineno - func.lineno)
            else:
                lengths.append(len(ast.unparse(func).split('\n')))
        
        return {
            'count': len(functions),
            'avg_length': sum(lengths) / len(lengths)
        }
    
    def _estimate_diff_complexity(self, diff: str) -> float:
        """Estimate complexity from raw diff"""
        lines_added = len([l for l in diff.split('\n') if l.startswith('+')])
        lines_removed = len([l for l in diff.split('\n') if l.startswith('-')])
        
        # Simple heuristic: more lines = more complexity
        total_changes = lines_added + lines_removed
        return min(10.0, total_changes / 20)
    
    def _is_tight_loop(self, node) -> bool:
        """Check if a loop is 'tight' (no yield/async)"""
        # Simplified check
        for child in ast.walk(node):
            if isinstance(child, (ast.Await, ast.Yield, ast.YieldFrom)):
                return False
            # Check for time.sleep or asyncio.sleep
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id in ['sleep', 'asyncio.sleep']:
                        return False
        return True
    
    def _generate_validation_hash(
        self, 
        file_diff: str, 
        biometric_context: Dict[str, Any]
    ) -> str:
        """Generate a proof hash for Terracare ledger"""
        data = f"{file_diff}:{biometric_context.get('hrv')}:{biometric_context.get('timestamp')}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
