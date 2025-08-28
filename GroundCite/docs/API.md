# API Documentation

## Overview

GroundCite provides a comprehensive REST API built with FastAPI that enables HTTP-based access to all query analysis capabilities. The API supports the full pipeline including search, validation, and parsing operations.

## Base Configuration

- **Base URL**: `http://localhost:8000` (default)
- **API Version**: `v1`
- **Content Type**: `application/json`
- **Documentation**: `/docs` (Swagger UI) or `/redoc` (ReDoc)

## Authentication

Currently, the API uses API key authentication passed in request bodies. In production, consider implementing:
- Header-based API key authentication
- OAuth 2.0 / JWT tokens
- Rate limiting per API key

## Core Endpoints

### 1. Query Analysis

#### `POST /api/v1/analyze`

Performs comprehensive query analysis with configurable pipeline stages.

**Request Structure:**

```json
{
  "query": "string",                    // Required: Query to analyze
  "system_instruction": "string",       // Optional: System instruction for AI
  "config": {
    "validate": false,                  // Enable AI validation
    "parse": false,                     // Enable structured parsing
    "schema": "{}",                     // JSON schema for parsing
    "siteConfig": {
      "includeList": "",                // Comma-separated domains to include
      "excludeList": ""                 // Comma-separated domains to exclude
    }
  },
  "parsing_provider": "gemini",         // AI provider: "gemini" or "openai"
  "search_model_name": "string",        // Required: Model for search
  "validate_model_name": "string",      // Required if validation enabled
  "parse_model_name": "string",         // Required if parsing enabled
  "search_gemini_params": {},           // Gemini-specific search parameters
  "validate_gemini_params": {},         // Gemini-specific validation parameters
  "parsing_gemini_params": {},          // Gemini-specific parsing parameters
  "parsing_openai_params": {},          // OpenAI-specific parsing parameters
  "api_keys": {
    "gemini": {
      "primary": "string",              // Required: Primary Gemini API key
      "secondary": "string"             // Optional: Backup Gemini API key
    },
    "openai": "string"                  // Required if using OpenAI provider
  }
}
```

**Response Structure:**

```json
{
  "success": true,
  "data": {
    "completed": true,                  // Overall completion status
    "final_content": "any",             // Final structured content (if parsing)
    "search_results": [],               // Raw search results
    "search_metadata": {},              // Search operation metadata
    "validated_content": "string",      // AI-validated content (if validation)
    "validation_analysis": {},          // Validation results (if validation)
    "execution_metrics": {
      "token_usage": {},                // Token consumption by operation
      "session_id": "string",           // Session identifier
      "correlation_id": "string",       // Request correlation ID
      "execution_time_seconds": 1.23,   // Total execution time
      "total_nodes_executed": 5,        // Number of pipeline nodes executed
      "nodes_completion_status": {
        "search": true,
        "validation": false,
        "parsing": true
      }
    }
  },
  "execution_time": 1.23,              // API-level execution time
  "correlation_id": "string"           // Request tracking ID
}
```

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the latest developments in quantum computing?",
    "config": {
      "validate": true,
      "parse": true,
      "schema": "{\"title\":{\"type\":\"string\"},\"summary\":{\"type\":\"string\"},\"key_developments\":{\"type\":\"array\",\"items\":{\"type\":\"string\"}}}"
    },
    "search_model_name": "gemini-2.5-flash",
    "validate_model_name": "gemini-2.5-flash",
    "parse_model_name": "gemini-2.5-flash",
    "parsing_provider": "gemini",
    "api_keys": {
      "gemini": {
        "primary": "your_gemini_api_key"
      }
    }
  }'
```

### 2. Configuration Management

#### `GET /api/v1/configurations`

Retrieves all saved analysis configurations.

**Response:**
```json
{
  "configurations": [
    {
      "id": "uuid",
      "name": "string",
      "description": "string",
      "config": {},
      "created_at": "2025-01-01T00:00:00",
      "updated_at": "2025-01-01T00:00:00"
    }
  ],
  "total": 1
}
```

#### `POST /api/v1/configurations`

Saves a new analysis configuration for reuse.

**Request:**
```json
{
  "name": "My Analysis Config",
  "description": "Configuration for market research analysis",
  "config": {
    "validate": true,
    "parse": true,
    "schema": "{...}"
  },
  "parsing_provider": "gemini",
  "search_model_name": "gemini-2.5-flash",
  "validate_model_name": "gemini-2.5-flash",
  "parse_model_name": "gemini-2.5-flash",
  "api_keys": {
    "gemini": {
      "primary": "your_key"
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "id": "uuid",
  "message": "Analysis configuration saved successfully",
  "configuration": {
    "id": "uuid",
    "name": "My Analysis Config",
    // ... full configuration
  }
}
```

#### `PUT /api/v1/configurations/{config_id}`

Updates an existing configuration.

#### `DELETE /api/v1/configurations/{config_id}`

Deletes a saved configuration.

#### `GET /api/v1/configurations/{config_id}`

Retrieves a specific configuration by ID.

### 3. Health and Status

#### `GET /api/v1/health`

Comprehensive health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T00:00:00",
  "version": "1.0.0",
  "groundcite_ready": true
}
```

#### `GET /`

Basic health check and API information.

## Model Configuration

### Available Models

#### Gemini Models
- `gemini-2.5-flash` - Fast, efficient model for most tasks
- `gemini-1.5-pro` - High-quality model for complex analysis
- `gemini-1.0-pro` - Balanced performance model

#### OpenAI Models
- `gpt-4` - High-quality general purpose model
- `gpt-4-turbo` - Fast, capable model
- `gpt-3.5-turbo` - Cost-effective option

### Provider-Specific Parameters

#### Gemini Parameters
```json
{
  "temperature": 0.7,          // Creativity level (0-1)
  "top_p": 0.9,               // Nucleus sampling
  "top_k": 40,                // Top-k sampling
  "max_output_tokens": 2048,   // Maximum response length
  "candidate_count": 1,        // Number of candidates
  "stop_sequences": []         // Stop generation sequences
}
```

#### OpenAI Parameters
```json
{
  "temperature": 0.7,          // Creativity level (0-2)
  "max_tokens": 2048,          // Maximum response length
  "top_p": 1.0,               // Nucleus sampling
  "frequency_penalty": 0.0,    // Frequency penalty (0-2)
  "presence_penalty": 0.0,     // Presence penalty (0-2)
  "stop": []                   // Stop sequences
}
```

## Schema Definition

### Parsing Schema Format

The parsing schema follows JSON Schema specification:

```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "Main title of the content"
    },
    "summary": {
      "type": "string",
      "description": "Brief summary of key points"
    },
    "key_findings": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of important findings"
    },
    "confidence_score": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Confidence in the analysis (0-1)"
    },
    "sources": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "url": {"type": "string"},
          "title": {"type": "string"},
          "relevance": {"type": "number"}
        },
        "required": ["url", "title"]
      }
    }
  },
  "required": ["title", "summary"]
}
```

### Common Schema Patterns

#### Research Analysis
```json
{
  "type": "object",
  "properties": {
    "research_question": {"type": "string"},
    "methodology": {"type": "string"},
    "findings": {
      "type": "array",
      "items": {"type": "string"}
    },
    "conclusion": {"type": "string"},
    "limitations": {"type": "string"}
  }
}
```

#### Market Analysis
```json
{
  "type": "object",
  "properties": {
    "market_size": {"type": "string"},
    "key_players": {
      "type": "array",
      "items": {"type": "string"}
    },
    "trends": {
      "type": "array",
      "items": {"type": "string"}
    },
    "opportunities": {"type": "string"},
    "risks": {"type": "string"}
  }
}
```

## Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": "Error description",
  "execution_time": 1.23,
  "correlation_id": "uuid"
}
```

### Common Error Codes

| HTTP Code | Error Type | Description |
|-----------|------------|-------------|
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid API keys |
| 404 | Not Found | Configuration not found |
| 422 | Validation Error | Request validation failed |
| 500 | Internal Error | Server processing error |
| 503 | Service Unavailable | AI provider unavailable |

### Error Examples

#### Missing API Key
```json
{
  "success": false,
  "error": "Gemini API key is required",
  "execution_time": 0.001,
  "correlation_id": "abc123"
}
```

#### Invalid Schema
```json
{
  "success": false,
  "error": "Invalid JSON schema provided",
  "execution_time": 0.1,
  "correlation_id": "def456"
}
```

## Rate Limiting

Currently not implemented but recommended for production:

- **Per API Key**: 1000 requests per hour
- **Per IP**: 100 requests per hour
- **Concurrent**: 10 concurrent requests per key

## Best Practices

### 1. Request Optimization

- Use appropriate model sizes for your use case
- Set reasonable token limits to control costs
- Include only necessary parameters
- Use correlation IDs for tracking

### 2. Error Handling

```javascript
async function analyzeQuery(query, config) {
  try {
    const response = await fetch('/api/v1/analyze', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        query,
        config,
        // ... other parameters
      })
    });
    
    const result = await response.json();
    
    if (!result.success) {
      throw new Error(result.error);
    }
    
    return result.data;
  } catch (error) {
    console.error('Analysis failed:', error);
    throw error;
  }
}
```

### 3. Configuration Reuse

```python
import requests

# Save frequently used configurations
config_response = requests.post('/api/v1/configurations', json={
    "name": "Standard Analysis",
    "config": {"validate": True, "parse": True},
    # ... other settings
})

config_id = config_response.json()['id']

# Reuse configuration
analysis_response = requests.post('/api/v1/analyze', json={
    "query": "New query",
    "configuration_id": config_id  # Future feature
})
```

### 4. Monitoring

Track important metrics:
- Request latency
- Token usage patterns
- Error rates
- Success rates by query type

## SDK and Client Libraries

### Python Client Example

```python
import asyncio
import aiohttp

class GroundCiteClient:
    def __init__(self, base_url="http://localhost:8000", gemini_key=None):
        self.base_url = base_url
        self.gemini_key = gemini_key
    
    async def analyze(self, query, validate=False, parse=False, schema=None):
        async with aiohttp.ClientSession() as session:
            payload = {
                "query": query,
                "config": {
                    "validate": validate,
                    "parse": parse,
                    "schema": schema or "{}"
                },
                "search_model_name": "gemini-2.5-flash",
                "parsing_provider": "gemini",
                "api_keys": {
                    "gemini": {"primary": self.gemini_key}
                }
            }
            
            if validate:
                payload["validate_model_name"] = "gemini-2.5-flash"
            if parse:
                payload["parse_model_name"] = "gemini-2.5-flash"
            
            async with session.post(
                f"{self.base_url}/api/v1/analyze",
                json=payload
            ) as response:
                result = await response.json()
                if not result["success"]:
                    raise Exception(result["error"])
                return result["data"]

# Usage
client = GroundCiteClient(gemini_key="your_key")
result = asyncio.run(client.analyze("What is AI?", validate=True))
```

### JavaScript Client Example

```javascript
class GroundCiteClient {
  constructor(baseUrl = 'http://localhost:8000', geminiKey = null) {
    this.baseUrl = baseUrl;
    this.geminiKey = geminiKey;
  }
  
  async analyze(query, options = {}) {
    const {
      validate = false,
      parse = false,
      schema = '{}',
      provider = 'gemini'
    } = options;
    
    const payload = {
      query,
      config: { validate, parse, schema },
      search_model_name: 'gemini-2.5-flash',
      parsing_provider: provider,
      api_keys: {
        gemini: { primary: this.geminiKey }
      }
    };
    
    if (validate) payload.validate_model_name = 'gemini-2.5-flash';
    if (parse) payload.parse_model_name = 'gemini-2.5-flash';
    
    const response = await fetch(`${this.baseUrl}/api/v1/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    const result = await response.json();
    if (!result.success) {
      throw new Error(result.error);
    }
    
    return result.data;
  }
}

// Usage
const client = new GroundCiteClient('http://localhost:8000', 'your_key');
const result = await client.analyze('What is quantum computing?', {
  validate: true,
  parse: true,
  schema: '{"summary": {"type": "string"}}'
});
```

This API documentation provides comprehensive coverage of all endpoints, request/response formats, error handling, and best practices for integrating with the GroundCite service.
