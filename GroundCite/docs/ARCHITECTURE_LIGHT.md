# GroundCite Architecture - Quick Overview

## System Overview
GroundCite is an AI-powered query analysis library that processes user queries through a multi-stage pipeline to provide comprehensive research results.

## 🏗️ Architecture

GroundCite uses a sophisticated graph-based architecture that orchestrates multiple AI processing stages:

```
┌─────────────────┐
│   Entry Point   │
│                 │
│ ┌─────────────┐ │
│ │     CLI     │ │
│ │ Interface   │ │
│ └─────────────┘ │
│                 │
│ ┌─────────────┐ │
│ │  REST API   │ │
│ │  (FastAPI)  │ │
│ └─────────────┘ │
│                 │
│ ┌─────────────┐ │
│ │ Python Lib  │ │
│ │   Direct    │ │
│ └─────────────┘ │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   AI Agent      │
│  Orchestrator   │
│                 │
│ ┌─────────────┐ │
│ │    Graph    │ │
│ │  Executor   │ │
│ └─────────────┘ │
└─────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────┐
│                   Graph-Based Pipeline                      │
│                                                              │
│ ┌─────────────┐    ┌─────────────┐    ┌─────────────┐       │
│ │Orchestration│───▶│   Search    │───▶│Search Aggr. │       │
│ │    Node     │    │    Node     │    │    Node     │       │
│ └─────────────┘    └─────────────┘    └─────────────┘       │
│         │                                     │             │
│         │                                     ▼             │
│         │              ┌─────────────┐    ┌─────────────┐    │
│         │              │ Validation  │◀───│Valid. Aggr. │    │
│         │              │    Node     │    │    Node     │    │
│         │              │ (Optional)  │    │ (Optional)  │    │
│         │              └─────────────┘    └─────────────┘    │
│         │                     │                 │           │
│         │                     ▼                 ▼           │
│         │              ┌─────────────┐    ┌─────────────┐    │
│         │              │   Parsing   │◀───│   Parsing   │    │
│         │              │    Node     │    │   Router    │    │
│         │              │ (Optional)  │    │ (Optional)  │    │
│         │              └─────────────┘    └─────────────┘    │
│         │                     │                             │
│         ▼                     ▼                             │
│ ┌─────────────┐               │                             │
│ │     END     │◀──────────────┘                             │
│ │  (Final)    │                                             │
│ └─────────────┘                                             │
└──────────────────────────────────────────────────────────────┘
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


