"""
Citation models for document reference tracking.

This module defines Pydantic models for managing citations and their associated
web segments. Citations track document references with scoring, positioning,
and source validation capabilities.
"""

from typing import List
from pydantic import BaseModel


class Citation(BaseModel):
    """
    Citation model for tracking document references and source validation.
    
    Represents a citation within a document including its position, relevance score,
    and associated web segments that provide supporting evidence. Used in the
    validation pipeline to assess source credibility and relevance.
    
    Attributes:
        score (float): Relevance or confidence score for this citation
        start_index (int): Starting character position in the document
        end_index (int): Ending character position in the document
        text (str): The actual text content being cited
        segments (List[Segments]): Web segments supporting this citation
    """
    score: float
    start_index: int
    end_index: int
    text: str 
    segments: List['Segments']    
   

class Segments(BaseModel):
    """
    Web segment model for citation source tracking.
    
    Represents a web-based source segment that supports a citation,
    including metadata for link resolution, content indexing, and
    placeholder text replacement.
    
    Attributes:
        title (str): Title or description of the web segment
        chunk_index (int): Index position in the source content chunks
        link (str): Original or intermediate URL for the source
        original_link (str, optional): Resolved final destination URL
        placeholder (str, optional): Placeholder text used in document citations
    """
    title: str
    chunk_index: int
    link: str
    original_link: str | None = None 
    placeholder: str | None = None 

    def get_formated_link(self) -> str:
        """
        Format the segment as a markdown link.
        
        Creates a markdown-formatted link using the chunk index and original URL.
        
        Returns:
            str: Markdown formatted link in the format [[index](url)]
        """
        return f"[[{self.chunk_index+1}]({self.original_link})]"  #if self.chunk_index >= 0 else ""    

    def get_placeholder(self) -> str:
        """
        Get the placeholder text for this segment.
        
        Returns the placeholder text used to reference this segment
        within the document text.
        
        Returns:
            str: Placeholder text with appropriate spacing
        """
        return f" {self.placeholder}" 

