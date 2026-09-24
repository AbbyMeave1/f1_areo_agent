"""
Physics calculations module for F1 aerodynamics.
"""

from .mcp_client import MCPPhysicsClient, get_physics_client
from . import calculations

__all__ = ['MCPPhysicsClient', 'get_physics_client', 'calculations']

# Made with Bob
