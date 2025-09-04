"""
FastAPI application for the GroundCite query analysis service.

This module provides a REST API interface for the GroundCite library, allowing
HTTP-based access to query analysis capabilities including search, validation,
and parsing operations.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

# Import GroundCite library components
from gemini_groundcite.config.settings import AppSettings
from gemini_groundcite.core.agents.ai_agent import AIAgent
from gemini_groundcite.core.di.core_di import CoreDi
from gemini_groundcite.exceptions import GroundCiteError

# Create FastAPI application with comprehensive metadata
app = FastAPI(
    title="GroundCite Query Analysis API",
    version="1.1.0",
    description="AI-powered query analysis and research API using the GroundCite library",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests and responses
class QueryAnalysisRequest(BaseModel):
    """
    Request model for query analysis operations.
    
    Contains all necessary parameters for configuring and executing
    a comprehensive query analysis workflow.
    """
    query: str
    system_instruction: str = ""
    
    # Analysis configuration
    config: Dict[str, Any]
    
    # AI Provider configuration
    parsing_provider: str = "gemini"
    search_model_name: str
    validate_model_name: str = ""
    parse_model_name: str = ""
    
    # Provider-specific parameters
    search_gemini_params: Dict[str, Any] = {}
    validate_gemini_params: Dict[str, Any] = {}
    parsing_gemini_params: Dict[str, Any] = {}
    parsing_openai_params: Dict[str, Any] = {}
    
    # API authentication
    api_keys: Dict[str, Any]


class QueryAnalysisResponse(BaseModel):
    """
    Response model for query analysis operations.
    
    Contains the results of the analysis workflow along with
    execution metadata and any error information.
    """
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    correlation_id: Optional[str] = None


class AnalysisConfigurationModel(BaseModel):
    """
    Model for saving and managing analysis configurations.
    
    Allows users to save frequently used analysis setups
    for easy reuse and management.
    """
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    
    # Analysis settings
    config: Dict[str, Any]
    parsing_provider: str = "gemini"
    
    # Model configurations
    search_model_name: str
    validate_model_name: str = ""
    parse_model_name: str = ""
    
    # Provider parameters
    search_gemini_params: Dict[str, Any] = {}
    validate_gemini_params: Dict[str, Any] = {}
    parsing_gemini_params: Dict[str, Any] = {}
    parsing_openai_params: Dict[str, Any] = {}
    
    # API keys (stored securely in production)
    api_keys: Dict[str, Any]
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class APIHealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    version: str
    groundcite_ready: bool

# In-memory storage (replace with database in production)
configurations_store = {}

@app.post("/api/v1/analyze", response_model=QueryAnalysisResponse)
async def analyze_query_endpoint(request: QueryAnalysisRequest):
    """
    Analyze a query using AI-powered research and analysis.
    
    This endpoint orchestrates a comprehensive query analysis workflow including:
    - Web search for relevant information
    - AI-powered content validation (optional)
    - Structured data parsing with custom schemas (optional)
    
    Args:
        request (QueryAnalysisRequest): Analysis configuration and parameters
    
    Returns:
        QueryAnalysisResponse: Analysis results with execution metadata
    
    Raises:
        HTTPException: For validation errors or processing failures
    """
    start_time = datetime.now()
    correlation_id = str(uuid.uuid4())
    
    try:
        # Input validation
        if not request.query.strip():
            raise HTTPException(
                status_code=400, 
                detail="Query cannot be empty"
            )
        
        # API key validation
        gemini_keys = request.api_keys.get("gemini", {})
        if not gemini_keys.get("primary"):
            raise HTTPException(
                status_code=400,
                detail="Gemini API key is required"
            )
        
        if request.parsing_provider == "openai" and not request.api_keys.get("openai"):
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key is required when using OpenAI as parsing provider"
            )
        
        # Model configuration validation
        missing_models = []
        if not request.search_model_name:
            missing_models.append("search_model_name")
        if request.config.get('validate', False) and not request.validate_model_name:
            missing_models.append("validate_model_name")
        if request.config.get('parse', False) and not request.parse_model_name:
            missing_models.append("parse_model_name")
        
        if missing_models:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required model configuration(s): {', '.join(missing_models)}"
            )
        
        # Configure GroundCite settings
        settings = AppSettings()
        
        # Analysis configuration
        settings.ANALYSIS_CONFIG.query = request.query
        settings.ANALYSIS_CONFIG.system_instruction = request.system_instruction
        settings.ANALYSIS_CONFIG.validate = request.config.get('validate', False)
        settings.ANALYSIS_CONFIG.parse = request.config.get('parse', False)
        settings.ANALYSIS_CONFIG.parse_schema = request.config.get('schema', '{}')
        
        # Site filtering configuration
        site_config = request.config.get('siteConfig', {})
        settings.ANALYSIS_CONFIG.included_sites = site_config.get('includeList', '')
        settings.ANALYSIS_CONFIG.excluded_sites = site_config.get('excludeList', '')
        
        # AI provider configuration
        settings.AI_CONFIG.gemini_ai_key_primary = gemini_keys.get('primary', '')
        settings.AI_CONFIG.open_ai_key = request.api_keys.get('openai', '')
        settings.AI_CONFIG.parsing_provider = request.parsing_provider
        
        # Model configuration
        settings.AI_CONFIG.search_model_name = request.search_model_name
        settings.AI_CONFIG.validate_model_name = request.validate_model_name
        settings.AI_CONFIG.parse_model_name = request.parse_model_name
        
        # Provider-specific parameters
        settings.AI_CONFIG.search_gemini_params = request.search_gemini_params
        settings.AI_CONFIG.validate_gemini_params = request.validate_gemini_params
        settings.AI_CONFIG.parsing_gemini_params = request.parsing_gemini_params
        settings.AI_CONFIG.parsing_openai_params = request.parsing_openai_params
        
        # Initialize GroundCite components
        agent = AIAgent(settings=settings)
        
        # Execute analysis
        analysis_results = await agent.analyze_query(correlation_id=correlation_id)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return QueryAnalysisResponse(
            success=True,
            data=analysis_results,
            execution_time=execution_time,
            correlation_id=correlation_id
        )
        
    except HTTPException:
        raise
    except GroundCiteError as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        return QueryAnalysisResponse(
            success=False,
            error=f"GroundCite Error: {e.message}",
            execution_time=execution_time,
            correlation_id=correlation_id
        )
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        return QueryAnalysisResponse(
            success=False,
            error=f"Unexpected error: {str(e)}",
            execution_time=execution_time,
            correlation_id=correlation_id
        )

@app.get("/api/v1/configurations")
async def get_all_configurations():
    """
    Retrieve all saved analysis configurations.
    
    Returns:
        Dict: List of all saved configurations with metadata
    """
    return {
        "configurations": list(configurations_store.values()),
        "total": len(configurations_store)
    }


@app.post("/api/v1/configurations")
async def save_configuration(config: AnalysisConfigurationModel):
    """
    Save a new analysis configuration for reuse.
    
    Args:
        config (AnalysisConfigurationModel): Configuration to save
    
    Returns:
        Dict: Success response with configuration ID
    
    Raises:
        HTTPException: If saving fails
    """
    try:
        config_id = str(uuid.uuid4())
        config.id = config_id
        config.created_at = datetime.now()
        config.updated_at = datetime.now()
        
        configurations_store[config_id] = config.dict()
        
        return {
            "success": True,
            "id": config_id,
            "message": "Analysis configuration saved successfully",
            "configuration": config.dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save configuration: {str(e)}"
        )


@app.put("/api/v1/configurations/{config_id}")
async def update_configuration(config_id: str, config: AnalysisConfigurationModel):
    """
    Update an existing analysis configuration.
    
    Args:
        config_id (str): ID of configuration to update
        config (AnalysisConfigurationModel): Updated configuration data
    
    Returns:
        Dict: Success response
    
    Raises:
        HTTPException: If configuration not found or update fails
    """
    if config_id not in configurations_store:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    try:
        config.id = config_id
        config.updated_at = datetime.now()
        # Preserve original creation time
        config.created_at = configurations_store[config_id].get("created_at")
        
        configurations_store[config_id] = config.dict()
        
        return {
            "success": True,
            "message": "Configuration updated successfully",
            "configuration": config.dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update configuration: {str(e)}"
        )


@app.delete("/api/v1/configurations/{config_id}")
async def delete_configuration(config_id: str):
    """
    Delete a saved analysis configuration.
    
    Args:
        config_id (str): ID of configuration to delete
    
    Returns:
        Dict: Success response
    
    Raises:
        HTTPException: If configuration not found
    """
    if config_id not in configurations_store:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    deleted_config = configurations_store.pop(config_id)
    
    return {
        "success": True,
        "message": "Configuration deleted successfully",
        "deleted_configuration_name": deleted_config.get("name", "Unknown")
    }


@app.get("/api/v1/configurations/{config_id}")
async def get_configuration_by_id(config_id: str):
    """
    Retrieve a specific analysis configuration by ID.
    
    Args:
        config_id (str): ID of configuration to retrieve
    
    Returns:
        Dict: Configuration data
    
    Raises:
        HTTPException: If configuration not found
    """
    if config_id not in configurations_store:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    return {
        "configuration": configurations_store[config_id],
        "id": config_id
    }


@app.get("/", response_model=APIHealthResponse)
async def root():
    """
    Root endpoint and basic health check.
    
    Returns:
        APIHealthResponse: Basic API status and information
    """
    try:
        # Test GroundCite library availability
        settings = AppSettings()
        groundcite_ready = True
    except Exception:
        groundcite_ready = False
    
    return APIHealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.1.0",
        groundcite_ready=groundcite_ready
    )


@app.get("/api/v1/health", response_model=APIHealthResponse)
async def detailed_health_check():
    """
    Comprehensive health check endpoint.
    
    Returns:
        APIHealthResponse: Detailed system health status
    """
    try:
        # Test GroundCite components
        settings = AppSettings()
        logger = CoreDi.global_instance().resolve(AppLogger)
        groundcite_ready = True
    except Exception:
        groundcite_ready = False
    
    return APIHealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.1.0",
        groundcite_ready=groundcite_ready
    )


# Legacy endpoints for backward compatibility
@app.post("/api/analyze")
async def legacy_analyze_endpoint(request: QueryAnalysisRequest):
    """Legacy analyze endpoint for backward compatibility."""
    return await analyze_query_endpoint(request)


@app.get("/api/configs")
async def legacy_get_configurations():
    """Legacy configuration endpoint for backward compatibility."""
    return await get_all_configurations()


@app.get("/api/health")
async def legacy_health_check():
    """Legacy health check endpoint."""
    health_response = await detailed_health_check()
    return health_response.dict()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)