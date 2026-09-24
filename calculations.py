"""
F1-specific aerodynamic calculations using the physics MCP client.
"""

import numpy as np
from typing import Dict, Any, List, Tuple
from .mcp_client import get_physics_client


# F1 typical parameters
F1_FRONTAL_AREA = 1.5  # m² (approximate)
F1_FRONT_WING_AREA = 1.0  # m² (approximate)
F1_REAR_WING_AREA = 0.8  # m² (approximate)
F1_FRONT_WING_CL = -3.5  # Typical front wing lift coefficient (negative = downforce)
F1_REAR_WING_CL = -3.0  # Typical rear wing lift coefficient
F1_CD_DRS_CLOSED = 0.9  # Drag coefficient with DRS closed
F1_CD_DRS_OPEN = 0.7  # Drag coefficient with DRS open
AIR_DENSITY = 1.225  # kg/m³ at sea level, 15°C


def calculate_front_wing_downforce_vs_speed(
    speed_range: Tuple[float, float] = (50, 350),
    num_points: int = 50
) -> Dict[str, Any]:
    """
    Calculate front wing downforce across a speed range.
    
    Args:
        speed_range: (min_speed, max_speed) in km/h
        num_points: Number of calculation points
        
    Returns:
        Dictionary with speeds, downforce values, and metadata
    """
    client = get_physics_client()
    
    # Convert km/h to m/s
    speeds_kmh = np.linspace(speed_range[0], speed_range[1], num_points)
    speeds_ms = speeds_kmh / 3.6
    
    downforce_values = []
    
    for v in speeds_ms:
        # Calculate dynamic pressure
        q_result = client.calculate_dynamic_pressure(v, AIR_DENSITY)
        q = q_result["dynamic_pressure"]
        
        # Calculate downforce (negative lift)
        lift_result = client.calculate_lift_force(q, F1_FRONT_WING_AREA, F1_FRONT_WING_CL)
        downforce = lift_result["downforce"]
        downforce_values.append(downforce)
    
    return {
        "speeds_kmh": speeds_kmh.tolist(),
        "speeds_ms": speeds_ms.tolist(),
        "downforce_n": downforce_values,
        "wing_area": F1_FRONT_WING_AREA,
        "cl": F1_FRONT_WING_CL,
        "air_density": AIR_DENSITY,
        "assumptions": [
            f"Front wing area: {F1_FRONT_WING_AREA} m²",
            f"Lift coefficient (C_l): {F1_FRONT_WING_CL}",
            f"Air density: {AIR_DENSITY} kg/m³ (sea level, 15°C)",
            "Constant C_l (reality: varies with ride height, angle of attack)"
        ],
        "equations": [
            "q = 0.5 * ρ * v²",
            "F_downforce = q * A * |C_l|"
        ]
    }


def calculate_drag_at_speed(
    speed_kmh: float,
    drs_open: bool = False,
    speed_range: Tuple[float, float] = (100, 350),
    num_points: int = 60
) -> Dict[str, Any]:
    """
    Calculate total drag force at a specific speed and provide a drag-speed curve.
    
    Args:
        speed_kmh: Speed in km/h
        drs_open: Whether DRS is open
        speed_range: Speed range for explanatory curve in km/h
        num_points: Number of curve points
        
    Returns:
        Dictionary with drag force, queried point, and curve data
    """
    client = get_physics_client()
    
    # Convert to m/s
    speed_ms = speed_kmh / 3.6
    
    # Select drag coefficient
    cd = F1_CD_DRS_OPEN if drs_open else F1_CD_DRS_CLOSED
    
    # Calculate dynamic pressure
    q_result = client.calculate_dynamic_pressure(speed_ms, AIR_DENSITY)
    q = q_result["dynamic_pressure"]
    
    # Calculate drag force
    drag_result = client.calculate_drag_force(q, F1_FRONTAL_AREA, cd)
    
    # Build explanatory drag curve across speed range
    curve_speeds_kmh = np.linspace(speed_range[0], speed_range[1], num_points)
    curve_speeds_ms = curve_speeds_kmh / 3.6
    curve_dynamic_pressure = []
    curve_drag_force = []
    
    for v in curve_speeds_ms:
        curve_q_result = client.calculate_dynamic_pressure(v, AIR_DENSITY)
        curve_q = curve_q_result["dynamic_pressure"]
        curve_drag_result = client.calculate_drag_force(curve_q, F1_FRONTAL_AREA, cd)
        curve_dynamic_pressure.append(curve_q)
        curve_drag_force.append(curve_drag_result["drag_force"])
    
    return {
        "speed_kmh": speed_kmh,
        "speed_ms": speed_ms,
        "drag_force_n": drag_result["drag_force"],
        "dynamic_pressure_pa": q,
        "frontal_area": F1_FRONTAL_AREA,
        "cd": cd,
        "drs_open": drs_open,
        "air_density": AIR_DENSITY,
        "curve_speeds_kmh": curve_speeds_kmh.tolist(),
        "curve_speeds_ms": curve_speeds_ms.tolist(),
        "curve_dynamic_pressure_pa": curve_dynamic_pressure,
        "curve_drag_force_n": curve_drag_force,
        "assumptions": [
            f"Frontal area: {F1_FRONTAL_AREA} m²",
            f"C_d (DRS {'open' if drs_open else 'closed'}): {cd}",
            f"Air density: {AIR_DENSITY} kg/m³",
            "Constant C_d (reality: varies with Reynolds number, yaw angle)"
        ],
        "equations": [
            "q = 0.5 * ρ * v²",
            "F_drag = q * A * C_d"
        ]
    }


def compare_drs_drag(
    speed_range: Tuple[float, float] = (200, 350),
    num_points: int = 30
) -> Dict[str, Any]:
    """
    Compare drag force with DRS open vs closed across speed range.
    
    Args:
        speed_range: (min_speed, max_speed) in km/h
        num_points: Number of calculation points
        
    Returns:
        Dictionary with comparison data
    """
    client = get_physics_client()
    
    speeds_kmh = np.linspace(speed_range[0], speed_range[1], num_points)
    speeds_ms = speeds_kmh / 3.6
    
    drag_closed = []
    drag_open = []
    drag_reduction = []
    
    for v in speeds_ms:
        q_result = client.calculate_dynamic_pressure(v, AIR_DENSITY)
        q = q_result["dynamic_pressure"]
        
        # DRS closed
        closed_result = client.calculate_drag_force(q, F1_FRONTAL_AREA, F1_CD_DRS_CLOSED)
        drag_closed.append(closed_result["drag_force"])
        
        # DRS open
        open_result = client.calculate_drag_force(q, F1_FRONTAL_AREA, F1_CD_DRS_OPEN)
        drag_open.append(open_result["drag_force"])
        
        # Reduction percentage
        reduction = ((closed_result["drag_force"] - open_result["drag_force"]) / 
                    closed_result["drag_force"] * 100)
        drag_reduction.append(reduction)
    
    return {
        "speeds_kmh": speeds_kmh.tolist(),
        "speeds_ms": speeds_ms.tolist(),
        "drag_closed_n": drag_closed,
        "drag_open_n": drag_open,
        "drag_reduction_percent": drag_reduction,
        "cd_closed": F1_CD_DRS_CLOSED,
        "cd_open": F1_CD_DRS_OPEN,
        "frontal_area": F1_FRONTAL_AREA,
        "air_density": AIR_DENSITY,
        "assumptions": [
            f"Frontal area: {F1_FRONTAL_AREA} m²",
            f"C_d (DRS closed): {F1_CD_DRS_CLOSED}",
            f"C_d (DRS open): {F1_CD_DRS_OPEN}",
            f"Air density: {AIR_DENSITY} kg/m³",
            "DRS primarily affects rear wing drag"
        ],
        "equations": [
            "q = 0.5 * ρ * v²",
            "F_drag = q * A * C_d",
            "Reduction% = (F_closed - F_open) / F_closed * 100"
        ]
    }


def analyze_ground_effect(
    freestream_velocity: float = 300,
    diffuser_velocity_ratio: float = 1.4,
    speed_range: Tuple[float, float] = (150, 350),
    num_points: int = 50
) -> Dict[str, Any]:
    """
    Analyze ground effect and diffuser pressure dynamics.
    
    Uses simplified Bernoulli equation to show pressure reduction
    in the diffuser/venturi region under the car.
    
    Args:
        freestream_velocity: Freestream velocity in km/h
        diffuser_velocity_ratio: Ratio of diffuser velocity to freestream
        speed_range: Speed range for explanatory curves in km/h
        num_points: Number of curve points
        
    Returns:
        Dictionary with pressure analysis and explanatory curve data
    """
    client = get_physics_client()
    
    # Convert to m/s
    v_freestream = freestream_velocity / 3.6
    v_diffuser = v_freestream * diffuser_velocity_ratio
    
    # Calculate pressure change using Bernoulli
    pressure_result = client.calculate_pressure_change(
        v_diffuser, v_freestream, AIR_DENSITY
    )
    
    # Negative pressure change = suction (downforce)
    pressure_drop = -pressure_result["pressure_change"]
    
    # Estimate downforce (simplified)
    floor_area = 2.5  # m² approximate effective floor area
    downforce_estimate = pressure_drop * floor_area
    
    # Build explanatory curves across speed range
    curve_speeds_kmh = np.linspace(speed_range[0], speed_range[1], num_points)
    curve_freestream_ms = curve_speeds_kmh / 3.6
    curve_diffuser_ms = curve_freestream_ms * diffuser_velocity_ratio
    curve_pressure_drop = []
    curve_downforce = []
    
    for v_free, v_diff in zip(curve_freestream_ms, curve_diffuser_ms):
        curve_pressure_result = client.calculate_pressure_change(v_diff, v_free, AIR_DENSITY)
        curve_drop = -curve_pressure_result["pressure_change"]
        curve_pressure_drop.append(curve_drop)
        curve_downforce.append(curve_drop * floor_area)
    
    return {
        "freestream_velocity_kmh": freestream_velocity,
        "freestream_velocity_ms": v_freestream,
        "diffuser_velocity_ms": v_diffuser,
        "velocity_ratio": diffuser_velocity_ratio,
        "pressure_drop_pa": pressure_drop,
        "estimated_downforce_n": downforce_estimate,
        "floor_area": floor_area,
        "air_density": AIR_DENSITY,
        "curve_speeds_kmh": curve_speeds_kmh.tolist(),
        "curve_freestream_velocity_ms": curve_freestream_ms.tolist(),
        "curve_diffuser_velocity_ms": curve_diffuser_ms.tolist(),
        "curve_pressure_drop_pa": curve_pressure_drop,
        "curve_estimated_downforce_n": curve_downforce,
        "assumptions": [
            f"Freestream velocity: {freestream_velocity} km/h",
            f"Diffuser velocity ratio: {diffuser_velocity_ratio}x",
            f"Effective floor area: {floor_area} m²",
            f"Air density: {AIR_DENSITY} kg/m³",
            "Simplified Bernoulli (incompressible, inviscid)",
            "Venturi effect accelerates air under car",
            "Actual ground effect includes complex 3D flow, vortices"
        ],
        "equations": [
            "ΔP = 0.5 * ρ * (v_diffuser² - v_freestream²)",
            "F_downforce ≈ ΔP * A_floor",
            "Venturi: A₁v₁ = A₂v₂ (continuity)"
        ],
        "explanation": (
            "Ground effect creates downforce by accelerating air through the "
            "venturi-shaped floor/diffuser. Higher velocity under the car "
            "creates lower pressure (Bernoulli), generating suction force. "
            "The diffuser expands the flow, recovering pressure while maintaining "
            "the low-pressure region."
        )
    }

# Made with Bob
