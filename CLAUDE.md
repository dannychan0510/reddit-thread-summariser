# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

CLI tool that takes a Reddit post URL, scrapes the thread from old.reddit.com (no API key needed), sends it to Google Gemini for analysis, and outputs a formatted summary with stock pros/cons and per-commenter sentiment breakdown.

## How To Run

```bash
.venv/bin/python3 main.py <reddit_post_url>
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Requires `GEMINI_API_KEY` environment variable: `export GEMINI_API_KEY='your-key'`

## Architecture

The pipeline is: **scrape → truncate → prompt → parse → display**.

- `main.py` — CLI entry point. Orchestrates the pipeline and renders output using `rich`. Warning suppression lives here.
- `reddit_client.py` — Scrapes old.reddit.com with `requests` + `BeautifulSoup`. Flattens nested comments, filters deleted/AutoModerator, sorts by score descending.
- `summariser.py` — Builds a prompt from the thread data, sends it to Gemini with `response_schema=AnalysisResult` for structured JSON output. Handles truncation and retries.
- `models.py` — All Pydantic `BaseModel` classes. `RedditThread`/`RedditComment` for internal data, `AnalysisResult`/`CommenterSentiment`/`Sentiment` for Gemini response schema. `Field(description=...)` values act as inline prompt engineering.
- `config.py` — Module-level env var constants. Default Gemini model is `gemini-3-flash-preview`.

## Python Compatibility

Always use Python 3.9-compatible syntax. Do NOT use `list[str]`, `dict[str, Any]`, `tuple[...]` etc. — use `from typing import List, Dict, Tuple, Optional` instead. This applies to all type hints in function signatures and variable annotations.

## API & External Services

Before implementing features that require API keys or external service credentials, ask the user if they have access. Prefer approaches that don't require authentication (e.g., web scraping over API clients) unless the user confirms they have credentials.

## Bug Prevention

When working with ML model outputs (embeddings, logits, similarity scores), always verify that values are on compatible scales before combining or comparing them. Log intermediate values during development to catch normalization issues early.

## Key Constraints

- No Reddit API credentials — the scraper relies on old.reddit.com HTML structure.
