# GroundCite FAQ

## What is GroundCite?
GroundCite is a Gemini based multi-agent library that adds layers of source filtering, cite validation and output structuring through a multi-stage pipeline to provide comprehensive research results

## Who should use GroundCite?
If you’re building tools for journalism, academic research, policy analysis, or enterprise reporting, you know that an LLM without reliable grounding is a liability. A missing or irrelevant source can turn a solid output into a trust-breaking one. Use GroundCite with gemini to add layers of validation and grounding with structured outputs.

## What features does GroundCite provide on top of Gemini+ Grounding 
1.Allow configurable source preferences — Make the model prefer categories and sites like .gov, .edu, or official organizational domains.

2.Support configurable exclusions — blacklist unreliable or unwanted domains/sites permanently.

3.Validate citations — ensuring the cited page is live, accessible, and contains the relevant content. Configure removal of chunks with invalid citations

4.Validation to check that result returned is relevant to the query and not the “Next best”.

5.Add inline numbered citations — so every fact in the output maps back to a verifiable source.

6.Enable JSON outputs with citations — by enriching text first, then parsing into structured form.

7.Configurable Strategy:- You control which models to use for JSON Parsing, what level of strictness to create for including/excluding sites and confidence levels for citations

## Where will you store my gemini/openAI keys?
We do not store your keys.

## How do I install it?
```bash
pip install gemini-groundcite
```

## What API keys do I need?
- **Required**: Google Gemini API key from [Google AI Studio](https://aistudio.google.com/)
- **Optional**: OpenAI API key from [OpenAI Platform](https://platform.openai.com/) (for structured JSON responses with Citations)

## How do I run a basic query?
```bash
gemini-groundcite analyze -q "What are the benefits of renewable energy?" --gemini-key your_gemini_key
```

## How do I enable validation?
```bash
gemini-groundcite analyze -q "query" --validate --gemini-key your_gemini_key
```
## What is the validation logic? 

## How do I extract structured data (parse)?
```bash
gemini-groundcite analyze -q "query" --parse --schema '{"companies": ["string"]}' --gemini-key your_gemini_key/OpenAI Key
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
## When i include a site does it get data only from that site or is it just a preferance? 

## How do I use the REST API?
```bash
uvicorn gemini_groundcite.main:app --reload
```
Then POST to `/api/v1/analyze` with your query data.


