"""
MCP (Model Context Protocol) client abstraction for physics calculations.

This module provides an interface to the IBM chuk-mcp-physics server.
Currently implements a fallback analytic calculator while maintaining
the interface for future MCP integration.
"""

import json
from typing import Dict, Any, Optional


class MCPPhysicsClient:
    """
    Abstraction layer for physics calculations via MCP.
    
    This client is designed to communicate with the IBM chuk-mcp-physics
    MCP server. Currently uses a fallback implementation but maintains
    the interface for seamless MCP integration.
    """
    
    def __init__(self, use_mcp: bool = False, mcp_server_path: Optional[str] = None):
        """
        Initialize the physics client.
        
        Args:
            use_mcp: Whether to use actual MCP server (not yet implemented)
            mcp_server_path: Path to MCP server executable
        """
        self.use_mcp = use_mcp
        self.mcp_server_path = mcp_server_path
        self.connected = False
        
        if use_mcp:
            # Future: Initialize MCP connection
            # For now, fall back to analytic
            print("Warning: MCP integration not yet implemented, using fallback")
            self.use_mcp = False
    
    def calculate_dynamic_pressure(self, velocity: float, density: float = 1.225) -> Dict[str, Any]:
        """
        Calculate dynamic pressure: q = 0.5 * rho * v^2
        
        Args:
            velocity: Velocity in m/s
            density: Air density in kg/m^3 (default: sea level)
            
        Returns:
            Dictionary with calculation results
        """
        q = 0.5 * density * velocity ** 2
        
        return {
            "dynamic_pressure": q,
            "velocity": velocity,
            "density": density,
            "equation": "q = 0.5 * ρ * v²",
            "units": "Pa (N/m²)"
        }
    
    def calculate_lift_force(self, dynamic_pressure: float, area: float, 
                            cl: float) -> Dict[str, Any]:
        """
        Calculate lift/downforce: F_l = q * A * C_l
        
        Args:
            dynamic_pressure: Dynamic pressure in Pa
            area: Reference area in m²
            cl: Lift coefficient (negative for downforce)
            
        Returns:
            Dictionary with calculation results
        """
        force = dynamic_pressure * area * cl
        
        return {
            "lift_force": force,
            "downforce": -force if cl < 0 else 0,
            "dynamic_pressure": dynamic_pressure,
            "area": area,
            "cl": cl,
            "equation": "F_l = q * A * C_l",
            "units": "N"
        }
    
    def calculate_drag_force(self, dynamic_pressure: float, area: float,
                            cd: float) -> Dict[str, Any]:
        """
        Calculate drag force: F_d = q * A * C_d
        
        Args:
            dynamic_pressure: Dynamic pressure in Pa
            area: Reference area in m²
            cd: Drag coefficient
            
        Returns:
            Dictionary with calculation results
        """
        force = dynamic_pressure * area * cd
        
        return {
            "drag_force": force,
            "dynamic_pressure": dynamic_pressure,
            "area": area,
            "cd": cd,
            "equation": "F_d = q * A * C_d",
            "units": "N"
        }
    
    def calculate_pressure_change(self, velocity_1: float, velocity_2: float,
                                 density: float = 1.225) -> Dict[str, Any]:
        """
        Calculate pressure change using simplified Bernoulli equation.
        ΔP = 0.5 * ρ * (v₁² - v₂²)
        
        Args:
            velocity_1: Initial velocity in m/s
            velocity_2: Final velocity in m/s
            density: Air density in kg/m³
            
        Returns:
            Dictionary with calculation results
        """
        delta_p = 0.5 * density * (velocity_1 ** 2 - velocity_2 ** 2)
        
        return {
            "pressure_change": delta_p,
            "velocity_1": velocity_1,
            "velocity_2": velocity_2,
            "density": density,
            "equation": "ΔP = 0.5 * ρ * (v₁² - v₂²)",
            "units": "Pa"
        }
    
    def close(self):
        """Close MCP connection if active."""
        if self.connected:
            # Future: Close MCP connection
            self.connected = False


# Singleton instance
_client_instance = None


def get_physics_client(use_mcp: bool = False) -> MCPPhysicsClient:
    """
    Get or create the global physics client instance.
    
    Args:
        use_mcp: Whether to attempt MCP connection
        
    Returns:
        MCPPhysicsClient instance
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = MCPPhysicsClient(use_mcp=use_mcp)
    return _client_instance

# Made with Bob
