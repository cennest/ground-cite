"""
Citation processing utilities for the GroundCite library.

This module provides comprehensive citation management including deduplication,
URL canonicalization, markdown formatting, and citation integration with
content. It ensures consistent citation handling across the analysis pipeline.
"""

from typing import Dict, List, Any, Tuple
import re

from ...models.citation import Citation, Segments


class CitationProcessor:
    """
    Unified citation processor for deduplicating and managing citations.
    
    This class provides comprehensive citation processing capabilities including
    URL deduplication, canonical ID assignment, markdown formatting, and
    citation integration with content. It maintains state across processing
    operations to ensure consistent citation numbering and formatting.
    
    Key Features:
    - URL deduplication with canonical ID assignment
    - Markdown citation formatting ([[id](url)])
    - Citation extraction from text content
    - Citation integration with processed content
    - State management for consistent processing
    
    Attributes:
        url_to_canonical_id (Dict[str, int]): Mapping of URLs to canonical IDs
        canonical_counter (int): Counter for generating unique canonical IDs
        citation_pattern (str): Regex pattern for detecting citations in text
    """
    
    def __init__(self):
        self.url_to_canonical_id: Dict[str, int] = {}
        self.canonical_counter: int = 1
        self.citation_pattern = r'\[\[(\d+)\]\((https?://[^\)]+)\)\]'
    
    def reset(self) -> None:
        """
        Reset the processor state to initial conditions.
        
        Clears all URL mappings and resets the canonical counter to 1.
        This is useful when processing a new batch of citations that
        should have independent ID numbering.
        """
        self.url_to_canonical_id.clear()
        self.canonical_counter = 1
    
    def _get_canonical_id(self, url: str) -> int:
        """
        Get or create a canonical ID for a URL.
        
        Returns an existing canonical ID if the URL has been seen before,
        or creates a new unique ID if this is the first occurrence.
        
        Args:
            url (str): URL to get or create canonical ID for
            
        Returns:
            int: Canonical ID for the URL
        """
        if url not in self.url_to_canonical_id:
            self.url_to_canonical_id[url] = self.canonical_counter
            self.canonical_counter += 1
        return self.url_to_canonical_id[url]
    
    def _collect_urls_from_citations(self, citations: List[Citation]) -> None:
        """
        Collect URLs from Citation objects for canonical ID assignment.
        
        Scans through all citation objects and their segments to collect
        unique URLs, assigning canonical IDs as needed.
        
        Args:
            citations (List[Citation]): List of Citation objects to process
        """
        for citation in citations:
            for segment in citation.segments:
                url = segment.original_link or segment.link
                if url:
                    self._get_canonical_id(url)
    
    def _collect_urls_from_text(self, text: str) -> None:
        """
        Collect URLs from markdown citation patterns in text.
        
        Uses regex pattern to find citation links in the format [[id](url)]
        and assigns canonical IDs to discovered URLs.
        
        Args:
            text (str): Text containing citation patterns to process
        """
        matches = re.findall(self.citation_pattern, text)
        for _, url in matches:
            self._get_canonical_id(url)
    
    def _update_citation_objects(self, citations: List[Citation]) -> List[Citation]:
        """
        Update Citation objects with canonical IDs.
        
        Creates new Citation objects with updated segment chunk_index values
        based on canonical URL IDs. Preserves all other citation metadata.
        
        Args:
            citations (List[Citation]): Original citations to update
            
        Returns:
            List[Citation]: Updated citations with canonical IDs
        """
        updated_citations = []
        
        for citation in citations:
            updated_segments = []
            for segment in citation.segments:
                url = segment.original_link or segment.link
                canonical_id = self._get_canonical_id(url)
                
                updated_segment = Segments(
                    title=segment.title,
                    chunk_index=canonical_id - 1,  # Convert to 0-based index
                    link=segment.link,
                    original_link=segment.original_link,
                    placeholder=segment.placeholder
                )
                updated_segments.append(updated_segment)
            
            updated_citation = Citation(
                score=citation.score,
                start_index=citation.start_index,
                end_index=citation.end_index,
                text=citation.text,
                segments=updated_segments
            )
            updated_citations.append(updated_citation)
        
        return updated_citations
    
    def _update_text_citations(self, text: str) -> str:
        """
        Update text citations with canonical IDs.
        
        Replaces citation patterns in text with updated canonical IDs
        while preserving the original URL. Updates [[id](url)] patterns.
        
        Args:
            text (str): Text containing citation patterns to update
            
        Returns:
            str: Text with updated canonical citation IDs
        """
        def replace_citation(match):
            url = match.group(2)
            canonical_id = self._get_canonical_id(url)
            return f"[[{canonical_id}]({url})]"
        
        return re.sub(self.citation_pattern, replace_citation, text)
    
    def _collect_urls_from_data(self, data: Any) -> None:
        """
        Recursively collect URLs from any data structure.
        
        Traverses nested data structures (dictionaries, lists, strings)
        to find and collect URLs from both Citation objects and text patterns.
        Handles mixed data types intelligently.
        
        Args:
            data (Any): Data structure to scan for URLs
        """
        if isinstance(data, dict):
            for value in data.values():
                self._collect_urls_from_data(value)
        elif isinstance(data, list):
            if data and isinstance(data[0], Citation):
                self._collect_urls_from_citations(data)
            else:
                for item in data:
                    self._collect_urls_from_data(item)
        elif isinstance(data, str):
            self._collect_urls_from_text(data)
    
    def _process_data_structure(self, data: Any) -> Any:
        """
        Recursively process and update data structure with canonical IDs.
        
        Traverses nested data structures and applies appropriate processing:
        - Citation objects: Updates with canonical IDs and converts to dict
        - Text strings: Updates citation patterns with canonical IDs
        - Nested structures: Recursively processes contents
        
        Args:
            data (Any): Data structure to process
            
        Returns:
            Any: Processed data structure with updated canonical IDs
        """
        if isinstance(data, dict):
            return {key: self._process_data_structure(value) for key, value in data.items()}
        elif isinstance(data, list):
            if data and isinstance(data[0], Citation):
                return self._convert_citations_to_dict(self._update_citation_objects(data))
            else:
                return [self._process_data_structure(item) for item in data]
        elif isinstance(data, str):
            return self._update_text_citations(data)
        else:
            return data
            
    
    def _convert_citations_to_dict(self, citations: List[Citation]) -> List[Dict]:
        """
        Convert Citation objects to dictionary format for serialization.
        
        Transforms Citation and Segments objects into plain dictionaries
        suitable for JSON serialization and API responses.
        
        Args:
            citations (List[Citation]): Citation objects to convert
            
        Returns:
            List[Dict]: List of citation dictionaries
        """
        result = []
        for citation in citations:
            segments_dict = []
            for segment in citation.segments:
                segment_dict = {
                    "title": segment.title,
                    "chunk_index": segment.chunk_index,
                    "link": segment.link,
                    "original_link": segment.original_link,
                    "placeholder": segment.placeholder
                }
                segments_dict.append(segment_dict)
            
            citation_dict = {
                "score": citation.score,
                "start_index": citation.start_index,
                "end_index": citation.end_index,
                "text": citation.text,
                "segments": segments_dict
            }
            result.append(citation_dict)
        
        return result
    

    def _split_and_deduplicate_segments(self, text: str) -> str:
        """
        Split citation-rich text into logical segments and remove duplicate citations.
        
        Analyzes text with embedded citations to create logical segments and
        removes duplicate citations within each segment while preserving content
        flow and readability.
        
        Args:
            text (str): Text containing citation patterns to segment and deduplicate
            
        Returns:
            str: Cleaned text with deduplicated citations per segment
            
        Features:
            - Intelligent text segmentation based on citation boundaries
            - Per-segment deduplication to avoid citation repetition
            - Preservation of text flow and readability
        """
        full_citation_pattern = re.compile(r'\[\[\d+\]\(https?://[^\)]+\)\]')

        # Use finditer instead of findall to avoid tuple issue
        matches = list(full_citation_pattern.finditer(text))
        tokens = full_citation_pattern.split(text)

        segments = []
        current = ""

        for i in range(len(tokens)):
            current += tokens[i].strip()
            if i < len(matches):
                current += " " + matches[i].group(0)
                # If next token is plain text, treat as new segment
                if i + 1 < len(tokens) and tokens[i + 1].strip():
                    segments.append(current.strip())
                    current = ""

        if current.strip():
            segments.append(current.strip())

        # Deduplicate citations per segment
        def deduplicate(segment: str) -> str:
            seen = set()
            result = ""
            last_end = 0
            for m in full_citation_pattern.finditer(segment):
                start, end = m.span()
                url = re.search(r'\((https?://[^\)]+)\)', m.group(0)).group(1)

                result += segment[last_end:start]
                if url not in seen:
                    result += m.group(0)
                    seen.add(url)
                last_end = end

            result += segment[last_end:]
            return result.strip()

        cleaned_segments = [deduplicate(seg) for seg in segments]
        return " ".join(cleaned_segments)



    def apply_segment_deduplication(self, data: Any) -> Any:
        """
        Recursively apply segment deduplication to all string fields in data structures.
        
        Traverses nested data structures and applies citation deduplication
        to all text content, ensuring consistent citation handling across
        the entire data structure.
        
        Args:
            data (Any): Data structure containing text with citations
            
        Returns:
            Any: Data structure with deduplicated citations in all text fields
        """
        if isinstance(data, dict):
            return {k: self.apply_segment_deduplication(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.apply_segment_deduplication(item) for item in data]
        elif isinstance(data, str):
            return self._split_and_deduplicate_segments(data)
        else:
            return data
    
    def deduplicate_citations(self, citations: List[Citation]) -> Tuple[List[Citation], Dict[str, int]]:
        """
        Deduplicate Citation objects by URL and reassign canonical chunk_index values.
        
        Processes a list of Citation objects to remove URL duplicates and assign
        consistent canonical IDs across all segments. Useful for normalizing
        citation references in analysis results.
        
        Args:
            citations (List[Citation]): Citation objects to deduplicate
            
        Returns:
            Tuple[List[Citation], Dict[str, int]]: 
                - Deduplicated citations with canonical IDs
                - URL to canonical ID mapping
        """
        self.reset()
        self._collect_urls_from_citations(citations)
        deduplicated_citations = self._update_citation_objects(citations)
        final_data = self._split_and_deduplicate_segments(deduplicated_citations)
        return final_data, self.url_to_canonical_id.copy()
    
    def deduplicate_text_citations(self, text: str) -> Tuple[str, Dict[str, int]]:
        """
        Deduplicate citations in markdown text format [[id](url)].
        
        Processes text containing markdown citation patterns to normalize
        citation IDs and remove duplicates while preserving text content
        and readability.
        
        Args:
            text (str): Text with markdown citation patterns
            
        Returns:
            Tuple[str, Dict[str, int]]:
                - Updated text with canonical citation IDs
                - URL to canonical ID mapping dictionary
        """
        self.reset()
        self._collect_urls_from_text(text)
        updated_text = self._update_text_citations(text)
        final_data = self._split_and_deduplicate_segments(updated_text)
        return final_data, self.url_to_canonical_id.copy()
    
    def process_mixed_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process mixed data containing both Citation objects and citation text.
        
        Handles complex data structures that may contain Citation objects,
        text with citation patterns, or a mixture of both. Provides comprehensive
        deduplication and normalization across all data types.
        
        Args:
            data (Dict[str, Any]): Mixed data structure to process
            
        Returns:
            Dict[str, Any]: Comprehensive processing results containing:
                - 'deduplicated_data': Processed data with canonical citations
                - 'citation_mappings': URL to canonical ID mapping
                - 'total_unique_citations': Count of unique citations found
                
        Features:
            - Three-pass processing for thorough deduplication
            - Support for nested data structures
            - Comprehensive statistics and mappings
        """
        self.reset()
        
        # First pass: collect all URLs
        self._collect_urls_from_data(data)
        
        # Second pass: process and update data
        deduplicated_data = self._process_data_structure(data)

        # Third pass: remove duplicates per segment
        final_data = self.apply_segment_deduplication(deduplicated_data)
        
        return {
            "deduplicated_data": final_data,
            "citation_mappings": self.url_to_canonical_id.copy(),
            "total_unique_citations": len(self.url_to_canonical_id)
        }


