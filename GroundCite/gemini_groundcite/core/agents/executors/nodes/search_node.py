"""
Search node for performing web search operations in the analysis pipeline.

This module implements the search functionality that gathers relevant information
from the web using Google Search integration with Gemini AI. It processes search
requests and returns structured search results with citations.
"""

import json
from typing import Any, Dict, Callable, Tuple

from ..core_helper import add_inline_citations, extract_citations, filter_citations_by_filters, get_url_map, remove_content_by_citations, unmask_urls, update_citations
from ...clients.google_gen_ai_client import GoogleGenAI
from .....config.logger import AppLogger
from .....config.settings import AppSettings
from ..graph_state import AgentState, NodeState, WorkflowMetrics, SearchResult
from ....models import SearchRequest


def create_search_node(
    settings: AppSettings,
    logger: AppLogger,
    get_log_dimensions: Callable[[WorkflowMetrics, ...], Dict[str, Any]]  # type: ignore
) -> Tuple[Callable[[AgentState], dict], Callable[[AgentState], str]]:
    """
    Creates a search node that performs web search operations using Google Search with Gemini AI.
    
    Processes search requests and returns structured search results with filtered citations
    based on included/excluded site configurations.
    
    Args:
        settings: Application configuration settings
        logger: Logger instance for logging operations
        get_log_dimensions: Function to generate logging dimensions
        
    Returns:
        Tuple containing the node function and router function
    """

    logger.log_info("Creating search node.")

    async def node(agent_state: AgentState) -> dict:
        """
        Main search node function that performs web search operations using Google Search.
        
        Executes search requests through Gemini AI, processes citations, applies site filters,
        and returns structured search results with proper content formatting.
        
        Args:
            agent_state: Current state of the workflow execution
            
        Returns:
            Dictionary containing search results or empty results on failure
        """
        token_usage = {}
        
        # Extract state components from agent state
        search_aggregator_state:NodeState = agent_state["search_aggregator_state"]
        workflow_metrics = agent_state["workflow_metrics"]
        request:SearchRequest = agent_state["current_search_request"]

        # Increment node execution count for metrics tracking
        workflow_metrics.total_nodes_executed += 1
        default_response = {"search_state": {"results": []}}

        try:
            logger.log_debug(
                f"Attempting Google search {request.id} (Attempt {search_aggregator_state.retry_count + 1}/{search_aggregator_state.max_retries})",
                custom_dimensions=get_log_dimensions(
                    workflow_metrics,
                    retry_count=search_aggregator_state.retry_count,
                    node="search"
                )
            )

            # Configure AI model and API key for search
            model_id = settings.AI_CONFIG.search_model_name
            # Use primary key for first attempt, secondary for retries
            api_key = (
                settings.AI_CONFIG.gemini_ai_key_primary
                if search_aggregator_state.retry_count == 0
                else (
                    settings.AI_CONFIG.gemini_ai_key_secondary
                    or settings.AI_CONFIG.gemini_ai_key_primary
                )
            )

            logger.log_debug(
                f"Using model {model_id} with {'primary' if api_key == settings.AI_CONFIG.gemini_ai_key_primary else 'secondary'} API key",
                custom_dimensions=get_log_dimensions(
                    workflow_metrics,
                    model=model_id,
                    retry_count=search_aggregator_state.retry_count
                )
            )

            # Initialize Google GenAI client for search operations
            ai_client = GoogleGenAI(api_key=api_key, default_model_id=model_id)

            # Parse excluded sites from configuration
            excluded_sites = [
                site.strip()
                for site in settings.ANALYSIS_CONFIG.excluded_sites.split(",")
                if site.strip()
            ]

            # Parse included sites from configuration
            included_sites = [
                site.strip()
                for site in settings.ANALYSIS_CONFIG.included_sites.split(",")
                if site.strip()
            ]

            # Execute the search request through Gemini AI
            response = await ai_client.search(
                prompt=request.user_prompt,
                system_prompt=request.system_prompt,
                **settings.AI_CONFIG.search_gemini_params
            )

            # Extract and process search response components
            response_object = response["response_object"]
            filtered_citations =  await update_citations(extract_citations(response_object), placeholder_part=request.id)
            content = response_object.text
            removable_citations = []

            # Apply site filters to citations if configured
            if excluded_sites or included_sites:
                filtered_citations,removable_citations = filter_citations_by_filters(filtered_citations, excluded_sites, included_sites, removable_citations)    

            # Add inline citations if validation is disabled
            if not settings.ANALYSIS_CONFIG.validate:
                content = add_inline_citations(content, filtered_citations)
                content = remove_content_by_citations(removable_citations, content)

            # Unmask URLs if neither validation nor parsing is enabled
            if not settings.ANALYSIS_CONFIG.validate and not settings.ANALYSIS_CONFIG.parse:    
                url_map = get_url_map(filtered_citations)
                if url_map:
                    content = unmask_urls(content, url_map)
            
            # Extract and record token usage metrics
            token_usage = response.get("token_usage", None)
            if token_usage:
                workflow_metrics.assign_token_usage("search", token_usage)

            # Validate search response and content quality
            if response is None:
                raise ValueError("Empty response object received from Google search")

            original_text = content or ""
            if not original_text.strip():
                raise ValueError("Empty response content received from Google search")

            if not filtered_citations:
                raise ValueError("Empty citation received from Google search")

            # Create structured search result object
            result = SearchResult(
                id=request.id,
                content=content,
                citations=filtered_citations,
                removable_citations=removable_citations,
                response_object=response_object
            )

            logger.log_debug(
                f"Search completed successfully: {request.id}",
                custom_dimensions=get_log_dimensions(
                    workflow_metrics,
                    node="search",
                    status="success",
                    token_usage=json.dumps(token_usage)
                )
            )
 
            # Return successful search results
            return {"search_state": {"results": [result]}}

        except Exception as e:
            # Handle search errors by logging and returning empty results
            logger.log_error(
                f"Error in Google search (Attempt {search_aggregator_state.retry_count + 1}/{search_aggregator_state.max_retries})",
                exception=e,
                custom_dimensions=get_log_dimensions(
                    workflow_metrics,
                    retry_count=search_aggregator_state.retry_count,
                    node="search",
                    status="error",
                    token_usage=json.dumps(token_usage)
                )
            )
            return default_response

    return node
