"""
Search request model for AI search operations.

This module defines the data structure for search requests sent to AI models,
including prompt configuration and request identification.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SearchRequest:
    """
    Data model for search requests to AI providers.
    
    Represents a structured search request containing prompts and metadata
    for AI model interactions. Used to standardize request formatting
    across different AI providers and operations.
    
    Attributes:
        id (str, optional): Unique identifier for the search request
        user_prompt (str, optional): User-provided search or query
        system_prompt (str, optional): System-level instructions for the AI model
    """
    id: Optional[str] = None
    user_prompt: Optional[str] = None
    system_prompt: Optional[str] = None



