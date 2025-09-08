# GroundCite - Powering Gemini with Smarter, Controlled and Reliable Grounding and Citations

![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

<h1>Fix Gemini’s Broken Citations with GroundCite</h1>
**GroundCite** is a Python library for adding better grounding and valid Citation support when searching using Gemini with google grounding . It combines web search using Gemini with google grounding with context validation, and structured data parsing using multiple AI providers to deliver accurate and reliable answers to complex questions.

If you’ve ever faced:

- **Broken citations** in Gemini’s outputs,  
- **Irrelevant/Invalid citations** pointing to 404 pages or unrelated content, or  
- **No Citations** in Structured JSON responses,  
- **Grounding Issues: Gemini disregarding your instructions wrt source of data** ( no inclusions or exclusions),  
then GroundCite is your solution.

**Read more about why we made GroundCite**  https://www.cennest.com/fix-geminis-broken-citations-with-groundcite-complete-guide/

**Playground app for feature testing** https://groundcite.cennest.com/  

**GroundCite in Action** https://youtu.be/b1sCCRSgi38

## 🚀 Features

### Core Capabilities
- **Intelligent Search Integration**: Intelligent grounding search with site filtering and content aggregation
- **AI-Powered Validation**: Optional citation validation using advanced AI models
- **Structured Data Parsing with Citation**: Extract structured data with Citations using custom JSON schemas
- **MultiAgent Graph-Based Pipeline**: Consistent output with automatic retry logic and error handling
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

### FAQs
https://github.com/cennest/ground-cite/blob/main/GroundCite/docs/FAQ.md

### Detailed Architecture and usage
-https://github.com/cennest/ground-cite/blob/main/GroundCite/docs/ARCHITECTURE.md</br>
-https://github.com/cennest/ground-cite/blob/main/GroundCite/docs/ARCHITECTURE_LIGHT.md</br>
-https://github.com/cennest/ground-cite/blob/main/GroundCite/docs/USAGE.md
- **Detailed Documentation**: [Full documentation](https://github.com/cennest/ground-cite/tree/main/GroundCite/docs)

## 📋 Requirements

- **Python**: 3.12 or higher
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
gemini-groundcite analyze -q "What are the latest developments in AI?" --gemini-key your_gemini_key

# With validation and parsing
gemini-groundcite analyze -q "Company X financials" --validate --parse --gemini-key your_gemini_key

# Using OpenAI provider
gemini-groundcite analyze -q "Market trends" --provider openai --openai-key your_key --gemini-key your_gemini_key
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

## 🤝 Contributing

We welcome contributions! Please reach out to anshulee@cennest.com or even better send us a PR..

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

```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **GitHub Issues**: [Report bugs and request features](https://github.com/cennest/ground-cite/issues)
- **Email**: anshulee@cennest.com

## 🏆 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph) for workflow orchestration
- Powered by Google Gemini and OpenAI APIs
- CLI interface built with [Click](https://click.palletsprojects.com/) and [Rich](https://rich.readthedocs.io/)
- Web API built with [FastAPI](https://fastapi.tiangolo.com/)

---

**GroundCite** - *Empowering intelligent query analysis with AI*
