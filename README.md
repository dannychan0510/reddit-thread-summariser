# Reddit Thread Summariser

CLI tool that scrapes a Reddit investment/stock discussion thread and uses Google Gemini to produce a structured analysis: stock tickers mentioned, a discussion summary, bullish/bearish arguments, and per-commenter sentiment classification.

No Reddit API key needed -- scrapes old.reddit.com directly.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set your Gemini API key:

```bash
export GEMINI_API_KEY='your-key'
```

## Usage

```bash
.venv/bin/python3 main.py <reddit_post_url>
```

Example:

```bash
.venv/bin/python3 main.py https://www.reddit.com/r/ValueInvesting/comments/abc123/what_do_you_think_of_aapl/
```

## Output

The tool produces:

- **Ticker badges** -- stock symbols identified in the discussion
- **Discussion summary** -- 3-5 sentence overview of the thread
- **Pros & Cons table** -- bullish vs bearish arguments side by side
- **Sentiment breakdown** -- bar chart showing positive/negative/neutral split
- **Per-commenter table** -- each commenter's sentiment with a one-line reason

## Configuration

All configuration is via environment variables:

| Variable | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | Yes | -- | Google Gemini API key |
| `GEMINI_MODEL` | No | `gemini-3-flash-preview` | Gemini model to use |
| `MAX_COMMENT_CHARS` | No | `800000` | Max characters of comment text to send to Gemini |

## Architecture

The pipeline is: **scrape -> truncate -> prompt -> parse -> display**.

```
main.py          CLI entry point + rich output rendering
reddit_client.py Scrapes old.reddit.com, flattens comments, filters junk
summariser.py    Builds prompt, calls Gemini, parses structured response
models.py        Pydantic models for both scraped data and Gemini schema
config.py        Module-level env var constants
```

## Dependencies

- `requests` + `beautifulsoup4` -- Reddit scraping
- `google-genai` -- Gemini API client
- `pydantic` -- structured output schema / data models
- `rich` -- terminal formatting (panels, tables, colour bars)
