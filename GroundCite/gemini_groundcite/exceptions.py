"""
Custom exceptions for the GroundCite library.

This module defines all custom exceptions that can be raised by the GroundCite
library during query analysis, AI processing, and configuration operations.
"""


class GroundCiteError(Exception):
    """
    Base exception for all GroundCite library errors.
    
    This is the parent class for all custom exceptions in the GroundCite library.
    It provides a consistent interface for error handling and allows users to
    catch all library-specific errors with a single except clause.
    
    Attributes:
        message (str): Human-readable error message
        details (dict): Additional error context and debugging information
    """
    
    def __init__(self, message: str, details: dict = None):
        """
        Initialize the exception with message and optional details.
        
        Args:
            message (str): Human-readable error description
            details (dict, optional): Additional context information
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.details:
            return f"{self.message}. Details: {self.details}"
        return self.message


class AIAgentError(GroundCiteError):
    """
    Raised when errors occur during AI agent execution.
    
    This exception is raised when the AI agent encounters issues during
    query analysis, model inference, or pipeline execution.
    """
    pass


class ConfigurationError(GroundCiteError):
    """
    Raised when configuration is invalid or incomplete.
    
    This exception is raised when:
    - Required API keys are missing
    - Model configurations are invalid
    - Analysis settings are incompatible
    - Required parameters are not provided
    """
    pass


class GraphExecutionError(GroundCiteError):
    """
    Raised when errors occur during graph execution pipeline.
    
    This exception is raised when the graph executor encounters issues
    during node execution, state management, or pipeline orchestration.
    """
    pass