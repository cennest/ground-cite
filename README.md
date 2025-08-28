# GroundCite - AI-Powered Query Analysis Library

GroundCite is a comprehensive Python library for AI-powered query analysis and research. It combines web search, content validation, and structured data parsing using multiple AI providers to deliver accurate and reliable answers to complex queries.

## 🌟 Features

- **Multi-Provider AI Support**: Integrate with OpenAI GPT models and Google Gemini
- **Intelligent Web Search**: Automated web search with source filtering and relevance ranking
- **Content Validation**: AI-powered validation of search results for accuracy and reliability
- **Structured Data Parsing**: Extract structured information using custom JSON schemas
- **Graph-Based Pipeline**: Flexible workflow orchestration with retry logic and error handling
- **Comprehensive Logging**: Detailed execution tracking and performance metrics
- **REST API Interface**: FastAPI-based web service for HTTP access
- **Command Line Interface**: Rich CLI for interactive query analysis
- **Configuration Management**: Flexible settings with validation and templates

## 🚀 Quick Start

### Installation

```bash
pip install gemini_groundcite
```

### Basic Usage

```python
import asyncio
from gemini_groundcite import AIAgent, AppSettings

async def analyze_query():
    # Configure settings
    settings = AppSettings()
    settings.ANALYSIS_CONFIG.query = "What are the latest developments in AI?"
    settings.AI_CONFIG.gemeni_ai_key_primary = "your-gemini-api-key"
    settings.AI_CONFIG.search_model_name = "gemini-1.5-flash"
    
    # Create and run agent
    agent = AIAgent(settings=settings)
    results = await agent.analyze_query()
    
    print(f"Final Content: {results['final_content']}")

asyncio.run(analyze_query())
```

### Command Line Usage

```bash
# Basic query analysis
gemini_groundcite analyze -q "What are the benefits of renewable energy?" --gemini-key your-key

# Advanced analysis with validation and parsing
gemini_groundcite analyze -q "Tesla's financial performance"  --gemini-key your-key  --validate --parse --verbose

# Using OpenAI models
gemini_groundcite analyze -q "AI market trends" --provider openai --gemini-key your-key --openai-key your-key
```

### REST API Usage

```bash
# Start the API server
python -m gemini_groundcite.main

# Analyze a query via HTTP
curl -X POST "http://localhost:8000/api/v1/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What is machine learning?",
       "config": {"validate": true, "parse": false},
       "search_model_name": "gemini-1.5-flash",
       "api_keys": {"gemini": {"primary": "your-key"}}
     }'
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph) for workflow orchestration
- Uses [FastAPI](https://fastapi.tiangolo.com/) for the REST API
- CLI powered by [Rich](https://github.com/Textualize/rich) and [Click](https://click.palletsprojects.com/)

## 📞 Support

- **Documentation**: [https://gemini_groundcite-docs.example.com](https://gemini_groundcite-docs.example.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/gemini_groundcite/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/gemini_groundcite/discussions)
- **Email**: anshulee@cennest.com

---

**Made with ❤️ by the GroundCite Team**
