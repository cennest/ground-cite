"""
Parse node for structured data extraction in the analysis pipeline.

This module implements content parsing functionality that transforms unstructured
search results into structured JSON data using predefined schemas. It supports
both OpenAI and Gemini AI models for parsing operations.
"""

import json
from typing import Any, Dict, Callable

from ...clients.google_gen_ai_client import GoogleGenAI
from ..core_helper import *
from ..graph_state import *
from .....config.logger import AppLogger
from .....config.settings import AppSettings
from ...clients.open_ai_client import OpenAIClient


def create_parsing_node(
    settings: AppSettings,
    logger: AppLogger,
    get_log_dimensions: Callable[[WorkflowMetrics, ...], Dict[str, Any]]
) -> Callable[[AgentState], dict]:
    """
    Creates a parsing node that transforms unstructured content into structured JSON data.
    
    Args:
        settings: Application configuration settings
        logger: Logger instance for logging operations
        get_log_dimensions: Function to generate logging dimensions
        
    Returns:
        Tuple containing the node function and router function
    """

    logger.log_info("Creating parsing node.")

    async def node(agent_state: AgentState) -> dict:
        """
        Main parsing node function that converts unstructured content to structured JSON.
        
        Processes search results or validation results through AI models (OpenAI/Gemini)
        to extract structured data according to predefined schemas.
        
        Args:
            agent_state: Current state of the workflow execution
            
        Returns:
            Updated agent state with parsing results
        """
        token_usage = {}

        # Extract state components from agent state
        search_state = agent_state["search_state"]
        validation_state = agent_state["validation_state"]
        parse_state = agent_state["parse_state"]
        workflow_metrics = agent_state["workflow_metrics"]

        # Increment node execution count for metrics tracking
        workflow_metrics.total_nodes_executed += 1

        # Reset parse state if this is a retry attempt
        if parse_state.retry_count > 0:
            parse_state.reset_for_retry()

        try:
            logger.log_debug(
                f"Parsing response (Attempt {parse_state.retry_count + 1}/{parse_state.max_retries})",
                custom_dimensions=get_log_dimensions(
                    workflow_metrics,
                    retry_count=parse_state.retry_count,
                    node="parse"
                )
            )
            
            # Prepare content for parsing based on validation settings
            cited_content = ""
            citations = []
            if settings.ANALYSIS_CONFIG.validate: 
                # Use validated content with citations
                cited_content = "\n\n".join([
                    r.citations_content for r in validation_state["results"] if r.citations_content
                ])
                citations = [c for r in validation_state["results"] for c in r.citations]
            else:
                # Use raw search results content
                cited_content = "\n\n".join([
                    r.content for r in search_state["results"] if r.content
                ])
                citations = [c for r in search_state["results"] for c in r.citations]
    
            # Create URL mapping for citation handling
            url_map = get_url_map(citations)

            # Configure AI model for parsing
            model_id = settings.AI_CONFIG.parse_model_name 
           
            # Initialize AI client based on configured provider
            config = {}
            if settings.AI_CONFIG.parsing_provider == 'gemini':
                # Use primary key for first attempt, secondary for retries
                api_key = (
                    settings.AI_CONFIG.gemini_ai_key_primary
                    if parse_state.retry_count == 0
                    else (
                        settings.AI_CONFIG.gemini_ai_key_secondary
                        or settings.AI_CONFIG.gemini_ai_key_primary
                    )
                )
                ai_client = GoogleGenAI(api_key=api_key, default_model_id=model_id)
                config = settings.AI_CONFIG.parsing_gemini_params

                logger.log_debug(
                f"Using model {model_id} with {'primary' if api_key == settings.AI_CONFIG.gemini_ai_key_primary else 'secondary'} API key",
                custom_dimensions=get_log_dimensions(
                    workflow_metrics,
                    model=model_id,
                    retry_count=parse_state.retry_count
                ))
            else:
                # Use OpenAI client configuration
                api_key = settings.AI_CONFIG.open_ai_key                                
                ai_client = OpenAIClient(api_key=api_key, default_model_id=model_id)
                config = settings.AI_CONFIG.parsing_openai_params

                logger.log_debug(
                f"Using model {model_id} with primary API key",
                custom_dimensions=get_log_dimensions(
                    workflow_metrics,
                    model=model_id,
                    retry_count=parse_state.retry_count
                ))              


            # Generate structured output using AI client
            ai_response = await ai_client.parse_content(
                content=cited_content,
                schema=parse_state.schema,
                **config
            )
            
            # Extract response data and token usage metrics
            structured_data = ai_response["response"]
            token_usage = ai_response["token_usage"]
            
            # Record token usage for workflow metrics
            if token_usage:
                workflow_metrics.assign_token_usage("parse", token_usage)

            # Restore original URLs from masked citations
            if url_map:
                structured_data = unmask_urls(structured_data, url_map)

            # Validate that structured output is not empty
            if not structured_data or not structured_data.strip():
                parse_state.increment_retry()
                parse_state.set_error("Empty structured output received")

                logger.log_warning(
                    f"Empty structured output (Attempt {parse_state.retry_count}/{parse_state.max_retries})",
                    custom_dimensions=get_log_dimensions(
                        workflow_metrics,
                        parse_retry_count=parse_state.retry_count,
                        node="parse",
                        issue="empty_output",
                        token_usage=json.dumps(token_usage)
                    )
                )
                return agent_state

            # Success - store the successfully parsed output
            parse_state.set_success(
                citations=citations,
                parsed_cited_content=cited_content,
                parsed_content=structured_data
            )

            logger.log_debug(
                "Parsing completed successfully",
                custom_dimensions=get_log_dimensions(
                    workflow_metrics,
                    final_retry_count=parse_state.retry_count,
                    node="parse",
                    status="success",
                    token_usage=json.dumps(token_usage)
                )
            )

            return agent_state

        except Exception as e:
            # Handle parsing errors by updating state and logging
            parse_state.increment_retry()
            parse_state.set_error(str(e))

            logger.log_error(
                f"Error in parsing response (Attempt {parse_state.retry_count}/{parse_state.max_retries})",
                exception=e,
                custom_dimensions=get_log_dimensions(
                    workflow_metrics,
                    parse_retry_count=parse_state.retry_count,
                    node="parse",
                    status="error",
                    token_usage=json.dumps(token_usage)
                )
            )
            return agent_state

    async def router(agent_state: AgentState) -> str:
        """
        Router function that determines the next workflow step based on parsing completion status.
        
        Args:
            agent_state: Current state of the workflow execution
            
        Returns:
            String indicating the next workflow step ("continue", "retry", "end")
        """
        parse_state = agent_state["parse_state"]
        workflow_metrics = agent_state["workflow_metrics"]

        # If parsing completed successfully, continue workflow
        if parse_state.completed and parse_state.has_valid_content():
            logger.log_debug(
                "Parsing successful, continuing workflow",
                custom_dimensions=get_log_dimensions(
                    workflow_metrics,
                    decision="continue",
                    node="parse",
                    status="success"
                )
            )
            return "continue"

        # Attempt retry if retries are still available
        if parse_state.is_retry_available():
            # Calculate exponential backoff delay
            delay_time = 2
            delay_time *= (parse_state.retry_count + 1) * 1.5
            await asyncio.sleep(delay_time)

            logger.log_debug(
                f"Retrying parsing (Attempt {parse_state.retry_count + 1}/{parse_state.max_retries})",
                custom_dimensions=get_log_dimensions(
                    workflow_metrics,
                    decision="retry",
                    node="parse",
                    next_attempt=parse_state.retry_count + 1
                )
            )
            return "retry"

        # Maximum retries exceeded - end the workflow
        logger.log_error(
            f"Max parsing retries ({parse_state.max_retries}) exceeded. Ending with failed state.",
            custom_dimensions=get_log_dimensions(
                workflow_metrics,
                decision="end",
                node="parse",
                final_retry_count=parse_state.retry_count,
                max_retries_exceeded=True
            )
        )
        return "end"

    return node, router
