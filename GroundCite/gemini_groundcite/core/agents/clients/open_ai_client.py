"""
OpenAI client for the GroundCite library.

This module provides a specialized client wrapper for OpenAI's language models,
focusing on structured data parsing and content transformation. The client is
optimized for JSON output generation and integrates seamlessly with the
GroundCite analysis pipeline.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from ...utils.prompt_utils import get_parsing_system_prompt, get_parsing_user_prompt
from openai import AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion


class OpenAIClient:
    """
    OpenAI client specialized for structured data parsing operations.
    
    This class provides a focused interface to OpenAI's chat completion models,
    specifically optimized for parsing unstructured content into structured JSON
    format. It handles API authentication, request formatting, and token usage
    tracking for OpenAI models.
    
    Key Features:
    - Structured JSON output generation
    - Support for custom parsing schemas
    - Token usage tracking and billing
    - Async operation support
    - Integration with GroundCite prompt utilities
    
    Attributes:
        default_model_id (str): Default OpenAI model for operations
        _client (AsyncOpenAI): Authenticated OpenAI async client instance
    """
    def __init__(self, *, api_key: str, default_model_id: str = "o3-mini") -> None:
        """
        Initialize the OpenAI client with authentication and default model settings.
        
        Sets up the async OpenAI client with API key authentication and establishes
        default model preferences for content parsing operations.
        
        Args:
            api_key (str): OpenAI API key for authentication
            default_model_id (str): Default OpenAI model identifier
                                   (e.g., 'o3-mini', 'gpt-4', 'gpt-4-turbo')
                                   
        Raises:
            AuthenticationError: If the API key is invalid
        """
        self.default_model_id = default_model_id
        self._client = AsyncOpenAI(api_key=api_key)

    async def parse_content(
        self,
        content: str,
        model_id: Optional[str] = None,
        schema: str = None,      
        **config_kwargs: Any,                       
    ) -> str:
        """
        Parse unstructured content into structured JSON using OpenAI models.
        
        This method is the primary interface for structured data extraction using
        OpenAI's chat completion models. It combines system prompts, user content,
        and optional JSON schemas to produce reliable structured output.
        
        Args:
            content (str): Unstructured content to parse (text, markdown, etc.)
            model_id (str, optional): Specific OpenAI model to use (overrides default)
            schema (str, optional): JSON schema string defining expected output structure
            **config_kwargs: Additional OpenAI API parameters (temperature, max_tokens, etc.)
            
        Returns:
            str: Dictionary containing:
                - 'response': Structured JSON output as string
                - 'token_usage': Token consumption metrics with input/output/total counts
                
        Raises:
            APIError: If OpenAI API request fails
            JSONDecodeError: If the model output is not valid JSON
            
        Note:
            Uses OpenAI's JSON mode to ensure valid JSON output format.
        """
                
        # 1) Prepare schema text (if provided)
        # Convert JSON schema to readable format for the model
        schema_block = ""
        if schema is not None:
            schema_block = f"\n\nSchema to follow:\n```json\n{schema}\n```"

        # 2) Build messages using GroundCite prompt utilities
        # System prompt instructs the model on parsing behavior
        # User prompt contains the content to parse plus schema
        messages = [
            {
                "role": "system",
                "content": get_parsing_system_prompt(),
            },
            {
                "role": "user",
                "content": get_parsing_user_prompt(markdown_content=content) + schema_block,
            },
        ]

        # 3) Assemble request with JSON mode enabled
        # JSON mode ensures the output is valid JSON format
        request_kwargs: Dict[str, Any] = {
            "model": model_id,
            "messages": messages,
            "response_format": {"type": "json_object"},  # ← JSON mode
            **config_kwargs,
        }

        # 4) Execute OpenAI API request asynchronously
        response: ChatCompletion = await self._client.chat.completions.create(**request_kwargs)

        # 5) Extract structured JSON content from response
        structured = response.choices[0].message.content

        # 6) Extract comprehensive token usage metrics for billing and optimization
        # OpenAI provides detailed token counts for prompt, completion, and total
        token_usage = None
        if response.usage is not None:
            token_usage = {
                'input_tokens': response.usage.prompt_tokens,
                'output_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }

        return {
            "response": structured,
            "token_usage": token_usage
        }

