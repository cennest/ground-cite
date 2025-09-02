# GroundCite Architecture - Quick Overview

## System Overview
GroundCite is an AI-powered query analysis library that processes user queries through a multi-stage pipeline to provide comprehensive research results.

## Flow Chart

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    User     │    │   Config    │    │  AI Agent  │
│   Query     │───▶│  Settings   │───▶│ (Orchestr.) │
└─────────────┘    └─────────────┘    └─────┬───────┘
                                             │
                   ┌─────────────────────────▼─────────────────────────┐
                   │                PIPELINE                          │
                   │                                                  │
┌─────────────┐    │  ┌─────────────┐    ┌─────────────┐    ┌─────────┴───┐
│   Search    │◄───┼──┤   Search    │    │ Validation  │    │   Parsing   │
│   Results   │    │  │  Executor   │───▶│ Aggregator  │───▶│    Node     │
└─────────────┘    │  └─────────────┘    └─────────────┘    └─────────────┘
                   │        │                   │                   │
                   │        ▼                   ▼                   ▼
                   │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
                   │  │   Retry     │    │   Retry     │    │   Retry     │
                   │  │   Logic     │    │   Logic     │    │   Logic     │
                   │  └─────────────┘    └─────────────┘    └─────────────┘
                   └──────────────────────────────────────────────────────┘
                                             │
                   ┌─────────────────────────▼─────────────────────────┐
                   │                 RESULTS                          │
                   │                                                  │
                   │  ┌─────────────┐    ┌─────────────┐    ┌─────────┴───┐
                   │  │  Analysis   │    │  Execution  │    │   Error     │
                   │  │   Data      │    │  Metadata   │    │  Handling   │
                   │  └─────────────┘    └─────────────┘    └─────────────┘
                   └──────────────────────────────────────────────────────┘
```

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
