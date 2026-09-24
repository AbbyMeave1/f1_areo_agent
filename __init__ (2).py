"""
F1 Aerodynamics Agent module.
"""

from .core import F1AeroAgent
from .prompt import classify_question, get_supported_questions_text, get_enhanced_supported_questions_text, SYSTEM_PROMPT

__all__ = ['F1AeroAgent', 'classify_question', 'get_supported_questions_text', 'get_enhanced_supported_questions_text', 'SYSTEM_PROMPT']

# Made with Bob
