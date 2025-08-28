"""
Dependency Injection module for the GroundCite library.

This module provides a lightweight dependency injection framework built on top
of the punq library. It enables loose coupling, testability, and flexible
configuration management throughout the application.
"""

from .core_di import CoreDi, coredi_injectable, Scope, inject, inject_privately

# Export all dependency injection components
__all__ = ["CoreDi", "coredi_injectable", "Scope", "inject", "inject_privately"]