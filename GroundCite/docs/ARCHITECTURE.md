# GroundCite Architecture Documentation

## Table of Contents
- [System Overview](#system-overview)
- [Core Components](#core-components)
- [Data Flow](#data-flow)
- [State Management](#state-management)
- [Processing Pipeline](#processing-pipeline)
- [Integration Points](#integration-points)
- [Scalability Considerations](#scalability-considerations)

## System Overview

GroundCite is designed as a modular, graph-based AI query analysis system that can be deployed as a library, CLI tool, or web service. The architecture emphasizes flexibility, maintainability, and extensibility.

### Design Principles

1. **Modularity**: Each component has a single responsibility and can be independently tested and modified
2. **Configurability**: All behavior is controlled through configuration objects
3. **Extensibility**: New AI providers and processing nodes can be easily added
4. **Observability**: Comprehensive logging and metrics throughout the system
5. **Fault Tolerance**: Retry mechanisms and graceful error handling

## Core Components

### 1. Configuration Layer (`gemini_groundcite.config`)

```
config/
├── __init__.py
├── settings.py      # AppSettings - Central configuration
└── logger.py        # AppLogger - Logging infrastructure
```

**Responsibilities:**
- Centralized configuration management
- Environment variable parsing
- Configuration validation
- Logging setup and management

**Key Classes:**
- `AppSettings`: Main configuration container
- `AppLogger`: Standardized logging interface

### 2. Dependency Injection (`gemini_groundcite.core.di`)

```
di/
├── __init__.py
└── core_di.py       # CoreDi - IoC container
```

**Responsibilities:**
- Dependency injection container
- Service registration and resolution
- Lifecycle management

### 3. AI Agents Layer (`gemini_groundcite.core.agents`)

```
agents/
├── __init__.py
├── ai_agent.py      # AIAgent - Main orchestrator
└── clients/         # AI provider implementations
    ├── __init__.py
    ├── google_gen_ai_client.py
    └── open_ai_client.py
```

**Responsibilities:**
- High-level query analysis orchestration
- AI provider abstraction
- Configuration validation
- Error handling and retry logic

### 4. Execution Engine (`gemini_groundcite.core.executors`)

```
executors/
├── __init__.py
├── graph_executor.py      # Main graph workflow executor
├── graph_state.py         # State management classes
├── core_helper.py         # Utility functions
└── nodes/                 # Processing node implementations
    ├── orchestration_node.py
    ├── search_node.py
    ├── search_aggregator_node.py
    ├── validation_node.py
    ├── validation_aggregator_node.py
    └── parse_node.py
```

**Responsibilities:**
- Graph-based workflow execution
- State management across pipeline stages
- Node routing and conditional logic
- Metrics collection and performance tracking

### 5. Data Models (`gemini_groundcite.core.models`)

```
models/
├── __init__.py
├── citation.py           # Citation data structures
└── search_request.py     # Search request models
```

**Responsibilities:**
- Data structure definitions
- Validation schemas
- Type safety

### 6. Interfaces (`gemini_groundcite`)

```
gemini_groundcite/
├── cli.py          # Command-line interface
├── main.py         # FastAPI web service
└── __main__.py     # Python module entry point
```

**Responsibilities:**
- User interface implementations
- Request/response handling
- Input validation

## Data Flow

### 1. Request Initiation

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    CLI      │    │  REST API   │    │ Python Lib  │
│ Interface   │    │  (FastAPI)  │    │   Direct    │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                          ▼
                 ┌─────────────┐
                 │ Configuration│
                 │  Validation │
                 └──────┬──────┘
                        │
                        ▼
                 ┌─────────────┐
                 │  AI Agent   │
                 │Orchestrator │
                 └──────┬──────┘
                        │
                        ▼
                 ┌─────────────┐
                 │   Graph     │
                 │  Executor   │
                 └─────────────┘
```

### 2. Pipeline Execution Flow

```
                    ┌─────────────────┐
                    │ Orchestration   │◄──┐
                    │     Node        │   │
                    └────────┬────────┘   │
                             │            │
                    ┌────────▼────────┐   │
                    │     Search      │   │
                    │      Node       │   │
                    └────────┬────────┘   │
                             │            │
                    ┌────────▼────────┐   │ Retry Logic:
                    │    Search       │   │ If Search Aggregator
                    │  Aggregator     │◄──┤ fails, retry by going
                    └────────┬────────┘   │ back to Search Node
                             │            │
                             ▼            │
                    ┌─────────────────┐   │ 
                    │   Validation    │   │ 
                    │      Node       │   │ 
                    └────────┬────────┘   │
                             │            │
                    ┌────────▼────────┐   │ Retry Logic:
                    │   Validation    │   │ If Validation Aggregator
                    │   Aggregator    │◄──┤ fails, retry by going
                    └────────┬────────┘   │ back to Validation Node
                             │            │
                             ▼            │
                    ┌─────────────────┐   │ Retry Logic:
                    │    Parsing      │   │ If Parsing Node
                    │     Node        │◄──┤ fails, retry by going
                    └────────┬────────┘   │ back to itself
                             │            │
                             │            │
                             ▼            │
                    ┌─────────────────┐   │
                    │      END        │◄──┘
                    │   (Results)     │
                    └─────────────────┘
```

### 3. State Transitions

Each node in the pipeline manages its own state while contributing to the global workflow state:

```python
# Example state flow through the pipeline
AgentState = {
    "orchestration_state": OrchestrationState(),
    "search_state": SearchState(results=[]),
    "validation_state": ValidationState(results=[]),
    "parse_state": ParseState(schema="..."),
    "workflow_metrics": WorkflowMetrics(),
    # Node-specific states for tracking execution
    "search_aggregator_state": NodeState(),
    "validation_aggregator_state": NodeState(),
    # ... other node states
}
```

## State Management

### State Classes Hierarchy

```
Result (Base)
├── SearchResult
└── ValidateResult

NodeState (Base execution state)
├── ParseState (extends with schema)
└── ... (other specialized states)

OrchestrationState (Global workflow state)
├── search_content
├── validated_content
├── final_content
├── completion status
└── metadata

WorkflowMetrics (Performance tracking)
├── timing information
├── token usage
├── execution counts
└── correlation tracking
```

### State Flow Patterns

1. **Immutable State Updates**: Each node receives state and returns updated state
2. **Merge Operations**: Custom merge functions handle state consolidation
3. **Conditional Routing**: State determines next execution path
4. **Individual Node Retry Mechanisms**: Each processing node has its own retry logic:
   - **Search Aggregator**: If fails, routes back to Search Node
   - **Validation Aggregator**: If fails, routes back to Validation Node  
   - **Parsing Node**: If fails, retries itself with incremented counter
5. **Retry Counters**: Each node state tracks retry attempts vs. max retries

## Processing Pipeline

### Node Types and Responsibilities

#### 1. Orchestration Node
- **Purpose**: Central coordination and flow control
- **Input**: Initial query and configuration
- **Output**: Routing decisions based on enabled features
- **Logic**: Determines whether to run search, validation, parsing

#### 2. Search Node
- **Purpose**: Web search execution
- **Input**: Query and search parameters
- **Output**: Raw search results
- **Logic**: Multi-tier search with site filtering

#### 3. Search Aggregator Node
- **Purpose**: Search result processing and consolidation
- **Input**: Raw search results
- **Output**: Processed and formatted search content
- **Logic**: Content deduplication, formatting, metadata extraction
- **Retry**: If aggregation fails, routes back to Search Node for retry

#### 4. Validation Node
- **Purpose**: AI-powered content validation
- **Input**: Search results and validation prompt
- **Output**: Validated content with confidence scores
- **Logic**: AI model evaluation of content quality and relevance

#### 5. Validation Aggregator Node
- **Purpose**: Validation result processing
- **Input**: Validation responses
- **Output**: Consolidated validation results
- **Logic**: Confidence scoring, content filtering
- **Retry**: If aggregation fails, routes back to Validation Node for retry

#### 6. Parsing Node
- **Purpose**: Structured data extraction
- **Input**: Validated content and JSON schema
- **Output**: Structured data conforming to schema
- **Logic**: AI-powered parsing with validation retry
- **Retry**: If parsing fails, retries itself with adjusted parameters

### Routing Logic

```python
# Example routing decision logic for each node

def orchestration_router(state: AgentState) -> str:
    """Route based on configuration and current state"""
    if not state.search_state.completed:
        return "search"
    elif settings.validate and not state.validation_state.completed:
        return "validation"
    elif settings.parse and not state.parse_state.completed:
        return "parse"
    else:
        return "end"

def search_aggregator_router(state: AgentState) -> str:
    """Route based on search aggregation results"""
    if state.search_aggregator_state.retry_count < state.search_aggregator_state.max_retries:
        if not state.search_aggregator_state.completed:
            return "search"  # Retry by going back to search
    return "continue"  # Proceed to next stage

def validation_aggregator_router(state: AgentState) -> str:
    """Route based on validation aggregation results"""
    if state.validation_aggregator_state.retry_count < state.validation_aggregator_state.max_retries:
        if not state.validation_aggregator_state.completed:
            return "validation"  # Retry by going back to validation
    return "continue"  # Proceed to next stage

def parsing_node_router(state: AgentState) -> str:
    """Route based on parsing results"""
    if state.parse_state.retry_count < state.parse_state.max_retries:
        if not state.parse_state.completed:
            return "retry"  # Retry parsing itself
    return "continue"  # Complete execution
```

## Integration Points

### AI Provider Integration

```
                    ┌─────────────────┐
                    │   Client        │
                    │   Factory       │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
   ┌──────▼──────┐  ┌────────▼────────┐  ┌──────▼──────┐
   │   Google    │  │     OpenAI      │  │   Future    │
   │   Gemini    │  │     Client      │  │   Provider  │
   │   Client    │  │                 │  │             │
   └─────────────┘  └─────────────────┘  └─────────────┘
```

**Common Interface:**
```python
async def generate_content(
    prompt: str,
    model: str,
    parameters: Dict[str, Any]
) -> GenerationResponse
```

### External Service Integration

1. **Web Search APIs**: Abstracted through search nodes
2. **Logging Services**: Centralized through AppLogger
3. **Configuration Sources**: Environment variables, files, databases
4. **Monitoring Systems**: Metrics export through standardized interfaces

## Scalability Considerations

### Horizontal Scaling

1. **Stateless Design**: All state is passed through the pipeline
2. **Async/Await**: Non-blocking operations throughout
3. **Configurable Concurrency**: Adjustable parallel execution limits
4. **Load Distribution**: Multiple instances can share workload

### Performance Optimization

1. **Token Usage Tracking**: Monitor and optimize AI service costs
2. **Caching Strategies**: Results caching at multiple levels
3. **Batching**: Group similar operations for efficiency
4. **Retry Logic**: Intelligent backoff and retry strategies

### Resource Management

```python
# Concurrent execution with limits
async def aexec(
    collection: List[Task],
    exec: Callable,
    max_concurrent_tasks: int = 5,
    timeout_per_task: Optional[float] = None
) -> List[Result]:
    """Execute tasks with concurrency control"""
```

### Monitoring and Observability

1. **Correlation IDs**: Track requests end-to-end
2. **Structured Logging**: Consistent log format with dimensions
3. **Metrics Collection**: Performance counters and usage statistics
4. **Health Checks**: System readiness and dependency validation

## Extension Points

### Adding New AI Providers

1. Implement the common client interface
2. Register with the dependency injection container
3. Add configuration options
4. Update routing logic if needed

### Adding New Processing Nodes

1. Implement node function with proper signature
2. Add routing logic for the new node
3. Update state management if new state types needed
4. Add configuration options for the new functionality

### Custom Processing Logic

1. Extend existing nodes with additional logic
2. Add new pipeline stages through graph modification
3. Implement custom aggregation or validation logic
4. Add specialized output formatting

This architecture enables GroundCite to be both powerful and flexible, supporting current use cases while being extensible for future requirements.
