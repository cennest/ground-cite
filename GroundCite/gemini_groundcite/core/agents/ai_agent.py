"""
AI Agent for query analysis and research.

This module contains the main AIAgent class that orchestrates the query analysis
pipeline using AI models and a graph-based execution framework.
"""

from collections import defaultdict
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

from ..di.core_di import CoreDi, coredi_injectable
from ...config import AppLogger, AppSettings
from ...exceptions import AIAgentError, ConfigurationError
from .executors import GraphExecutor


@coredi_injectable()
class AIAgent:
    """
    Primary AI agent for executing query analysis workflows.
    
    The AIAgent is the main entry point for the GroundCite library's query analysis
    capabilities. It coordinates the execution of search, validation, and parsing
    operations through a graph-based pipeline using various AI models.
    
    Key Features:
    - Orchestrates multi-step query analysis pipeline
    - Supports multiple AI providers (OpenAI, Google Gemini)
    - Provides retry logic for robust execution
    - Comprehensive logging and error handling
    - Flexible configuration for different analysis scenarios
    
    Attributes:
        settings (AppSettings): Configuration settings for AI and analysis
    """
    
    def __init__(self, settings: AppSettings):
        """
        Initialize the AI agent with required dependencies.
        
        Args:
            settings (AppSettings): Application configuration settings
        
        Raises:
            ConfigurationError: If required configuration is missing or invalid
        """
        self.logger = CoreDi.global_instance().resolve(AppLogger)
        self.settings = settings
        self.executor = GraphExecutor(settings=settings, logger=self.logger)
        
        # Validate configuration on initialization
        is_valid, errors = self.settings.validate_all_configurations()
        if not is_valid:
            raise ConfigurationError(
                "Invalid configuration provided to AI Agent",
                {"errors": errors}
            )
    
    async def analyze_query(self, 
                             query: str = None,
                             system_instruction: str = None,
                             correlation_id: str = None,
                             max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        Analyze a query using the configured AI pipeline.
        
        This is the main entry point for query analysis. It executes the
        graph-based pipeline which may include search, validation, and parsing
        steps depending on the configuration.
        
        Args:
            query (str, optional): Query to analyze (overrides config if provided)
            system_instruction (str, optional): System instruction (overrides config if provided)
            correlation_id (str, optional): Unique ID for tracking this analysis
            max_retries (int): Maximum number of retry attempts (default: 3)
        
        Returns:
            Optional[Dict[str, Any]]: Analysis results containing:
                - search_results: Web search findings
                - validated_content: AI-validated information (if validation enabled)
                - parsed_data: Structured data (if parsing enabled)
                - metadata: Execution metadata and statistics
        
        Raises:
            AIAgentError: If the analysis execution fails
            ConfigurationError: If configuration is invalid for the analysis
        """
        # Override configuration if parameters provided
        if query:
            self.settings.ANALYSIS_CONFIG.query = query
        if system_instruction:
            self.settings.ANALYSIS_CONFIG.system_instruction = system_instruction
            
        # Generate correlation ID if not provided
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        # Validate that we have a query to analyze
        if not self.settings.ANALYSIS_CONFIG.query:
            raise ConfigurationError(
                "No query provided for analysis",
                {"correlation_id": correlation_id}
            )
        
        # Prepare execution metadata
        start_time = datetime.now()
        execution_metadata = {
            "correlation_id": correlation_id,
            "query": self.settings.ANALYSIS_CONFIG.query,
            "validation_enabled": self.settings.ANALYSIS_CONFIG.validate,
            "parsing_enabled": self.settings.ANALYSIS_CONFIG.parse,
            "start_time": start_time.isoformat(),
            "ai_provider": self.settings.AI_CONFIG.parsing_provider,
            "max_retries": max_retries
        }
        
        self.logger.log_info(
            message=f"Starting query analysis: {self.settings.ANALYSIS_CONFIG.query[:100]}...",
            custom_dimensions=execution_metadata
        )
        
        try:
            # Execute the analysis pipeline
            result = await self.executor.ainvoke(
                max_retries=max_retries, 
                correlation_id=correlation_id
            )
            
            # Add execution metadata to result
            end_time = datetime.now()
            execution_duration = (end_time - start_time).total_seconds()
            
            if result:
                result["execution_metadata"] = {
                    **execution_metadata,
                    "end_time": end_time.isoformat(),
                    "duration_seconds": execution_duration,
                    "status": "success"
                }
                
                self.logger.log_info(
                    message=f"Successfully completed query analysis in {execution_duration:.2f}s",
                    custom_dimensions={
                        **execution_metadata,
                        "duration_seconds": execution_duration,
                        "result_keys": list(result.keys()) if result else []
                    }
                )
            else:
                self.logger.log_warning(
                    message="Query analysis completed but returned no results",
                    custom_dimensions={
                        **execution_metadata,
                        "duration_seconds": execution_duration
                    }
                )
            
            return result
            
        except Exception as e:
            error_details = {
                **execution_metadata,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
            
            self.logger.log_error(
                message=f"Query analysis failed: {str(e)}",
                custom_dimensions=error_details
            )
            
            raise AIAgentError(
                f"Failed to analyze query: {str(e)}",
                error_details
            )
    
    async def graph_execute(self) -> Optional[Dict[str, Any]]:
        """
        Execute the analysis pipeline using current configuration.
        
        This method provides backward compatibility and delegates to analyze_query
        with default parameters from the current configuration.
        
        Returns:
            Optional[Dict[str, Any]]: Analysis results from the pipeline
        
        Raises:
            AIAgentError: If the analysis execution fails
        """
        return await self.analyze_query()
    
    def get_execution_status(self) -> Dict[str, Any]:
        """
        Get current execution status and configuration summary.
        
        Returns:
            Dict[str, Any]: Status information including:
                - configuration_summary: Current settings summary
                - executor_status: Graph executor status
                - last_execution: Information about the last execution (if available)
        """
        return {
            "configuration_summary": self.settings.get_configuration_summary(),
            "executor_status": self.executor.get_status() if hasattr(self.executor, 'get_status') else "unknown",
            "agent_ready": self.is_ready_for_execution()
        }
    
    def is_ready_for_execution(self) -> bool:
        """
        Check if the agent is ready to execute analysis.
        
        Returns:
            bool: True if the agent has valid configuration and is ready for execution
        """
        is_valid, _ = self.settings.validate_all_configurations()
        return is_valid and bool(self.settings.ANALYSIS_CONFIG.query)
