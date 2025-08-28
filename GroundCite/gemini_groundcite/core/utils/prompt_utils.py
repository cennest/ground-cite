"""
Prompt generation utilities for AI model interactions.

This module provides functions to generate system and user prompts for various
AI-powered operations including content parsing, factual validation, and
citation analysis. These prompts are designed to work with LLM providers
like OpenAI and Google Gemini.
"""

import textwrap
import json


def get_parsing_system_prompt() -> str:
    """
    Generate system prompt for document parsing operations.
    
    Creates a system prompt that instructs the AI model to extract structured
    JSON data from documents while ensuring proper citation handling.
    
    Returns:
        str: System prompt for parsing operations
    """
    return textwrap.dedent(
        """\
        You are a document-to-JSON extraction agent.

        Your task is to extract a structured JSON object from a given document,
        ensuring that all factual information is explicitly supported by citations.

        """
    )

def get_parsing_user_prompt(markdown_content: str) -> str:
    """
    Generate user prompt for document parsing with specific content.
    
    Creates a detailed user prompt that provides the content to parse along
    with specific instructions for citation handling and JSON formatting.
    
    Args:
        markdown_content (str): The document content to parse
        
    Returns:
        str: Complete user prompt for parsing the provided content
    """
    content = markdown_content.strip()
    return textwrap.dedent(
        f"""
        Convert the following document into a structured JSON object.

        Instructions:
        • Use only facts explicitly present in the document below.
        • Citations are in the format: URL_A_1 (e.g., "Scheme of Amalgamation URL_A_1").
        • Every property with a real value must include at least one such citation.
        • Do not invent or assume citations.
        • If a property includes multiple instances of the same URL, include it only once.
        • If the JSON object is an array, include only items with at least one non-empty property. 
          Do not return placeholder or fully empty objects.
        • For properties that are empty, do not attach any citation.
        • Do not alter the citation format — keep `URL_A_X` exactly as-is.
        • Return only the JSON object — do not add explanations, comments, or extra text.

        Example:
        Input text: "The company has 200 offices. URL_A_1"
        Output:
        {{
          "office_count": "200 URL_A_1",
          "employee_count": ""
        }}

        Document Content:
        {content}
        """
    )

def get_validation_system_prompt() -> str:
    """
    Generate system prompt for factual validation operations.
    
    Creates a system prompt that instructs the AI model to validate citations
    and assess the relevance of web sources to document claims.
    
    Returns:
        str: System prompt for validation operations
    """
    return textwrap.dedent("""
        You are a factual validation agent. Your task is to evaluate a list of citations. Each citation represents a document span (claim) and contains one or more supporting segments linked to URLs.

        Each citation has:
        - `text`: the referenced segment from the document (claim to validate)
        - `segments`: a list of associated web sources that may support the claim

        Each segment includes:
        - `chunk_index`: index in the source list
        - `link`: intermediate or redirected URL
        - `original_link`: the resolved final destination URL
        - `placeholder`: an identifier used in the text for this segment

        Your task:
        - For each segment in each citation, determine whether the content at `original_link` supports the claim (`text`)
        - Provide a relevance label: `"relevant"`, `"partial"`, or `"irrelevant"`
        - Assign a confidence score between 0 and 1
        - Provide a brief `evidence_snippet`: either a direct quote or paraphrased support from the page content

        Return only valid JSON in the format:
        {
        "verdicts": [
            {
            "citation_text": string,
            "chunk_index": int,
            "original_link": string,
            "placeholder": string,
            "relevance": "relevant" | "partial" | "irrelevant",
            "confidence": float,
            "evidence_snippet": string
            }
        ]
        }

        Notes:
        - Each citation can have multiple segments — evaluate each segment independently.
        - Include all segment evaluations in the output.
        - Do not include explanations, comments, or markdown — return only valid JSON.
    """)

def get_validation_user_prompt(citations: list) -> str:
    """
    Generate user prompt for citation validation with specific citations.
    
    Builds a user prompt using serialized Citation objects that need validation.
    Each Citation includes text claims and supporting web segments that need
    to be assessed for relevance and accuracy.

    Args:
        citations (list): List of Citation objects to validate
        
    Returns:
        str: Complete user prompt for validating the provided citations
        
    Note:
        Each Citation includes:
        - `text`: the document segment or claim
        - `segments`: a list of web-based sources that may support the text
            - Each segment has a `chunk_index`, `link`, `original_link`, and `placeholder`
    """

    serialized = json.dumps([c.dict() for c in citations], indent=2)

    return textwrap.dedent(f"""
        You are given citation metadata used to validate factual claims in a document.

        Each citation includes:
        - `text`: A specific segment (claim) from the document.
        - `segments`: A list of sources potentially supporting the text.
            - Each segment has:
                - `chunk_index`: numeric index pointing to the chunk
                - `link`: intermediate or redirected URL
                - `original_link`: final destination URL
                - `placeholder`: identifier token used in the original text

        Task:
        - For each segment, determine if the `original_link` supports the claim (`text`)
        - Assess relevance as one of: "relevant", "partial", or "irrelevant"
        - Provide a confidence score between 0 and 1
        - Include a short `evidence_snippet` from the content to justify the verdict

        Return only structured JSON using the format defined in the system prompt.

        citation_metadata:
        {serialized}
    """)


