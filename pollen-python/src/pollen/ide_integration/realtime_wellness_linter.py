"""
Realtime Wellness Linter - In-Editor Code Analysis

Analyzes code as it's being typed for stress-inducing patterns.
Provides immediate feedback in the IDE.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..validation.wellness_code_validator import WellnessCodeValidator, ViolationType

logger = logging.getLogger(__name__)


class LintSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


@dataclass
class WellnessLintDiagnostic:
    """Single lint diagnostic"""
    severity: LintSeverity
    message: str
    line: int
    column: int
    length: int
    code: str
    source: str = "pollen-wellness"
    related_info: Optional[List[Dict]] = None


class RealtimeWellnessLinter:
    """
    Real-time linter for wellness-aware code analysis.
    
    Analyzes code as it's being typed and provides immediate
    feedback on stress-inducing patterns.
    
    Integration with VSCode/Language Server Protocol:
        - Provides diagnostics on textDocument/didChange
        - Returns LSP-compatible diagnostic format
        - Updates in real-time as user types
    
    Usage:
        linter = RealtimeWellnessLinter()
        
        # On every keystroke or save
        diagnostics = linter.lint_document(code, language='typescript')
        
        # Send to IDE
        for diagnostic in diagnostics:
            publish_diagnostic(diagnostic)
    """
    
    # Patterns that indicate stress-inducing code
    STRESS_PATTERNS = {
        'tight_loop': {
            'patterns': [
                r'while\s*\(\s*true\s*\)',
                r'for\s*\(\s*;\s*;\s*\)',
                r'setInterval\s*\([^,]+,\s*\d+\s*\)',
            ],
            'message': 'Tight loop detected - may cause UI freezing',
            'severity': LintSeverity.WARNING,
            'wellness_impact': 'UI freezing causes user frustration and stress',
            'suggestion': 'Add yield points or use requestAnimationFrame',
        },
        'deep_nesting': {
            'patterns': [],  # Detected via AST
            'message': 'Deep nesting (>{depth} levels) increases cognitive load',
            'severity': LintSeverity.WARNING,
            'wellness_impact': 'Hard to read, increases mental fatigue',
            'suggestion': 'Extract into smaller functions',
        },
        'long_function': {
            'patterns': [],  # Detected via line counting
            'message': 'Function is {lines} lines - consider breaking down',
            'severity': LintSeverity.INFO,
            'wellness_impact': 'Long functions are harder to understand',
            'suggestion': 'Split into smaller, focused functions',
        },
        'aggressive_animation': {
            'patterns': [
                r'transition.*:\s*\d+ms',  # Fast transitions
                r'animation.*:\s*\w+\s+0\.\d+s',  # Sub-second animations
                r'shake|bounce|flash|pulse',  # Attention-grabbing animations
            ],
            'message': 'Aggressive animation may startle users',
            'severity': LintSeverity.WARNING,
            'wellness_impact': 'Unexpected motion can trigger anxiety',
            'suggestion': 'Use gentler animations (300ms+)',
        },
        'notification_spam': {
            'patterns': [
                r'Notification\s*\.\s*requestPermission',
                r'new\s+Notification\s*\(',
                r'push\s*\(\s*[^)]+\s*\)',
            ],
            'message': 'Notification code detected - ensure mindful usage',
            'severity': LintSeverity.INFO,
            'wellness_impact': 'Frequent notifications increase anxiety',
            'suggestion': 'Batch notifications and respect quiet hours',
        },
        'infinite_scroll_pattern': {
            'patterns': [
                r'onScrollToBottom|loadMore|infiniteScroll',
                r'scroll.*loading|loading.*scroll',
            ],
            'message': 'Infinite scroll pattern detected',
            'severity': LintSeverity.WARNING,
            'wellness_impact': 'Encourages compulsive behavior',
            'suggestion': 'Use pagination with intentional breaks',
        },
        'dark_pattern': {
            'patterns': [
                r'confirm.*tricky|trickyConfirm',
                r'optOut.*hidden|hiddenOptOut',
                r'preselected.*true|checked.*true',
            ],
            'message': 'Potential dark pattern detected',
            'severity': LintSeverity.ERROR,
            'wellness_impact': 'Erodes trust and causes decision fatigue',
            'suggestion': 'Use transparent, clear user choices',
        },
        'complex_logic': {
            'patterns': [
                r'if\s*\([^)]+\)\s*\{[^}]*if\s*\(',  # Nested ifs
                r'\?\s*\?\s*\?',  # Multiple null coalescing
            ],
            'message': 'Complex logic detected',
            'severity': LintSeverity.INFO,
            'wellness_impact': 'Increases cognitive load',
            'suggestion': 'Simplify or add clear comments',
        },
        'vibration_haptics': {
            'patterns': [
                r'navigator\.vibrate',
                r'Haptics\.impactAsync',
                r'Vibration API',
            ],
            'message': 'Haptic feedback detected',
            'severity': LintSeverity.HINT,
            'wellness_impact': 'Unexpected vibrations can startle',
            'suggestion': 'Use gentle haptics sparingly',
        },
    }
    
    def __init__(self):
        self.validator = WellnessCodeValidator()
        
    def lint_document(
        self, 
        code: str, 
        language: str = 'typescript',
        file_path: Optional[str] = None
    ) -> List[WellnessLintDiagnostic]:
        """
        Lint a document for wellness violations.
        
        Args:
            code: The code to lint
            language: Programming language
            file_path: Optional file path for context
            
        Returns:
            List of wellness diagnostics
        """
        diagnostics = []
        
        # Pattern-based linting
        diagnostics.extend(self._lint_patterns(code))
        
        # Language-specific linting
        if language in ['typescript', 'javascript', 'jsx', 'tsx']:
            diagnostics.extend(self._lint_javascript(code))
        elif language in ['python']:
            diagnostics.extend(self._lint_python(code))
        elif language in ['css', 'scss']:
            diagnostics.extend(self._lint_css(code))
        
        # Calculate complexity score
        complexity = self._estimate_complexity(code)
        if complexity > 7:
            diagnostics.append(WellnessLintDiagnostic(
                severity=LintSeverity.INFO,
                message=f'High complexity ({complexity}/10) - consider simplifying',
                line=1,
                column=0,
                length=0,
                code='WELLNESS_COMPLEXITY',
                related_info=[{
                    'message': f'Cognitive load: {complexity}/10',
                    'location': {'line': 1, 'column': 0}
                }]
            ))
        
        return diagnostics
    
    def lint_incremental(
        self,
        old_code: str,
        new_code: str,
        change_range: Dict[str, Any],
        language: str = 'typescript'
    ) -> List[WellnessLintDiagnostic]:
        """
        Lint only the changed portion of code (for performance).
        
        Args:
            old_code: Previous code state
            new_code: New code state
            change_range: {start_line, end_line, start_col, end_col}
            language: Programming language
            
        Returns:
            List of wellness diagnostics for changed region
        """
        # Extract changed region
        lines = new_code.split('\\n')
        start_line = change_range.get('start_line', 0)
        end_line = change_range.get('end_line', len(lines))
        
        changed_code = '\\n'.join(lines[start_line:end_line + 1])
        
        # Lint only changed region
        diagnostics = self.lint_document(changed_code, language)
        
        # Adjust line numbers
        for diag in diagnostics:
            diag.line += start_line
        
        return diagnostics
    
    def _lint_patterns(self, code: str) -> List[WellnessLintDiagnostic]:
        """Lint using regex patterns"""
        diagnostics = []
        lines = code.split('\\n')
        
        for pattern_name, pattern_config in self.STRESS_PATTERNS.items():
            for pattern in pattern_config.get('patterns', []):
                try:
                    for match in re.finditer(pattern, code, re.IGNORECASE):
                        line_num = code[:match.start()].count('\\n')
                        col_num = match.start() - code.rfind('\\n', 0, match.start()) - 1
                        
                        diagnostic = WellnessLintDiagnostic(
                            severity=pattern_config['severity'],
                            message=pattern_config['message'],
                            line=line_num,
                            column=col_num,
                            length=len(match.group()),
                            code=f'WELLNESS_{pattern_name.upper()}',
                            related_info=[{
                                'message': f"Impact: {pattern_config['wellness_impact']}",
                                'location': {'line': line_num, 'column': col_num}
                            }, {
                                'message': f"Suggestion: {pattern_config['suggestion']}",
                                'location': {'line': line_num, 'column': col_num}
                            }]
                        )
                        
                        diagnostics.append(diagnostic)
                        
                except re.error:
                    logger.warning(f"Invalid regex pattern: {pattern}")
        
        return diagnostics
    
    def _lint_javascript(self, code: str) -> List[WellnessLintDiagnostic]:
        """JavaScript/TypeScript specific linting"""
        diagnostics = []
        lines = code.split('\\n')
        
        # Check for function length
        in_function = False
        function_start = 0
        brace_count = 0
        
        for i, line in enumerate(lines):
            # Detect function start
            if re.search(r'(function|=>)\\s*\\(|async\\s+function', line):
                in_function = True
                function_start = i
                brace_count = line.count('{') - line.count('}')
            elif in_function:
                brace_count += line.count('{') - line.count('}')
                
                # Function ended
                if brace_count == 0:
                    function_length = i - function_start + 1
                    
                    if function_length > 50:
                        diagnostics.append(WellnessLintDiagnostic(
                            severity=LintSeverity.WARNING,
                            message=f'Function spans {function_length} lines - consider breaking down',
                            line=function_start,
                            column=0,
                            length=len(lines[function_start]),
                            code='WELLNESS_LONG_FUNCTION',
                            related_info=[{
                                'message': 'Long functions increase cognitive load',
                                'location': {'line': function_start, 'column': 0}
                            }]
                        ))
                    
                    in_function = False
        
        # Check for nested callbacks (callback hell)
        for i, line in enumerate(lines):
            if line.count('=>') > 2 or line.count('function') > 2:
                diagnostics.append(WellnessLintDiagnostic(
                    severity=LintSeverity.INFO,
                    message='Multiple callbacks on one line - consider async/await',
                    line=i,
                    column=0,
                    length=len(line),
                    code='WELLNESS_CALLBACK_HELL'
                ))
        
        return diagnostics
    
    def _lint_python(self, code: str) -> List[WellnessLintDiagnostic]:
        """Python specific linting"""
        diagnostics = []
        lines = code.split('\\n')
        
        # Check indentation depth (Python-specific)
        max_depth = 0
        for i, line in enumerate(lines):
            depth = len(line) - len(line.lstrip())
            max_depth = max(max_depth, depth)
            
            if depth > 16:  # 4 levels of indentation
                diagnostics.append(WellnessLintDiagnostic(
                    severity=LintSeverity.WARNING,
                    message=f'Deep nesting ({depth//4} levels) - consider refactoring',
                    line=i,
                    column=0,
                    length=len(line),
                    code='WELLNESS_DEEP_NESTING'
                ))
        
        return diagnostics
    
    def _lint_css(self, code: str) -> List[WellnessLintDiagnostic]:
        """CSS specific linting"""
        diagnostics = []
        
        # Check for aggressive animations
        if re.search(r'transition.*:\s*\d{1,2}ms', code):
            diagnostics.append(WellnessLintDiagnostic(
                severity=LintSeverity.INFO,
                message='Very fast transition detected - consider 150ms+ for calmer UX',
                line=0,
                column=0,
                length=0,
                code='WELLNESS_FAST_TRANSITION'
            ))
        
        # Check for jarring colors
        if re.search(r'color.*:\s*#ff0000|color.*:\s*red', code, re.IGNORECASE):
            diagnostics.append(WellnessLintDiagnostic(
                severity=LintSeverity.HINT,
                message='Pure red detected - consider a calmer color',
                line=0,
                column=0,
                length=0,
                code='WELLNESS_JARRING_COLOR'
            ))
        
        return diagnostics
    
    def _estimate_complexity(self, code: str) -> float:
        """Estimate code complexity (0-10)"""
        lines = code.split('\\n')
        
        # Simple heuristics
        score = 0.0
        
        # Line count
        if len(lines) > 100:
            score += 2
        elif len(lines) > 50:
            score += 1
        
        # Nesting indicators
        indent_levels = set()
        for line in lines:
            indent = len(line) - len(line.lstrip())
            indent_levels.add(indent)
        
        if len(indent_levels) > 4:
            score += 2
        elif len(indent_levels) > 2:
            score += 1
        
        # Control flow complexity
        control_keywords = ['if', 'for', 'while', 'switch', 'try', 'catch']
        for keyword in control_keywords:
            count = len(re.findall(rf'\\b{keyword}\\b', code))
            if count > 5:
                score += 1
        
        # Function/class density
        function_count = len(re.findall(r'(function|def|class)\\s+\\w+', code))
        if function_count > 10:
            score += 1
        
        return min(10.0, score)
    
    def to_lsp_diagnostic(self, diagnostic: WellnessLintDiagnostic) -> Dict[str, Any]:
        """Convert to Language Server Protocol diagnostic format"""
        severity_map = {
            LintSeverity.ERROR: 1,
            LintSeverity.WARNING: 2,
            LintSeverity.INFO: 3,
            LintSeverity.HINT: 4,
        }
        
        return {
            'range': {
                'start': {
                    'line': diagnostic.line,
                    'character': diagnostic.column,
                },
                'end': {
                    'line': diagnostic.line,
                    'character': diagnostic.column + diagnostic.length,
                }
            },
            'severity': severity_map.get(diagnostic.severity, 2),
            'code': diagnostic.code,
            'source': diagnostic.source,
            'message': diagnostic.message,
            'relatedInformation': [
                {
                    'location': {
                        'uri': '',  # Would be file path
                        'range': {
                            'start': info['location'],
                            'end': info['location']
                        }
                    },
                    'message': info['message']
                }
                for info in (diagnostic.related_info or [])
            ]
        }
