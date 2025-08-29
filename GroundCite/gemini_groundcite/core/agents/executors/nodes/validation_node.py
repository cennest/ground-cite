"""
Validation node for AI-powered content verification in the analysis pipeline.

This module implements content validation functionality that uses AI models to
assess the accuracy, relevance, and credibility of search results. It provides
citation validation and content verification capabilities.
"""

import json
from typing import Any, Dict, Callable, Tuple
from ..core_helper import *
from ..graph_state import *
from .....config.logger import AppLogger
from .....config.settings import AppSettings


def create_validation_node(
    settings: AppSettings,
    logger: AppLogger,
    get_log_dimensions: Callable[[WorkflowMetrics, ...], Dict[str, Any]]  # type: ignore
) -> Tuple[Callable[[AgentState], dict], Callable[[AgentState], str]]:
    """
    Creates a validation node that performs AI-powered content verification.
    
    Uses AI models to assess accuracy, relevance, and credibility of search results,
    providing citation validation and content verification capabilities.
    
    Args:
        settings: Application configuration settings
        logger: Logger instance for logging operations
        get_log_dimensions: Function to generate logging dimensions
        
    Returns:
        Tuple containing the node function and router function
    """

    logger.log_info("Creating validation node.")

    async def node(agent_state: AgentState) -> dict:
        """
        Main validation node function that performs AI-powered content verification.
        
        Validates search results through AI analysis, filters citations based on credibility,
        and returns verified content with validated citations.
        
        Args:
            agent_state: Current state of the workflow execution
            
        Returns:
            Dictionary containing validation results or empty results on failure
        """
        from ...clients.google_gen_ai_client import GoogleGenAI

        total_token_usage = {}
        
        # Extract state components from agent state
        validation_agg_state:NodeState = agent_state["validation_aggregator_state"]
        workflow_metrics = agent_state["workflow_metrics"]
        request:SearchResult = agent_state["current_validation_request"]

        # Increment node execution count for metrics tracking
        workflow_metrics.total_nodes_executed += 1
        default_response = {"validation_state": {"results": []}}

        try:
            logger.log_debug(
                f"Validating response {request.id} (Attempt {validation_agg_state.retry_count + 1}/{validation_agg_state.max_retries})",
                custom_dimensions=get_log_dimensions(
                    workflow_metrics,
                    retry_count=validation_agg_state.retry_count,
                    node="validation"
                )
            )

            async def on_progress(completed, total):
                """Progress callback function for tracking validation completion."""
                logger.log_debug(
                    f"Validation Completed: {completed}/{total}",
                    custom_dimensions=get_log_dimensions(
                        workflow_metrics
                    )
                )
            
            # TODO: Move the retry logic to validation aggregator    
            async def make_validation(idx: int, item: Tuple[str, List[Citation]], ai_client: GoogleGenAI) -> Tuple[dict, List[Citation], List[Citation]]:
                """
                Performs validation for a single citation group with retry logic.
                
                Args:
                    idx: Index of the item being validated
                    item: Tuple containing URL and citation list
                    ai_client: Google GenAI client for validation
                    
                Returns:
                    Tuple containing validation response, filtered citations, and removable citations
                """
                key, value = item
                max_retries = 2
                
                # Attempt validation with retry logic
                for attempt in range(max_retries + 1):  # 0, 1, 2 (total of 3 attempts)
                    # Perform AI-powered validation of citations
                    validated_response = await ai_client.validate_search(
                        citations=value,
                        **settings.AI_CONFIG.validate_gemini_params
                    )
                    json_response = to_json_string(validated_response["response"])

                    # Record token usage for metrics
                    workflow_metrics.assign_token_usage("validation", validated_response["token_usage"])
                    
                    # Handle empty validation response
                    if not json_response:
                        if attempt == max_retries:
                            # Last attempt failed, return with empty results
                            default_token_usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
                            res = {"response": "", "token_usage": validated_response.get("token_usage", default_token_usage) if validated_response else default_token_usage}
                            return res, [], value
                        continue
                    
                    # Filter citations based on AI validation verdicts
                    is_valid, filtered_citations, removable_citations = filter_citations_by_verdicts(
                        verdict_payload_json=json_response,
                        citations=value,
                        removable_citations=[]
                    )
                    
                    if is_valid:
                        # Success, return the results
                        return validated_response, filtered_citations, removable_citations
                    
                    # is_valid is False, retry if we haven't reached max attempts
                    if attempt < max_retries:
                        logger.log_error(
                            message=f"Validation failed for item {idx}, attempt {attempt + 1}/{max_retries + 1}. Retrying...", 
                            custom_dimensions=get_log_dimensions(
                                workflow_metrics,
                                node="validation",
                                retry_count=validation_agg_state.retry_count,
                                token_usage=json.dumps(validated_response["token_usage"])
                            )
                        )
                        continue
                    else:
                        # Max retries reached and still not valid
                        logger.log_error(
                            message=f"Validation failed for item {idx} after {max_retries + 1} attempts.",
                            custom_dimensions=get_log_dimensions(
                                workflow_metrics,
                                node="validation",
                                retry_count=validation_agg_state.retry_count,
                                token_usage=json.dumps(validated_response["token_usage"])
                            )
                        )
                        return validated_response, filtered_citations, removable_citations
        
            # Group citations by their original source links for validation
            grouped = group_citations_by_original_link(request.citations)
            grouped_items = list(grouped.items())

            # Configure AI model and API key for validation
            model_id = settings.AI_CONFIG.validate_model_name 
            # Use primary key for first attempt, secondary for retries
            api_key = (
                settings.AI_CONFIG.gemini_ai_key_primary
                if validation_agg_state.retry_count == 0
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
                    retry_count=validation_agg_state.retry_count
                )
            )

            # Initialize Google GenAI client for validation operations
            ai_client = GoogleGenAI(api_key=api_key, default_model_id=model_id)

            # Execute concurrent validation tasks for all citation groups
            _results = await aexec(
                grouped_items,
                make_validation,
                max_concurrent_tasks=20,
                on_progress=on_progress,
                ai_client=ai_client
            )
            # Filter out None results and task errors
            results = [r for r in _results if r is not None and not isinstance(r, TaskError)]

            # Initialize result aggregation variables
            text_with_citations = None
            validated_response = ""
            token_usages: List[dict] = []
            filtered_citations: List[Citation] = []
            removable_citations: List[Citation] = []

            # Aggregate results from all validation tasks
            for first, second, third in results:
                validated_response += f"\n{first['response']}"
                token_usages.append(first["token_usage"])
                filtered_citations.extend(second)
                removable_citations.extend(third)

            # Merge all token usage metrics into total counts
            for usage in token_usages:
                for k, token_count in usage.items():
                    token_count = token_count or 0
                    total_token_usage[k] = total_token_usage.get(k, 0) + token_count

            # Process citations and create final validated content
            if filtered_citations:
                # Remove duplicates from removable citations
                reference_texts = {citation.text for citation in filtered_citations}
                removable_citations = [citation for citation in removable_citations if citation.text not in reference_texts]

                # Add inline citations to content and remove invalid content
                text_with_citations = add_inline_citations(request.content, filtered_citations)
                text_with_citations = remove_content_by_citations(removable_citations, text_with_citations)

            # Unmask URLs if parsing is disabled
            if not settings.ANALYSIS_CONFIG.parse:
                url_map = get_url_map(filtered_citations)
                if url_map:
                    text_with_citations = unmask_urls(text_with_citations, url_map)
    
            # Create structured validation result object
            result = ValidateResult(
                id=request.id,
                is_valid=True,
                citations=filtered_citations,
                citations_content=text_with_citations,
                content=validated_response
            )
            
            logger.log_debug(
                f"Validation completed successfully: {request.id}",
                custom_dimensions=get_log_dimensions(
                    workflow_metrics,
                    node="validation",
                    status="success",
                    token_usage=json.dumps(total_token_usage)
                )
            )

            # Return successful validation results
            return {"validation_state": {"results": [result]}}

        except Exception as e:
            # Handle validation errors by logging and returning empty results
            logger.log_error(
                f"Validation failed (Attempt {validation_agg_state.retry_count + 1}/{validation_agg_state.max_retries})",
                exception=e,
                custom_dimensions=get_log_dimensions(
                    workflow_metrics,
                    retry_count=validation_agg_state.retry_count,
                    node="validation",
                    status="error",
                    token_usage=json.dumps(total_token_usage)
                )
            )
            return default_response

    return node
