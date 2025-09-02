# GroundCite Architecture - Quick Overview

## System Overview
GroundCite is an AI-powered query analysis library that processes user queries through a multi-stage pipeline to provide comprehensive research results.

## Core Components

### 1. Pipeline Flow
```
Query → Search → Validate → Parse → Results
```

### 2. Key Components
- **AI Agent** - Main orchestrator
- **Search Executor** - Web search operations
- **Validation Aggregator** - Content validation (optional)
- **Parsing Node** - Structured data extraction (optional)

### 3. AI Providers
- **Google Gemini** - Primary AI provider
- **OpenAI** - Alternative parsing provider

## Data Flow

1. **Input**: User query + configuration
2. **Search**: Find relevant web content
3. **Validate**: AI-powered content validation (if enabled)
4. **Parse**: Extract structured data (if enabled)
5. **Output**: Analysis results + metadata

## Deployment Options

### Local Development
```
Python CLI → Core Library → AI APIs
```

### REST API
```
HTTP Request → FastAPI → Core Library → AI APIs
```

### Azure Functions
```
HTTP Trigger → Function App → Core Library → AI APIs
```

## Configuration
- **Analysis Config**: Query settings, validation, parsing
- **AI Config**: Models, API keys, parameters
- **Site Config**: Include/exclude lists for search

## Error Handling
- Retry logic for each pipeline stage
- Comprehensive error logging
- Graceful degradation

## Performance
- Async operations
- Token usage tracking
- Configurable timeouts
- Memory-efficient processing

## Security
- API key management
- Input validation
- Error sanitization
- Secure configuration handling
