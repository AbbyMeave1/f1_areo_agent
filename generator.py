"""
Visualization generator for F1 aerodynamics analysis.
Saves plots to local files using matplotlib.
"""

import os
from typing import Dict, Any, Optional
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


# Output directory for visualizations
OUTPUT_DIR = "f1_aero_visualizations"


def ensure_output_dir():
    """Create output directory if it doesn't exist."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def generate_timestamp() -> str:
    """Generate timestamp for unique filenames."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def plot_front_wing_downforce(data: Dict[str, Any]) -> str:
    """
    Generate plot for front wing downforce vs speed.
    
    Args:
        data: Calculation results from calculate_front_wing_downforce_vs_speed
        
    Returns:
        Path to saved plot file
    """
    ensure_output_dir()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    speeds = data["speeds_kmh"]
    downforce = data["downforce_n"]
    
    ax.plot(speeds, downforce, 'b-', linewidth=2, label='Front Wing Downforce')
    ax.fill_between(speeds, 0, downforce, alpha=0.3)
    
    ax.set_xlabel('Speed (km/h)', fontsize=12)
    ax.set_ylabel('Downforce (N)', fontsize=12)
    ax.set_title('F1 Front Wing Downforce vs Speed', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Add annotations
    textstr = '\n'.join([
        f'Wing Area: {data["wing_area"]:.2f} m²',
        f'C_l: {data["cl"]:.2f}',
        f'Air Density: {data["air_density"]:.3f} kg/m³'
    ])
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
            fontsize=9)
    
    plt.tight_layout()
    
    filename = f"front_wing_downforce_{generate_timestamp()}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(filepath, dpi=150)
    plt.close()
    
    return filepath


def plot_drag_force(data: Dict[str, Any]) -> str:
    """
    Generate explanatory drag-force plots with the queried point highlighted.
    
    Args:
        data: Calculation results from calculate_drag_at_speed
        
    Returns:
        Path to saved plot file
    """
    ensure_output_dir()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    curve_speeds = data["curve_speeds_kmh"]
    curve_drag = data["curve_drag_force_n"]
    curve_q = data["curve_dynamic_pressure_pa"]
    query_speed = data["speed_kmh"]
    query_drag = data["drag_force_n"]
    query_q = data["dynamic_pressure_pa"]
    drs_status = 'DRS Open' if data['drs_open'] else 'DRS Closed'
    
    ax1.plot(curve_speeds, curve_drag, color='red', linewidth=2,
             label=f'Drag curve ({drs_status})')
    ax1.scatter([query_speed], [query_drag], color='black', s=70, zorder=3,
                label=f'Query point: {query_speed:.0f} km/h')
    ax1.axvline(query_speed, color='gray', linestyle='--', alpha=0.6)
    ax1.axhline(query_drag, color='gray', linestyle='--', alpha=0.6)
    ax1.set_ylabel('Drag Force (N)', fontsize=12)
    ax1.set_xlabel('Speed (km/h)', fontsize=12)
    ax1.set_title('Drag Force vs Speed', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    ax2.plot(curve_speeds, curve_q, color='navy', linewidth=2,
             label='Dynamic pressure q = 0.5ρv²')
    ax2.scatter([query_speed], [query_q], color='black', s=70, zorder=3)
    ax2.axvline(query_speed, color='gray', linestyle='--', alpha=0.6)
    ax2.axhline(query_q, color='gray', linestyle='--', alpha=0.6)
    ax2.set_ylabel('Dynamic Pressure (Pa)', fontsize=12)
    ax2.set_xlabel('Speed (km/h)', fontsize=12)
    ax2.set_title('Dynamic Pressure vs Speed', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    textstr = '\n'.join([
        f'Query speed: {query_speed:.0f} km/h ({data["speed_ms"]:.1f} m/s)',
        f'Drag force: {query_drag:.0f} N',
        f'Dynamic pressure: {query_q:.0f} Pa',
        f'F_drag = q · A · C_d,  C_d = {data["cd"]:.2f}'
    ])
    fig.text(0.5, 0.02, textstr, ha='center', fontsize=9,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    filename = f"drag_force_{generate_timestamp()}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(filepath, dpi=150)
    plt.close()
    
    return filepath


def plot_drs_comparison(data: Dict[str, Any]) -> str:
    """
    Generate plot comparing DRS open vs closed.
    
    Args:
        data: Calculation results from compare_drs_drag
        
    Returns:
        Path to saved plot file
    """
    ensure_output_dir()
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
    
    speeds = data["speeds_kmh"]
    drag_closed = data["drag_closed_n"]
    drag_open = data["drag_open_n"]
    reduction = data["drag_reduction_percent"]
    
    # Drag force comparison
    ax1.plot(speeds, drag_closed, 'r-', linewidth=2, label='DRS Closed')
    ax1.plot(speeds, drag_open, 'g-', linewidth=2, label='DRS Open')
    ax1.fill_between(speeds, drag_open, drag_closed, alpha=0.3, color='yellow',
                     label='Drag Reduction')
    
    ax1.set_xlabel('Speed (km/h)', fontsize=12)
    ax1.set_ylabel('Drag Force (N)', fontsize=12)
    ax1.set_title('DRS Drag Comparison', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Drag reduction percentage
    ax2.plot(speeds, reduction, 'b-', linewidth=2)
    ax2.fill_between(speeds, 0, reduction, alpha=0.3)
    
    ax2.set_xlabel('Speed (km/h)', fontsize=12)
    ax2.set_ylabel('Drag Reduction (%)', fontsize=12)
    ax2.set_title('DRS Drag Reduction Percentage', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Add annotations
    textstr = '\n'.join([
        f'C_d (Closed): {data["cd_closed"]:.2f}',
        f'C_d (Open): {data["cd_open"]:.2f}',
        f'Frontal Area: {data["frontal_area"]:.2f} m²',
        f'Avg Reduction: {np.mean(reduction):.1f}%'
    ])
    ax1.text(0.02, 0.98, textstr, transform=ax1.transAxes,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
            fontsize=9)
    
    plt.tight_layout()
    
    filename = f"drs_comparison_{generate_timestamp()}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(filepath, dpi=150)
    plt.close()
    
    return filepath


def plot_ground_effect(data: Dict[str, Any]) -> str:
    """
    Generate explanatory ground-effect plots tied to Bernoulli-style reasoning.
    
    Args:
        data: Calculation results from analyze_ground_effect
        
    Returns:
        Path to saved plot file
    """
    ensure_output_dir()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    curve_speeds = data["curve_speeds_kmh"]
    curve_pressure = data["curve_pressure_drop_pa"]
    curve_downforce = data["curve_estimated_downforce_n"]
    query_speed = data["freestream_velocity_kmh"]
    query_pressure = data["pressure_drop_pa"]
    query_downforce = data["estimated_downforce_n"]
    
    ax1.plot(curve_speeds, curve_pressure, color='darkorange', linewidth=2,
             label='Pressure drop from ΔP = 0.5ρ(v_diff² - v_free²)')
    ax1.scatter([query_speed], [query_pressure], color='black', s=70, zorder=3,
                label=f'Query point: {query_speed:.0f} km/h')
    ax1.axvline(query_speed, color='gray', linestyle='--', alpha=0.6)
    ax1.axhline(query_pressure, color='gray', linestyle='--', alpha=0.6)
    ax1.set_ylabel('Pressure Drop (Pa)', fontsize=12)
    ax1.set_xlabel('Freestream Speed (km/h)', fontsize=12)
    ax1.set_title('Ground-Effect Pressure Drop vs Speed', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    ax2.plot(curve_speeds, curve_downforce, color='green', linewidth=2,
             label='Estimated downforce = ΔP · A_floor')
    ax2.scatter([query_speed], [query_downforce], color='black', s=70, zorder=3)
    ax2.axvline(query_speed, color='gray', linestyle='--', alpha=0.6)
    ax2.axhline(query_downforce, color='gray', linestyle='--', alpha=0.6)
    ax2.set_ylabel('Estimated Downforce (N)', fontsize=12)
    ax2.set_xlabel('Freestream Speed (km/h)', fontsize=12)
    ax2.set_title('Ground-Effect Downforce vs Speed', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    textstr = '\n'.join([
        f'Query speed: {query_speed:.0f} km/h',
        f'Velocity ratio: {data["velocity_ratio"]:.2f}x',
        f'Pressure drop: {query_pressure:.0f} Pa',
        f'Estimated downforce: {query_downforce:.0f} N'
    ])
    fig.text(0.5, 0.02, textstr, ha='center', fontsize=9,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    filename = f"ground_effect_{generate_timestamp()}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(filepath, dpi=150)
    plt.close()
    
    return filepath


def generate_visualization(question_type: str, data: Dict[str, Any]) -> Optional[str]:
    """
    Generate appropriate visualization based on question type.
    
    Args:
        question_type: Type of question/analysis
        data: Calculation results
        
    Returns:
        Path to saved visualization file, or None if unsupported
    """
    generators = {
        "front_wing_downforce": plot_front_wing_downforce,
        "drag_force": plot_drag_force,
        "drs_comparison": plot_drs_comparison,
        "ground_effect": plot_ground_effect
    }
    
    generator = generators.get(question_type)
    if generator:
        return generator(data)
    
    return None

# Made with Bob
