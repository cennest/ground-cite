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

- Python 3.12 or higher
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

## Contribution Guidelines

### Types of Contributions

We welcome several types of contributions:

1. **Bug Reports** - Help us identify and fix issues
2. **Feature Requests** - Suggest new functionality
3. **Code Contributions** - Implement features or fix bugs
4. **Documentation** - Improve or add documentation
5. **Performance Improvements** - Optimize existing code


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
   - Update documentation as needed

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add support for new AI provider"
   
   # Follow conventional commit format:
   # feat: new feature
   # fix: bug fix
   # docs: documentation
   # refactor: code refactoring
   # style: formatting
   # chore: maintenance
   ```

4. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create pull request on GitHub
   ```

### Pull Request Requirements

- [ ] **Clear description** - Explain what changes were made and why
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

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
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
- Python Version: [e.g. 3.12]
- GroundCite Version: [e.g. 1.0.5]
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

```

### Coding Standards


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

2. **Update configuration**
   ```python
   # In settings.py
   class AIConfig:
       new_provider_api_key: str = ""
       new_provider_model_name: str = "default-model"
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


## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes (backwards compatible)

### Release Checklist

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
