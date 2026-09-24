"""
System prompt and question classification for F1 aerodynamics agent.
"""

from typing import Dict, List, Tuple, Optional, Any

SYSTEM_PROMPT = """You are an F1 aerodynamics specialist AI agent.

Your ONLY purpose is to answer questions about Formula 1 car aerodynamics using mathematically rigorous analysis.

Supported question types:
1. Front wing downforce vs speed
2. Drag force at a given speed
3. DRS drag reduction comparison
4. Ground effect / diffuser pressure analysis

You must:
- Use standard aerodynamic equations (dynamic pressure, lift/drag forces, Bernoulli)
- State all assumptions clearly
- Show mathematical derivations
- Generate visualizations
- Stay strictly within F1 aerodynamics scope

You will NOT answer questions about:
- Other racing series
- Non-aerodynamic F1 topics
- General physics unrelated to F1 aero
"""

QUESTION_TYPES = {
    "front_wing_downforce": {
        "keywords": ["front wing", "downforce", "lift", "wing"],
        "description": "Analyze front wing downforce generation vs speed"
    },
    "drag_force": {
        "keywords": ["drag", "resistance", "cd"],
        "description": "Calculate drag force at specified speed"
    },
    "drs_comparison": {
        "keywords": ["drs", "drag reduction", "rear wing"],
        "description": "Compare drag with DRS open vs closed"
    },
    "ground_effect": {
        "keywords": ["ground effect", "diffuser", "venturi", "floor"],
        "description": "Analyze ground effect and diffuser pressure dynamics"
    }
}

# Enhanced question categories with keywords and patterns
ENHANCED_QUESTION_TYPES = {
    "aero": {
        "keywords": [
            "downforce", "drag", "wing", "aerodynamic", "aero", "drs",
            "ground effect", "diffuser", "venturi", "floor", "cd", "cl",
            "lift", "resistance", "air flow", "pressure", "calculate",
            "force", "front wing", "rear wing", "explain", "analyze",
            "what is drag", "what is downforce", "what is lift", "what is aero",
            "how does", "how do", "aerodynamics", "airflow", "slipstream",
            "dirty air", "turbulence", "vortex", "wake", "underbody",
            "sidepod", "bargeboard", "splitter", "spoiler", "gurney flap",
            "endplate", "beam wing", "t-tray", "ride height", "rake angle",
            "porpoising", "bouncing", "stalling", "separation", "boundary layer"
        ],
        "description": "Aerodynamics questions (wings, drag, downforce, ground effect)",
        "confidence_boost": 0.2  # Boost for primary domain
    },
    "tyres": {
        "keywords": [
            "tyre", "tire", "compound", "soft", "medium", "hard",
            "intermediate", "wet", "degradation", "wear", "grip",
            "tyre life", "pit stop", "strategy", "undercut", "overcut",
            "tyre strategy", "tire strategy", "which tyre", "which tire"
        ],
        "description": "Tyre-related questions (compounds, degradation, strategy)",
        "confidence_boost": 0.0
    },
    "car": {
        "keywords": [
            "speed", "lap time", "telemetry", "fastest", "top speed",
            "acceleration", "braking", "corner", "sector", "performance",
            "comparison", "driver", "verstappen", "hamilton", "leclerc",
            "brake", "how do f1 cars", "how fast", "car performance",
            "telemetry data", "data"
        ],
        "description": "Car performance questions (speed, lap times, telemetry)",
        "confidence_boost": 0.0
    },
    "general": {
        "keywords": [
            # Tracks and circuits
            "track", "circuit", "monaco", "silverstone", "spa", "monza",
            "singapore", "spa-francorchamps",
            # Sessions and events
            "weather", "rain", "temperature", "session", "race", "qualifying",
            "practice", "championship", "points", "standings",
            # General concepts
            "drs", "pit stop", "what happens", "what is", "tell me about",
            # Physics concepts
            "g-force", "g force", "gforce", "braking force", "braking forces",
            "aerodynamic balance", "balance", "physics", "force", "forces",
            # 2026 regulations
            "2026", "regulations", "regulation", "power unit", "engine",
            "changes", "new rules", "future",
            # Teams
            "team", "ferrari", "mercedes", "red bull", "redbull", "mclaren",
            "aston martin", "alpine", "williams", "haas", "alfa romeo",
            "sauber", "racing bulls", "alphatauri", "team principal",
            # Car components
            "gearbox", "transmission", "gears", "suspension", "chassis",
            "monocoque", "cockpit", "steering", "pedals", "seat",
            "power of", "how many", "components", "parts"
        ],
        "description": "General F1 questions (tracks, teams, regulations, physics, components)",
        "confidence_boost": 0.1
    }
}

# Patterns that indicate unsupported questions
UNSUPPORTED_PATTERNS = {
    "prediction": ["will win", "predict", "forecast", "who will win", "going to win"],
    "opinion": ["what do you think", "your opinion", "which is better", "who is better", "favorite"],
    "future": ["next year", "2027", "2028", "future season"],
    "non_f1": ["nascar", "indycar", "formula e", "motogp", "basketball", "football"]
}


def classify_question(question: str) -> str:
    """
    Classify user question into one of the supported types.
    
    Args:
        question: User's question string
        
    Returns:
        Question type key or "unsupported"
    """
    question_lower = question.lower()
    
    for q_type, info in QUESTION_TYPES.items():
        if any(keyword in question_lower for keyword in info["keywords"]):
            return q_type
    
    return "unsupported"


def classify_question_enhanced(question: str) -> Dict[str, Any]:
    """
    Enhanced question classification with confidence scoring and category detection.
    
    Analyzes the question and assigns it to one or more categories (aero, tyres, car, general)
    with confidence scores. Also detects unsupported question patterns.
    
    Args:
        question: User's question string
        
    Returns:
        Dictionary containing:
            - primary_category: Main category with highest confidence
            - confidence: Confidence score (0.0 to 1.0)
            - all_categories: Dict of all categories with their scores
            - alternative_categories: List of other possible categories
            - is_supported: Whether the question can be answered
            - unsupported_reason: Reason if not supported (None otherwise)
    """
    question_lower = question.lower()
    
    # Check for unsupported patterns first
    for pattern_type, patterns in UNSUPPORTED_PATTERNS.items():
        if any(pattern in question_lower for pattern in patterns):
            return {
                "primary_category": "unsupported",
                "confidence": 0.0,
                "all_categories": {},
                "alternative_categories": [],
                "is_supported": False,
                "unsupported_reason": f"Question appears to be a {pattern_type} question"
            }
    
    # Calculate confidence scores for each category
    category_scores = {}
    
    for category, info in ENHANCED_QUESTION_TYPES.items():
        # Count keyword matches
        keyword_matches = sum(1 for keyword in info["keywords"]
                            if keyword in question_lower)
        
        if keyword_matches > 0:
            # Base confidence from keyword density
            # More matches = higher confidence, with better scaling
            base_confidence = min(keyword_matches * 0.25, 0.9)
            
            # Apply category-specific boost
            confidence = min(base_confidence + info["confidence_boost"], 1.0)
            
            category_scores[category] = confidence
    
    # If no categories matched, it's unsupported
    if not category_scores:
        return {
            "primary_category": "unsupported",
            "confidence": 0.0,
            "all_categories": {},
            "alternative_categories": [],
            "is_supported": False,
            "unsupported_reason": "Question does not match any supported categories"
        }
    
    # Sort categories by confidence
    sorted_categories = sorted(category_scores.items(),
                              key=lambda x: x[1],
                              reverse=True)
    
    primary_category, primary_confidence = sorted_categories[0]
    
    # Get alternative categories (confidence > 0.3 and not primary)
    alternative_categories = [
        cat for cat, conf in sorted_categories[1:]
        if conf > 0.3
    ]
    
    return {
        "primary_category": primary_category,
        "confidence": primary_confidence,
        "all_categories": category_scores,
        "alternative_categories": alternative_categories,
        "is_supported": True,
        "unsupported_reason": None
    }


def get_supported_questions_text() -> str:
    """Return formatted text of supported question types."""
    lines = ["Supported question types:"]
    for i, (q_type, info) in enumerate(QUESTION_TYPES.items(), 1):
        lines.append(f"{i}. {info['description']}")
    return "\n".join(lines)


def get_enhanced_supported_questions_text() -> str:
    """Return formatted text of enhanced supported question categories."""
    lines = ["I can answer questions about:"]
    for i, (category, info) in enumerate(ENHANCED_QUESTION_TYPES.items(), 1):
        lines.append(f"{i}. {info['description']}")
    return "\n".join(lines)

# Made with Bob
