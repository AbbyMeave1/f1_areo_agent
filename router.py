"""
Question Router

Routes questions to appropriate handlers based on enhanced classification
with confidence thresholds and fallback logic.
"""

from typing import Dict, Any, Optional
from .prompt import classify_question_enhanced


class QuestionRouter:
    """
    Routes questions to appropriate handlers based on category and confidence.
    
    Uses priority-based routing with confidence thresholds to determine
    which handler should process a given question.
    """
    
    # Confidence thresholds for each category
    CONFIDENCE_THRESHOLDS = {
        "aero": 0.3,      # Lower threshold to catch simple aerodynamics questions
        "tyres": 0.4,     # Lower threshold
        "car": 0.4,       # Lower threshold
        "general": 0.3    # Lowest threshold for general questions
    }
    
    # Minimum confidence to avoid fallback
    MIN_CONFIDENCE = 0.3
    
    def __init__(self):
        """Initialize the question router."""
        pass
    
    def route_question(self, question: str) -> Dict[str, Any]:
        """
        Route a question to the appropriate handler.
        
        Analyzes the question using enhanced classification and determines
        which handler should process it based on confidence scores and
        category-specific thresholds.
        
        Args:
            question: User's question string
            
        Returns:
            Dictionary containing:
                - handler: Handler name to use ('aero', 'tyres', 'car', 'general', 'fallback')
                - classification: Full classification result
                - should_fallback: Whether to use fallback response
                - fallback_reason: Reason for fallback (if applicable)
        """
        # Get enhanced classification
        classification = classify_question_enhanced(question)
        
        # Check if question is supported
        if not classification["is_supported"]:
            return {
                "handler": "fallback",
                "classification": classification,
                "should_fallback": True,
                "fallback_reason": classification["unsupported_reason"]
            }
        
        primary_category = classification["primary_category"]
        confidence = classification["confidence"]
        
        # Check if confidence meets the threshold for the primary category
        threshold = self.CONFIDENCE_THRESHOLDS.get(primary_category, self.MIN_CONFIDENCE)
        
        if confidence >= threshold:
            # Confidence is sufficient, route to primary handler
            return {
                "handler": primary_category,
                "classification": classification,
                "should_fallback": False,
                "fallback_reason": None
            }
        
        # Check alternative categories
        for alt_category in classification["alternative_categories"]:
            alt_confidence = classification["all_categories"].get(alt_category, 0.0)
            alt_threshold = self.CONFIDENCE_THRESHOLDS.get(alt_category, self.MIN_CONFIDENCE)
            
            if alt_confidence >= alt_threshold:
                # Alternative category meets threshold
                return {
                    "handler": alt_category,
                    "classification": classification,
                    "should_fallback": False,
                    "fallback_reason": None
                }
        
        # No category meets threshold, use fallback
        return {
            "handler": "fallback",
            "classification": classification,
            "should_fallback": True,
            "fallback_reason": (
                f"Confidence too low for {primary_category} "
                f"({confidence:.2f} < {threshold:.2f})"
            )
        }
    
    def get_routing_info(self, question: str) -> str:
        """
        Get human-readable routing information for debugging.
        
        Args:
            question: User's question string
            
        Returns:
            Formatted string with routing details
        """
        routing = self.route_question(question)
        classification = routing["classification"]
        
        lines = []
        lines.append("=== Question Routing Analysis ===")
        lines.append(f"Question: {question}")
        lines.append("")
        lines.append(f"Primary Category: {classification['primary_category']}")
        lines.append(f"Confidence: {classification['confidence']:.2f}")
        lines.append(f"Handler: {routing['handler']}")
        lines.append(f"Should Fallback: {routing['should_fallback']}")
        
        if routing['fallback_reason']:
            lines.append(f"Fallback Reason: {routing['fallback_reason']}")
        
        if classification['alternative_categories']:
            lines.append("")
            lines.append("Alternative Categories:")
            for alt_cat in classification['alternative_categories']:
                alt_conf = classification['all_categories'][alt_cat]
                lines.append(f"  - {alt_cat}: {alt_conf:.2f}")
        
        lines.append("")
        lines.append("All Category Scores:")
        for cat, score in sorted(classification['all_categories'].items(), 
                                key=lambda x: x[1], reverse=True):
            threshold = self.CONFIDENCE_THRESHOLDS.get(cat, self.MIN_CONFIDENCE)
            status = "✓" if score >= threshold else "✗"
            lines.append(f"  {status} {cat}: {score:.2f} (threshold: {threshold:.2f})")
        
        return "\n".join(lines)
    
    def update_threshold(self, category: str, threshold: float) -> None:
        """
        Update the confidence threshold for a category.
        
        Args:
            category: Category name
            threshold: New threshold value (0.0 to 1.0)
            
        Raises:
            ValueError: If threshold is out of range
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")
        
        self.CONFIDENCE_THRESHOLDS[category] = threshold
    
    def get_thresholds(self) -> Dict[str, float]:
        """
        Get current confidence thresholds for all categories.
        
        Returns:
            Dictionary of category thresholds
        """
        return self.CONFIDENCE_THRESHOLDS.copy()

# Made with Bob