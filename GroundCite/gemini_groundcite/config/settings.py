"""
Configuration settings for the GroundCite library.

This module contains configuration classes that manage AI provider settings,
analysis parameters, and application-wide configuration for the GroundCite library.
All settings are designed to be flexible and support multiple AI providers
and analysis scenarios.
"""

import os
from typing import Dict, Any, Optional
from ..core.di.core_di import coredi_injectable, Scope


class AIConfig:
    """
    Configuration for AI model providers and API settings.
    
    This class manages API keys, model names, and provider-specific parameters
    for different AI services including OpenAI and Google Gemini.
    
    Attributes:
        open_ai_key (str): OpenAI API key for accessing GPT models
        gemini_ai_key_primary (str): Primary Google Gemini API key
        gemini_ai_key_secondary (str): Secondary/fallback Google Gemini API key
        search_model_name (str): Model name for search query generation
        validate_model_name (str): Model name for content validation
        parse_model_name (str): Model name for content parsing
        parsing_provider (str): Provider for parsing operations ('openai' or 'gemini')
        search_gemini_params (Dict): Gemini-specific parameters for search operations
        validate_gemini_params (Dict): Gemini-specific parameters for validation
        parsing_gemini_params (Dict): Gemini-specific parameters for parsing
        parsing_openai_params (Dict): OpenAI-specific parameters for parsing
    """
    
    def __init__(self):
        """Initialize AI configuration with default values."""
        # API Keys
        self.open_ai_key: Optional[str] = None
        self.gemini_ai_key_primary: Optional[str] = None
        self.gemini_ai_key_secondary: Optional[str] = None
        
        # Model Names
        self.search_model_name: Optional[str] = None
        self.validate_model_name: Optional[str] = None
        self.parse_model_name: Optional[str] = None
        
        # Provider Selection
        self.parsing_provider: Optional[str] = None  # 'openai' or 'gemini'
        
        # Provider-specific Parameters
        self.search_gemini_params: Dict[str, Any] = {}
        self.validate_gemini_params: Dict[str, Any] = {}
        self.parsing_gemini_params: Dict[str, Any] = {}
        self.parsing_openai_params: Dict[str, Any] = {}
    
    def validate_configuration(self) -> bool:
        """
        Validate that required configuration is present.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        # At least one API key must be present
        if not (self.open_ai_key or self.gemini_ai_key_primary):
            return False
        
        # If parsing provider is specified, corresponding key must exist
        if self.parsing_provider == 'openai' and not self.open_ai_key:
            return False
        if self.parsing_provider == 'gemini' and not self.gemini_ai_key_primary:
            return False
            
        return True


class AnalysisConfig:
    """
    Configuration for query analysis operations.
    
    This class manages the parameters for query analysis including the query
    to analyze, processing options, parsing schemas, and site filtering preferences.
    
    Attributes:
        query (str): The main query to analyze and research
        system_instruction (str): System-level instructions for AI processing
        validate (bool): Whether to enable content validation step
        parse (bool): Whether to enable content parsing step
        parse_schema (str): JSON schema for parsing structured data
        excluded_sites (str): Comma-separated list of sites to exclude from search
        included_sites (str): Comma-separated list of sites to include in search
    """
    
    def __init__(self):
        """Initialize analysis configuration with default values."""
        # Core Analysis Parameters
        self.query: Optional[str] = None
        self.system_instruction: Optional[str] = None
        
        # Processing Options
        self.validate: bool = False  # Enable validation step
        self.parse: bool = False     # Enable parsing step
        
        # Parsing Configuration
        self.parse_schema: Optional[str] = None  # JSON schema for parsing
        
        # Search Filtering
        self.excluded_sites: Optional[str] = ''  # Sites to exclude
        self.included_sites: Optional[str] = ''  # Sites to include
    
    def get_excluded_sites_list(self) -> list[str]:
        """
        Get excluded sites as a list.
        
        Returns:
            List[str]: List of excluded site domains
        """
        if not self.excluded_sites:
            return []
        return [site.strip() for site in self.excluded_sites.split(',') if site.strip()]
    
    def get_included_sites_list(self) -> list[str]:
        """
        Get included sites as a list.
        
        Returns:
            List[str]: List of included site domains
        """
        if not self.included_sites:
            return []
        return [site.strip() for site in self.included_sites.split(',') if site.strip()]
    
    def is_valid(self) -> bool:
        """
        Check if the analysis configuration is valid.
        
        Returns:
            bool: True if configuration is valid for analysis
        """
        # Must have a query to analyze
        if not self.query or not self.query.strip():
            return False
        
        # If parsing is enabled, must have a schema
        if self.parse and not self.parse_schema:
            return False
            
        return True


@coredi_injectable()
class AppSettings:
    """
    Main application settings container.
    
    This class combines all configuration classes and provides application-wide
    settings for the GroundCite library. It includes AI configuration, analysis
    configuration, and system-level settings.
    
    Attributes:
        AI_CONFIG (AIConfig): AI provider and model configuration
        ANALYSIS_CONFIG (AnalysisConfig): Query analysis configuration
        BASE_DIR (str): Base directory path for the application
    """
    
    def __init__(self):
        """Initialize application settings with default configurations."""
        # Configuration Components
        self.AI_CONFIG = AIConfig()
        self.ANALYSIS_CONFIG = AnalysisConfig()
        
        # System Settings
        self.BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    def validate_all_configurations(self) -> tuple[bool, list[str]]:
        """
        Validate all configuration components.
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate AI configuration
        if not self.AI_CONFIG.validate_configuration():
            errors.append("AI configuration is invalid - missing required API keys")
        
        # Validate analysis configuration
        if not self.ANALYSIS_CONFIG.is_valid():
            errors.append("Analysis configuration is invalid - missing required parameters")
        
        return len(errors) == 0, errors
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current configuration (excluding sensitive data).
        
        Returns:
            Dict[str, Any]: Configuration summary without API keys
        """
        return {
            "ai_config": {
                "has_openai_key": bool(self.AI_CONFIG.open_ai_key),
                "has_gemini_key": bool(self.AI_CONFIG.gemini_ai_key_primary),
                "parsing_provider": self.AI_CONFIG.parsing_provider,
                "search_model": self.AI_CONFIG.search_model_name,
                "validate_model": self.AI_CONFIG.validate_model_name,
                "parse_model": self.AI_CONFIG.parse_model_name,
            },
            "analysis_config": {
                "has_query": bool(self.ANALYSIS_CONFIG.query),
                "validation_enabled": self.ANALYSIS_CONFIG.validate,
                "parsing_enabled": self.ANALYSIS_CONFIG.parse,
                "has_parse_schema": bool(self.ANALYSIS_CONFIG.parse_schema),
                "has_site_filters": bool(self.ANALYSIS_CONFIG.excluded_sites or self.ANALYSIS_CONFIG.included_sites),
            },
            "base_dir": self.BASE_DIR,
        }