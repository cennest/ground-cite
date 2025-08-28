# GroundCite - AI-Powered Query Analysis Library

![Version](https://img.shields.io/badge/version-1.0.3-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**GroundCite** is an advanced AI-powered query analysis library that provides comprehensive search, validation, and structured data extraction capabilities. Built with a modular, graph-based architecture, it supports multiple AI providers and offers both CLI and REST API interfaces.

## 🚀 Features

### Core Capabilities
- **Multi-Provider AI Support**: Seamlessly integrate with Google Gemini and OpenAI models
- **Graph-Based Pipeline**: State-driven execution with automatic retry logic and error handling
- **Web Search Integration**: Intelligent web search with site filtering and content aggregation
- **AI-Powered Validation**: Optional content validation using advanced AI models
- **Structured Data Parsing**: Extract structured data using custom JSON schemas
- **Comprehensive Logging**: Detailed execution metrics and token usage tracking

### Interface Options
- **Command Line Interface (CLI)**: Feature-rich CLI with rich text formatting
- **REST API**: FastAPI-based web service for HTTP integration
- **Python Library**: Direct integration into Python applications

### Advanced Features
- **Retry Logic**: Robust error handling with configurable retry mechanisms
- **Token Usage Tracking**: Monitor AI service consumption and costs
- **Correlation Tracking**: End-to-end request tracing and debugging
- **Configuration Management**: Flexible settings with validation
- **Site Filtering**: Include/exclude specific domains in search results

## 📋 Requirements

- **Python**: 3.10 or higher
- **Dependencies**: See [requirements.txt](requirements.txt) for full list

### Key Dependencies
- `langgraph` - Graph-based workflow orchestration
- `google-genai` - Google Gemini AI integration
- `openai` - OpenAI API integration
- `fastapi` - REST API framework
- `click` - CLI framework
- `rich` - Enhanced terminal output
- `pydantic` - Data validation and settings

## 🔧 Installation

### From Source
```bash
git clone https://github.com/cennest/ground-cite.git
cd ground-cite/GroundCite
pip install -e .
```

### Using pip (when published)
```bash
pip install gemini-groundcite
```

## ⚡ Quick Start

### 1. Basic CLI Usage

```bash
# Simple query analysis
gemini-groundcite analyze -q "What are the latest developments in AI?"

# With validation and parsing
gemini-groundcite analyze -q "Company X financials" --validate --parse

# Using OpenAI provider
gemini-groundcite analyze -q "Market trends" --provider openai --openai-key your_key
```

### 2. Python Library Usage

```python
from gemini_groundcite.config.settings import AppSettings
from gemini_groundcite.core.agents import AIAgent

# Configure settings
settings = AppSettings()
settings.ANALYSIS_CONFIG.query = "What are quantum computing breakthroughs?"
settings.ANALYSIS_CONFIG.validate = True
settings.ANALYSIS_CONFIG.parse = True
settings.AI_CONFIG.gemini_ai_key_primary = "your_gemini_key"

# Initialize and run analysis
agent = AIAgent(settings=settings)
results = await agent.analyze_query()

print(f"Analysis completed: {results['completed']}")
print(f"Results: {results['final_content']}")
```

### 3. REST API Usage

```bash
# Start the API server
python -m gemini_groundcite.main

# Make analysis requests
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Latest AI developments",
    "config": {"validate": true, "parse": true},
    "search_model_name": "gemini-2.5-flash",
    "api_keys": {"gemini": {"primary": "your_key"}}
  }'
```

## 🏗️ Architecture

GroundCite uses a sophisticated graph-based architecture that orchestrates multiple AI processing stages:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Entry Point   │    │  Configuration  │    │   AI Providers  │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ CLI         │ │    │ │ Settings    │ │    │ │ Google      │ │
│ │ Interface   │ │    │ │ Validation  │ │    │ │ Gemini      │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ REST API    │ │────┤ │ Dependency  │ │────┤ │ OpenAI      │ │
│ │ (FastAPI)   │ │    │ │ Injection   │ │    │ │ Client      │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    └─────────────────┘    └─────────────────┘
│ │ Python Lib  │ │
│ │ Direct      │ │
│ └─────────────┘ │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   AI Agent      │
│  Orchestrator   │
│                 │
│ ┌─────────────┐ │
│ │ Graph       │ │
│ │ Executor    │ │
│ └─────────────┘ │
└─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Graph-Based Pipeline                         │
│                                                                │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │Orchestration│    │   Search    │    │Search Aggr. │         │
│  │    Node     │───▶│    Node     │───▶│    Node     │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                                      │               │
│         ▼                                      ▼               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │    END      │    │ Validation  │    │Valid. Aggr. │         │
│  │   (Final)   │◀───│    Node     │◀───│    Node     │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         ▲                                      │               │
│         │                                      ▼               │
│         │             ┌─────────────┐    ┌─────────────┐       │
│         └─────────────│   Parsing   │◀───│   Parsing   │       │
│                       │   Node      │    │   Router    │       │
│                       └─────────────┘    └─────────────┘       │
│                                                                │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. **AI Agent** (`gemini_groundcite.core.agents.AIAgent`)
- Central orchestrator for query analysis
- Manages configuration and pipeline execution
- Provides retry logic and error handling

#### 2. **Graph Executor** (`gemini_groundcite.core.executors.GraphExecutor`)
- Implements the graph-based workflow using LangGraph
- Manages state transitions and node execution
- Handles concurrent operations and routing

#### 3. **Processing Nodes**
- **Orchestration Node**: Controls overall execution flow
- **Search Node**: Performs web searches
- **Search Aggregator**: Consolidates search results
- **Validation Node**: AI-powered content validation
- **Validation Aggregator**: Processes validation results
- **Parsing Node**: Extracts structured data

#### 4. **AI Clients**
- **Google Gemini Client**: Integration with Google's AI models
- **OpenAI Client**: Integration with OpenAI's models
- **Client Utils**: Shared utilities and abstractions

#### 5. **Configuration System**
- **AppSettings**: Centralized configuration management
- **Validation**: Configuration validation and error reporting

## 📊 Data Flow

### 1. Request Processing
```
User Query → Configuration → AI Agent → Graph Executor
```

### 2. Pipeline Execution
```
Orchestration → Search → Aggregation → [Validation] → [Parsing] → Results
```

### 3. Response Generation
```
Results → Metrics Collection → Logging → Response Formatting
```

## 🔨 CLI Reference

### Main Commands

#### `analyze` - Analyze a query
```bash
gemini-groundcite analyze [OPTIONS]

Options:
  -q, --query TEXT            Query to analyze [required]
  -v, --validate             Enable AI-powered validation
  -p, --parse                Enable structured data parsing
  -s, --schema TEXT          JSON schema for parsing
  --gemini-key TEXT          Google Gemini API key
  --openai-key TEXT          OpenAI API key
  --provider [gemini|openai] AI provider for parsing
  --search_model TEXT        Model for search operations
  --validate_model TEXT      Model for validation
  --parse_model TEXT         Model for parsing
  --verbose                  Show detailed execution info
```

#### `config` - Manage configuration
```bash
gemini-groundcite config [OPTIONS]

Options:
  --show        Show current configuration
  --validate    Validate configuration
```

#### `version` - Show version information
```bash
gemini-groundcite version
```

### Examples

```bash
# Basic analysis
gemini-groundcite analyze -q "What is quantum computing?"

# Full pipeline with validation and parsing
gemini-groundcite analyze \
  -q "Latest AI research findings" \
  --validate \
  --parse \
  --schema '{"summary": {"type": "string"}, "findings": {"type": "array"}}' \
  --verbose

# Using OpenAI for parsing
gemini-groundcite analyze \
  -q "Market analysis" \
  --provider openai \
  --openai-key your_openai_key \
  --search_model gemini-2.5-flash \
  --parse_model gpt-4

# Configuration management
gemini-groundcite config --show
gemini-groundcite config --validate
```

## 🌐 REST API Reference

### Base URL
```
http://localhost:8000
```

### Endpoints

#### `POST /api/v1/analyze` - Analyze Query
Performs comprehensive query analysis with configurable pipeline stages.

**Request Body:**
```json
{
  "query": "string",
  "system_instruction": "string",
  "config": {
    "validate": "boolean",
    "parse": "boolean",
    "schema": "string",
    "siteConfig": {
      "includeList": "string",
      "excludeList": "string"
    }
  },
  "parsing_provider": "gemini|openai",
  "search_model_name": "string",
  "validate_model_name": "string",
  "parse_model_name": "string",
  "search_gemini_params": {},
  "validate_gemini_params": {},
  "parsing_gemini_params": {},
  "parsing_openai_params": {},
  "api_keys": {
    "gemini": {
      "primary": "string",
      "secondary": "string"
    },
    "openai": "string"
  }
}
```

**Response:**
```json
{
  "success": "boolean",
  "data": {
    "completed": "boolean",
    "final_content": "any",
    "search_results": "array",
    "validated_content": "string",
    "execution_metrics": {
      "execution_time_seconds": "float",
      "token_usage": "object",
      "correlation_id": "string"
    }
  },
  "execution_time": "float",
  "correlation_id": "string"
}
```

#### `GET /api/v1/health` - Health Check
Returns API health status and system information.

#### `GET /api/v1/configurations` - List Configurations
Retrieves all saved analysis configurations.

#### `POST /api/v1/configurations` - Save Configuration
Saves a reusable analysis configuration.

#### `PUT /api/v1/configurations/{id}` - Update Configuration
Updates an existing configuration.

#### `DELETE /api/v1/configurations/{id}` - Delete Configuration
Removes a saved configuration.

### Example API Usage

```python
import requests

# Analyze query
response = requests.post('http://localhost:8000/api/v1/analyze', json={
    "query": "What are the benefits of renewable energy?",
    "config": {
        "validate": True,
        "parse": True,
        "schema": '{"summary": {"type": "string"}, "benefits": {"type": "array"}}'
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
})

result = response.json()
print(f"Analysis completed: {result['data']['completed']}")
print(f"Results: {result['data']['final_content']}")
```

## ⚙️ Configuration

### Configuration File (Python)
```python
from gemini_groundcite.config.settings import AppSettings

settings = AppSettings()

# Analysis Configuration
settings.ANALYSIS_CONFIG.validate = True
settings.ANALYSIS_CONFIG.parse = True
settings.ANALYSIS_CONFIG.parse_schema = '{"summary": {"type": "string"}}'

# AI Configuration
settings.AI_CONFIG.gemini_ai_key_primary = "your_key"
settings.AI_CONFIG.parsing_provider = "gemini"
settings.AI_CONFIG.search_model_name = "gemini-2.5-flash"

# Validate configuration
is_valid, errors = settings.validate_all_configurations()
if not is_valid:
    print("Configuration errors:", errors)
```

## 🔍 Advanced Usage

### Custom Schema Parsing
```python
# Define custom JSON schema for structured extraction
schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "key_points": {
            "type": "array",
            "items": {"type": "string"}
        },
        "confidence_score": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
        },
        "sources": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "title": {"type": "string"}
                }
            }
        }
    },
    "required": ["title", "summary", "key_points"]
}

# Use in CLI
gemini-groundcite analyze \
  -q "Climate change impacts" \
  --parse \
  --schema '$(echo $schema | jq -c)'
```

### Site Filtering
```python
# Include only specific domains
settings.ANALYSIS_CONFIG.included_sites = "nature.com,science.org,arxiv.org"

# Exclude unreliable sources
settings.ANALYSIS_CONFIG.excluded_sites = "example-spam.com,unreliable.net"
```

## 📈 Monitoring and Logging

### Token Usage Tracking
```python
# Access token usage from results
result = await agent.analyze_query()
token_usage = result['execution_metrics']['token_usage']

print(f"Search tokens: {token_usage.get('search', [])}")
print(f"Validation tokens: {token_usage.get('validation', [])}")
print(f"Parsing tokens: {token_usage.get('parse', [])}")
```

### Execution Metrics
```python
metrics = result['execution_metrics']
print(f"Execution time: {metrics['execution_time_seconds']:.2f}s")
print(f"Nodes executed: {metrics['total_nodes_executed']}")
print(f"Correlation ID: {metrics['correlation_id']}")
print(f"Completion status: {metrics['nodes_completion_status']}")
```

### Logging Configuration
```python
from gemini_groundcite.config.logger import AppLogger

# Access logger instance
logger = AppLogger()

# Custom logging with correlation tracking
logger.log_info(
    "Custom analysis step completed",
    custom_dimensions={
        "correlation_id": "custom_id",
        "operation": "custom_step",
        "duration": 1.23
    }
)
```

### Production Considerations
- Use environment variables for API keys
- Configure proper logging levels
- Set up monitoring and alerting
- Implement rate limiting
- Use database for configuration storage
- Set up load balancing for high traffic

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone the repository
git clone https://github.com/cennest/ground-cite.git
cd ground-cite/GroundCite

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black gemini_groundcite/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **GitHub Issues**: [Report bugs and request features](https://github.com/cennest/ground-cite/issues)
- **Documentation**: [Full documentation](https://github.com/cennest/ground-cite)
- **Email**: anshulee@cennest.com

## 🏆 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph) for workflow orchestration
- Powered by Google Gemini and OpenAI APIs
- CLI interface built with [Click](https://click.palletsprojects.com/) and [Rich](https://rich.readthedocs.io/)
- Web API built with [FastAPI](https://fastapi.tiangolo.com/)

---

**GroundCite** - *Empowering intelligent query analysis with AI*
