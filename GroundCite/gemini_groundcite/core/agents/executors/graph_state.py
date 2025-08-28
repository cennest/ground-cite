"""
Graph state management for the GroundCite query analysis pipeline.

This module defines the complete state management system for the graph-based
workflow execution. It includes all data structures for tracking search results,
validation outcomes, parsing states, and workflow metrics throughout the
multi-stage analysis process.
"""

import json
import uuid
from dataclasses import dataclass, field
from typing import Annotated, Any, Dict, Optional, TypedDict, List

from ...models.citation import Citation
from ...models.search_request import SearchRequest


@dataclass
class Result:
    """
    Base class for operation results in the analysis pipeline.
    
    Provides common attributes for all types of results generated during
    the query analysis workflow, including identification and tiering.
    
    Attributes:
        id (str, optional): Unique identifier for the result
        tier (str, optional): Processing tier or priority level
    """
    id: Optional[str] = None
    tier: Optional[str] = None

@dataclass
class SearchResult(Result):
    """
    Container for web search operation results.
    
    Extends Result to include search-specific data including content,
    citations, and metadata from search operations.
    
    Attributes:
        content (str, optional): Main search result content
        citations (List[Citation], optional): Citations found in the search
        removable_citations (List[Citation], optional): Citations that can be filtered
        response_object (dict, optional): Raw response data from search API
    """
    content: Optional[str] = None
    citations: Optional[List[Citation]] = None
    removable_citations: Optional[List[Citation]] = None
    response_object: Optional[dict] = None

@dataclass
class ValidateResult(Result):
    """
    Container for content validation operation results.
    
    Stores validation outcomes including validated content, citations,
    and validation status from AI-powered verification processes.
    
    Attributes:
        content (str, optional): Validated content after verification
        citations (List[Citation], optional): Validated citations
        citations_content (str, optional): Content with citation references
        is_valid (bool): Whether the validation process succeeded
    """
    content: Optional[str] = None
    citations: Optional[List[Citation]] = None
    citations_content: Optional[str] = None
    is_valid: bool = False

@dataclass
class NodeState:
    """
    Base state tracking for individual workflow nodes.
    
    Manages execution state, error handling, and retry logic for
    individual processing nodes in the analysis pipeline.
    
    Attributes:
        completed (bool): Whether the node has completed successfully
        error (str, optional): Error message if node execution failed
        retry_count (int): Number of retry attempts made
        max_retries (int): Maximum allowed retry attempts
    """
    completed: bool = False
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

    def reset(self) -> None:
        """
        Reset the node state to initial conditions.
        
        Clears completion status, errors, and retry count to prepare
        for fresh execution.
        """
        self.completed = False
        self.error = None
        self.retry_count = 0

    def reset_for_retry(self) -> None:
        """
        Reset node state for retry attempt.
        
        Clears completion and error status while preserving retry count
        for tracking retry attempts.
        """
        self.completed = False
        self.error = None

    def is_retry_available(self) -> bool:
        """
        Check if retry attempts are still available.
        
        Returns:
            bool: True if retry count is below maximum retry limit
        """
        return self.retry_count < self.max_retries

    def increment_retry(self) -> None:
        """
        Increment the retry counter.
        
        Increases the retry count by one for tracking retry attempts.
        """
        self.retry_count += 1

    def set_error(self, error: str) -> None:
        """
        Set error state for the node.
        
        Args:
            error (str): Error message describing the failure
        """
        self.completed = False
        self.error = error


# ================================
# Parse State
# ================================

@dataclass
class ParseState(NodeState):
    """
    State management for content parsing operations.
    
    Extends NodeState to track parsing-specific data including schemas,
    parsed content, and citation processing results.
    
    Attributes:
        schema (str): JSON schema defining expected output structure
        final_content (str, optional): Main parsed content result
        parsed_citation_content (str, optional): Content with integrated citations
        parsed_citation (List[Citation], optional): Parsed citation objects
    """
    schema: str = None
    parsed_content: Optional[str] = None
    parsed_citation_content: Optional[str] = None
    parsed_citation: Optional[List[Citation]] = None

    def reset(self) -> None:
        super().reset()
        self.parsed_content = None
        self.parsed_citation_content = None
        self.parsed_citation = None

    def reset_for_retry(self) -> None:
        super().reset_for_retry()
        self.parsed_content = None
        self.parsed_citation_content = None
        self.parsed_citation = None

    def set_success(self, parsed_content: str, parsed_cited_content: str, citations: List[Citation]) -> None:
        """
        Mark parsing as successful and store results.
        
        Args:
            parsed_content (str): Successfully parsed main content
            parsed_cited_content (str): Content with citation references
            citations (List[Citation]): List of parsed citation objects
        """
        self.completed = True
        self.error = None
        self.parsed_content = parsed_content
        self.parsed_citation_content = parsed_cited_content
        self.parsed_citation = citations
 
    def has_valid_content(self) -> bool:
        """
        Check if parsing produced valid content.
        
        Returns:
            bool: True if parsed content exists and is not empty
        """
        return bool(self.parsed_content and self.parsed_content.strip())

# ================================
# Orchestration State
# ================================

@dataclass
class OrchestrationState:
    """
    Central state management for workflow orchestration.
    
    Manages the overall execution state of the analysis pipeline,
    tracking progress across different processing tiers and storing
    cumulative results from all processing stages.
    
    Attributes:
        tier_index (int): Current processing tier index (-1 = not started)
        current_tier (str, optional): Name of the current processing tier
        completed (bool): Whether the entire orchestration is complete
        search_requests (List[SearchRequest]): Generated search requests
        final_content (str): Final processed content result
        search_content (str): Raw content from search operations
        validated_content (str): Content after validation processing
        validation_response (str): Response from validation operations
        search_meta_data (str): Metadata from search operations
        search_citations (List[Citation]): Citations from search results
        validated_citations (List[Citation]): Citations after validation
    """
    tier_index: Optional[int] = -1    
    current_tier: Optional[str] = None
    completed: Optional[bool] = False

    search_requests: Optional[List[SearchRequest]] = field(default_factory=list)
    final_content: Optional[str] = ""
    search_content: Optional[str] = ""
    validated_content: Optional[str] = ""
    validation_response: Optional[str] = ""
    search_meta_data: Optional[str] = ""
    search_citations: Optional[List[Citation]] = field(default_factory=list)
    validated_citations: Optional[List[Citation]] = field(default_factory=list)

# ================================
# TypedDicts for search/Validate States
# ================================

class SearchState(TypedDict):
    """
    Type definition for search operation state.
    
    Defines the structure for tracking search operation results
    including primary and secondary search result collections.
    
    Attributes:
        results (List[Result]): Primary search results
    """
    results: List[Result]
 

class ValidationState(TypedDict):
    """
    Type definition for validation operation state.
    
    Defines the structure for tracking validation operation results
    across the analysis pipeline.
    
    Attributes:
        results (List[Result]): Collection of validation results
    """
    results: List[Result]

# ================================
# Workflow Metrics
# ================================

@dataclass
class WorkflowMetrics:
    """
    Comprehensive metrics tracking for workflow execution.
    
    Tracks execution timing, node completion, token usage, and other
    performance metrics throughout the analysis pipeline.
    
    Attributes:
        session_id (str): Unique session identifier (auto-generated)
        category (str, optional): Analysis category or type
        correlation_id (str, optional): External correlation identifier
        start_time (float, optional): Execution start timestamp
        end_time (float, optional): Execution end timestamp
        total_nodes_executed (int): Count of processing nodes executed
        token_usage (dict, optional): Token consumption by operation type
    """
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    category: Optional[str] = None
    correlation_id: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    total_nodes_executed: int = 0
    token_usage: Optional[dict] = None

    def get_execution_time(self) -> Optional[float]:
        """
        Calculate total execution time in seconds.
        
        Returns:
            float: Execution duration in seconds, or None if timing incomplete
        """
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    def assign_token_usage(self, key, token_usage):
        """
        Assign token usage data for a specific operation.
        
        Args:
            key (str): Operation identifier (e.g., 'search', 'validation', 'parsing')
            token_usage (dict): Token usage data with counts
        """
        if not token_usage:
            return

        if self.token_usage is None:
            self.token_usage = {key: [token_usage]}
        elif key not in self.token_usage:
            self.token_usage[key] = [token_usage]
        else:
            self.token_usage[key].append(token_usage)
    
    def merge_token_usage(self) -> str:
        """
        Merge and aggregate token usage across all operations.
        
        Combines token usage data from all operations into a consolidated
        summary with totals for each token type.
        
        Returns:
            str: JSON string with merged token usage data by operation
        """
        result = ''
        if self.token_usage:
            merged_token_usage = {}
            for key, token_usages in self.token_usage.items():
                # Initialize counters for all token types
                merged = {
                    "input_tokens": 0, 
                    "output_tokens": 0, 
                    "total_tokens": 0, 
                    "thoughts_tokens": 0, 
                    "tool_use_prompt_tokens": 0
                }
                # Sum up token usage across all instances of this operation
                for token_usage in token_usages:
                    for k in merged.keys():
                        merged[k] += token_usage.get(k, 0)
                merged_token_usage[key] = merged

            result = json.dumps(merged_token_usage)
        return result

# ================================
# Agent State
# ================================

def merge_state(current: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge state updates with existing state data.
    
    Intelligently combines current state with updates, avoiding duplicates
    based on result IDs and preserving existing data integrity.
    
    Args:
        current (Dict[str, Any]): Current state dictionary
        updates (Dict[str, Any]): State updates to merge
        
    Returns:
        Dict[str, Any]: Merged state dictionary with deduplicated results
    """
    if current is None:
        current = {}
    if updates is None:
        return current

    merged = current.copy()
    # Merge results arrays while avoiding duplicates based on ID
    for key in ["results"]:
        if key in current or key in updates:
            current_results = current.get(key, [])
            updates_results = updates.get(key, [])
            # Track existing IDs to prevent duplicates
            existing_ids = {r.id for r in current_results if hasattr(r, "id")}
            # Only add new results that don't already exist
            merged[key] = current_results + [
                r for r in updates_results if getattr(r, "id", None) not in existing_ids
            ]
    return merged

class AgentState(TypedDict):
    """
    Complete state definition for the AI agent workflow.
    
    Defines the comprehensive state structure that tracks all aspects
    of the query analysis pipeline execution, including orchestration,
    search, validation, parsing, and metrics.
    
    Attributes:
        orchestration_state (OrchestrationState): Central workflow coordination state
        search_aggregator_state (NodeState): Search result aggregation state
        validation_aggregator_state (NodeState): Validation result aggregation state
        parse_state (ParseState): Content parsing operation state
        search_state (SearchState): Search operation results (with merge support)
        validation_state (ValidationState): Validation operation results (with merge support)
        workflow_metrics (WorkflowMetrics): Execution metrics and performance data
    
    Note:
        Search and validation states use annotated merge functions to handle
        state updates intelligently without data loss or duplication.
    """
    orchestration_state: OrchestrationState
    search_aggregator_state: NodeState
    validation_aggregator_state: NodeState
    parse_state: ParseState
    search_state: Annotated[SearchState, merge_state]
    validation_state: Annotated[ValidationState, merge_state]
    workflow_metrics: WorkflowMetrics
