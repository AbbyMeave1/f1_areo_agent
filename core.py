"""
Core agent logic for F1 aerodynamics analysis.
"""

from typing import Dict, Any, Optional, List, Tuple
import re
from .prompt import (
    classify_question,
    classify_question_enhanced,
    get_supported_questions_text,
    get_enhanced_supported_questions_text,
    SYSTEM_PROMPT
)
from .router import QuestionRouter
from ..physics import calculations
from ..physics.mcp_client import MCPPhysicsClient
from ..visualization import generator
from ..data.fastf1_client import FastF1Client
from ..data.knowledge_base import KnowledgeBase
from ..data.cache_manager import CacheManager


class F1AeroAgent:
    """
    F1 Aerodynamics AI Agent.
    
    Analyzes F1 aerodynamics questions using physics calculations
    and generates visualizations. Now supports tyre, car performance,
    and general F1 questions in addition to aerodynamics.
    """
    
    def __init__(
        self,
        cache_manager: Optional[CacheManager] = None,
        enable_fastf1: bool = True,
        enable_mcp: bool = False
    ):
        """
        Initialize the agent.
        
        Args:
            cache_manager: Optional CacheManager instance for data caching
            enable_fastf1: Whether to enable Fast-F1 integration (default: True)
            enable_mcp: Whether to enable MCP physics server integration (experimental)
        """
        self.system_prompt = SYSTEM_PROMPT
        self.router = QuestionRouter()
        self.knowledge_base = KnowledgeBase()
        
        # Initialize conversation memory (stores last 10 Q&A pairs)
        self.conversation_history = []
        self.max_history_size = 10
        
        # Initialize Fast-F1 client if enabled
        self.fastf1_client = None
        self.fastf1_enabled = enable_fastf1
        if enable_fastf1:
            try:
                self.fastf1_client = FastF1Client(cache_manager)
                print("✓ Fast-F1 integration enabled - Real F1 data available")
            except ImportError:
                print("⚠ Warning: Fast-F1 library not available. Install with: pip install fastf1>=3.0.0")
                self.fastf1_enabled = False
        
        # Initialize MCP physics client if enabled
        self.mcp_client = None
        self.mcp_enabled = enable_mcp
        if enable_mcp:
            try:
                self.mcp_client = MCPPhysicsClient(use_mcp=True)
                print("✓ MCP physics server integration enabled (experimental)")
            except Exception as e:
                print(f"⚠ Warning: MCP integration failed: {e}")
                self.mcp_client = MCPPhysicsClient(use_mcp=False)  # Fallback to analytic
                self.mcp_enabled = False
        else:
            # Always have an MCP client available (fallback mode)
            self.mcp_client = MCPPhysicsClient(use_mcp=False)
    
    def process_question(self, question: str) -> Dict[str, Any]:
        """
        Process a user question about F1 (aerodynamics, tyres, car performance, or general).
        
        Uses enhanced classification and routing to direct questions to appropriate handlers.
        Supports aerodynamics (primary), tyres, car performance, and general F1 questions.
        Now includes conversation memory for context-aware responses.
        
        Args:
            question: User's question string
            
        Returns:
            Dictionary containing analysis results, visualization path, and metadata
        """
        # Check for context references in the question
        question_with_context = self._resolve_context_references(question)
        
        # Check if visualization is requested
        question_lower = question_with_context.lower()
        generate_viz = self._is_visualization_request(question_with_context)
        
        # Route the question using enhanced classification
        routing = self.router.route_question(question_with_context)
        handler = routing["handler"]
        
        # Handle fallback cases
        if routing["should_fallback"]:
            result = self._generate_fallback_response(question_with_context, routing)
            self._add_to_history(question, result)
            return result
        
        # Route to appropriate handler
        try:
            if handler == "aero":
                # Use legacy classification for aero questions to maintain compatibility
                question_type = classify_question(question_with_context)
                if question_type == "front_wing_downforce":
                    result = self._analyze_front_wing_downforce(question_with_context, generate_viz)
                elif question_type == "drag_force":
                    result = self._analyze_drag_force(question_with_context, generate_viz)
                elif question_type == "drs_comparison":
                    result = self._analyze_drs_comparison(question_with_context, generate_viz)
                elif question_type == "ground_effect":
                    result = self._analyze_ground_effect(question_with_context, generate_viz)
                else:
                    # Aero category but no specific calculation match - try conceptual answer
                    result = self._handle_conceptual_aero_question(question_with_context)
                    if result is None:
                        result = self._generate_fallback_response(question_with_context, routing)
                        self._add_to_history(question, result)
                        return result
                
                result["question_type"] = question_type if question_type != "unsupported" else "conceptual_aero"
            
            elif handler == "tyres":
                result = self._handle_tyre_question(question_with_context)
            
            elif handler == "car":
                result = self._handle_car_question(question_with_context)
            
            elif handler == "general":
                result = self._handle_general_question(question_with_context)
            
            else:
                result = self._generate_fallback_response(question_with_context, routing)
                self._add_to_history(question, result)
                return result
            
            result["success"] = True
            result["question"] = question
            result["handler"] = handler
            result["classification"] = routing["classification"]
            
            # Add to conversation history
            self._add_to_history(question, result)
            
            return result
            
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "question": question,
                "handler": handler,
                "classification": routing.get("classification")
            }
            self._add_to_history(question, result)
            return result
    
    def _analyze_front_wing_downforce(self, question: str, generate_viz: bool = False) -> Dict[str, Any]:
        """Analyze front wing downforce vs speed."""
        # Perform calculations
        calc_data = calculations.calculate_front_wing_downforce_vs_speed()
        
        # Format response
        speeds = calc_data["speeds_kmh"]
        downforce = calc_data["downforce_n"]
        
        response = {
            "analysis_type": "Front Wing Downforce vs Speed",
            "summary": (
                f"Front wing downforce increases quadratically with speed, "
                f"ranging from {downforce[0]:.0f} N at {speeds[0]:.0f} km/h "
                f"to {downforce[-1]:.0f} N at {speeds[-1]:.0f} km/h."
            ),
            "explanation": (
                "The front wing generates downforce through aerodynamic lift (negative lift). "
                "As the car moves faster, the dynamic pressure increases rapidly, so the wing pushes the car harder into the track. "
                "That gives the car more grip in faster corners and explains why aerodynamic load grows so strongly with speed."
            ),
            "math_explanation": (
                "The mathematical model uses dynamic pressure q = 0.5 * ρ * v² and downforce magnitude "
                "F_downforce = q * A * |C_l|. Because velocity is squared, downforce also scales approximately "
                "with v², so doubling speed produces roughly four times the downforce."
            ),
            "assumptions": calc_data["assumptions"],
            "equations": calc_data["equations"],
            "key_results": {
                "min_speed_kmh": speeds[0],
                "max_speed_kmh": speeds[-1],
                "min_downforce_n": downforce[0],
                "max_downforce_n": downforce[-1],
                "wing_area_m2": calc_data["wing_area"],
                "lift_coefficient": calc_data["cl"]
            },
            "data": calc_data
        }
        
        # Generate visualization when requested or when the analysis is inherently comparative/trend-based
        if generate_viz or any(keyword in question.lower() for keyword in ["different speeds", "vs", "versus", "compare", "comparison"]):
            viz_path = generator.generate_visualization("front_wing_downforce", calc_data)
            if viz_path:
                response["visualization"] = viz_path
                response["graph_path"] = viz_path
                response["visualization_message"] = f"Visualization created and saved to {viz_path}"
        
        return response
    
    def _analyze_drag_force(self, question: str, generate_viz: bool = False) -> Dict[str, Any]:
        """Analyze drag force at a specific speed."""
        # Extract speed from question (simple heuristic)
        import re
        speed_match = re.search(r'(\d+)\s*(?:km/?h|kph)', question.lower())
        speed_kmh = float(speed_match.group(1)) if speed_match else 300.0
        
        # Check for DRS mention
        drs_open = 'drs' in question.lower() and 'open' in question.lower()
        
        # Perform calculations
        calc_data = calculations.calculate_drag_at_speed(speed_kmh, drs_open)
        
        # Format response
        response = {
            "analysis_type": "Drag Force Analysis",
            "summary": (
                f"At {speed_kmh:.0f} km/h with DRS {'open' if drs_open else 'closed'}, "
                f"the drag force is {calc_data['drag_force_n']:.0f} N. "
                f"Dynamic pressure: {calc_data['dynamic_pressure_pa']:.0f} Pa."
            ),
            "explanation": (
                f"Drag is the aerodynamic resistance pushing against the car as it moves through the air. "
                f"At {speed_kmh:.0f} km/h, that resistance is substantial, and {'opening DRS reduces rear-wing drag at the cost of downforce' if drs_open else 'keeping DRS closed preserves downforce but increases resistance'}. "
                f"This is why straight-line speed and cornering performance are always a trade-off in F1."
            ),
            "math_explanation": (
                f"The calculation uses q = 0.5 * ρ * v² for dynamic pressure and F_drag = q * A * C_d for drag force. "
                f"Here, q = {calc_data['dynamic_pressure_pa']:.0f} Pa and C_d = {calc_data['cd']:.2f}, so the resulting drag force is "
                f"{calc_data['drag_force_n']:.0f} N. Because velocity is squared, drag rises very quickly as speed increases."
            ),
            "assumptions": calc_data["assumptions"],
            "equations": calc_data["equations"],
            "key_results": {
                "speed_kmh": speed_kmh,
                "drag_force_n": calc_data["drag_force_n"],
                "dynamic_pressure_pa": calc_data["dynamic_pressure_pa"],
                "drag_coefficient": calc_data["cd"],
                "drs_status": "open" if drs_open else "closed"
            },
            "data": calc_data
        }
        
        # Generate visualization for explicit requests and direct aerodynamic calculations
        if generate_viz or "calculate drag" in question.lower() or "drag at" in question.lower():
            viz_path = generator.generate_visualization("drag_force", calc_data)
            if viz_path:
                response["visualization"] = viz_path
                response["graph_path"] = viz_path
                response["visualization_message"] = f"Visualization created and saved to {viz_path}"
        
        return response
    
    def _analyze_drs_comparison(self, question: str, generate_viz: bool = False) -> Dict[str, Any]:
        """Compare DRS open vs closed."""
        # Perform calculations
        calc_data = calculations.compare_drs_drag()
        
        # Calculate average reduction
        import numpy as np
        avg_reduction = np.mean(calc_data["drag_reduction_percent"])
        
        # Format response
        response = {
            "analysis_type": "DRS Drag Reduction Comparison",
            "summary": (
                f"DRS (Drag Reduction System) reduces drag by an average of {avg_reduction:.1f}% "
                f"across the speed range {calc_data['speeds_kmh'][0]:.0f}-{calc_data['speeds_kmh'][-1]:.0f} km/h. "
                f"This is achieved by reducing the drag coefficient from {calc_data['cd_closed']:.2f} "
                f"to {calc_data['cd_open']:.2f}."
            ),
            "explanation": (
                "DRS opens the rear wing to reduce aerodynamic resistance on straights. "
                f"That makes the car faster in a straight line by lowering drag, but it also reduces rear downforce. "
                f"The result is a clear trade-off: better top speed and overtaking potential, but less aerodynamic load."
            ),
            "math_explanation": (
                f"The comparison uses F_drag = q * A * C_d across a speed range, with q = 0.5 * ρ * v². "
                f"Changing the drag coefficient from {calc_data['cd_closed']:.2f} to {calc_data['cd_open']:.2f} lowers drag at every speed, "
                f"producing an average reduction of {avg_reduction:.1f}%. Because q grows with v², the absolute drag savings become larger at higher speeds."
            ),
            "assumptions": calc_data["assumptions"],
            "equations": calc_data["equations"],
            "key_results": {
                "avg_drag_reduction_percent": avg_reduction,
                "cd_closed": calc_data["cd_closed"],
                "cd_open": calc_data["cd_open"],
                "speed_range_kmh": [calc_data['speeds_kmh'][0], calc_data['speeds_kmh'][-1]]
            },
            "data": calc_data
        }
        
        # Generate visualization for explicit requests and comparison analyses
        if generate_viz or any(keyword in question.lower() for keyword in ["compare", "comparison", "vs", "versus", "drs open vs closed"]):
            viz_path = generator.generate_visualization("drs_comparison", calc_data)
            if viz_path:
                response["visualization"] = viz_path
                response["graph_path"] = viz_path
                response["visualization_message"] = f"Visualization created and saved to {viz_path}"
        
        return response
    
    def _analyze_ground_effect(self, question: str, generate_viz: bool = False) -> Dict[str, Any]:
        """Analyze ground effect and diffuser dynamics."""
        # Extract speed if mentioned
        import re
        speed_match = re.search(r'(\d+)\s*(?:km/?h|kph)', question.lower())
        speed_kmh = float(speed_match.group(1)) if speed_match else 300.0
        
        # Perform calculations
        calc_data = calculations.analyze_ground_effect(freestream_velocity=speed_kmh)
        
        # Format response with enhanced explanation
        response = {
            "analysis_type": "Ground Effect Analysis",
            "summary": (
                f"At {speed_kmh:.0f} km/h, the ground effect generates approximately "
                f"{calc_data['estimated_downforce_n']:.0f} N of downforce through the venturi effect. "
                f"Air accelerates to {calc_data['diffuser_velocity_ms']:.1f} m/s under the car "
                f"(from {calc_data['freestream_velocity_ms']:.1f} m/s), creating a pressure drop "
                f"of {calc_data['pressure_drop_pa']:.0f} Pa."
            ),
            "explanation": (
                f"{calc_data['explanation']}\n\n"
                f"In practical terms, faster airflow under the car lowers pressure beneath the floor, so the car is pulled downward toward the track. "
                f"That extra load improves grip without adding much mass, which is why ground effect is so important in modern F1."
            ),
            "math_explanation": (
                f"The model applies continuity and Bernoulli-style reasoning. Air speed rises from "
                f"{calc_data['freestream_velocity_ms']:.1f} m/s to {calc_data['diffuser_velocity_ms']:.1f} m/s, creating a pressure drop of "
                f"{calc_data['pressure_drop_pa']:.0f} Pa. Estimated downforce is then approximated with F_downforce ≈ ΔP * A_floor, "
                f"giving about {calc_data['estimated_downforce_n']:.0f} N."
            ),
            "assumptions": calc_data["assumptions"],
            "equations": calc_data["equations"],
            "key_results": {
                "freestream_velocity_kmh": speed_kmh,
                "diffuser_velocity_ms": calc_data["diffuser_velocity_ms"],
                "pressure_drop_pa": calc_data["pressure_drop_pa"],
                "estimated_downforce_n": calc_data["estimated_downforce_n"],
                "velocity_ratio": calc_data["velocity_ratio"]
            },
            "data": calc_data
        }
        
        # Generate visualization only if requested
        if generate_viz:
            viz_path = generator.generate_visualization("ground_effect", calc_data)
            if viz_path:
                response["visualization"] = viz_path
                response["graph_path"] = viz_path
                response["visualization_message"] = f"Visualization created and saved to {viz_path}"
        
        return response
    
    def _handle_conceptual_aero_question(self, question: str) -> Optional[Dict[str, Any]]:
        """
        Handle conceptual aerodynamics questions that don't require calculations.
        
        Args:
            question: User's conceptual aerodynamics question
            
        Returns:
            Dictionary with conceptual explanation, or None if not recognized
        """
        question_lower = question.lower()
        
        # Define conceptual aerodynamics topics
        aero_concepts = {
            "drag": {
                "name": "Drag Force",
                "summary": (
                    "Drag is the aerodynamic force that opposes a car's motion through the air. "
                    "In F1, drag increases with the square of velocity and is a major factor limiting top speed."
                ),
                "explanation": (
                    "Drag Force in Formula 1:\n\n"
                    "Drag is the resistance force that air exerts on the car as it moves forward. "
                    "It's one of the two primary aerodynamic forces (along with downforce) that affect F1 car performance.\n\n"
                    "Key characteristics:\n"
                    "• Increases with the square of velocity (F_drag = 0.5 × ρ × v² × A × C_d)\n"
                    "• Opposes the car's motion, requiring more power to overcome\n"
                    "• Typical F1 drag coefficient (C_d): 0.7-1.1 depending on configuration\n"
                    "• At 300 km/h, drag force can exceed 6,000 N (about 600 kg)\n\n"
                    "Trade-offs:\n"
                    "• High downforce setups increase drag (more rear wing angle)\n"
                    "• Low drag setups sacrifice downforce for higher top speed\n"
                    "• DRS (Drag Reduction System) reduces drag by ~10-15% when activated\n\n"
                    "Impact on performance:\n"
                    "• Limits top speed on straights\n"
                    "• Affects fuel consumption and energy management\n"
                    "• Teams balance drag vs downforce based on track characteristics"
                ),
                "related_topics": ["downforce", "drs", "drag coefficient"]
            },
            "downforce": {
                "name": "Downforce",
                "summary": (
                    "Downforce is the vertical aerodynamic force that pushes the car down onto the track, "
                    "increasing grip and allowing higher cornering speeds. Modern F1 cars generate more downforce than their own weight."
                ),
                "explanation": (
                    "Downforce in Formula 1:\n\n"
                    "Downforce is negative lift - an aerodynamic force that pushes the car toward the ground. "
                    "It's the most important aerodynamic factor for lap time performance.\n\n"
                    "How it's generated:\n"
                    "• Front wing: Creates ~25-30% of total downforce\n"
                    "• Floor and diffuser: Creates ~50-60% of total downforce (ground effect)\n"
                    "• Rear wing: Creates ~15-20% of total downforce\n"
                    "• Other elements: Bargeboard, sidepods, etc.\n\n"
                    "Key characteristics:\n"
                    "• Increases with the square of velocity (like drag)\n"
                    "• At 300 km/h, modern F1 cars generate 3,000-4,000 kg of downforce\n"
                    "• Allows cars to theoretically drive upside down in a tunnel\n"
                    "• Increases tire grip without adding weight\n\n"
                    "Benefits:\n"
                    "• Higher cornering speeds (up to 6G lateral acceleration)\n"
                    "• Better braking performance\n"
                    "• Improved traction out of corners\n\n"
                    "Trade-offs:\n"
                    "• More downforce = more drag = lower top speed\n"
                    "• Teams adjust wing angles based on track layout"
                ),
                "related_topics": ["front wing", "ground effect", "drag"]
            },
            "front wing": {
                "name": "Front Wing",
                "summary": (
                    "The front wing is the first aerodynamic element to meet the air. "
                    "It generates downforce, manages airflow to the rest of the car, and is crucial for balance."
                ),
                "explanation": (
                    "Front Wing Aerodynamics:\n\n"
                    "The front wing is one of the most complex and important aerodynamic components on an F1 car.\n\n"
                    "Primary functions:\n"
                    "1. Generate downforce on the front axle (~25-30% of total)\n"
                    "2. Condition airflow for downstream components\n"
                    "3. Create outwash to direct air around the tires\n"
                    "4. Balance the car's aerodynamic platform\n\n"
                    "Design features:\n"
                    "• Multiple elements (typically 3-5 flaps)\n"
                    "• Adjustable angle for different tracks\n"
                    "• Endplates to manage vortices\n"
                    "• Highly cambered profiles for maximum lift coefficient\n\n"
                    "How it works:\n"
                    "• Air flows faster over the top surface than the bottom\n"
                    "• Creates pressure difference (Bernoulli's principle)\n"
                    "• Lower pressure on top = downward force\n"
                    "• Typical lift coefficient (C_l): -3.0 to -4.0\n\n"
                    "Adjustability:\n"
                    "• Teams can adjust the angle between sessions\n"
                    "• More angle = more downforce but more drag\n"
                    "• Less angle = less downforce but higher top speed\n\n"
                    "Sensitivity:\n"
                    "• Very sensitive to ride height and rake angle\n"
                    "• Easily damaged, affecting overall car balance\n"
                    "• Critical for following other cars (dirty air effect)"
                ),
                "related_topics": ["downforce", "wing", "aerodynamics"]
            },
            "rear wing": {
                "name": "Rear Wing",
                "summary": (
                    "The rear wing generates downforce on the rear axle and houses the DRS system. "
                    "It's the most visible and adjustable aerodynamic element."
                ),
                "explanation": (
                    "Rear Wing Aerodynamics:\n\n"
                    "The rear wing is the most prominent aerodynamic device, creating significant downforce and drag.\n\n"
                    "Primary functions:\n"
                    "1. Generate downforce on the rear axle (~15-20% of total)\n"
                    "2. Balance the front wing's downforce\n"
                    "3. House the DRS (Drag Reduction System)\n"
                    "4. Manage wake and reduce drag when possible\n\n"
                    "Design features:\n"
                    "• Two main elements (main plane and flap)\n"
                    "• DRS actuator on the top flap\n"
                    "• Endplates to contain airflow\n"
                    "• Beam wing underneath (smaller secondary wing)\n\n"
                    "Track-specific configurations:\n"
                    "• High downforce (Monaco, Hungary): Steep angles, maximum downforce\n"
                    "• Low downforce (Monza, Spa): Shallow angles, minimal drag\n"
                    "• Medium downforce: Balanced setup for most tracks\n\n"
                    "DRS (Drag Reduction System):\n"
                    "• Opens the top flap to reduce drag by ~10-15%\n"
                    "• Reduces rear downforce but increases top speed\n"
                    "• Only available in designated zones when within 1 second\n"
                    "• Typical speed gain: 10-15 km/h on straights"
                ),
                "related_topics": ["drs", "downforce", "drag"]
            },
            "ground effect": {
                "name": "Ground Effect",
                "summary": (
                    "Ground effect is the phenomenon where the car's floor and diffuser create low pressure underneath, "
                    "generating massive downforce. It's the primary source of downforce in modern F1 cars."
                ),
                "explanation": (
                    "Ground Effect Aerodynamics:\n\n"
                    "Ground effect is the most efficient way to generate downforce in F1, producing 50-60% of total downforce.\n\n"
                    "How it works:\n"
                    "1. Air is forced under the car through narrow channels\n"
                    "2. Venturi effect: Air accelerates as the channel narrows\n"
                    "3. Bernoulli's principle: Faster air = lower pressure\n"
                    "4. Pressure difference creates suction force\n"
                    "5. Diffuser at rear gradually expands flow, recovering pressure\n\n"
                    "Key components:\n"
                    "• Underbody floor with shaped channels\n"
                    "• Venturi tunnels along the sides\n"
                    "• Diffuser at the rear (expanding section)\n"
                    "• Edge floor and skid blocks\n\n"
                    "Advantages:\n"
                    "• Very efficient: High downforce with relatively low drag\n"
                    "• Less affected by following other cars (vs. wings)\n"
                    "• Scales well with speed\n\n"
                    "Challenges:\n"
                    "• Sensitive to ride height (must run car low)\n"
                    "• Porpoising: Aerodynamic bouncing at high speed\n"
                    "• Stalling: Loss of downforce if floor sealing is compromised\n"
                    "• Requires precise suspension setup\n\n"
                    "2022 regulations:\n"
                    "• Reintroduced ground effect as primary downforce source\n"
                    "• Aimed to improve racing by reducing dirty air effect\n"
                    "• Venturi tunnels replace complex bargeboards"
                ),
                "related_topics": ["diffuser", "downforce", "venturi"]
            },
            "drs": {
                "name": "DRS (Drag Reduction System)",
                "summary": (
                    "DRS is a movable rear wing flap that reduces drag to help overtaking. "
                    "It can only be used in designated zones when within 1 second of the car ahead."
                ),
                "explanation": (
                    "DRS (Drag Reduction System):\n\n"
                    "DRS is an overtaking aid introduced in 2011 to make racing more exciting.\n\n"
                    "How it works:\n"
                    "• Opens a gap in the rear wing's top flap\n"
                    "• Reduces the wing's angle of attack\n"
                    "• Decreases drag coefficient by ~10-15%\n"
                    "• Reduces rear downforce but increases top speed\n\n"
                    "Activation rules:\n"
                    "• Only in designated DRS zones (usually on straights)\n"
                    "• Must be within 1 second of car ahead at detection point\n"
                    "• Automatically disabled when driver brakes\n"
                    "• Not available in first 2 laps or wet conditions\n\n"
                    "Performance impact:\n"
                    "• Speed gain: 10-15 km/h on straights\n"
                    "• Drag reduction: ~10-15%\n"
                    "• Downforce loss: ~15-20% on rear axle\n"
                    "• Lap time gain: 0.2-0.4 seconds per activation\n\n"
                    "Strategic considerations:\n"
                    "• Defending driver cannot use DRS\n"
                    "• Multiple DRS zones can create 'DRS trains'\n"
                    "• Effectiveness varies by track and car setup\n"
                    "• Can be used in qualifying (all laps, all zones)"
                ),
                "related_topics": ["drag", "rear wing", "overtaking"]
            },
            "lift": {
                "name": "Lift (Negative Lift)",
                "summary": (
                    "In F1, 'lift' usually refers to negative lift (downforce). "
                    "Positive lift is undesirable as it reduces grip and stability."
                ),
                "explanation": (
                    "Lift in Formula 1:\n\n"
                    "In aerodynamics, lift is the force perpendicular to the direction of motion. "
                    "F1 cars are designed to generate negative lift (downforce).\n\n"
                    "Negative lift (downforce):\n"
                    "• Desired force that pushes car toward ground\n"
                    "• Generated by wings, floor, and diffuser\n"
                    "• Increases with speed squared\n"
                    "• Improves cornering and braking performance\n\n"
                    "Positive lift (undesirable):\n"
                    "• Reduces tire grip and stability\n"
                    "• Can occur when car is airborne or in dirty air\n"
                    "• Dangerous at high speeds\n"
                    "• Prevented by careful aerodynamic design\n\n"
                    "Lift coefficient (C_l):\n"
                    "• Negative values indicate downforce\n"
                    "• Front wing: C_l ≈ -3.0 to -4.0\n"
                    "• Rear wing: C_l ≈ -2.5 to -3.5\n"
                    "• Total car: C_l ≈ -3.0 to -4.0\n\n"
                    "The equation:\n"
                    "F_lift = 0.5 × ρ × v² × A × C_l\n"
                    "Where negative C_l gives downforce (negative lift)"
                ),
                "related_topics": ["downforce", "wing", "aerodynamics"]
            },
            "aerodynamics": {
                "name": "F1 Aerodynamics",
                "summary": (
                    "Aerodynamics is the study of how air flows around the F1 car. "
                    "It's the most important performance differentiator in modern F1."
                ),
                "explanation": (
                    "Formula 1 Aerodynamics Overview:\n\n"
                    "Aerodynamics is the science of managing airflow to generate downforce while minimizing drag.\n\n"
                    "Primary goals:\n"
                    "1. Maximize downforce for cornering speed\n"
                    "2. Minimize drag for straight-line speed\n"
                    "3. Balance front and rear downforce\n"
                    "4. Manage airflow to cooling systems\n"
                    "5. Reduce sensitivity to following other cars\n\n"
                    "Key components:\n"
                    "• Front wing: First element, conditions airflow\n"
                    "• Floor and diffuser: Largest downforce contributor (ground effect)\n"
                    "• Rear wing: Balances front, houses DRS\n"
                    "• Sidepods: Cooling and airflow management\n"
                    "• Bargeboards (pre-2022): Complex vortex generators\n\n"
                    "Fundamental principles:\n"
                    "• Bernoulli's principle: Pressure + velocity = constant\n"
                    "• Venturi effect: Narrowing channel accelerates flow\n"
                    "• Boundary layer: Thin layer of slow-moving air on surfaces\n"
                    "• Vortices: Rotating air structures that manage flow\n\n"
                    "Performance impact:\n"
                    "• Accounts for ~40% of lap time performance\n"
                    "• More important than engine power in modern F1\n"
                    "• Heavily regulated to control costs and improve racing\n\n"
                    "Development:\n"
                    "• Wind tunnel testing (limited hours)\n"
                    "• CFD (Computational Fluid Dynamics) simulations\n"
                    "• Track testing and correlation\n"
                    "• Continuous evolution throughout season"
                ),
                "related_topics": ["downforce", "drag", "ground effect", "wings"]
            }
        }
        
        # Check which concept matches the question
        for concept_key, concept_data in aero_concepts.items():
            if concept_key in question_lower or any(topic in question_lower for topic in concept_data.get("related_topics", [])):
                return {
                    "analysis_type": concept_data["name"],
                    "summary": concept_data["summary"],
                    "explanation": concept_data["explanation"],
                    "key_results": {
                        "concept": concept_data["name"],
                        "category": "Aerodynamics",
                        "related_topics": concept_data.get("related_topics", [])
                    },
                    "data": {
                        "concept_type": "aerodynamics",
                        "concept_name": concept_data["name"]
                    }
                }
        
        # No matching concept found
        return None
    
    def _handle_tyre_question(self, question: str) -> Dict[str, Any]:
        """
        Handle tyre-related questions using the knowledge base.
        
        Args:
            question: User's question about tyres
            
        Returns:
            Dictionary with tyre information and analysis
        """
        question_lower = question.lower()
        
        # Check for comparison questions
        if "difference" in question_lower or "compare" in question_lower or "vs" in question_lower:
            # Try to identify compounds being compared
            compounds = []
            for compound in ["soft", "medium", "hard", "intermediate", "wet"]:
                if compound in question_lower:
                    compounds.append(compound.upper())
            
            if len(compounds) >= 2:
                comparison = self.knowledge_base.compare_tyres(compounds[0], compounds[1])
                
                return {
                    "analysis_type": "Tyre Comparison",
                    "summary": (
                        f"Comparing {compounds[0]} and {compounds[1]} tyres: "
                        f"{comparison['comparison']['grip']}. "
                        f"{comparison['comparison']['durability']}."
                    ),
                    "explanation": self._format_tyre_comparison(comparison),
                    "data": comparison
                }
        
        # Check for specific compound info
        for compound in ["soft", "medium", "hard", "intermediate", "wet"]:
            if compound in question_lower:
                tyre_info = self.knowledge_base.get_tyre_info(compound.upper())
                
                if tyre_info:
                    return {
                        "analysis_type": f"{tyre_info['name']} Tyre Information",
                        "summary": (
                            f"{tyre_info['name']} tyres ({tyre_info['color']} marking) provide "
                            f"{tyre_info['grip_level'].lower()} grip with {tyre_info['durability'].lower()} durability. "
                            f"Typical life: {tyre_info['typical_life_laps']} laps."
                        ),
                        "explanation": self._format_tyre_info(tyre_info),
                        "data": tyre_info
                    }
        
        # General tyre strategy question
        if "strategy" in question_lower:
            return {
                "analysis_type": "Tyre Strategy Information",
                "summary": (
                    "Tyre strategy depends on track characteristics, degradation rates, "
                    "and race conditions. Teams must balance speed vs durability."
                ),
                "explanation": self._format_tyre_strategy_info(),
                "data": {
                    "compounds": self.knowledge_base.get_all_tyre_compounds(),
                    "concepts": ["undercut", "overcut", "pit_stop"]
                }
            }
        
        # Default tyre overview
        return {
            "analysis_type": "Tyre Information",
            "summary": (
                "F1 uses five tyre compounds: Soft (red), Medium (yellow), Hard (white), "
                "Intermediate (green), and Wet (blue). Each has different grip and durability characteristics."
            ),
            "explanation": self._format_all_tyres_info(),
            "data": {
                "compounds": self.knowledge_base.get_all_tyre_compounds()
            }
        }
    
    def _handle_car_question(self, question: str) -> Dict[str, Any]:
        """
        Handle car performance questions using Fast-F1 data.
        
        Args:
            question: User's question about car performance
            
        Returns:
            Dictionary with car performance information
        """
        question_lower = question.lower()
        
        # Check if Fast-F1 is available
        if not self.fastf1_enabled or self.fastf1_client is None:
            return {
                "analysis_type": "Car Performance Query",
                "summary": (
                    "Car performance data requires the Fast-F1 library integration. "
                    "This feature is currently not available."
                ),
                "explanation": (
                    "To access real-time car performance data (speed, lap times, telemetry), "
                    "the Fast-F1 library must be installed and enabled. "
                    "Install with: pip install fastf1>=3.0.0\n\n"
                    "I can still answer questions about aerodynamics, tyres, and general F1 topics."
                ),
                "data": {}
            }
        
        # Parse question for year, event, and driver information
        parsed_info = self._parse_car_question(question)
        
        # If we have specific event/driver info, try to fetch Fast-F1 data
        if parsed_info.get('year') and parsed_info.get('event'):
            try:
                return self._fetch_fastf1_data(parsed_info, question_lower)
            except Exception as e:
                # Fall through to general info if data fetch fails
                print(f"Fast-F1 data fetch failed: {e}")
        
        # Provide general information about car performance
        return {
            "analysis_type": "Car Performance Information",
            "summary": (
                "F1 car performance is measured through lap times, sector times, top speeds, "
                "and telemetry data including throttle, brake, and steering inputs."
            ),
            "explanation": (
                "Modern F1 cars can reach speeds over 350 km/h on long straights like Monza. "
                "Lap times vary significantly by track - from around 1:10 at Monaco to 1:20 at Spa. "
                "Performance is influenced by aerodynamics, power unit, tyres, and driver skill.\n\n"
                "Key performance metrics:\n"
                "• Top speed: 350+ km/h (with DRS)\n"
                "• 0-100 km/h: ~2.6 seconds\n"
                "• 0-200 km/h: ~5 seconds\n"
                "• Braking: 200-0 km/h in ~65 meters\n"
                "• Lateral G-force: Up to 6G in high-speed corners\n\n"
                "💡 Tip: For specific data, ask about a particular year, event, and driver.\n"
                "   Example: 'What was Verstappen's fastest lap in Monaco 2024?'"
            ),
            "data": {
                "general_performance": {
                    "top_speed_kmh": "350+",
                    "acceleration_0_100_s": 2.6,
                    "max_lateral_g": 6.0
                },
                "fastf1_enabled": True,
                "tip": "Specify year, event, and driver for real data"
            }
        }
    
    def _parse_car_question(self, question: str) -> Dict[str, Any]:
        """
        Parse a car performance question to extract year, event, and driver.
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with parsed information
        """
        question_lower = question.lower()
        parsed = {}
        
        # Extract year (2020-2026)
        year_match = re.search(r'\b(202[0-6])\b', question)
        if year_match:
            parsed['year'] = int(year_match.group(1))
        
        # Common event names
        events = [
            'bahrain', 'saudi', 'australia', 'japan', 'china', 'miami',
            'monaco', 'spain', 'canada', 'austria', 'britain', 'silverstone',
            'hungary', 'belgium', 'spa', 'netherlands', 'italy', 'monza',
            'singapore', 'usa', 'mexico', 'brazil', 'vegas', 'abu dhabi'
        ]
        for event in events:
            if event in question_lower:
                parsed['event'] = event.title()
                break
        
        # Common driver abbreviations and names
        drivers = {
            'verstappen': 'VER', 'ver': 'VER', 'max': 'VER',
            'hamilton': 'HAM', 'ham': 'HAM', 'lewis': 'HAM',
            'leclerc': 'LEC', 'lec': 'LEC', 'charles': 'LEC',
            'sainz': 'SAI', 'sai': 'SAI', 'carlos': 'SAI',
            'perez': 'PER', 'per': 'PER', 'sergio': 'PER',
            'russell': 'RUS', 'rus': 'RUS', 'george': 'RUS',
            'norris': 'NOR', 'nor': 'NOR', 'lando': 'NOR',
            'alonso': 'ALO', 'alo': 'ALO', 'fernando': 'ALO',
            'piastri': 'PIA', 'pia': 'PIA', 'oscar': 'PIA'
        }
        for name, abbr in drivers.items():
            if name in question_lower:
                parsed['driver'] = abbr
                break
        
        # Determine query type
        if 'lap time' in question_lower or 'fastest lap' in question_lower:
            parsed['query_type'] = 'lap_times'
        elif 'speed' in question_lower or 'top speed' in question_lower:
            parsed['query_type'] = 'speed'
        elif 'telemetry' in question_lower:
            parsed['query_type'] = 'telemetry'
        else:
            parsed['query_type'] = 'general'
        
        return parsed
    
    def _fetch_fastf1_data(self, parsed_info: Dict[str, Any], question_lower: str) -> Dict[str, Any]:
        """
        Fetch data from Fast-F1 based on parsed question information.
        
        Args:
            parsed_info: Parsed question information
            question_lower: Lowercase question string
            
        Returns:
            Dictionary with Fast-F1 data results
        """
        year = parsed_info.get('year')
        event = parsed_info.get('event')
        driver = parsed_info.get('driver')
        query_type = parsed_info.get('query_type', 'general')
        
        # Determine session type (default to Race)
        session_type = 'Race'
        if 'qualifying' in question_lower or 'quali' in question_lower:
            session_type = 'Qualifying'
        elif 'practice' in question_lower or 'fp' in question_lower:
            session_type = 'FP1'
        
        try:
            if query_type == 'lap_times':
                # Get lap times
                lap_data = self.fastf1_client.get_lap_times(year, event, session_type, driver)
                
                if lap_data.empty:
                    raise ValueError(f"No lap data found for {driver} at {event} {year}")
                
                fastest_lap = lap_data.loc[lap_data['LapTime'].idxmin()]
                avg_lap = lap_data['LapTime'].mean()
                
                return {
                    "analysis_type": f"Lap Time Analysis - {event} {year}",
                    "summary": (
                        f"{driver}'s fastest lap at {event} {year} ({session_type}): "
                        f"{fastest_lap['LapTime']}. "
                        f"Average lap time: {avg_lap}."
                    ),
                    "explanation": (
                        f"Lap time data for {driver} at {event} {year}:\n"
                        f"• Fastest lap: {fastest_lap['LapTime']} (Lap {fastest_lap['LapNumber']})\n"
                        f"• Tyre compound: {fastest_lap['Compound']}\n"
                        f"• Total laps: {len(lap_data)}\n"
                        f"• Average lap time: {avg_lap}\n\n"
                        f"Sector times for fastest lap:\n"
                        f"• Sector 1: {fastest_lap['Sector1Time']}\n"
                        f"• Sector 2: {fastest_lap['Sector2Time']}\n"
                        f"• Sector 3: {fastest_lap['Sector3Time']}"
                    ),
                    "key_results": {
                        "driver": driver,
                        "event": event,
                        "year": year,
                        "session": session_type,
                        "fastest_lap": str(fastest_lap['LapTime']),
                        "fastest_lap_number": int(fastest_lap['LapNumber']),
                        "compound": fastest_lap['Compound'],
                        "total_laps": len(lap_data)
                    },
                    "data": {
                        "lap_times": lap_data.to_dict('records')
                    },
                    "equations": ["Lap Time = Sector1 + Sector2 + Sector3"],
                    "assumptions": ["Data from Fast-F1 official timing"]
                }
            
            elif query_type == 'speed':
                # Get speed data
                speed_data = self.fastf1_client.get_speed_data(year, event, session_type, driver)
                
                max_speed = speed_data['Speed'].max()
                avg_speed = speed_data['Speed'].mean()
                
                return {
                    "analysis_type": f"Speed Analysis - {event} {year}",
                    "summary": (
                        f"{driver}'s top speed at {event} {year}: {max_speed:.1f} km/h. "
                        f"Average speed: {avg_speed:.1f} km/h."
                    ),
                    "explanation": (
                        f"Speed telemetry for {driver} at {event} {year}:\n"
                        f"• Maximum speed: {max_speed:.1f} km/h\n"
                        f"• Average speed: {avg_speed:.1f} km/h\n"
                        f"• Data points: {len(speed_data)}\n\n"
                        f"This data represents the fastest lap telemetry."
                    ),
                    "key_results": {
                        "driver": driver,
                        "event": event,
                        "year": year,
                        "max_speed_kmh": float(max_speed),
                        "avg_speed_kmh": float(avg_speed),
                        "data_points": len(speed_data)
                    },
                    "data": {
                        "telemetry_summary": {
                            "max_speed": float(max_speed),
                            "avg_speed": float(avg_speed)
                        }
                    },
                    "equations": ["Speed from GPS telemetry"],
                    "assumptions": ["Data from Fast-F1 telemetry"]
                }
            
            else:
                # General session info
                session_info = self.fastf1_client.get_session_info(year, event, session_type)
                
                return {
                    "analysis_type": f"Session Information - {event} {year}",
                    "summary": (
                        f"{event} {year} {session_type}: {session_info['total_laps']} total laps. "
                        f"Drivers: {', '.join(session_info['drivers'][:5])}..."
                    ),
                    "explanation": (
                        f"Session details for {event} {year}:\n"
                        f"• Event: {session_info['event']}\n"
                        f"• Location: {session_info['location']}, {session_info['country']}\n"
                        f"• Session: {session_type}\n"
                        f"• Date: {session_info['date']}\n"
                        f"• Total laps: {session_info['total_laps']}\n"
                        f"• Drivers: {len(session_info['drivers'])}\n\n"
                        f"💡 Ask about specific drivers for detailed lap times or speed data."
                    ),
                    "key_results": session_info,
                    "data": session_info,
                    "equations": [],
                    "assumptions": ["Data from Fast-F1"]
                }
        
        except Exception as e:
            raise Exception(f"Failed to fetch Fast-F1 data: {str(e)}")
    
    def _handle_general_question(self, question: str) -> Dict[str, Any]:
        """
        Handle general F1 questions using the knowledge base.
        
        Args:
            question: User's general F1 question
            
        Returns:
            Dictionary with general F1 information
        """
        question_lower = question.lower()
        
        # Check for physics concepts (g-force, downforce, braking, etc.)
        for concept in self.knowledge_base.get_all_physics_concepts():
            if concept.replace('_', ' ') in question_lower or concept.replace('_', '-') in question_lower:
                concept_info = self.knowledge_base.get_physics_concept(concept)
                
                if concept_info:
                    return {
                        "analysis_type": f"{concept_info['name']} - Physics Concept",
                        "summary": concept_info.get('definition', concept_info.get('description', '')),
                        "explanation": self._format_physics_concept(concept, concept_info),
                        "data": concept_info
                    }
        
        # Check for 2026 regulations
        if "2026" in question_lower:
            if "power unit" in question_lower or "engine" in question_lower:
                regs = self.knowledge_base.get_2026_regulations("power_unit")
                if regs:
                    return {
                        "analysis_type": "2026 Power Unit Regulations",
                        "summary": regs.get('summary', 'Information about 2026 power unit regulations'),
                        "explanation": self._format_2026_regulations("power_unit", regs),
                        "data": regs
                    }
            elif "aero" in question_lower or "aerodynamic" in question_lower:
                regs = self.knowledge_base.get_2026_regulations("aerodynamics")
                if regs:
                    return {
                        "analysis_type": "2026 Aerodynamics Regulations",
                        "summary": regs.get('summary', 'Information about 2026 aerodynamics regulations'),
                        "explanation": self._format_2026_regulations("aerodynamics", regs),
                        "data": regs
                    }
            else:
                # General 2026 regulations
                all_regs = self.knowledge_base.get_2026_regulations()
                if all_regs and isinstance(all_regs, dict):
                    return {
                        "analysis_type": "2026 F1 Regulations",
                        "summary": "Major regulation changes coming in 2026 for power units, aerodynamics, and chassis.",
                        "explanation": self._format_all_2026_regulations(all_regs),
                        "data": all_regs
                    }
        
        # Check for team information
        for team in self.knowledge_base.get_all_teams():
            if team.lower() in question_lower:
                team_info = self.knowledge_base.get_team_info(team)
                
                if team_info:
                    return {
                        "analysis_type": f"{team} Team Information",
                        "summary": (
                            f"{team} is based in {team_info['base']}, uses {team_info['power_unit']} power units, "
                            f"and is led by Team Principal {team_info['team_principal']}."
                        ),
                        "explanation": self._format_team_info(team, team_info),
                        "data": team_info
                    }
        
        # Check for car components
        for component in self.knowledge_base.get_all_car_components():
            if component.replace('_', ' ') in question_lower:
                component_info = self.knowledge_base.get_car_component_info(component)
                
                if component_info:
                    return {
                        "analysis_type": f"{component_info['name']} - Car Component",
                        "summary": component_info['description'],
                        "explanation": self._format_car_component(component, component_info),
                        "data": component_info
                    }
        
        # Check for track information
        for track in self.knowledge_base.get_all_tracks():
            if track.lower() in question_lower:
                track_info = self.knowledge_base.get_track_info(track)
                
                return {
                    "analysis_type": f"{track} Circuit Information",
                    "summary": (
                        f"{track} is a {track_info['type'].lower()} with {track_info['surface'].lower()} surface. "
                        f"Typical strategy: {track_info['typical_strategy']}."
                    ),
                    "explanation": self._format_track_info(track, track_info),
                    "data": track_info
                }
        
        # Check for racing concepts
        for concept in self.knowledge_base.get_all_racing_concepts():
            if concept in question_lower:
                concept_info = self.knowledge_base.get_racing_concept(concept)
                
                return {
                    "analysis_type": f"{concept_info['name']} Information",
                    "summary": concept_info['description'],
                    "explanation": self._format_racing_concept(concept, concept_info),
                    "data": concept_info
                }
        
        # General F1 information
        return {
            "analysis_type": "General F1 Information",
            "summary": (
                "Formula 1 is the pinnacle of motorsport, featuring cutting-edge technology "
                "and the world's best drivers competing on circuits around the globe."
            ),
            "explanation": (
                "I can provide information about:\n"
                "• Physics: G-force, downforce, braking forces, aerodynamic balance\n"
                "• 2026 Regulations: Power units, aerodynamics, chassis changes\n"
                "• Teams: Ferrari, Mercedes, Red Bull, McLaren, and more\n"
                "• Car Components: Engine, gearbox, brakes, suspension\n"
                "• Tracks: Monaco, Silverstone, Spa, Monza, Singapore\n"
                "• Racing concepts: DRS, pit stops, undercut, overcut\n"
                "• Tyres: Compounds, degradation, strategy\n\n"
                "Please ask a more specific question about any of these topics."
            ),
            "data": {
                "available_tracks": self.knowledge_base.get_all_tracks(),
                "available_concepts": self.knowledge_base.get_all_racing_concepts(),
                "available_teams": self.knowledge_base.get_all_teams(),
                "available_components": self.knowledge_base.get_all_car_components()
            }
        }
    
    def _format_physics_concept(self, concept: str, concept_info: Dict[str, Any]) -> str:
        """Format physics concept information for display."""
        name = concept_info.get('name', concept.replace('_', ' ').title())
        definition = concept_info.get('definition', concept_info.get('description', ''))
        explanation = f"{name}: {definition}\n\n"
        
        # Handle F1 context
        if 'f1_context' in concept_info:
            explanation += "F1 Context:\n"
            for key, value in concept_info['f1_context'].items():
                explanation += f"• {key.replace('_', ' ').title()}: {value}\n"
            explanation += "\n"
        
        # Handle driver impact
        if 'driver_impact' in concept_info:
            explanation += "Driver Impact:\n"
            for impact in concept_info['driver_impact']:
                explanation += f"• {impact}\n"
            explanation += "\n"
        
        # Handle sources
        if 'sources' in concept_info:
            explanation += "Sources:\n"
            for source in concept_info['sources']:
                explanation += f"• {source}\n"
            explanation += "\n"
        
        # Handle typical values
        if 'typical_values' in concept_info:
            explanation += f"Typical Values: {concept_info['typical_values']}\n\n"
        
        # Handle examples
        if 'examples' in concept_info:
            explanation += "Examples:\n"
            for example in concept_info['examples']:
                explanation += f"• {example}\n"
        
        return explanation
    
    def _format_2026_regulations(self, category: str, regs: Dict[str, Any]) -> str:
        """Format 2026 regulations information for display."""
        explanation = f"{regs.get('summary', '')}\n\n"
        
        if 'key_changes' in regs:
            explanation += "Key Changes:\n"
            for change in regs['key_changes']:
                explanation += f"• {change}\n"
        
        if 'specifications' in regs:
            explanation += "\nSpecifications:\n"
            for key, value in regs['specifications'].items():
                explanation += f"• {key.replace('_', ' ').title()}: {value}\n"
        
        if 'impact' in regs:
            explanation += f"\nImpact: {regs['impact']}\n"
        
        return explanation
    
    def _format_all_2026_regulations(self, all_regs: Dict[str, Any]) -> str:
        """Format all 2026 regulations for display."""
        explanation = "2026 F1 Regulations Overview:\n\n"
        
        for category, regs in all_regs.items():
            explanation += f"{category.replace('_', ' ').title()}:\n"
            explanation += f"{regs.get('summary', '')}\n\n"
        
        return explanation
    
    def _format_team_info(self, team: str, team_info: Dict[str, Any]) -> str:
        """Format team information for display."""
        explanation = f"{team} Team Information:\n\n"
        explanation += f"Base: {team_info['base']}\n"
        explanation += f"Team Principal: {team_info['team_principal']}\n"
        explanation += f"Power Unit: {team_info['power_unit']}\n"
        explanation += f"Championships: {team_info['championships']}\n"
        
        if 'notable_drivers' in team_info:
            explanation += f"\nNotable Drivers:\n"
            for driver in team_info['notable_drivers']:
                explanation += f"• {driver}\n"
        
        if 'history' in team_info:
            explanation += f"\nHistory: {team_info['history']}\n"
        
        return explanation
    
    def _format_car_component(self, component: str, component_info: Dict[str, Any]) -> str:
        """Format car component information for display."""
        name = component_info.get('name', component.replace('_', ' ').title())
        description = component_info.get('description', '')
        explanation = f"{name}: {description}\n\n"
        
        if 'specifications' in component_info:
            explanation += "Specifications:\n"
            specs = component_info['specifications']
            if isinstance(specs, dict):
                for key, value in specs.items():
                    explanation += f"• {key.replace('_', ' ').title()}: {value}\n"
            explanation += "\n"
        
        if 'key_features' in component_info:
            explanation += "Key Features:\n"
            for feature in component_info['key_features']:
                explanation += f"• {feature}\n"
            explanation += "\n"
        
        if 'regulations' in component_info:
            explanation += f"Regulations: {component_info['regulations']}\n"
        
        return explanation
    
    def _generate_fallback_response(
        self,
        question: str,
        routing: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a fallback response for unsupported questions.
        
        Args:
            question: User's question
            routing: Routing information from the router
            
        Returns:
            Dictionary with fallback message
        """
        classification = routing.get("classification", {})
        reason = routing.get("fallback_reason", "Question type not supported")
        
        return {
            "success": False,
            "error": "Unable to answer this question",
            "message": f"I'm unable to answer this question. {reason}",
            "question": question,
            "classification": classification,
            "fallback_reason": reason
        }
    def _is_visualization_request(self, question: str) -> bool:
        """Return True when the user is asking for a visualization."""
        question_lower = question.lower()
        visualization_keywords = [
            "visualize", "visualization", "graph", "chart", "plot",
            "show me", "show", "create", "display"
        ]
        return any(keyword in question_lower for keyword in visualization_keywords)

    def _extract_topic_from_text(self, text: str) -> Optional[str]:
        """Extract the most relevant aero/tyre topic from free text."""
        text_lower = text.lower()
        topic_patterns = [
            ("drs_comparison", ["drs", "drag reduction system"]),
            ("drag_force", ["drag"]),
            ("front_wing_downforce", ["front wing", "downforce"]),
            ("ground_effect", ["ground effect", "diffuser", "venturi", "floor"]),
            ("tyres", ["tyre", "tyres", "tire", "tires", "soft", "medium", "hard", "intermediate", "wet"])
        ]

        for topic, keywords in topic_patterns:
            if any(keyword in text_lower for keyword in keywords):
                return topic

        return None

    def _extract_speed_from_text(self, text: str) -> Optional[float]:
        """Extract a speed in km/h from text if present."""
        speed_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:km/?h|kph)', text.lower())
        if speed_match:
            return float(speed_match.group(1))
        return None

    def _get_recent_context_candidates(self, limit: int = 3) -> List[Dict[str, Any]]:
        """Return the most recent conversation entries to inspect for context."""
        if not self.conversation_history:
            return []
        return list(reversed(self.conversation_history[-limit:]))

    def _build_visualization_followup_question(self, question: str) -> Optional[str]:
        """
        Convert vague visualization follow-ups into explicit questions using memory.
        
        Examples:
        - "Can you create a visualization for this?" -> explicit drag/downforce graph request
        - "Show me a graph of that" -> explicit graph request for prior topic
        """
        if not self.conversation_history:
            return None

        question_lower = question.lower()
        context_references = ["this", "that", "it"]
        if not self._is_visualization_request(question):
            return None
        if not any(ref in question_lower for ref in context_references):
            return None

        for qa in self._get_recent_context_candidates(limit=3):
            last_question = qa.get("question", "")
            last_result = qa.get("result", {})
            combined_text = " ".join([
                last_question,
                last_result.get("analysis_type", ""),
                last_result.get("summary", ""),
                last_result.get("explanation", "")
            ])

            topic = (
                last_result.get("question_type")
                or self._extract_topic_from_text(combined_text)
            )

            if topic == "unsupported":
                topic = self._extract_topic_from_text(combined_text)

            if topic == "drag_force":
                speed = (
                    last_result.get("key_results", {}).get("speed_kmh")
                    or self._extract_speed_from_text(last_question)
                    or self._extract_speed_from_text(last_result.get("summary", ""))
                    or 300.0
                )
                drs_status = last_result.get("key_results", {}).get("drs_status", "closed")
                drs_phrase = " with DRS open" if drs_status == "open" else ""
                return f"Create a graph of drag force at {speed:.0f} km/h{drs_phrase}"

            if topic == "front_wing_downforce":
                return "Create a visualization of front wing downforce versus speed"

            if topic == "drs_comparison":
                return "Create a graph comparing DRS open vs closed drag"

            if topic == "ground_effect":
                speed = (
                    last_result.get("key_results", {}).get("freestream_velocity_kmh")
                    or self._extract_speed_from_text(last_question)
                    or 300.0
                )
                return f"Create a visualization of ground effect at {speed:.0f} km/h"

            if topic == "tyres":
                compounds = []
                for compound in ["soft", "medium", "hard", "intermediate", "wet"]:
                    if compound in combined_text.lower():
                        compounds.append(compound)

                if len(compounds) >= 2:
                    return f"Compare {compounds[0]} and {compounds[1]} tyres"
                if compounds:
                    return f"Explain the {compounds[0]} tyre"
                return "Compare soft and hard tyres"

        return None

    def _resolve_context_references(self, question: str) -> str:
        """
        Resolve context references in questions using conversation history.
        
        Handles follow-up questions like:
        - "What about at 250 km/h?" (referring to previous speed question)
        - "Compare that to the rear wing" (referring to previous wing discussion)
        - "What about the soft compound?" (referring to previous tyre discussion)
        - "Can you create a visualization for this?" (referring to previous analysis)
        
        Args:
            question: User's question
            
        Returns:
            Question with context resolved, or original if no context needed
        """
        if not self.conversation_history:
            return question

        visualization_followup = self._build_visualization_followup_question(question)
        if visualization_followup:
            return visualization_followup
        
        question_lower = question.lower()
        
        # Check for context reference keywords
        context_keywords = ['that', 'it', 'this', 'what about', 'how about', 'compare']
        has_context_reference = any(keyword in question_lower for keyword in context_keywords)
        
        if not has_context_reference:
            return question
        
        # Get the last Q&A pair
        last_qa = self.conversation_history[-1]
        last_question = last_qa.get("question", "")
        
        # Extract key context from last question/answer
        context_info = []
        
        # Check for speed references
        speed_match = re.search(r'(\d+)\s*km/?h', last_question.lower())
        if speed_match:
            context_info.append(f"previous speed: {speed_match.group(1)} km/h")
        
        # Check for component references (wing, tyre, etc.)
        components = ['front wing', 'rear wing', 'floor', 'diffuser', 'soft', 'medium', 'hard', 'intermediate', 'wet']
        for component in components:
            if component in last_question.lower():
                context_info.append(f"previous topic: {component}")
                break
        
        # If question is very short and vague, append context
        if len(question.split()) <= 5 and context_info:
            # For questions like "What about at 250 km/h?"
            if 'what about' in question_lower or 'how about' in question_lower:
                return f"{question} (context: {', '.join(context_info)})"
        
        return question
    
    def _add_to_history(self, question: str, result: Dict[str, Any]) -> None:
        """
        Add a Q&A pair to conversation history.
        
        Maintains a rolling window of the last max_history_size Q&A pairs.
        
        Args:
            question: User's question
            result: Processing result dictionary
        """
        self.conversation_history.append({
            "question": question,
            "result": result,
            "timestamp": None  # Could add timestamp if needed
        })
        
        # Keep only last max_history_size entries
        if len(self.conversation_history) > self.max_history_size:
            self.conversation_history = self.conversation_history[-self.max_history_size:]
    
    def get_conversation_history(self) -> list:
        """
        Retrieve the conversation history.
        
        Returns:
            List of Q&A pairs in chronological order
        """
        return self.conversation_history.copy()
    
    def clear_conversation_history(self) -> None:
        """
        Clear the conversation history.
        
        Useful for starting a fresh conversation session.
        """
        self.conversation_history = []
    
    
    def _format_tyre_info(self, tyre_info: Dict[str, Any]) -> str:
        """Format tyre information for display."""
        lines = [
            f"{tyre_info['name']} Compound Characteristics:",
            f"• Color marking: {tyre_info['color']}",
            f"• Grip level: {tyre_info['grip_level']}",
            f"• Durability: {tyre_info['durability']}",
            f"• Optimal temperature: {tyre_info['optimal_temp_range']}",
            f"• Typical life: {tyre_info['typical_life_laps']} laps",
            f"• Degradation rate: {tyre_info['degradation_rate']}",
            "",
            "Key characteristics:"
        ]
        for char in tyre_info['characteristics']:
            lines.append(f"  - {char}")
        
        return "\n".join(lines)
    
    def _format_tyre_comparison(self, comparison: Dict[str, Any]) -> str:
        """Format tyre comparison for display."""
        c1 = comparison['compound1']
        c2 = comparison['compound2']
        
        lines = [
            f"Comparing {c1['name']} vs {c2['name']} tyres:",
            "",
            f"{c1['name']} ({c1['data']['color']}):",
            f"  • Grip: {c1['data']['grip_level']}",
            f"  • Durability: {c1['data']['durability']}",
            f"  • Life: {c1['data']['typical_life_laps']} laps",
            "",
            f"{c2['name']} ({c2['data']['color']}):",
            f"  • Grip: {c2['data']['grip_level']}",
            f"  • Durability: {c2['data']['durability']}",
            f"  • Life: {c2['data']['typical_life_laps']} laps",
            "",
            "Summary:",
            f"  • {comparison['comparison']['grip']}",
            f"  • {comparison['comparison']['durability']}",
            f"  • {comparison['comparison']['degradation']}"
        ]
        
        return "\n".join(lines)
    
    def _format_tyre_strategy_info(self) -> str:
        """Format tyre strategy information."""
        undercut = self.knowledge_base.get_racing_concept("undercut")
        overcut = self.knowledge_base.get_racing_concept("overcut")
        
        return (
            "Tyre Strategy Concepts:\n\n"
            f"Undercut: {undercut['description']}\n"
            f"  • Advantage: {undercut['advantage']}\n"
            f"  • Risk: {undercut['risk']}\n\n"
            f"Overcut: {overcut['description']}\n"
            f"  • Advantage: {overcut['advantage']}\n"
            f"  • Risk: {overcut['risk']}\n\n"
            "Strategy depends on track characteristics, tyre degradation, "
            "and race position. Teams use real-time data to optimize pit stop timing."
        )
    
    def _format_all_tyres_info(self) -> str:
        """Format information about all tyre compounds."""
        lines = ["F1 Tyre Compounds:\n"]
        
        for compound in ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]:
            info = self.knowledge_base.get_tyre_info(compound)
            if info:
                lines.append(
                    f"{info['name']} ({info['color']}): "
                    f"{info['grip_level']} grip, {info['durability']} durability"
                )
        
        return "\n".join(lines)
    
    def _format_track_info(self, track_name: str, track_info: Dict[str, Any]) -> str:
        """Format track information for display."""
        lines = [
            f"{track_name} Circuit:",
            f"• Type: {track_info['type']}",
            f"• Surface: {track_info['surface']}",
            f"• Tyre stress: {track_info['tyre_stress']}",
            f"• Typical strategy: {track_info['typical_strategy']}",
            f"• Preferred compounds: {', '.join(track_info['preferred_compounds'])}",
            "",
            "Characteristics:"
        ]
        for char in track_info['characteristics']:
            lines.append(f"  - {char}")
        
        return "\n".join(lines)
    
    def _format_racing_concept(self, concept: str, concept_info: Dict[str, Any]) -> str:
        """Format racing concept information for display."""
        lines = [f"{concept_info.get('name', concept.upper())}:"]
        
        for key, value in concept_info.items():
            if key != 'name' and key != 'description':
                formatted_key = key.replace('_', ' ').title()
                lines.append(f"  • {formatted_key}: {value}")
        
        return "\n".join(lines)
    
    def format_response(self, result: Dict[str, Any]) -> str:
        """
        Format analysis result as human-readable text.
        
        Args:
            result: Analysis result dictionary
            
        Returns:
            Formatted text response
        """
        # ANSI color codes
        BLACK = '\033[30m'
        RESET = '\033[0m'
        
        if not result.get("success", False):
            return f"{BLACK}Error: {result.get('error', 'Unknown error')}\n{result.get('message', '')}{RESET}"
        
        lines = []
        lines.append(f"{BLACK}{'=' * 80}")
        lines.append(f"F1 AERODYNAMICS ANALYSIS: {result['analysis_type']}")
        lines.append("=" * 80)
        lines.append("")
        
        lines.append("SUMMARY:")
        lines.append(result['summary'])
        lines.append("")
        
        if 'explanation' in result:
            lines.append("DESCRIPTION:")
            lines.append(result['explanation'])
            lines.append("")
        
        if 'math_explanation' in result:
            lines.append("MATHEMATICAL EXPLANATION:")
            lines.append(result['math_explanation'])
            lines.append("")
        
        if 'key_results' in result and result['key_results']:
            lines.append("KEY RESULTS:")
            for key, value in result['key_results'].items():
                formatted_key = key.replace('_', ' ').title()
                if isinstance(value, float):
                    lines.append(f"  • {formatted_key}: {value:.2f}")
                else:
                    lines.append(f"  • {formatted_key}: {value}")
            lines.append("")
        
        if 'equations' in result and result['equations']:
            lines.append("EQUATIONS USED:")
            for eq in result['equations']:
                lines.append(f"  • {eq}")
            lines.append("")
        
        if 'assumptions' in result and result['assumptions']:
            lines.append("ASSUMPTIONS:")
            for assumption in result['assumptions']:
                lines.append(f"  • {assumption}")
            lines.append("")
        
        if result.get('visualization_message'):
            lines.append("VISUALIZATION:")
            lines.append(result['visualization_message'])
            lines.append("")
        elif result.get('graph_path'):
            lines.append("VISUALIZATION:")
            lines.append(
                f"Visualization created and saved to {result['graph_path']}"
            )
            lines.append("")
        elif result.get('visualization'):
            lines.append("VISUALIZATION:")
            lines.append(
                f"Visualization created and saved to {result['visualization']}"
            )
            lines.append("")
        
        lines.append("=" * 80 + RESET)
        
        return "\n".join(lines)

# Made with Bob
