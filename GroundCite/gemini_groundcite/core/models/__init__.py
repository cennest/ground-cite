"""Data models for the GroundCite library.

This module contains Pydantic models and dataclasses that define the data
structures used throughout the GroundCite library for request handling,
response formatting, and data validation."""

from .search_request import SearchRequest

# Export all model classes
__all__ = ["SearchRequest"]