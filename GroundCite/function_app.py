"""
Azure Functions implementation for GroundCite Query Analysis API.

This module provides native Azure Functions endpoints for the GroundCite library,
implementing the same functionality as main.py but as individual Azure Functions.
"""

import azure.functions as func
import logging
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

# Import GroundCite library components
from gemini_groundcite.config.settings import AppSettings
from gemini_groundcite.core.agents.ai_agent import AIAgent
from gemini_groundcite.core.di.core_di import CoreDi
from gemini_groundcite.exceptions import GroundCiteError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Azure Functions app
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# In-memory storage for configurations (replace with database in production)
configurations_store = {}

# Configure logging for Azure Functions
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_request_data(req_body: dict) -> tuple[bool, str]:
    """
    Validate the request data for query analysis.
    
    Args:
        req_body (dict): Request body data
        
    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    # Check required fields
    if not req_body.get('query', '').strip():
        return False, "Query cannot be empty"
    
    # API key validation
    api_keys = req_body.get('api_keys', {})
    gemini_keys = api_keys.get('gemini', {})
    if not gemini_keys.get('primary'):
        return False, "Gemini API key is required"
    
    parsing_provider = req_body.get('parsing_provider', 'gemini')
    if parsing_provider == 'openai' and not api_keys.get('openai'):
        return False, "OpenAI API key is required when using OpenAI as parsing provider"
    
    # Model configuration validation
    config = req_body.get('config', {})
    missing_models = []
    
    if not req_body.get('search_model_name'):
        missing_models.append('search_model_name')
    if config.get('validate', False) and not req_body.get('validate_model_name'):
        missing_models.append('validate_model_name')
    if config.get('parse', False) and not req_body.get('parse_model_name'):
        missing_models.append('parse_model_name')
    
    if missing_models:
        return False, f"Missing required model configuration(s): {', '.join(missing_models)}"
    
    return True, ""


def configure_settings(req_body: dict) -> AppSettings:
    """
    Configure GroundCite settings from request data.
    
    Args:
        req_body (dict): Request body data
        
    Returns:
        AppSettings: Configured settings object
    """
    settings = AppSettings()
    
    # Analysis configuration
    settings.ANALYSIS_CONFIG.query = req_body['query']
    settings.ANALYSIS_CONFIG.system_instruction = req_body.get('system_instruction', '')
    settings.ANALYSIS_CONFIG.validate = req_body.get('config', {}).get('validate', False)
    settings.ANALYSIS_CONFIG.parse = req_body.get('config', {}).get('parse', False)
    settings.ANALYSIS_CONFIG.parse_schema = req_body.get('config', {}).get('schema', '{}')
    
    # Site filtering configuration
    site_config = req_body.get('config', {}).get('siteConfig', {})
    settings.ANALYSIS_CONFIG.included_sites = site_config.get('includeList', '')
    settings.ANALYSIS_CONFIG.excluded_sites = site_config.get('excludeList', '')
    
    # AI provider configuration
    api_keys = req_body.get('api_keys', {})
    gemini_keys = api_keys.get('gemini', {})
    settings.AI_CONFIG.gemini_ai_key_primary = gemini_keys.get('primary', '')
    settings.AI_CONFIG.open_ai_key = api_keys.get('openai', '')
    settings.AI_CONFIG.parsing_provider = req_body.get('parsing_provider', 'gemini')
    
    # Model configuration
    settings.AI_CONFIG.search_model_name = req_body.get('search_model_name', '')
    settings.AI_CONFIG.validate_model_name = req_body.get('validate_model_name', '')
    settings.AI_CONFIG.parse_model_name = req_body.get('parse_model_name', '')
    
    # Provider-specific parameters
    settings.AI_CONFIG.search_gemini_params = req_body.get('search_gemini_params', {})
    settings.AI_CONFIG.validate_gemini_params = req_body.get('validate_gemini_params', {})
    settings.AI_CONFIG.parsing_gemini_params = req_body.get('parsing_gemini_params', {})
    settings.AI_CONFIG.parsing_openai_params = req_body.get('parsing_openai_params', {})
    
    return settings


@app.route(route="analyze", methods=["POST"])
async def analyze_query(req: func.HttpRequest) -> func.HttpResponse:
    """
    Analyze a query using AI-powered research and analysis.
    
    This function orchestrates a comprehensive query analysis workflow including:
    - Web search for relevant information
    - AI-powered content validation (optional)
    - Structured data parsing with custom schemas (optional)
    """
    start_time = datetime.now()
    correlation_id = str(uuid.uuid4())
    
    try:
        # Parse request body
        try:
            req_body = req.get_json()
            if not req_body:
                return func.HttpResponse(
                    json.dumps({"success": False, "error": "Invalid JSON in request body"}),
                    status_code=400,
                    headers={"Content-Type": "application/json"}
                )
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"success": False, "error": f"Failed to parse JSON: {str(e)}"}),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )
        
        # Validate request
        is_valid, error_msg = validate_request_data(req_body)
        if not is_valid:
            execution_time = (datetime.now() - start_time).total_seconds()
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": error_msg,
                    "execution_time": execution_time,
                    "correlation_id": correlation_id
                }),
                status_code=400,
                headers={"Content-Type": "application/json"}
            )
        
        # Configure GroundCite settings
        settings = configure_settings(req_body)
        
        # Initialize GroundCite components
        agent = AIAgent(settings=settings)
        
        # Execute analysis
        analysis_results = await agent.analyze_query(correlation_id=correlation_id)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        response = {
            "success": True,
            "data": analysis_results,
            "execution_time": execution_time,
            "correlation_id": correlation_id
        }
        
        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
        
    except GroundCiteError as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        response = {
            "success": False,
            "error": f"GroundCite Error: {e.message}",
            "execution_time": execution_time,
            "correlation_id": correlation_id
        }
        return func.HttpResponse(
            json.dumps(response),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        response = {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "execution_time": execution_time,
            "correlation_id": correlation_id
        }
        logger.error(f"Unexpected error in analyze_query: {str(e)}")
        return func.HttpResponse(
            json.dumps(response),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )


@app.route(route="configs", methods=["GET"])
async def get_configurations(req: func.HttpRequest) -> func.HttpResponse:
    """
    Retrieve all saved analysis configurations.
    """
    try:
        response = {
            "configurations": list(configurations_store.values()),
            "total": len(configurations_store)
        }
        
        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        logger.error(f"Error getting configurations: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Failed to get configurations: {str(e)}"}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )


@app.route(route="health", methods=["GET"])
async def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """
    Comprehensive health check endpoint.
    """
    try:
        # Test GroundCite library availability
        try:
            settings = AppSettings()
            groundcite_ready = True
        except Exception as e:
            logger.warning(f"GroundCite not ready: {str(e)}")
            groundcite_ready = False
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "function_app": "GroundCite Query Analysis",
            "version": "1.0.0",
            "groundcite_ready": groundcite_ready,
            "environment": "Azure Functions"
        }
        
        return func.HttpResponse(
            json.dumps(health_status),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Health check failed: {str(e)}"}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )


@app.route(route="", methods=["GET"])
async def root(req: func.HttpRequest) -> func.HttpResponse:
    """
    Root endpoint and basic API information.
    """
    try:
        # Test GroundCite library availability
        try:
            settings = AppSettings()
            groundcite_ready = True
        except Exception:
            groundcite_ready = False
        
        api_info = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "groundcite_ready": groundcite_ready,
            "endpoints": {
                "analyze": "/api/v1/analyze",
                "configurations": "/api/v1/configurations",
                "health": "/health"
            },
            "description": "GroundCite Query Analysis API - Azure Functions"
        }
        
        return func.HttpResponse(
            json.dumps(api_info),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
        
    except Exception as e:
        logger.error(f"Root endpoint failed: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Root endpoint failed: {str(e)}"}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )
