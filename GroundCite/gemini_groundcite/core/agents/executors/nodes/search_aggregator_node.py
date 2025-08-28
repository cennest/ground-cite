"""
Search Aggregator Node for the workflow execution system.

This module provides functionality to aggregate search results and determine 
the next workflow step based on search completion status and retry logic.
"""

from typing import Any, Dict, Callable, Tuple
import asyncio
from .....config.logger import AppLogger
from .....config.settings import AppSettings
from ..graph_state import AgentState, NodeState, OrchestrationState, WorkflowMetrics
from ..core_helper import get_search_nodes, get_validation_nodes


def create_search_aggregator_node(
    settings: AppSettings,
    logger: AppLogger,
    get_log_dimensions: Callable[[WorkflowMetrics, ...], Dict[str, Any]]  # type: ignore
) -> Tuple[Callable[[AgentState], dict], Callable[[AgentState], str]]:
    """
    Creates a search aggregator node that manages search result collection and workflow routing.
    
    Args:
        settings: Application configuration settings
        logger: Logger instance for logging operations
        get_log_dimensions: Function to generate logging dimensions
        
    Returns:
        Tuple containing the node function and router function
    """

    logger.log_info("Creating search aggregator node.")

    async def node(agent_state: AgentState) -> dict:
        """
        Main node function that processes search results and determines completion status.
        
        Args:
            agent_state: Current state of the workflow execution
            
        Returns:
            Updated agent state
        """
        # Extract state components from agent state
        orchestration_state:OrchestrationState = agent_state["orchestration_state"]
        search_aggregator_state:NodeState = agent_state["search_aggregator_state"]
        search_state = agent_state["search_state"]
        workflow_metrics = agent_state["workflow_metrics"]

        # Increment node execution count for metrics tracking
        workflow_metrics.total_nodes_executed += 1

        # Reset search state if this is a retry attempt
        if search_aggregator_state.retry_count > 0:
            search_aggregator_state.reset_for_retry()

        try:
            # Collect IDs of successfully completed search results
            existing_ids = {r.id for r in (search_state["results"] or []) if r.id}

            # Get the original search requests for comparison
            search_requests = orchestration_state.search_requests or []

            # Increment retry counter to track attempts
            search_aggregator_state.increment_retry()

            # Mark as completed if all searches done or no retries left
            if len(existing_ids) == len(search_requests) or not search_aggregator_state.is_retry_available():
                search_aggregator_state.completed = True

            return agent_state

        except Exception as e:
            # Handle errors by updating state and logging
            search_aggregator_state.increment_retry()
            search_aggregator_state.set_error(str(e))

            logger.log_error(
                f"Error in search aggregator (Attempt {search_aggregator_state.retry_count}/{search_aggregator_state.max_retries})",
                exception=e,
                custom_dimensions=get_log_dimensions(
                    workflow_metrics,
                    retry_count=search_aggregator_state.retry_count,
                    node="search_aggregator",
                    status="error"
                )
            )

            return agent_state

    async def router(agent_state: AgentState) -> str:
        """
        Router function that determines the next workflow step based on search completion status.
        
        Args:
            agent_state: Current state of the workflow execution
            
        Returns:
            String indicating the next workflow step ("continue", validation node, "end")
        """
        search_aggregator_state:NodeState = agent_state["search_aggregator_state"]
        workflow_metrics = agent_state["workflow_metrics"]

        # If search aggregation is completed, proceed to next step
        if search_aggregator_state.completed:
            logger.log_debug(
                "Search aggregator marked complete. Proceeding to validation.",
                custom_dimensions=get_log_dimensions(
                    workflow_metrics,
                    decision="continue",
                    node="search_aggregator"
                )
            )
            # Check if validation is enabled in settings
            if settings.ANALYSIS_CONFIG.validate :
                # Continue to validation step
                validation_nodes = get_validation_nodes(agent_state)
                return validation_nodes if validation_nodes else "continue"
            else: return "continue"

        # Attempt retry if retries are still available
        if search_aggregator_state.is_retry_available():
            # Calculate exponential backoff delay
            delay_time = 2
            delay_time *= (search_aggregator_state.retry_count + 1) * 1.5
            await asyncio.sleep(delay_time)

            logger.log_info(
                f"Retrying search (Attempt {search_aggregator_state.retry_count + 1}/{search_aggregator_state.max_retries})",
                custom_dimensions=get_log_dimensions(
                    workflow_metrics,
                    decision="retry",
                    node="search_aggregator",
                    next_attempt=search_aggregator_state.retry_count + 1
                )
            )
            # Route back to search nodes for retry
            search_nodes = get_search_nodes(agent_state)
            return search_nodes if search_nodes else "end"

        # Maximum retries exceeded - end the workflow
        logger.log_error(
            f"Max search retries ({search_aggregator_state.max_retries}) exceeded. Ending workflow.",
            custom_dimensions=get_log_dimensions(
                workflow_metrics,
                decision="end",
                node="search_aggregator",
                final_retry_count=search_aggregator_state.retry_count,
                max_retries_exceeded=True
            )
        )
        return "end"

    return node, router
