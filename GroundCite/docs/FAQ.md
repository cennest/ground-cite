# GroundCite FAQ

## What is GroundCite?
GroundCite is an AI-powered query analysis library that searches the web, validates content, and extracts structured data from search results.

## How do I install it?
```bash
pip install gemini-groundcite
```

## What API keys do I need?
- **Required**: Google Gemini API key from [Google AI Studio](https://aistudio.google.com/)
- **Optional**: OpenAI API key from [OpenAI Platform](https://platform.openai.com/) (for parsing)

## How do I run a basic query?
```bash
gemini-groundcite analyze -q "What are the benefits of renewable energy?" --gemini-key your_gemini_key
```

## How do I enable validation?
```bash
gemini-groundcite analyze -q "query" --validate --gemini-key your_gemini_key
```

## How do I extract structured data (parse)?
```bash
gemini-groundcite analyze -q "query" --parse --schema '{"companies": ["string"]}' --gemini-key your_gemini_key
```

## How do I filter search results by sites?
Include specific sites:
```bash
gemini-groundcite analyze -q "query" --include-sites "https://github.com,https://arxiv.org" --gemini-key your_gemini_key
```

Exclude specific sites:
```bash
gemini-groundcite analyze -q "query" --exclude-sites "https://reddit.com,https://twitter.com" --gemini-key your_gemini_key
```

## How do I use the REST API?
```bash
uvicorn gemini_groundcite.main:app --reload
```
Then POST to `/api/v1/analyze` with your query data.


