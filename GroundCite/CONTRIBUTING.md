# Contributing to GroundCite

We welcome contributions to GroundCite! This document provides guidelines for contributing to the project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contribution Guidelines](#contribution-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Development Workflow](#development-workflow)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

## Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

### Our Standards

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Virtual environment tool (venv, conda, etc.)
- Basic understanding of async/await patterns
- Familiarity with FastAPI and LangGraph (helpful but not required)

### Development Environment

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/ground-cite.git
   cd ground-cite/GroundCite
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Set up pre-commit hooks** (optional but recommended)
   ```bash
   pre-commit install
   ```

5. **Verify installation**
   ```bash
   pytest tests/
   gemini-groundcite --help
   ```

## Development Setup

### Environment Variables

Create a `.env` file in the project root:

```bash
# AI Provider Keys (for testing)
GEMINI_AI_KEY_PRIMARY=your_test_key
OPENAI_API_KEY=your_test_key

# Development Settings
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

### IDE Configuration

#### VS Code
Recommended extensions:
- Python
- Python Docstring Generator
- autoDocstring
- GitLens
- Python Test Explorer

Settings:
```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.testing.pytestEnabled": true
}
```

#### PyCharm
- Enable black formatting
- Configure pytest as the test runner
- Set up virtual environment interpreter

## Contribution Guidelines

### Types of Contributions

We welcome several types of contributions:

1. **Bug Reports** - Help us identify and fix issues
2. **Feature Requests** - Suggest new functionality
3. **Code Contributions** - Implement features or fix bugs
4. **Documentation** - Improve or add documentation
5. **Tests** - Add or improve test coverage
6. **Performance Improvements** - Optimize existing code

### What We're Looking For

- **New AI Provider Integrations** - Support for additional AI services
- **Processing Node Extensions** - New analysis capabilities
- **Performance Optimizations** - Speed and efficiency improvements
- **UI/UX Enhancements** - Better CLI and API interfaces
- **Documentation Improvements** - Clearer guides and examples
- **Test Coverage** - More comprehensive testing

## Pull Request Process

### Before You Start

1. **Check existing issues** - Look for related issues or discussions
2. **Create an issue** - For significant changes, create an issue first
3. **Fork and branch** - Work on a feature branch from your fork

### Development Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Make your changes**
   - Follow the coding standards
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run all tests
   pytest

   # Run with coverage
   pytest --cov=gemini_groundcite --cov-report=html

   # Test specific modules
   pytest tests/test_ai_agent.py -v
   ```

4. **Format and lint**
   ```bash
   # Format code
   black gemini_groundcite/ tests/

   # Check linting
   flake8 gemini_groundcite/ tests/

   # Type checking (if using mypy)
   mypy gemini_groundcite/
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add support for new AI provider"
   
   # Follow conventional commit format:
   # feat: new feature
   # fix: bug fix
   # docs: documentation
   # test: testing
   # refactor: code refactoring
   # style: formatting
   # chore: maintenance
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create pull request on GitHub
   ```

### Pull Request Requirements

- [ ] **Clear description** - Explain what changes were made and why
- [ ] **Tests pass** - All existing tests continue to pass
- [ ] **New tests** - Add tests for new functionality
- [ ] **Documentation** - Update relevant documentation
- [ ] **Backwards compatibility** - Avoid breaking existing APIs
- [ ] **Performance** - No significant performance regressions

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

## Issue Reporting

### Bug Reports

Use this template for bug reports:

```markdown
**Bug Description**
Clear, concise description of the bug

**To Reproduce**
Steps to reproduce the behavior:
1. Configure with '...'
2. Run command '...'
3. See error

**Expected Behavior**
What you expected to happen

**Environment**
- OS: [e.g. Windows 10, macOS 12, Ubuntu 20.04]
- Python Version: [e.g. 3.10.5]
- GroundCite Version: [e.g. 1.0.3]
- AI Provider: [e.g. Gemini, OpenAI]

**Additional Context**
Any other relevant information

**Logs**
```
Relevant log output
```
```

### Feature Requests

Use this template for feature requests:

```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Describe the problem this feature would solve

**Proposed Solution**
Describe how you envision this feature working

**Alternatives Considered**
Any alternative solutions you've considered

**Additional Context**
Any other relevant information
```

## Development Workflow

### Project Structure

```
gemini_groundcite/
├── __init__.py
├── cli.py                    # CLI interface
├── main.py                   # FastAPI application
├── config/                   # Configuration management
│   ├── settings.py
│   └── logger.py
├── core/                     # Core library
│   ├── agents/              # AI agent orchestration
│   ├── di/                  # Dependency injection
│   ├── executors/           # Graph execution engine
│   ├── models/              # Data models
│   └── utils/               # Utilities
├── exceptions.py            # Custom exceptions
└── ...

tests/
├── unit/                    # Unit tests
├── integration/             # Integration tests
├── fixtures/                # Test fixtures
└── conftest.py              # Pytest configuration
```

### Coding Standards

#### Python Style

Follow PEP 8 with these additions:
- Line length: 88 characters (Black default)
- Use type hints for all public functions
- Use docstrings for all public classes and functions
- Prefer async/await for I/O operations

#### Documentation Style

Use Google-style docstrings:

```python
async def analyze_query(
    self, 
    query: str,
    max_retries: int = 3
) -> Optional[Dict[str, Any]]:
    """
    Analyze a query using the configured AI pipeline.
    
    This method orchestrates the complete analysis workflow including
    search, validation, and parsing stages based on configuration.
    
    Args:
        query (str): The query to analyze
        max_retries (int): Maximum number of retry attempts
    
    Returns:
        Optional[Dict[str, Any]]: Analysis results containing search results,
            validated content, and parsed data if successful
    
    Raises:
        AIAgentError: If the analysis pipeline fails
        ConfigurationError: If configuration is invalid
    
    Example:
        >>> agent = AIAgent(settings)
        >>> result = await agent.analyze_query("What is AI?")
        >>> print(result['final_content'])
    """
```

#### Naming Conventions

- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_leading_underscore`
- Modules: `snake_case`

### Architecture Guidelines

#### Adding New AI Providers

1. **Create client class**
   ```python
   # gemini_groundcite/core/agents/clients/new_provider_client.py
   class NewProviderClient:
       async def generate_content(
           self, 
           prompt: str, 
           model: str, 
           **kwargs
       ) -> GenerationResponse:
           """Implement the common interface"""
   ```

2. **Register with DI container**
   ```python
   # In core_di.py
   def configure_ai_clients(container):
       container.register(NewProviderClient, instance=NewProviderClient())
   ```

3. **Update configuration**
   ```python
   # In settings.py
   class AIConfig:
       new_provider_api_key: str = ""
       new_provider_model_name: str = "default-model"
   ```

4. **Add tests**
   ```python
   # tests/unit/test_new_provider_client.py
   class TestNewProviderClient:
       async def test_generate_content(self):
           # Test implementation
   ```

#### Adding New Processing Nodes

1. **Create node function**
   ```python
   # gemini_groundcite/core/executors/nodes/new_node.py
   async def new_processing_node(state: AgentState) -> AgentState:
       """
       Process state and return updated state.
       
       Args:
           state: Current agent state
           
       Returns:
           Updated agent state
       """
   ```

2. **Add routing logic**
   ```python
   def new_node_router(state: AgentState) -> str:
       """Determine next node based on state"""
       if condition:
           return "next_node"
       return "end"
   ```

3. **Register in graph executor**
   ```python
   # In graph_executor.py __init__
   new_node = create_new_node(self.settings, self.logger)
   workflow.add_node("new_node", new_node)
   ```

## Testing Guidelines

### Test Structure

```python
import pytest
from unittest.mock import Mock, AsyncMock
from gemini_groundcite.core.agents import AIAgent

class TestAIAgent:
    """Test suite for AIAgent class"""
    
    @pytest.fixture
    def settings(self):
        """Provide test settings"""
        # Return configured test settings
    
    @pytest.fixture
    def agent(self, settings):
        """Provide configured AI agent"""
        return AIAgent(settings=settings)
    
    async def test_analyze_query_success(self, agent):
        """Test successful query analysis"""
        # Arrange
        query = "test query"
        
        # Act
        result = await agent.analyze_query(query)
        
        # Assert
        assert result is not None
        assert result['completed'] is True
    
    async def test_analyze_query_invalid_config(self, agent):
        """Test analysis with invalid configuration"""
        # Test error conditions
        with pytest.raises(ConfigurationError):
            await agent.analyze_query("")
```

### Test Categories

1. **Unit Tests** - Test individual functions/methods
2. **Integration Tests** - Test component interactions
3. **API Tests** - Test REST API endpoints
4. **CLI Tests** - Test command-line interface
5. **Performance Tests** - Test performance characteristics

### Mocking Guidelines

Mock external dependencies:
- AI provider APIs
- Web search APIs
- Network calls
- File system operations

```python
@pytest.mark.asyncio
async def test_with_mocked_ai_client(mocker):
    """Test with mocked AI client"""
    mock_client = mocker.patch('gemini_groundcite.core.agents.clients.GoogleGenAIClient')
    mock_client.generate_content.return_value = AsyncMock(
        return_value={"content": "test response"}
    )
    
    # Test with mocked client
```

### Test Data

Use fixtures for test data:

```python
# tests/fixtures/sample_data.py
SAMPLE_QUERY = "What is artificial intelligence?"

SAMPLE_SEARCH_RESULTS = [
    {
        "title": "AI Overview",
        "url": "https://example.com/ai",
        "content": "AI is..."
    }
]

SAMPLE_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"}
    }
}
```

## Documentation

### Types of Documentation

1. **API Documentation** - Comprehensive API reference
2. **User Guides** - How-to guides for common tasks
3. **Architecture Documentation** - System design and structure
4. **Contributing Guide** - This document
5. **Changelog** - Version history and changes

### Writing Guidelines

- **Clear and Concise** - Use simple, direct language
- **Examples** - Provide code examples for all features
- **Structure** - Use consistent formatting and organization
- **Accuracy** - Keep documentation up-to-date with code changes

### Documentation Updates

When making changes:
- Update relevant docstrings
- Update API documentation if needed
- Add examples for new features
- Update README if major changes
- Update CHANGELOG.md

### Building Documentation

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Build API documentation
sphinx-build -b html docs/ docs/_build/

# Serve documentation locally
cd docs/_build && python -m http.server 8080
```

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes (backwards compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in pyproject.toml
- [ ] Git tag created
- [ ] Release notes written

## Getting Help

### Community Support

- **GitHub Discussions** - General questions and discussions
- **GitHub Issues** - Bug reports and feature requests
- **Email** - anshulee@cennest.com for direct contact

### Development Questions

For development-related questions:
1. Check existing documentation
2. Search GitHub issues
3. Create a new discussion or issue
4. Join our community chat (if available)

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project README
- Special recognition for significant contributions

Thank you for contributing to GroundCite! 🚀
