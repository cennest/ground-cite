"""
Core helper utilities for the GroundCite graph execution framework.

This module provides essential utilities for asynchronous task execution,
error handling, data processing, and citation management within the
graph-based query analysis pipeline.
"""

import asyncio
from collections import defaultdict
import inspect
import json
import re
from typing import Dict, Tuple, Union, List, Callable, TypeVar, Awaitable, Any, Optional, AsyncIterable
import httpx
from langgraph.constants import Send
from ...models.citation import Citation, Segments

# Type variables for generic async execution functions
S = TypeVar("S")  # Source type for async collections
T = TypeVar("T")  # Target type for async execution results


class TaskError(Exception):
    """
    Custom exception for async task execution failures.
    
    Provides detailed error information including the task index,
    original item, and underlying exception for debugging and
    error recovery in concurrent operations.
    
    Attributes:
        index (int): Index of the failed task in the execution batch
        item (Any): Original item that caused the failure
        original_exception (Exception): Underlying exception that caused the failure
    """
    def __init__(self, index: int, item: Any, exc: Exception):
        self.index = index
        self.item = item
        self.original_exception = exc
        super().__init__(str(exc))
    
    def to_dict(self):
        return {
            "index": self.index,
            "error": str(self.original_exception)
        }


async def aexec(
    collection: Union[S, List[S], AsyncIterable[S]],
    exec: Callable[..., Awaitable[T]],
    max_concurrent_tasks: int = 5,
    timeout_per_task: Optional[float] = None,
    fail_fast: bool = False,
    on_progress: Optional[Callable[..., Awaitable[None]]] = None,
    on_tick: Optional[Callable[[int, int], Awaitable[None]]] = None,
    tick_interval: float = 1.0,
    **injectables: Any,
) -> Union[T, List[T]]:
    """
    Execute async functions concurrently with progress tracking and error handling.
    
    Provides a robust framework for running async tasks in parallel with configurable
    concurrency limits, timeout handling, progress callbacks, and flexible parameter injection.
    
    Args:
        collection: Items to process (single item, list, or async iterable)
        exec: Async function to execute on each item
        max_concurrent_tasks: Maximum number of concurrent tasks (default: 5)
        timeout_per_task: Optional timeout per task in seconds
        fail_fast: If True, stop on first error; if False, collect errors as TaskError
        on_progress: Optional progress callback function
        on_tick: Optional periodic tick callback function
        tick_interval: Interval for tick callbacks in seconds (default: 1.0)
        **injectables: Additional parameters to inject into exec function
        
    Returns:
        Single result if input was single item, otherwise list of results/TaskErrors
    """
    # Normalize input to list and determine if single item processing
    is_single_item = not isinstance(collection, (list, AsyncIterable))
    items = [collection] if is_single_item else (
        collection if isinstance(collection, list) else [item async for item in collection]
    )

    # Initialize concurrency control and result tracking
    total_items = len(items)
    semaphore = asyncio.Semaphore(max_concurrent_tasks)
    results = [None] * total_items
    counter = {"value": 0}
    done_counter = {"value": 0}
    lock = asyncio.Lock()

    # Analyze function signatures for dynamic parameter injection
    exec_param_names = set(inspect.signature(exec).parameters)
    progress_param_names = set(inspect.signature(on_progress).parameters) if on_progress else set()

    def build_dynamic_args(param_names: set, available_params: dict) -> dict:
        """Build dynamic arguments based on function signature"""
        return {key: value for key, value in available_params.items() if key in param_names}

    async def tick_worker():
        while True:
            await asyncio.sleep(tick_interval)
            async with lock:
                if on_tick:
                    await on_tick(done_counter["value"], total_items)
                if done_counter["value"] >= total_items:
                    break

    async def worker(item: S, idx: int):
        async with semaphore:
            async with lock:
                order = counter["value"] = counter["value"] + 1

            # Build available parameters for exec function
            available_params = {
                "item": item,
                "idx": idx,
                "order": order,
                **injectables
            }
            
            exec_args = build_dynamic_args(exec_param_names, available_params)
            
            result = None
            error = None
            
            try:
                result = await asyncio.wait_for(exec(**exec_args), timeout=timeout_per_task) if timeout_per_task else await exec(**exec_args)
            except Exception as e:
                error = e
                if fail_fast:
                    raise
                result = TaskError(idx, item, e)

            async with lock:
                done_counter["value"] += 1
                if on_progress:
                    # Build available parameters for progress callback
                    progress_available_params = {
                        "completed": done_counter["value"],
                        "total": total_items,
                        "item": item,
                        "idx": idx,
                        "order": order,
                        "result": result,
                        "error": error,
                        **injectables
                    }
                    
                    progress_args = build_dynamic_args(progress_param_names, progress_available_params)
                    
                    # Handle legacy positional calling (completed, total)
                    if not progress_args:
                        await on_progress(done_counter["value"], total_items)
                    else:
                        await on_progress(**progress_args)

            results[idx] = result

    tasks = [asyncio.create_task(worker(item, idx)) for idx, item in enumerate(items)]
    tick_task = asyncio.create_task(tick_worker()) if on_tick else None

    await asyncio.gather(*tasks)
    if tick_task:
        await tick_task

    return results[0] if is_single_item else results


# Generate alphabetical IDs for search requests (A, B, C, ..., AA, AB, etc.)
def get_alpha_id(idx):
    """
    Generate alphabetical identifiers for search requests in sequence.
    
    Converts numeric indices to alphabetical format: 0->A, 1->B, ..., 25->Z, 26->AA, etc.
    
    Args:
        idx: Numeric index to convert
        
    Returns:
        String alphabetical identifier
    """
    result = ""
    while True:
        idx, rem = divmod(idx, 26)
        result = chr(ord('A') + rem) + result
        if idx == 0:
            break
        idx -= 1
    return result

def create_domain_validator(url, require_https=False, include_subdomain=True):
    """
    Creates a domain validator function from a given URL.
    Args:
        url (str): The reference URL to extract domain from
        require_https (bool): If True, only allow HTTPS URLs. Default is False.
        include_subdomain (bool): If True, allow subdomains. Default is True.
    Returns:
        function: A validator function that checks if other URLs match the domain
    """
    from urllib.parse import urlparse
    
    def normalize_url(url_str):
        """Add scheme if missing for proper parsing"""
        if not url_str.startswith(('http://', 'https://')):
            url_str = 'https://' + url_str
        return url_str
    
    # Normalize and parse the reference URL
    normalized_url = normalize_url(url)
    parsed_url = urlparse(normalized_url)
    reference_domain = parsed_url.netloc.lower()
    
    # Create a wildcard pattern: remove the first subdomain level
    # Example: "dub.abc.com.br" -> "abc.com.br"
    #          "ai.google.dev" -> "google.dev"
    #          "google.com" -> "google.com"
    domain_parts = reference_domain.split('.')
    if len(domain_parts) > 2:
        # Remove first part (subdomain) to get the base domain
        base_domain = '.'.join(domain_parts[1:])
    else:
        # If only 2 parts or less, use the full domain
        base_domain = reference_domain
    
    def domain_validator(check_url):
        """
        Validate if the given URL matches the reference domain.
        
        Args:
            check_url (str): URL to validate against reference domain
            
        Returns:
            bool: True if domains match and requirements are met, False otherwise
            
        Validation Rules:
        - Exact domain match always returns True
        - Subdomain matching based on include_subdomain flag
        - HTTPS requirement based on require_https flag
        - Handles URL normalization and parsing errors
        """
        try:
            # Normalize the URL to check
            normalized_check_url = normalize_url(check_url)
            check_parsed = urlparse(normalized_check_url)
            check_domain = check_parsed.netloc.lower()
            check_scheme = check_parsed.scheme.lower()
            
            # Check HTTPS requirement if enabled
            if require_https and check_scheme != 'https':
                return False
            
            # Check if it's the exact same domain as reference
            if check_domain == reference_domain:
                return True
            
             # If subdomain inclusion is enabled, check for subdomain matches
            if include_subdomain:
                # Check if it ends with the base domain (allowing any subdomains)
                if check_domain.endswith('.' + base_domain):
                    return True
            
            # Check if it's the base domain itself
            if check_domain == base_domain:
                return True
            
            return False
            
        except Exception:
            return False  # Changed from True to False for safer default
    
    return domain_validator, reference_domain if not include_subdomain else base_domain


def to_serializable(obj):
    """
    Convert complex objects to JSON-serializable format recursively.
    
    Handles various object types including dataclasses, objects with __dict__,
    objects with to_dict methods, and nested collections.
    
    Args:
        obj: Object to convert to serializable format
        
    Returns:
        JSON-serializable representation of the object
    """
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    elif isinstance(obj, list):
        return [to_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: to_serializable(value) for key, value in obj.items()}
    elif hasattr(obj, '__dict__'):  # For objects like GroundingChunk, etc.
        return to_serializable(vars(obj))
    elif hasattr(obj, 'to_dict'):
        return to_serializable(obj.to_dict())
    else:
        return str(obj)  # Fallback: represent unknown object as string 


def get_search_nodes(agent_state:Any):
    """
    Create search node tasks for pending search requests.
    
    Generates LangGraph Send objects for search requests that haven't been processed yet,
    comparing orchestration requests with existing search results.
    
    Args:
        agent_state: Current workflow state containing orchestration and search data
        
    Returns:
        List of Send objects for unprocessed search requests
    """
    
    orchestration_state = agent_state["orchestration_state"]
    search_state = agent_state["search_state"]

    # Find search requests that haven't been processed yet
    existing_ids = {r.id for r in (search_state["results"] or []) if r.id}
    search_requests = [req for req in (orchestration_state.search_requests or []) if req.id not in existing_ids]
    
    # Create Send objects for unprocessed search requests
    search_nodes = [
        Send("search_node", {**agent_state, "current_search_request": req})
        for req in search_requests
    ]

    return search_nodes    



def get_validation_nodes(agent_state:Any):
    """
    Create validation node tasks for pending search result validations.
    
    Generates LangGraph Send objects for search results that haven't been validated yet,
    comparing search results with existing validation results.
    
    Args:
        agent_state: Current workflow state containing search and validation data
        
    Returns:
        List of Send objects for unvalidated search results
    """
    search_state = agent_state["search_state"]
    validation_state = agent_state["validation_state"]

    # Find search results that haven't been validated yet
    existing_ids = {r.id for r in (validation_state["results"] or []) if r.id}
    search_results = [res for res in (search_state["results"] or []) if res.id not in existing_ids]
    
    # Create Send objects for unvalidated search results
    validation_nodes = [
        Send("validation_node", {**agent_state, "current_validation_request": req})
        for req in search_results
    ]
    
    return validation_nodes


def get_grounding_metadata(results) -> str:
    """
    Extract and return serialized grounding metadata from a list of results.
    Returns a newline-separated string or an empty string if none exist.
    """
    if not results:
        return ""

    metadata_parts = []
    for result in results:
        response = result.response_object
        raw_metadata = (
            response.candidates[0].grounding_metadata
            if getattr(response, "candidates", None)
            and response.candidates
            and hasattr(response.candidates[0], "grounding_metadata")
            else None
        )
        grounding_metadata = to_serializable(raw_metadata)
        if grounding_metadata:
            metadata_parts.append(str(grounding_metadata))

    return "\n".join(metadata_parts)


def get_url_map(citations) -> Dict[str, str]:
    """
    Create a mapping from citation placeholders to formatted links.
    
    Extracts placeholder-to-URL mappings from citation segments for URL unmasking.
    
    Args:
        citations: List of Citation objects containing segments with placeholders
        
    Returns:
        Dictionary mapping placeholders to formatted links
    """
    return {
        segment.placeholder: segment.get_formated_link()
        for citation in citations
        for segment in citation.segments
    }

def extract_unique_citations(citations: list) -> list[dict[str, Any]]:
    """
    Extract unique citations with chunk indices and URLs.
    
    Processes citation list to create unique citation entries based on chunk_index,
    avoiding duplicates while preserving URL information.
    
    Args:
        citations: List of Citation objects with segments
        
    Returns:
        List of dictionaries containing unique chunk_index and url pairs
    """
    seen = set()
    unique_citations: list[dict[str, Any]] = []

    for citation in citations:
        segments = getattr(citation, "segments", None)
        if not segments:
            continue

        for seg in segments:
            chunk_index = getattr(seg, "chunk_index", None)
            url = getattr(seg, "original_link", None) or getattr(seg, "link", None)
            if chunk_index is not None and chunk_index not in seen:
                seen.add(chunk_index)
                unique_citations.append({
                    "chunk_index": chunk_index,
                    "url": url
                })

    return unique_citations


def unmask_urls(text: str, url_map: Dict[str, str]) -> str:
    """
    Replace URL placeholders in text with actual URLs.
    
    Processes text to replace citation placeholders with their corresponding URLs
    using the provided URL mapping dictionary.
    
    Args:
        text: Text containing URL placeholders
        url_map: Dictionary mapping placeholders to actual URLs
        
    Returns:
        Text with placeholders replaced by actual URLs
    """
    for ph in sorted(url_map, key=len, reverse=True):
        text = text.replace(ph, url_map[ph])
    return text


def extract_citations(response) -> List[Citation]:
    """
    Extract citations from Gemini response grounding metadata
    
    Args:
        response: Gemini API response object
        
    Returns:
        List of Citation objects
    """
    citations = []
    
    try:
        if not hasattr(response, 'candidates') or not response.candidates:
            return citations
            
        candidate = response.candidates[0]
        if not hasattr(candidate, 'grounding_metadata') or not candidate.grounding_metadata:
            return citations
            
        grounding_metadata = candidate.grounding_metadata
        if not hasattr(grounding_metadata, 'grounding_supports'):
            return citations
            
        for support in grounding_metadata.grounding_supports or []:
            try:
                if not hasattr(support, "segment") or support.segment is None:
                    continue  # Skip this support if segment info is missing  
                
                start_index = (
                    support.segment.start_index
                    if support.segment.start_index is not None
                    else 0
                )

                # Ensure end_index is present to form a valid segment
                if support.segment.end_index is None:
                    continue  # Skip if end_index is missing, as it's crucial

                end_index = support.segment.end_index        
                confidence_scores = getattr(support, 'confidence_scores', [])
                segments = []
                citation = Citation(
                        score=float(confidence_scores[0] if confidence_scores else 0.0),
                        start_index=int(start_index),
                        end_index=int(end_index),
                        text=support.segment.text if hasattr(support.segment, 'text') else None,
                        segments=segments
                    )
                citations.append(citation)
                
                if hasattr(support, "grounding_chunk_indices") and support.grounding_chunk_indices:
                    for chunk_index in support.grounding_chunk_indices:
                        try:
                            chunk = candidate.grounding_metadata.grounding_chunks[chunk_index]
                            segment = Segments(
                                title=(chunk.web.title.split(".")[:-1][0] if chunk.web and chunk.web.title and "." in chunk.web.title else ""),
                                chunk_index=int(chunk_index),
                                link=str(getattr(chunk.web, 'uri', '') or '')
                            )
                            segments.append(segment)    
                            
                        except (AttributeError, IndexError, TypeError, ValueError):
                            # Handle cases where chunk, web, uri, or resolved_map might be problematic
                            # For simplicity, we'll just skip adding this particular segment link
                            # In a production system, you might want to log this.
                            pass
                    citation.segments = segments    

            except (AttributeError, IndexError, TypeError, ValueError):
                continue
    except Exception:
        return citations
    
    return citations
    

def add_inline_citations(text: str, citations: List[Citation]):
    """
    Insert citation placeholders into text at appropriate positions.
    
    Processes citations in reverse order by end_index to insert placeholders
    without disrupting text indices for subsequent insertions.
    
    Args:
        text: Original text to add citations to
        citations: List of Citation objects with position and segment information
        
    Returns:
        Text with citation placeholders inserted at appropriate positions
    """
  
    # Sort citations by end_index in descending order.
    # If end_index is the same, secondary sort by start_index descending.
    # This ensures that insertions at the end of the string don't affect
    # the indices of earlier parts of the string that still need to be processed.
    sorted_citations = sorted(
        citations, key=lambda c: (c.end_index, c.start_index), reverse=True
    )

    modified_text = text
    text_encoded = modified_text.encode("utf-8")

    for citation_info in sorted_citations:
        # These indices refer to positions in the *original* text,
        # but since we iterate from the end, they remain valid for insertion
        # relative to the parts of the string already processed.
        end_idx = citation_info.end_index

        for segment in citation_info.segments:

            marker_to_insert = ""
            marker_to_insert += segment.get_placeholder()
            # Insert the citation marker at the original end_idx position
            char_end_index =  len(text_encoded[:end_idx].decode("utf-8", errors="ignore"))

            modified_text = (
                modified_text[:char_end_index] + marker_to_insert + modified_text[char_end_index:]
            )

    return modified_text


def filter_citations_by_filters(
    citations: List[Citation],
    excluded_sites: Optional[List[str]],
    included_sites: Optional[List[str]],
    removable_citations: List[Citation]
) -> Tuple[List[Citation], List[Citation]]:
    """
    Filter citations based on included and excluded site lists.
    
    Applies domain-based filtering to citations, removing segments from excluded sites
    and keeping only segments from included sites (if specified).
    
    Args:
        citations: List of Citation objects to filter
        excluded_sites: Optional list of sites to exclude
        included_sites: Optional list of sites to include (if None, includes all non-excluded)
        removable_citations: List to collect citations that become empty after filtering
        
    Returns:
        Tuple of (filtered_citations, updated_removable_citations)
    """
  
    filtered_citations = []
    
    # Create domain validators for filtering
    excluded_validators = [create_domain_validator(site)[0] for site in excluded_sites] if excluded_sites else []
    included_validators = [create_domain_validator(site)[0] for site in included_sites] if included_sites else []

    # Process each citation and its segments
    for cit in citations:
        remaining_segments = []

        for seg in cit.segments:
            if not seg.original_link:
                continue

            url = seg.original_link

            # Apply exclusion filters
            if any(ev(url) for ev in excluded_validators):
                continue

            # Apply inclusion filters (if specified)
            if included_sites:
                if not any(ev(url) for ev in included_validators):
                    continue

            # Segment passed all filtering checks
            remaining_segments.append(seg)

        # Handle citations with no remaining segments
        if not remaining_segments:
            removable_citations.append(cit)
        else:
            cit.segments = remaining_segments
            filtered_citations.append(cit)

    return filtered_citations, removable_citations


def filter_citations_by_verdicts(
    verdict_payload_json: str,
    citations: List[Citation],
    removable_citations: List[Citation]
) -> Tuple[bool, List[Citation], List[Citation]]:
    """
    Filter citations based on AI validation verdicts.
    
    Processes AI validation results to filter citations based on relevance
    and confidence scores from the validation response.
    
    Args:
        verdict_payload_json: JSON string containing validation verdicts
        citations: List of Citation objects to filter
        removable_citations: List to collect rejected citations
        
    Returns:
        Tuple of (is_valid, filtered_citations, updated_removable_citations)
    """

    # Validate and parse the verdict JSON payload
    if not verdict_payload_json:
        return False, [], citations

    try:
        verdict_payload = json.loads(verdict_payload_json)
    except json.JSONDecodeError:
        return False, [], citations
    
    verdicts = verdict_payload.get("verdicts", [])
    if not verdicts:
        return False, [], citations

    # Create mapping dictionaries for efficient lookup
    relevance_map: Dict[str, str] = {
        v.get("placeholder"): v.get("relevance", "irrelevant")
        for v in verdicts
    }
    confidence_map: Dict[str, float] = {
        v.get("placeholder"): v.get("confidence", 0.0)
        for v in verdicts
    }

    updated_citations: List[Citation] = []

    # Process each citation based on verdicts
    for cit in citations:
        # Filter segments based on relevance and confidence thresholds
        filtered_segments = [
            seg for seg in cit.segments
            if relevance_map.get(seg.placeholder) in ["relevant", "partial"] 
            and confidence_map.get(seg.placeholder, 0.0) >= 0.7
        ]

        # Handle citations with no valid segments
        if not filtered_segments:
            removable_citations.append(cit)
            continue  # Skip adding this citation

        # Keep citation with remaining valid segments
        cit.segments = filtered_segments
        updated_citations.append(cit)

    return True, updated_citations, removable_citations


def group_citations_by_original_link(citations: List[Citation]) -> Dict[Optional[str], List[Citation]]:
    """
    Group citations by original_link. For each URL group, citations only contain 
    segments that match that specific original_link.
    
    Args:
        citations: List of Citation objects
        
    Returns:
        Dictionary mapping original_link -> List of citations with only matching segments
    """
    groups = defaultdict(list)
    
    for citation in citations:
        # Group segments by their original_link
        segments_by_link = defaultdict(list)
        for segment in citation.segments:
            segments_by_link[segment.original_link].append(segment)
        
        # For each original_link, create a citation copy with only matching segments
        for original_link, matching_segments in segments_by_link.items():
            citation_copy = Citation(
                score=citation.score,
                start_index=citation.start_index,
                end_index=citation.end_index,
                text=citation.text,
                segments=matching_segments
            )
            groups[original_link].append(citation_copy)
    
    return dict(groups)

def remove_content_by_citations(citations: List[Citation], content: str) -> str:
    """
    Remove text segments from content based on citation text matches.
    
    Removes specific text segments from the content that correspond to
    the text spans identified in the citations.
    
    Args:
        citations: List of Citation objects containing text to remove
        content: Original content text
        
    Returns:
        Content with citation text segments removed
    """
    # Remove each citation's text from the content
    for cit in citations:
        if cit.text:
            content = content.replace(cit.text, "")
    
    return content.strip()


def to_json_string(raw: Any) -> str:
    """
    Clean and normalize raw data to JSON string format.
    
    Processes various input types to produce clean JSON strings by removing
    markdown code fences and ensuring proper string format.
    
    Args:
        raw: Raw data to convert to JSON string
        
    Returns:
        Clean JSON string ready for parsing
    """

    FENCE = re.compile(r"^\s*```(?:json)?\s*|\s*```$", re.I | re.M)

    # Handle list inputs by taking first element
    if isinstance(raw, list):
        raw = raw[0]

    # Remove markdown code fences from string inputs
    if isinstance(raw, str):
        raw = FENCE.sub("", raw).strip()

    # Ensure final payload is properly formatted JSON string
    if not isinstance(raw, str):
        raw = json.dumps(raw, ensure_ascii=False)  

    return raw

async def update_citations(citations: List[Citation], placeholder_part:str = "T", resolve:bool= True) -> List[Citation]:
    """
    Update citation segments with resolved links and unique placeholders.
    
    Processes citation segments to resolve redirects and assign unique placeholders
    for each segment, enabling proper citation tracking and URL resolution.
    
    Args:
        citations: List of Citation objects to update
        placeholder_part: Identifier part for placeholder generation (default: "T")
        resolve: Whether to resolve URL redirects (default: True)
        
    Returns:
        Updated list of Citation objects with resolved links and placeholders
    """

    async def process_segment(global_idx: int, segment: Segments):
        if segment.chunk_index >= 0:
            segment.placeholder = f"URL_{placeholder_part}_{global_idx}"
            segment.original_link = (await resolve_redirect(segment.link) or segment.link) if resolve else segment.link

    async def process_citation(start_idx: int, cit: Citation):
        await asyncio.gather(
            *[process_segment(start_idx + idx, seg) for idx, seg in enumerate(cit.segments)]
        )
        return cit

    # Flattened indexing to ensure global uniqueness across all segments
    idx_counter = 1
    tasks = []
    for cit in citations:
        tasks.append(process_citation(idx_counter, cit))
        idx_counter += len(cit.segments)

    await asyncio.gather(*tasks)
    return citations



async def resolve_redirect(redirect_url: str) -> str:
    try:
        REDIRECT_CODES = {301, 302, 303, 307, 308}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                redirect_url,
                follow_redirects=False,
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            
            if response.status_code in REDIRECT_CODES and 'location' in response.headers:
                return response.headers['location']
            elif response.status_code == 200:
                return str(response.url)
            else:
                return redirect_url
    except httpx.RequestError as e:
        return redirect_url





