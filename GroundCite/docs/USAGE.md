# GroundCite Usage Guide

This guide provides comprehensive examples and best practices for using GroundCite in various scenarios.

## Table of Contents
- [Quick Start](#quick-start)
- [CLI Usage](#cli-usage)
- [Python Library Usage](#python-library-usage)
- [REST API Usage](#rest-api-usage)
- [Common Use Cases](#common-use-cases)
- [Advanced Configuration](#advanced-configuration)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Installation and Setup

```bash
# Install GroundCite
pip install gemini-groundcite

# Set up environment variables
export GEMINI_AI_KEY_PRIMARY="your_gemini_api_key"
export OPENAI_API_KEY="your_openai_api_key"  # Optional

# Verify installation
gemini-groundcite --help
```

### Your First Analysis

```bash
# Simple query analysis
gemini-groundcite analyze -q "What are the benefits of renewable energy?"

# With validation and structured parsing
gemini-groundcite analyze \
  -q "Latest developments in quantum computing" \
  --validate \
  --parse \
  --schema '{"summary": {"type": "string"}, "developments": {"type": "array"}}'
```

## CLI Usage

### Basic Commands

#### 1. Simple Analysis
```bash
gemini-groundcite analyze -q "How does machine learning work?"
```

#### 2. Analysis with Validation
```bash
gemini-groundcite analyze \
  -q "Climate change impact on agriculture" \
  --validate \
  --verbose
```

#### 3. Full Pipeline with Custom Schema
```bash
gemini-groundcite analyze \
  -q "Market analysis for electric vehicles" \
  --validate \
  --parse \
  --schema '{
    "market_size": {"type": "string"},
    "key_players": {"type": "array", "items": {"type": "string"}},
    "growth_rate": {"type": "string"},
    "challenges": {"type": "array", "items": {"type": "string"}}
  }' \
  --verbose
```

### Advanced CLI Options

#### Provider Configuration
```bash
# Use OpenAI for parsing
gemini-groundcite analyze \
  -q "AI ethics considerations" \
  --provider openai \
  --openai-key your_openai_key \
  --parse \
  --parse_model gpt-4

# Use different models for different stages
gemini-groundcite analyze \
  -q "Blockchain technology overview" \
  --search_model gemini-1.5-pro \
  --validate_model gemini-2.5-flash \
  --parse_model gpt-4 \
  --provider openai \
  --validate \
  --parse
```

#### Site Filtering
```bash
# Include only academic sources
gemini-groundcite analyze \
  -q "Quantum computing research" \
  --include-sites "arxiv.org,nature.com,science.org" \
  --parse

# Exclude unreliable sources
gemini-groundcite analyze \
  -q "Health benefits of meditation" \
  --exclude-sites "spam.com,unreliable.net"
```

### Configuration Management
```bash
# Show current configuration
gemini-groundcite config --show

# Validate configuration
gemini-groundcite config --validate

# Show version and system info
gemini-groundcite version
```

## Python Library Usage

### Basic Setup

```python
import asyncio
from gemini_groundcite.config.settings import AppSettings
from gemini_groundcite.core.agents import AIAgent

# Configure settings
settings = AppSettings()
settings.AI_CONFIG.gemini_ai_key_primary = "your_key"
settings.ANALYSIS_CONFIG.validate = True
settings.ANALYSIS_CONFIG.parse = True

# Initialize agent
agent = AIAgent(settings=settings)
```

### Simple Analysis

```python
async def simple_analysis():
    settings = AppSettings()
    settings.ANALYSIS_CONFIG.query = "What is artificial intelligence?"
    settings.AI_CONFIG.gemini_ai_key_primary = "your_key"
    
    agent = AIAgent(settings=settings)
    result = await agent.analyze_query()
    
    print(f"Completed: {result['completed']}")
    print(f"Results: {result['final_content']}")

# Run the analysis
asyncio.run(simple_analysis())
```

### Advanced Analysis with Custom Configuration

```python
async def advanced_analysis():
    # Detailed configuration
    settings = AppSettings()
    
    # Analysis configuration
    settings.ANALYSIS_CONFIG.query = "Impact of AI on healthcare"
    settings.ANALYSIS_CONFIG.system_instruction = "Focus on evidence-based analysis"
    settings.ANALYSIS_CONFIG.validate = True
    settings.ANALYSIS_CONFIG.parse = True
    settings.ANALYSIS_CONFIG.parse_schema = '''
    {
        "type": "object",
        "properties": {
            "executive_summary": {"type": "string"},
            "key_impacts": {
                "type": "array",
                "items": {"type": "string"}
            },
            "benefits": {
                "type": "array",
                "items": {"type": "string"}
            },
            "challenges": {
                "type": "array",
                "items": {"type": "string"}
            },
            "future_outlook": {"type": "string"},
            "confidence_score": {
                "type": "number",
                "minimum": 0,
                "maximum": 1
            }
        },
        "required": ["executive_summary", "key_impacts"]
    }
    '''
    
    # AI configuration
    settings.AI_CONFIG.gemini_ai_key_primary = "your_key"
    settings.AI_CONFIG.search_model_name = "gemini-1.5-pro"
    settings.AI_CONFIG.validate_model_name = "gemini-2.5-flash"
    settings.AI_CONFIG.parse_model_name = "gemini-1.5-pro"
    
    # Site filtering
    settings.ANALYSIS_CONFIG.included_sites = "pubmed.ncbi.nlm.nih.gov,nejm.org,nature.com"
    
    # Initialize and run
    agent = AIAgent(settings=settings)
    result = await agent.analyze_query()
    
    return result

# Execute analysis
result = asyncio.run(advanced_analysis())
print(result['final_content'])
```

### Batch Processing

```python
async def batch_analysis(queries):
    """Process multiple queries in batch"""
    settings = AppSettings()
    settings.AI_CONFIG.gemini_ai_key_primary = "your_key"
    settings.ANALYSIS_CONFIG.validate = True
    
    agent = AIAgent(settings=settings)
    results = []
    
    for query in queries:
        try:
            result = await agent.analyze_query(query=query)
            results.append({
                "query": query,
                "success": True,
                "data": result
            })
        except Exception as e:
            results.append({
                "query": query,
                "success": False,
                "error": str(e)
            })
    
    return results

# Process multiple queries
queries = [
    "Benefits of solar energy",
    "Machine learning in finance",
    "Future of space exploration"
]

results = asyncio.run(batch_analysis(queries))
for result in results:
    print(f"Query: {result['query']}")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Summary: {result['data']['final_content']}")
    print("-" * 50)
```

### Error Handling

```python
from gemini_groundcite.exceptions import GroundCiteError, ConfigurationError

async def robust_analysis(query):
    """Analysis with comprehensive error handling"""
    try:
        settings = AppSettings()
        settings.ANALYSIS_CONFIG.query = query
        settings.AI_CONFIG.gemini_ai_key_primary = "your_key"
        
        # Validate configuration before proceeding
        is_valid, errors = settings.validate_all_configurations()
        if not is_valid:
            print(f"Configuration errors: {errors}")
            return None
        
        agent = AIAgent(settings=settings)
        result = await agent.analyze_query(max_retries=3)
        
        return result
        
    except ConfigurationError as e:
        print(f"Configuration error: {e.message}")
        print(f"Details: {e.details}")
        return None
        
    except GroundCiteError as e:
        print(f"GroundCite error: {e.message}")
        return None
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Usage
result = asyncio.run(robust_analysis("What is quantum computing?"))
if result:
    print("Analysis successful!")
```

## REST API Usage

### Starting the Server

```bash
# Start the API server
python -m gemini_groundcite.main

# Or with custom settings
uvicorn gemini_groundcite.main:app --host 0.0.0.0 --port 8000 --reload
```

### Basic Analysis Request

```python
import requests

def analyze_via_api(query):
    """Analyze query using REST API"""
    url = "http://localhost:8000/api/v1/analyze"
    
    payload = {
        "query": query,
        "config": {
            "validate": True,
            "parse": False
        },
        "search_model_name": "gemini-2.5-flash",
        "validate_model_name": "gemini-2.5-flash",
        "parsing_provider": "gemini",
        "api_keys": {
            "gemini": {
                "primary": "your_gemini_key"
            }
        }
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        if result["success"]:
            return result["data"]
        else:
            print(f"Analysis failed: {result['error']}")
            return None
    else:
        print(f"HTTP error: {response.status_code}")
        return None

# Usage
result = analyze_via_api("What are the benefits of renewable energy?")
if result:
    print(f"Analysis completed: {result['completed']}")
    print(f"Search results count: {len(result.get('search_results', []))}")
```

### Advanced API Usage with Parsing

```python
import requests
import json

def advanced_api_analysis():
    """Advanced analysis with parsing and custom schema"""
    url = "http://localhost:8000/api/v1/analyze"
    
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "summary": {"type": "string"},
            "key_points": {
                "type": "array",
                "items": {"type": "string"}
            },
            "sources": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "url": {"type": "string"}
                    }
                }
            }
        },
        "required": ["title", "summary"]
    }
    
    payload = {
        "query": "Latest developments in artificial intelligence",
        "system_instruction": "Provide a comprehensive analysis focusing on recent breakthroughs",
        "config": {
            "validate": True,
            "parse": True,
            "schema": json.dumps(schema),
            "siteConfig": {
                "includeList": "arxiv.org,nature.com,openai.com",
                "excludeList": ""
            }
        },
        "parsing_provider": "gemini",
        "search_model_name": "gemini-1.5-pro",
        "validate_model_name": "gemini-2.5-flash",
        "parse_model_name": "gemini-1.5-pro",
        "search_gemini_params": {
            "temperature": 0.3,
            "max_output_tokens": 2048
        },
        "parsing_gemini_params": {
            "temperature": 0.1,
            "max_output_tokens": 4096
        },
        "api_keys": {
            "gemini": {
                "primary": "your_gemini_key"
            }
        }
    }
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    if result["success"]:
        data = result["data"]
        print(f"Title: {data['final_content'].get('title', 'N/A')}")
        print(f"Summary: {data['final_content'].get('summary', 'N/A')}")
        print(f"Execution time: {result['execution_time']:.2f}s")
        print(f"Token usage: {data['execution_metrics']['token_usage']}")
    else:
        print(f"Error: {result['error']}")

# Run advanced analysis
advanced_api_analysis()
```

### Configuration Management via API

```python
def save_analysis_config():
    """Save a reusable analysis configuration"""
    url = "http://localhost:8000/api/v1/configurations"
    
    config = {
        "name": "Research Analysis",
        "description": "Configuration for academic research analysis",
        "config": {
            "validate": True,
            "parse": True,
            "schema": json.dumps({
                "findings": {"type": "array"},
                "methodology": {"type": "string"},
                "conclusion": {"type": "string"}
            })
        },
        "parsing_provider": "gemini",
        "search_model_name": "gemini-1.5-pro",
        "validate_model_name": "gemini-2.5-flash",
        "parse_model_name": "gemini-1.5-pro",
        "api_keys": {
            "gemini": {"primary": "your_key"}
        }
    }
    
    response = requests.post(url, json=config)
    if response.status_code == 200:
        result = response.json()
        print(f"Configuration saved with ID: {result['id']}")
        return result['id']
    else:
        print(f"Failed to save configuration: {response.status_code}")
        return None

# Save configuration
config_id = save_analysis_config()

# Later, retrieve and use the configuration
def get_saved_config(config_id):
    url = f"http://localhost:8000/api/v1/configurations/{config_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["configuration"]
    return None
```

## Common Use Cases

### 1. Academic Research

```python
async def academic_research_analysis(research_question):
    """Analyze academic research questions with scholarly sources"""
    settings = AppSettings()
    
    # Configure for academic analysis
    settings.ANALYSIS_CONFIG.query = research_question
    settings.ANALYSIS_CONFIG.system_instruction = """
    Provide a scholarly analysis based on peer-reviewed sources.
    Focus on evidence-based findings and cite credible sources.
    """
    settings.ANALYSIS_CONFIG.validate = True
    settings.ANALYSIS_CONFIG.parse = True
    settings.ANALYSIS_CONFIG.parse_schema = '''
    {
        "type": "object",
        "properties": {
            "research_question": {"type": "string"},
            "methodology": {"type": "string"},
            "key_findings": {
                "type": "array",
                "items": {"type": "string"}
            },
            "supporting_evidence": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "claim": {"type": "string"},
                        "source": {"type": "string"},
                        "credibility": {"type": "string"}
                    }
                }
            },
            "limitations": {"type": "string"},
            "future_research": {"type": "string"}
        }
    }
    '''
    
    # Filter for academic sources
    settings.ANALYSIS_CONFIG.included_sites = "arxiv.org,pubmed.ncbi.nlm.nih.gov,scholar.google.com,jstor.org"
    
    settings.AI_CONFIG.gemini_ai_key_primary = "your_key"
    
    agent = AIAgent(settings=settings)
    return await agent.analyze_query()

# Example usage
result = asyncio.run(academic_research_analysis(
    "What are the environmental impacts of cryptocurrency mining?"
))
```

### 2. Market Research

```python
async def market_research_analysis(market_topic):
    """Analyze market trends and opportunities"""
    settings = AppSettings()
    
    settings.ANALYSIS_CONFIG.query = f"Market analysis for {market_topic}"
    settings.ANALYSIS_CONFIG.validate = True
    settings.ANALYSIS_CONFIG.parse = True
    settings.ANALYSIS_CONFIG.parse_schema = '''
    {
        "type": "object",
        "properties": {
            "market_overview": {"type": "string"},
            "market_size": {"type": "string"},
            "growth_rate": {"type": "string"},
            "key_players": {
                "type": "array",
                "items": {"type": "string"}
            },
            "market_trends": {
                "type": "array",
                "items": {"type": "string"}
            },
            "opportunities": {
                "type": "array",
                "items": {"type": "string"}
            },
            "challenges": {
                "type": "array",
                "items": {"type": "string"}
            },
            "competitive_landscape": {"type": "string"},
            "recommendations": {
                "type": "array",
                "items": {"type": "string"}
            }
        }
    }
    '''
    
    # Include business and financial sources
    settings.ANALYSIS_CONFIG.included_sites = "bloomberg.com,reuters.com,marketwatch.com,forbes.com"
    
    settings.AI_CONFIG.gemini_ai_key_primary = "your_key"
    
    agent = AIAgent(settings=settings)
    return await agent.analyze_query()

# Example usage
result = asyncio.run(market_research_analysis("electric vehicle batteries"))
```

### 3. Technical Documentation Analysis

```python
async def technical_analysis(technology):
    """Analyze technical topics with implementation details"""
    settings = AppSettings()
    
    settings.ANALYSIS_CONFIG.query = f"Technical overview and implementation of {technology}"
    settings.ANALYSIS_CONFIG.validate = True
    settings.ANALYSIS_CONFIG.parse = True
    settings.ANALYSIS_CONFIG.parse_schema = '''
    {
        "type": "object",
        "properties": {
            "technology_overview": {"type": "string"},
            "key_concepts": {
                "type": "array",
                "items": {"type": "string"}
            },
            "implementation_approaches": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "approach": {"type": "string"},
                        "pros": {"type": "array", "items": {"type": "string"}},
                        "cons": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "best_practices": {
                "type": "array",
                "items": {"type": "string"}
            },
            "common_pitfalls": {
                "type": "array",
                "items": {"type": "string"}
            },
            "tools_and_frameworks": {
                "type": "array",
                "items": {"type": "string"}
            }
        }
    }
    '''
    
    # Include technical documentation sources
    settings.ANALYSIS_CONFIG.included_sites = "github.com,stackoverflow.com,medium.com,dev.to"
    
    settings.AI_CONFIG.gemini_ai_key_primary = "your_key"
    
    agent = AIAgent(settings=settings)
    return await agent.analyze_query()

# Example usage
result = asyncio.run(technical_analysis("microservices architecture"))
```

### 4. Content Fact-Checking

```python
async def fact_check_analysis(claim):
    """Fact-check claims with validation focus"""
    settings = AppSettings()
    
    settings.ANALYSIS_CONFIG.query = f"Fact-check and verify: {claim}"
    settings.ANALYSIS_CONFIG.system_instruction = """
    Carefully verify the accuracy of the given claim.
    Look for authoritative sources and evidence.
    Be explicit about confidence levels and source credibility.
    """
    settings.ANALYSIS_CONFIG.validate = True
    settings.ANALYSIS_CONFIG.parse = True
    settings.ANALYSIS_CONFIG.parse_schema = '''
    {
        "type": "object",
        "properties": {
            "claim": {"type": "string"},
            "verdict": {
                "type": "string",
                "enum": ["True", "False", "Partially True", "Misleading", "Unverifiable"]
            },
            "confidence_score": {
                "type": "number",
                "minimum": 0,
                "maximum": 1
            },
            "supporting_evidence": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "evidence": {"type": "string"},
                        "source": {"type": "string"},
                        "credibility_rating": {"type": "string"}
                    }
                }
            },
            "contradicting_evidence": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "evidence": {"type": "string"},
                        "source": {"type": "string"}
                    }
                }
            },
            "context": {"type": "string"},
            "caveats": {"type": "string"}
        }
    }
    '''
    
    # Include authoritative news and fact-checking sites
    settings.ANALYSIS_CONFIG.included_sites = "snopes.com,factcheck.org,politifact.com,reuters.com,ap.org"
    
    settings.AI_CONFIG.gemini_ai_key_primary = "your_key"
    
    agent = AIAgent(settings=settings)
    return await agent.analyze_query()

# Example usage
result = asyncio.run(fact_check_analysis(
    "Vaccines cause autism in children"
))
```

## Advanced Configuration

### Custom AI Provider Parameters

```python
# Gemini-specific parameters
settings.AI_CONFIG.search_gemini_params = {
    "temperature": 0.7,          # Creativity level
    "top_p": 0.9,               # Nucleus sampling
    "top_k": 40,                # Top-k sampling
    "max_output_tokens": 2048,   # Response length
    "candidate_count": 1,        # Number of candidates
    "stop_sequences": ["END", "STOP"]  # Stop generation
}

# OpenAI-specific parameters
settings.AI_CONFIG.parsing_openai_params = {
    "temperature": 0.1,          # Low for structured parsing
    "max_tokens": 4096,          # Maximum tokens
    "top_p": 1.0,               # Nucleus sampling
    "frequency_penalty": 0.0,    # Frequency penalty
    "presence_penalty": 0.0,     # Presence penalty
    "stop": ["---", "END"]       # Stop sequences
}
```

### Environment-Based Configuration

```python
import os

def configure_from_environment():
    """Configure GroundCite from environment variables"""
    settings = AppSettings()
    
    # AI keys from environment
    settings.AI_CONFIG.gemini_ai_key_primary = os.getenv("GEMINI_AI_KEY_PRIMARY")
    settings.AI_CONFIG.open_ai_key = os.getenv("OPENAI_API_KEY")
    
    # Analysis settings from environment
    settings.ANALYSIS_CONFIG.validate = os.getenv("ANALYSIS_VALIDATE", "false").lower() == "true"
    settings.ANALYSIS_CONFIG.parse = os.getenv("ANALYSIS_PARSE", "false").lower() == "true"
    
    # Site filtering from environment
    settings.ANALYSIS_CONFIG.included_sites = os.getenv("ANALYSIS_INCLUDED_SITES", "")
    settings.ANALYSIS_CONFIG.excluded_sites = os.getenv("ANALYSIS_EXCLUDED_SITES", "")
    
    return settings
```

### Configuration Validation

```python
def validate_and_fix_configuration(settings):
    """Validate configuration and provide fixes"""
    is_valid, errors = settings.validate_all_configurations()
    
    if not is_valid:
        print("Configuration issues found:")
        for error in errors:
            print(f"  - {error}")
        
        # Suggest fixes
        if not settings.AI_CONFIG.gemini_ai_key_primary:
            print("Fix: Set GEMINI_AI_KEY_PRIMARY environment variable")
        
        if settings.ANALYSIS_CONFIG.parse and not settings.ANALYSIS_CONFIG.parse_schema:
            print("Fix: Provide a JSON schema for parsing")
            settings.ANALYSIS_CONFIG.parse_schema = '{"summary": {"type": "string"}}'
        
        return False
    
    return True
```

## Best Practices

### 1. API Key Management

```python
# Don't hardcode API keys
# ❌ Bad
settings.AI_CONFIG.gemini_ai_key_primary = "actual_api_key_here"

# ✅ Good - Use environment variables
import os
settings.AI_CONFIG.gemini_ai_key_primary = os.getenv("GEMINI_AI_KEY_PRIMARY")

# ✅ Good - Use configuration files
import json
with open("config.json") as f:
    config = json.load(f)
    settings.AI_CONFIG.gemini_ai_key_primary = config["gemini_key"]
```

### 2. Error Handling

```python
async def robust_analysis_workflow(query):
    """Implement comprehensive error handling"""
    max_retries = 3
    current_retry = 0
    
    while current_retry < max_retries:
        try:
            settings = AppSettings()
            settings.ANALYSIS_CONFIG.query = query
            settings.AI_CONFIG.gemini_ai_key_primary = os.getenv("GEMINI_AI_KEY_PRIMARY")
            
            agent = AIAgent(settings=settings)
            result = await agent.analyze_query()
            
            # Validate result quality
            if result and result.get('completed'):
                return result
            else:
                print(f"Analysis incomplete, retrying... ({current_retry + 1}/{max_retries})")
                
        except Exception as e:
            print(f"Attempt {current_retry + 1} failed: {e}")
            current_retry += 1
            
            if current_retry >= max_retries:
                print("Max retries reached, analysis failed")
                raise
            
            # Exponential backoff
            await asyncio.sleep(2 ** current_retry)
    
    return None
```

### 3. Performance Optimization

```python
# Use appropriate model sizes
settings.AI_CONFIG.search_model_name = "gemini-2.5-flash"  # Fast for search
settings.AI_CONFIG.parse_model_name = "gemini-1.5-pro"    # Better for complex parsing

# Set reasonable token limits
settings.AI_CONFIG.search_gemini_params = {
    "max_output_tokens": 1024  # Sufficient for search
}
settings.AI_CONFIG.parsing_gemini_params = {
    "max_output_tokens": 4096  # More for detailed parsing
}

# Use caching for repeated queries (implement your own caching)
query_cache = {}

async def cached_analysis(query):
    if query in query_cache:
        return query_cache[query]
    
    result = await agent.analyze_query(query=query)
    query_cache[query] = result
    return result
```

### 4. Schema Design

```python
# ✅ Good schema design
good_schema = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
            "description": "Brief summary in 2-3 sentences"
        },
        "key_points": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 10,
            "description": "Main points, max 10 items"
        },
        "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Confidence score 0-1"
        }
    },
    "required": ["summary", "key_points"],
    "additionalProperties": False
}

# ❌ Avoid overly complex schemas
bad_schema = {
    "type": "object",
    "properties": {
        "deeply": {
            "type": "object",
            "properties": {
                "nested": {
                    "type": "object",
                    "properties": {
                        "structure": {"type": "string"}
                    }
                }
            }
        }
    }
}
```

### 5. Monitoring and Logging

```python
import logging

def setup_monitoring(agent):
    """Set up monitoring for analysis operations"""
    
    # Track token usage
    def log_token_usage(result):
        if result and 'execution_metrics' in result:
            metrics = result['execution_metrics']
            token_usage = metrics.get('token_usage', {})
            
            total_tokens = 0
            for operation, usage_list in token_usage.items():
                for usage in usage_list:
                    total_tokens += usage.get('total_tokens', 0)
            
            logging.info(f"Total tokens used: {total_tokens}")
            logging.info(f"Execution time: {metrics.get('execution_time_seconds', 0):.2f}s")
    
    return log_token_usage

# Usage
monitor = setup_monitoring(agent)
result = await agent.analyze_query("test query")
monitor(result)
```

## Troubleshooting

### Common Issues and Solutions

#### 1. API Key Issues

**Problem**: "Invalid API key" errors
```python
# Check if key is set
import os
key = os.getenv("GEMINI_AI_KEY_PRIMARY")
if not key:
    print("GEMINI_AI_KEY_PRIMARY not set")
else:
    print(f"Key present: {key[:10]}...")

# Validate key format
if not key.startswith("AIza"):
    print("Invalid Gemini API key format")
```

#### 2. Configuration Validation Errors

**Problem**: Configuration validation fails
```python
settings = AppSettings()
is_valid, errors = settings.validate_all_configurations()

if not is_valid:
    print("Configuration errors:")
    for error in errors:
        print(f"  - {error}")
    
    # Common fixes
    if "query" in str(errors):
        settings.ANALYSIS_CONFIG.query = "test query"
    
    if "gemini_key" in str(errors):
        settings.AI_CONFIG.gemini_ai_key_primary = os.getenv("GEMINI_AI_KEY_PRIMARY")
```

#### 3. Parsing Failures

**Problem**: JSON parsing fails repeatedly
```python
# Simplify schema
simple_schema = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"}
    },
    "required": ["summary"]
}

# Lower temperature for more consistent parsing
settings.AI_CONFIG.parsing_gemini_params = {
    "temperature": 0.1,
    "top_p": 0.8
}

# Add retries
result = await agent.analyze_query(max_retries=5)
```

#### 4. Performance Issues

**Problem**: Analysis takes too long
```python
# Use faster models
settings.AI_CONFIG.search_model_name = "gemini-2.5-flash"

# Reduce token limits
settings.AI_CONFIG.search_gemini_params = {
    "max_output_tokens": 1024
}

# Simplify operations
settings.ANALYSIS_CONFIG.validate = False  # Skip validation if not needed
```

#### 5. Rate Limiting

**Problem**: Rate limit exceeded
```python
import asyncio
from random import uniform

async def rate_limited_analysis(queries):
    """Analysis with rate limiting"""
    results = []
    
    for query in queries:
        try:
            result = await agent.analyze_query(query=query)
            results.append(result)
            
            # Add delay between requests
            delay = uniform(1, 3)  # Random delay 1-3 seconds
            await asyncio.sleep(delay)
            
        except Exception as e:
            if "rate limit" in str(e).lower():
                print("Rate limit hit, waiting...")
                await asyncio.sleep(60)  # Wait 1 minute
                # Retry the query
                result = await agent.analyze_query(query=query)
                results.append(result)
            else:
                raise
    
    return results
```

### Debugging Tips

1. **Enable verbose logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Use correlation IDs**:
   ```python
   result = await agent.analyze_query(correlation_id="debug-123")
   ```

3. **Check execution metrics**:
   ```python
   metrics = result['execution_metrics']
   print(f"Nodes executed: {metrics['total_nodes_executed']}")
   print(f"Node status: {metrics['nodes_completion_status']}")
   ```

4. **Validate inputs**:
   ```python
   # Test with minimal configuration
   settings = AppSettings()
   settings.ANALYSIS_CONFIG.query = "test"
   settings.AI_CONFIG.gemini_ai_key_primary = "your_key"
   
   is_valid, errors = settings.validate_all_configurations()
   print(f"Valid: {is_valid}, Errors: {errors}")
   ```

This comprehensive usage guide should help you effectively use GroundCite for various analysis tasks. Remember to start simple and gradually add complexity as you become more familiar with the system.
