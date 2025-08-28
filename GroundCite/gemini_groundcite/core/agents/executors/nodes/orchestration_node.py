"""
Orchestration node for coordinating the query analysis workflow.

This module contains the central orchestration logic that coordinates the
execution flow of the query analysis pipeline. It manages the sequence
of search, validation, and parsing operations based on configuration settings
and current workflow state.
"""

from dataclasses import asdict
from typing import Any, Dict, List, Callable, Tuple
from ..citation_processor import CitationProcessor
from ..core_helper import *
from ..graph_state import *
from .....config.logger import AppLogger
from .....config.settings import AppSettings
from ..core_helper import create_domain_validator, get_alpha_id
import json


def create_orchestration_node(
    settings: AppSettings,
    logger: AppLogger,
    get_log_dimensions: Callable[[WorkflowMetrics, ...], Dict[str, Any]]
) -> Tuple[Callable[[AgentState], dict], Callable[[AgentState], str]]:
    """
    Creates an orchestration node that coordinates the query analysis workflow.
    
    Manages the execution flow of search, validation, and parsing operations
    based on configuration settings and workflow state.
    
    Args:
        settings: Application configuration settings
        logger: Logger instance for logging operations
        get_log_dimensions: Function to generate logging dimensions
        
    Returns:
        Tuple containing the node function and router function
    """

    logger.log_info("Creating deep search node.")

    async def node(agent_state: AgentState) -> dict:
        """
        Main orchestration node function that coordinates the analysis workflow.
        
        Manages search request generation, result aggregation, and final content
        preparation based on the workflow configuration and current state.
        
        Args:
            agent_state: Current state of the workflow execution
            
        Returns:
            Updated agent state with orchestration results
        """
        # Configure total iterations for tier-based search
        total_iterations = 1
        
        # Extract state components from agent state
        orchestration_state:OrchestrationState = agent_state["orchestration_state"]
        search_agg_state:NodeState = agent_state["search_aggregator_state"]
        search_state = agent_state["search_state"]
        validation_agg_state:NodeState = agent_state["validation_aggregator_state"]
        validation_state = agent_state["validation_state"]
        parse_state = agent_state["parse_state"]
        workflow_metrics = agent_state["workflow_metrics"]

        # Increment node execution count for metrics tracking
        workflow_metrics.total_nodes_executed += 1

        try:
            # Advance to the next tier in the search iteration
            orchestration_state.tier_index += 1

            # Create search requests based on configuration settings
            search_requests = [SearchRequest(id=get_alpha_id(0), user_prompt=settings.ANALYSIS_CONFIG.query, system_prompt=settings.ANALYSIS_CONFIG.system_instruction)]    
            orchestration_state.search_requests = search_requests

            # Check if we've exceeded maximum iterations
            if orchestration_state.tier_index > total_iterations:
                logger.log_warning(
                    f"Tier-based search exhausted (Tier {orchestration_state.tier_index + 1}/{total_iterations})",
                    custom_dimensions=get_log_dimensions(
                        workflow_metrics,
                        tier_index=orchestration_state.tier_index,
                        node="orchestration"
                    )
                )
                orchestration_state.completed = True
                return agent_state

            # Process results if parsing or search aggregation is completed
            if parse_state.completed or search_agg_state.completed:
                
                final_data = {}

                # Aggregate search results and metadata
                if search_state["results"]:
                    orchestration_state.search_meta_data += f"\n\n{get_grounding_metadata(search_state.get('results'))}"   
                    for result in search_state["results"]:
                        orchestration_state.search_content += f"\n\n{result.content}"
                        orchestration_state.search_citations.extend(result.citations)

                # Aggregate validation results if available
                if validation_state["results"]:
                    for result in validation_state["results"]:
                        orchestration_state.validated_content += f"\n\n{result.citations_content}"
                        orchestration_state.validation_response += f"\n\n{result.content}"
                        orchestration_state.validated_citations.extend(result.citations)

                # Prepare final data based on workflow configuration
                if settings.ANALYSIS_CONFIG.parse:    
                    # Process parsed content with citation deduplication
                    cite_proc = CitationProcessor()
                    updated_raw_json, citations = cite_proc.deduplicate_text_citations(parse_state.parsed_content)
                    content = json.loads(updated_raw_json)

                    # Create final citations with proper formatting
                    final_citations = [
                        {"chunk_index": id - 1, "original_link": url, "title": create_domain_validator(url)[1]}
                        for url, id in citations.items()
                    ]
                    final_data["content"]  = content
                    final_data["citations"] = final_citations
                elif settings.ANALYSIS_CONFIG.validate:
                    # Use validated content and citations
                    final_data["content"] =  orchestration_state.validated_content   
                    final_data["citations"] = extract_unique_citations(orchestration_state.validated_citations)                        
                else:
                    # Use raw search content and citations
                    final_data["content"] =  orchestration_state.search_content
                    final_data["citations"] = extract_unique_citations(orchestration_state.search_citations)

                # Store final processed content
                orchestration_state.final_content =  final_data

                orchestration_state.completed = True
                return agent_state
                
            # Reset the state of all nodes for next iteration
            search_agg_state.reset()
            validation_agg_state.reset()
            parse_state.reset()
            search_state["results"] = []
            validation_state["results"] = []
 
            return agent_state

        except Exception as e:
            # Handle orchestration errors by logging and returning current state
            logger.log_error(
                "Error in Tier-based search evaluation",
                exception=e,
                custom_dimensions=get_log_dimensions(
                    workflow_metrics,
                    tier_index=orchestration_state.tier_index,
                    node="orchestration",
                    status="error"
                )
            )
            return agent_state

    async def router(agent_state: AgentState) -> str:
        """
        Router function that determines the next workflow step based on orchestration state.
        
        Controls the flow between orchestration, search nodes, and workflow termination
        based on completion status and iteration limits.
        
        Args:
            agent_state: Current state of the workflow execution
            
        Returns:
            String indicating the next workflow step ("end", search node, etc.)
        """
        # Configure total iterations for tier-based search
        total_iterations = 1
        orchestration_state = agent_state["orchestration_state"]
        workflow_metrics = agent_state["workflow_metrics"]

        # Check if orchestration workflow is completed
        if orchestration_state.completed:
            logger.log_debug(
                "Tier-based search completed",
                custom_dimensions=get_log_dimensions(
                    workflow_metrics,
                    node="should_handle_gaps"
                )
            )
            return "end"

        # Continue with additional tiers if within iteration limits
        if orchestration_state.tier_index < total_iterations:
            logger.log_debug(
                f"Tier-based search triggered (Tier {orchestration_state.tier_index + 1}/{total_iterations})",
                custom_dimensions=get_log_dimensions(
                    workflow_metrics,
                    tier_index=orchestration_state.tier_index,
                    node="should_handle_gaps"
                )
            )
            # Route to search nodes for continued processing
            search_nodes = get_search_nodes(agent_state)
            return search_nodes if search_nodes else "end"

        # Default to end if no other conditions are met
        return "end"

    return node, router
