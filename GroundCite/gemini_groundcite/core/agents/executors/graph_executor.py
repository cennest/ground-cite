"""
Graph Executor for orchestrating AI-powered query analysis pipeline.

This module contains the GraphExecutor class that manages a complex, graph-based
workflow for analyzing queries through multiple AI processing stages including
search, validation, and parsing operations.
"""

import re
import uuid
import time
from typing import Dict, Optional, Any

# Import state management
from .graph_state import *
from ....exceptions import GraphExecutionError

# LangGraph imports for workflow orchestration
from langgraph.graph import StateGraph, END
from langgraph.constants import Send

# Configuration and logging
from ....config import AppSettings, AppLogger
from ...di.core_di import coredi_injectable

# Import all processing nodes
from .nodes.orchestration_node import *
from .nodes.search_node import *
from .nodes.parse_node import *
from .nodes.validation_node import *
from .nodes.search_aggregator_node import *
from .nodes.validation_aggregator_node import *


@coredi_injectable()
class GraphExecutor:
    """
    Orchestrates the query analysis pipeline through a graph-based workflow.
    
    The GraphExecutor manages a complex workflow that processes queries through
    multiple AI-powered stages. It uses LangGraph to create a state machine that
    can handle different execution paths based on configuration and results.
    
    Workflow Stages:
    1. Orchestration: Coordinates overall execution and decides next steps
    2. Search: Performs web searches to gather relevant information
    3. Search Aggregation: Consolidates and processes search results
    4. Validation: AI-powered validation of gathered content (optional)
    5. Validation Aggregation: Processes validation results (optional)
    6. Parsing: Extracts structured data using provided schema (optional)
    
    Key Features:
    - State-driven execution with automatic retry logic
    - Configurable pipeline stages based on analysis requirements
    - Comprehensive metrics collection and logging
    - Error handling and graceful degradation
    - Token usage tracking for cost monitoring
    
    Attributes:
        logger (AppLogger): Application logger for operation tracking
        settings (AppSettings): Configuration settings for the pipeline
        graph: Compiled LangGraph workflow for execution
    """

    def __init__(self, settings: AppSettings, logger: AppLogger):
        """
        Initialize the GraphExecutor with settings and logger.
        
        This constructor builds the complete workflow graph by creating all
        processing nodes and defining their relationships and routing logic.
        
        Args:
            settings (AppSettings): Configuration settings for the pipeline
            logger (AppLogger): Logger instance for operation tracking
        
        """
        self.logger = logger
        self.settings = settings
        
        try:
            # Build the workflow graph with all processing nodes
            workflow = StateGraph(AgentState)
            
            # Create all processing nodes with their routing functions
            orchestration_node, orchestration_node_router = create_orchestration_node(
                self.settings, self.logger, self.get_log_dimensions
            )
            search_node = create_search_node(
                self.settings, self.logger, self.get_log_dimensions
            )
            search_aggregator_node, search_aggregator_node_router = create_search_aggregator_node(
                self.settings, self.logger, self.get_log_dimensions
            )
            validation_node = create_validation_node(
                self.settings, self.logger, self.get_log_dimensions
            )
            validation_aggregator_node, validation_aggregator_node_router = create_validation_aggregator_node(
                self.settings, self.logger, self.get_log_dimensions
            )
            parsing_node, parsing_node_router = create_parsing_node(
                self.settings, self.logger, self.get_log_dimensions
            )
           
            # Register all nodes in the workflow
            workflow.add_node("orchestration_node", orchestration_node)
            workflow.add_node("search_node", search_node)
            workflow.add_node("search_aggregator_node", search_aggregator_node)
            workflow.add_node("validation_node", validation_node)
            workflow.add_node("validation_aggregator_node", validation_aggregator_node)
            workflow.add_node("parse_node", parsing_node)
    
            # Set the orchestration node as the entry point
            workflow.set_entry_point("orchestration_node")
            
            # Define routing logic for orchestration node
            # This node coordinates the overall execution flow
            workflow.add_conditional_edges(
                "orchestration_node",
                orchestration_node_router,
                {
                    "end": END  # Complete execution when all steps are done
                }
            )
    
            # search workflow: search_node -> search_aggregator_node
            workflow.add_edge("search_node", "search_aggregator_node")
    
            # search aggregator decides whether to continue or return to orchestration
            workflow.add_conditional_edges(
                "search_aggregator_node",
                search_aggregator_node_router,
                {
                    # Continue to parsing if enabled, otherwise back to orchestration
                    "continue": "parse_node" if settings.ANALYSIS_CONFIG.parse else "orchestration_node",
                    "end": "orchestration_node"
                }
            )
    
            # Validation workflow: validation_node -> validation_aggregator_node
            workflow.add_edge("validation_node", "validation_aggregator_node")
    
            # Validation aggregator routing based on parsing configuration
            workflow.add_conditional_edges(
                "validation_aggregator_node",
                validation_aggregator_node_router,
                {
                    # Route to parsing if enabled, otherwise back to orchestration
                    "continue": "parse_node" if self.settings.ANALYSIS_CONFIG.parse else "orchestration_node",
                    "end": "parse_node" if self.settings.ANALYSIS_CONFIG.parse else "orchestration_node"
                }
            )
            
            # Parsing node with retry logic for handling invalid results
            workflow.add_conditional_edges(
                "parse_node",
                parsing_node_router,
                {
                    "retry": "parse_node",  # Retry parsing if validation fails
                    "continue": "orchestration_node",  # Continue to next step
                    "end": "orchestration_node"  # Complete execution
                }
            )
    
            # Compile the workflow into an executable graph
            self.graph = workflow.compile()
            
        except Exception as e:
            raise GraphExecutionError(
                f"Failed to initialize GraphExecutor: {str(e)}",
                {"settings_summary": settings.get_configuration_summary()}
            )


    async def execute_analysis(self, max_retries: int = 2, correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute the complete query analysis pipeline.
        
        This is the main execution method that runs the graph-based workflow
        to analyze queries through multiple AI-powered processing stages.
        
        Args:
            max_retries (int): Maximum number of retry attempts per node (default: 2)
            correlation_id (str, optional): Unique identifier for tracking this execution
        
        Returns:
            Dict[str, Any]: Comprehensive analysis results containing:
                - completed: Whether parsing was completed successfully
                - final_content: Final structured data (if parsing enabled)
                - search_content: Raw search results and metadata
                - validated_content: AI-validated content (if validation enabled)
                - validation_response: Validation analysis results
                - search_meta_data: Search operation metadata
                - execution_metrics: Performance and usage statistics
        
        Raises:
            GraphExecutionError: If the workflow execution fails
            ValueError: If max_retries is not provided or invalid
        """
        # Validate input parameters
        if max_retries is None or max_retries < 0:
            raise ValueError("max_retries must be specified and non-negative")

        # Generate correlation_id for tracking if not provided
        if correlation_id is None:
            correlation_id = f"exec_{uuid.uuid4().hex[:8]}"

        # Initialize workflow metrics for performance tracking
        workflow_metrics = WorkflowMetrics(correlation_id=correlation_id)
        workflow_metrics.token_usage = {'search': [], 'validation': [], 'parse': []}
        workflow_metrics.start_time = time.time()

        # Initialize the complete agent state with all node states
        agent_state = AgentState(
            # Node-specific states with retry configuration
            search_aggregator_state=NodeState(max_retries=max_retries),
            validation_aggregator_state=NodeState(max_retries=max_retries),
            parse_state=ParseState(
                max_retries=max_retries, 
                schema=self.settings.ANALYSIS_CONFIG.parse_schema
            ),
            
            # Workflow management states
            workflow_metrics=workflow_metrics,
            orchestration_state=OrchestrationState(),
            
            # Processing states for storing results
            search_state=SearchState(results=[]),
            validation_state=ValidationState(results=[])
        )

        
        # Configure the graph execution parameters
        config = {
            "configurable": {
                "thread_id": workflow_metrics.session_id
            },
            "recursion_limit": 100  # Prevent infinite loops in graph execution
        }

        # Execute the complete workflow graph
        try:
            self.logger.log_info(
                f"Starting query analysis pipeline execution",
                custom_dimensions=self.get_log_dimensions(
                    workflow_metrics,
                    max_retries=max_retries,
                    operation="execution_start",
                    query_length=len(self.settings.ANALYSIS_CONFIG.query or ""),
                    validation_enabled=self.settings.ANALYSIS_CONFIG.validate,
                    parsing_enabled=self.settings.ANALYSIS_CONFIG.parse
                )
            )
            
            # Execute the graph workflow asynchronously
            execution_result = await self.graph.ainvoke(agent_state, config)
            
            # Record execution completion time
            workflow_metrics.end_time = time.time()

            # Extract final states from execution result
            final_search_state: NodeState = execution_result["search_aggregator_state"]
            final_validation_state: NodeState = execution_result["validation_aggregator_state"]
            final_parse_state: ParseState = execution_result["parse_state"]
            final_metrics: WorkflowMetrics = execution_result["workflow_metrics"]
            final_orchestration_state: OrchestrationState = execution_result["orchestration_state"]

            # Consolidate token usage across all operations
            token_usage = final_metrics.merge_token_usage()

            # Log successful completion with comprehensive metrics
            self.logger.log_info(
                f"Query analysis pipeline completed successfully",
                custom_dimensions=self.get_log_dimensions(
                    final_metrics,
                    token_usage=token_usage,
                    operation="execution_complete",
                    completed=final_orchestration_state.completed,
                    execution_time=final_metrics.get_execution_time(),
                    validation_completed=final_validation_state.completed,
                    total_nodes_executed=final_metrics.total_nodes_executed,
                    search_completed=final_search_state.completed
                )
            )
  
            # Return comprehensive analysis results
            return {
                
                # Stage-specific Results
                "search_results": final_orchestration_state.search_content,
                "search_metadata": final_orchestration_state.search_meta_data,
                "validated_content": final_orchestration_state.validated_content,
                "validation_analysis": final_orchestration_state.validation_response,
                
                # Backward Compatibility Fields
                "completed": final_orchestration_state.completed,
                "final_content": final_orchestration_state.final_content,
                "search_content": final_orchestration_state.search_content,
                "validation_response": final_orchestration_state.validation_response,
                "search_meta_data": final_orchestration_state.search_meta_data,
                                
                # Execution Performance Metrics
                "execution_metrics": {
                    "token_usage": token_usage,
                    "session_id": final_metrics.session_id,
                    "correlation_id": final_metrics.correlation_id,
                    "execution_time_seconds": final_metrics.get_execution_time(),
                    "total_nodes_executed": final_metrics.total_nodes_executed,
                    "nodes_completion_status": {
                        "search": final_search_state.completed,
                        "validation": final_validation_state.completed,
                        "parsing": final_parse_state.completed
                    }
                }
            }
            
        except Exception as e:
            # Record end time even on failure for accurate metrics
            workflow_metrics.end_time = time.time()
            
            self.logger.log_error(
                f"Query analysis pipeline execution failed", 
                exception=e,
                custom_dimensions=self.get_log_dimensions(
                    workflow_metrics,
                    execution_time=workflow_metrics.get_execution_time(),
                    operation="execution_failed",
                    token_usage=workflow_metrics.merge_token_usage()
                )
            )
            
            raise GraphExecutionError(
                f"Pipeline execution failed: {str(e)}",
                {
                    "correlation_id": correlation_id,
                    "execution_time": workflow_metrics.get_execution_time(),
                    "error_type": type(e).__name__
                }
            )

    async def ainvoke(self, max_retries: int = 2, correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute the analysis pipeline (backward compatibility method).
        
        This method provides backward compatibility with the existing API
        while delegating to the new execute_analysis method.
        
        Args:
            max_retries (int): Maximum retry attempts per node
            correlation_id (str, optional): Execution tracking identifier
        
        Returns:
            Dict[str, Any]: Analysis results from the pipeline
        
        Raises:
            GraphExecutionError: If execution fails
        """
        return await self.execute_analysis(max_retries, correlation_id)

    def get_log_dimensions(self, workflow_metrics: WorkflowMetrics, **additional_dims) -> Dict[str, Any]:
        """
        Create consistent log dimensions for tracking and debugging.
        
        This helper method generates standardized logging dimensions that include
        workflow metrics and additional context information for comprehensive
        operation tracking and debugging.
        
        Args:
            workflow_metrics (WorkflowMetrics): Current workflow execution metrics
            **additional_dims: Additional key-value pairs to include in log dimensions
        
        Returns:
            Dict[str, Any]: Consolidated log dimensions with base metrics and additional data
        """
        base_dimensions = {
            "session_id": workflow_metrics.session_id,
            "category_id": workflow_metrics.category,
            "category": workflow_metrics.category,
            "correlation_id": workflow_metrics.correlation_id
        }
        
        # Merge additional dimensions while preserving base ones
        base_dimensions.update(additional_dims)
        return base_dimensions
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get current status and configuration of the analysis pipeline.
        
        Returns:
            Dict[str, Any]: Pipeline status including:
                - configuration_summary: Current settings and capabilities
                - pipeline_ready: Whether the pipeline is ready for execution
                - supported_operations: List of enabled pipeline operations
        """
        config_summary = self.settings.get_configuration_summary()
        
        return {
            "configuration_summary": config_summary,
            "pipeline_ready": self._is_pipeline_ready(),
            "supported_operations": self._get_supported_operations(),
            "graph_compiled": self.graph is not None
        }
    
    def _is_pipeline_ready(self) -> bool:
        """Check if the pipeline is ready for execution."""
        is_valid, _ = self.settings.validate_all_configurations()
        return is_valid and self.graph is not None
    
    def _get_supported_operations(self) -> list[str]:
        """Get list of operations supported by current configuration."""
        operations = ["search"]  # Search is always supported
        
        if self.settings.ANALYSIS_CONFIG.validate:
            operations.append("validation")
        
        if self.settings.ANALYSIS_CONFIG.parse:
            operations.append("parsing")
        
        return operations
