"""
GroundCite - An AI-powered query analysis and research library.

This library provides comprehensive AI-powered analysis capabilities for queries,
including web search, content validation, parsing, and intelligent processing
through a graph-based execution framework.

Key Features:
- AI-powered query analysis using multiple LLM providers (OpenAI, Google Gemini)
- Web search and content aggregation
- Content validation and parsing with custom schemas  
- Graph-based execution pipeline for complex analysis workflows
- Flexible configuration system for different analysis scenarios
- Built-in logging and dependency injection

Main Components:
- AIAgent: Primary interface for executing query analysis workflows
- GraphExecutor: Orchestrates the analysis pipeline through graph nodes
- Configuration classes: Manage AI models, API keys, and analysis settings
"""

# Library metadata
__version__ = "1.0.0"
__author__ = "Cennest Team"
__email__ = "support@cennest.com"
__title__ = "GroundCite"
__description__ = "AI-powered query analysis and research library"

# Import core public interfaces
from .core.agents import AIAgent
from .config.settings import AppSettings, AIConfig
from .config.logger import AppLogger
from .core.di.core_di import CoreDi

# Define public API
__all__ = [
    # Core classes
    "AIAgent",
    
    # Configuration
    "AppSettings", 
    "AIConfig",
    "AppLogger",
    
    # Dependency injection
    "CoreDi",
    
    # Exceptions
    "GroundCiteError",
]