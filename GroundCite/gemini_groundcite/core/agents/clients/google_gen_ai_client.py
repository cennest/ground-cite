"""
Google Gemini AI client for the GroundCite library.

This module provides a comprehensive client wrapper for Google's Gemini AI models,
offering search capabilities, content validation, structured data parsing, and
token usage tracking. The client supports various Gemini models and provides
both basic content generation and specialized analysis functions.
"""

import json
from typing import List, Optional, Any, Dict
from google import genai
from google.genai.types import GenerateContentConfig, GoogleSearch, Tool, UrlContext, GenerateContentResponse

from ...models.citation import Citation
from ...utils.prompt_utils import get_parsing_system_prompt, get_parsing_user_prompt, get_validation_system_prompt, get_validation_user_prompt


class GoogleGenAI:
    """
    Google Gemini AI client for query analysis and content processing.
    
    This class provides a high-level interface to Google's Gemini AI models,
    supporting web search, content validation, structured data parsing, and
    comprehensive token usage tracking. It handles API authentication, request
    configuration, and response processing for various AI-powered operations.
    
    Key Features:
    - Multi-model support (Gemini 1.5 Flash, Pro, etc.)
    - Integrated Google Search capabilities
    - Structured JSON output generation
    - Comprehensive token usage tracking
    - Configurable temperature and response parameters
    
    Attributes:
        default_model_id (str): Default Gemini model for operations
        client (genai.Client): Authenticated Google GenAI client instance
    """
    
    def __init__(self, api_key: str, default_model_id: str = "gemini-2.5-flash"):
        """
        Initialize the Google Gemini AI client with authentication and default settings.
        
        Sets up the authenticated client connection and establishes default model
        preferences for subsequent API calls.
        
        Args:
            api_key (str): Google AI API key for authentication
            default_model_id (str): Default Gemini model identifier
                                   (e.g., 'gemini-2.5-flash', 'gemini-1.5-pro')
        
        """
        self.default_model_id = default_model_id
        self.client = genai.Client(api_key=api_key)
    
    async def generate_content(
        self, 
        prompt: str,
        model_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[List] = None,
        temperature: float = 0.0,
        response_mime_type: Optional[str] = None,
        response_schema: Optional[Dict] = None,
        **config_kwargs
    ) -> GenerateContentResponse:
        """
        Generate content using Google Gemini models with flexible configuration.
        
        This is the core method for interacting with Gemini models, supporting
        various content generation tasks including text generation, structured output,
        and tool-assisted operations.
        
        Args:
            prompt (str): The user prompt or search to process
            model_id (str, optional): Specific model to use (overrides default)
            system_prompt (str, optional): System instructions for the model
            tools (List, optional): Tools to make available to the model
            temperature (float): Randomness in output (0.0 = deterministic, 1.0 = creative)
            response_mime_type (str, optional): Expected response format (e.g., 'application/json')
            response_schema (Dict, optional): JSON schema for structured responses
            **config_kwargs: Additional configuration parameters
            
        Returns:
            GenerateContentResponse: Complete response object from Gemini API
        """

        # Use provided model_id or fall back to default
        model_to_use = model_id or self.default_model_id
        
        config_params = {
            "response_modalities": ["TEXT"],
            "temperature": temperature,
            **config_kwargs
        }

        if system_prompt:
            config_params["system_instruction"] = system_prompt
        if tools:
            config_params["tools"] = tools
        if response_mime_type:
            config_params["response_mime_type"] = response_mime_type
        if response_schema:
            config_params["response_schema"] = response_schema
            
        config = GenerateContentConfig(**config_params)

        response = await self.client.aio.models.generate_content(
            model=model_to_use,
            contents=prompt,
            config=config
        )
        
        return response
    
    async def search(
        self,
        prompt: str,
        model_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[List] = None,
        include_google_search: bool = True,
        schema: str = None,
        **config_kwargs
    ) -> Dict[str, Any]:
        """
        Perform web search and content analysis using Gemini with Google Search integration.
        
        This method combines Gemini's language understanding with Google Search to
        provide comprehensive, up-to-date information on queries. It automatically
        includes search tools and handles response formatting.
        
        Args:
            prompt (str): Search query to investigate
            model_id (str, optional): Specific Gemini model for search operations
            system_prompt (str, optional): System instructions for search behavior
            tools (List, optional): Additional tools beyond Google Search
            include_google_search (bool): Whether to include Google Search tool (default: True)
            schema (str, optional): JSON schema for structured search results
            **config_kwargs: Additional configuration parameters
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - 'response_object': Full Gemini API response
                - 'token_usage': Token consumption metrics
                
        """

        schema_block = ""
        if schema is not None:
            schema_block = f"\n\nSchema to follow:\n```json\n{schema}\n```"

        if include_google_search:
            tools = tools or []
            tools.append(Tool(google_search=GoogleSearch()))

        response = await self.generate_content(
            prompt=prompt + schema_block,
            model_id=model_id,
            system_prompt=system_prompt,
            tools=tools,
            **config_kwargs
        )

        result = {
            'response_object': response,
            'token_usage': self.get_token_usage(response)
        }

        return result
    
    async def validate_search(
        self,
        citations: List[Citation],
        model_id: Optional[str] = None,
        tools: Optional[List] = None,
        **config_kwargs
    ) -> str:
        """
        Validate citations and web sources using Gemini with URL context analysis.
        
        This method uses Gemini's URL context capabilities to assess the relevance
        and credibility of citations by analyzing the actual content at source URLs.
        It provides detailed validation results for fact-checking purposes.
        
        Args:
            citations (List[Citation]): List of Citation objects to validate
            model_id (str, optional): Specific model for validation (recommend Pro models)
            tools (List, optional): Additional tools beyond URL context
            **config_kwargs: Additional configuration parameters
            
        Returns:
            str: Validation results containing:
                - 'response': Detailed validation analysis
                - 'token_usage': Token consumption metrics
                
        """

        tools = tools or []
        tools.append(Tool(url_context=UrlContext))

        response = await self.generate_content(
            prompt=get_validation_user_prompt(citations=citations),
            model_id=model_id,
            system_prompt=get_validation_system_prompt(),
            tools=tools,
            **config_kwargs
        )

        return { 
            'response': response.text, 
            'token_usage': self.get_token_usage(response)
        }
    
    
    async def parse_content(
        self,
        content: str,
        model_id: Optional[str] = None,
        response_mime_type: Optional[str] = 'application/json',
        schema: str = None,
        **config_kwargs
    ) -> str:
        """
        Parse unstructured content into structured JSON using predefined schemas.
        
        This method specializes in extracting structured data from unstructured text
        content using JSON schemas. It's optimized for data parsing, information
        extraction, and content transformation tasks.
        
        Args:
            content (str): Unstructured content to parse (markdown, text, etc.)
            model_id (str, optional): Specific model for parsing operations
            response_mime_type (str): Expected response format (default: 'application/json')
            schema (str, optional): JSON schema defining the expected output structure
            **config_kwargs: Additional configuration parameters
            
        Returns:
            str: Dictionary containing:
                - 'response': Structured JSON output matching the schema
                - 'token_usage': Token consumption metrics
                
        """

        response = await self.generate_content(
            prompt=get_parsing_user_prompt(markdown_content=content),
            model_id=model_id,
            system_prompt=get_parsing_system_prompt(),
            response_mime_type=response_mime_type,
            response_schema=json.loads(schema),
            **config_kwargs
        )
        
        structured = response.text

        return {
            'response': structured,
            'token_usage': self.get_token_usage(response)
        }
    
    
    def get_token_usage(self, response: GenerateContentResponse) -> Dict[str, int]:
        """
        Extract comprehensive token usage metrics from Gemini API responses.
        
        Parses the response usage metadata to provide detailed token consumption
        information including input tokens, output tokens, and specialized token
        counts for tools and reasoning.
        
        Args:
            response (GenerateContentResponse): Gemini API response object with usage metadata
            
        Returns:
            Dict[str, int]: Token usage metrics containing:
                - 'input_tokens': Tokens in the input prompt
                - 'output_tokens': Tokens in the generated response
                - 'total_tokens': Combined input and output tokens
                - 'thoughts_tokens': Tokens used for internal reasoning
                - 'tool_use_prompt_tokens': Tokens for tool interaction prompts
                
        Note:
            Returns 0 for any unavailable token counts. This helps with billing
            tracking and usage optimization.
        """
        input_tokens = None
        output_tokens = None
        total_tokens = None
        thoughts_tokens = None
        tool_use_prompt_tokens = None

        usage = response.usage_metadata
        if usage:
            input_tokens = getattr(usage, "prompt_token_count", 0) or 0
            output_tokens = getattr(usage, "candidates_token_count", 0) or 0
            total_tokens = getattr(usage, "total_token_count", 0) or 0
            thoughts_tokens = getattr(usage, "thoughts_token_count", 0) or 0
            tool_use_prompt_tokens = getattr(usage, "tool_use_prompt_token_count", 0) or 0

        return {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': total_tokens,
            'thoughts_tokens': thoughts_tokens,
            'tool_use_prompt_tokens': tool_use_prompt_tokens
        }
