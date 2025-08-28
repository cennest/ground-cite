"""
Validation Aggregator Node for coordinating content validation in the analysis pipeline.

This module provides functionality to aggregate validation results and determine 
the next workflow step based on validation completion status and retry logic.
"""

import asyncio
from typing import Any, Dict, Callable, Tuple
from .....config.logger import AppLogger
from .....config.settings import AppSettings
from ..core_helper import get_validation_nodes
from ..graph_state import AgentState, NodeState, WorkflowMetrics

def create_validation_aggregator_node(
    settings: AppSettings,
    logger: AppLogger,
    get_log_dimensions: Callable[[WorkflowMetrics, ...], Dict[str, Any]]  # type: ignore
) -> Tuple[Callable[[AgentState], dict], Callable[[AgentState], str]]:
    """
    Creates a validation aggregator node that manages validation result collection and workflow routing.
    
    Tracks validation progress across multiple search results and determines when
    validation is complete or if retries are needed.
    
    Args:
        settings: Application configuration settings
        logger: Logger instance for logging operations
        get_log_dimensions: Function to generate logging dimensions
        
    Returns:
        Tuple containing the node function and router function
    """
   
    logger.log_info("Creating validation aggregator node.")

    async def node(agent_state: AgentState) -> dict:
        """
        Main validation aggregator node function that tracks validation completion status.
        
        Monitors validation progress across all search results and determines
        when validation is complete or if additional processing is needed.
        
        Args:
            agent_state: Current state of the workflow execution
            
        Returns:
            Updated agent state
        """
        # Extract state components from agent state
        search_state = agent_state["search_state"]
        validation_state = agent_state["validation_state"]
        validation_agg:NodeState = agent_state["validation_aggregator_state"]
        metrics = agent_state["workflow_metrics"]

        # Increment node execution count for metrics tracking
        metrics.total_nodes_executed += 1

        # Reset validation aggregator state if this is a retry attempt
        if validation_agg.retry_count > 0:
            validation_agg.reset_for_retry()

        # Count completed validations and total search results
        validated_ids = {r.id for r in (validation_state.get("results") or []) if r.id}
        total_searches = len(search_state.get("results") or [])

        try:
            # Increment retry counter to track attempts
            validation_agg.increment_retry()

            # Mark as completed if all validations done or no retries left
            if len(validated_ids) == total_searches or not validation_agg.is_retry_available():
                validation_agg.completed = True

            return agent_state

        except Exception as e:
            # Handle errors by updating state and logging
            validation_agg.increment_retry()
            validation_agg.set_error(str(e))

            logger.log_error(
                f"Error in validation aggregator (Attempt {validation_agg.retry_count}/{validation_agg.max_retries})",
                exception=e,
                custom_dimensions=get_log_dimensions(
                    metrics,
                    retry_count=validation_agg.retry_count,
                    node="validation_aggregator",
                    status="error"
                )
            )
            return agent_state

    async def router(agent_state: AgentState) -> str:
        """
        Router function that determines the next workflow step based on validation completion status.
        
        Args:
            agent_state: Current state of the workflow execution
            
        Returns:
            String indicating the next workflow step ("continue", validation node, "end")
        """
        validation_agg:NodeState = agent_state["validation_aggregator_state"]
        metrics = agent_state["workflow_metrics"]

        # If validation aggregation is completed, proceed to next step
        if validation_agg.completed:
            logger.log_debug(
                "Validation aggregation complete; proceeding to parsing.",
                custom_dimensions=get_log_dimensions(
                    metrics,
                    decision="continue",
                    node="validation_aggregator",
                    status="success"
                )
            )
            return "continue"

        # Attempt retry if retries are still available
        if validation_agg.is_retry_available():
            # Calculate exponential backoff delay
            delay_time = 2
            delay_time *= (validation_agg.retry_count + 1) * 1.5
            await asyncio.sleep(delay_time)

            logger.log_info(
                f"Retrying validation (Attempt {validation_agg.retry_count + 1}/{validation_agg.max_retries})",
                custom_dimensions=get_log_dimensions(
                    metrics,
                    decision="retry",
                    node="validation_aggregator",
                    next_attempt=validation_agg.retry_count + 1
                )
            )

            # Route back to validation nodes for retry
            nodes = get_validation_nodes(agent_state)
            return nodes if nodes else "continue"

        # Maximum retries exceeded - end the workflow
        logger.log_error(
            f"Max validation retries ({validation_agg.max_retries}) exceeded; ending workflow.",
            custom_dimensions=get_log_dimensions(
                metrics,
                decision="end",
                node="validation_aggregator",
                final_retry_count=validation_agg.retry_count,
                max_retries_exceeded=True
            )
        )
        return "end"

    return node, router
