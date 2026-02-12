import logging
import random
import time
from typing import List

from google import genai
from google.genai import types

logging.getLogger("google_genai.types").setLevel(logging.ERROR)

import config
from models import AnalysisResult, RedditComment, RedditThread

MAX_RETRIES = 2
RETRY_DELAY_SECONDS = 2
MAX_COMMENTS_FOR_ANALYSIS = 50


def _sample_comments(comments: List[RedditComment], seed: int = None) -> List[RedditComment]:
    """Sample comments for analysis.

    If <= 50 comments: return all
    If > 50 comments: randomly select 50 using deterministic seeding

    Args:
        comments: List of comments to sample from
        seed: Random seed for reproducibility (uses hash of comment IDs if not provided)

    Returns:
        Sampled list of comments
    """
    if len(comments) <= MAX_COMMENTS_FOR_ANALYSIS:
        return comments

    # Use deterministic seed based on comment IDs for reproducibility
    if seed is None:
        seed = hash(''.join(c.comment_id for c in comments[:10])) % (2**32)

    rng = random.Random(seed)
    return rng.sample(comments, MAX_COMMENTS_FOR_ANALYSIS)


def build_prompt(thread: RedditThread) -> str:
    """Build the analysis prompt from thread data, truncating if needed."""
    comments, was_truncated, original_count = _truncate_comments(thread)

    # Sample comments if we have more than MAX_COMMENTS_FOR_ANALYSIS
    sampled_comments = _sample_comments(comments)
    was_sampled = len(sampled_comments) < len(comments)

    # Build note about truncation and/or sampling
    notes = []
    if was_truncated:
        notes.append(f"truncated from {original_count} to {len(comments)} highest-scored")
    if was_sampled:
        notes.append(f"randomly sampled {len(sampled_comments)} from {len(comments)} for analysis")

    truncation_note = " - " + ", ".join(notes) if notes else ""

    formatted_comments = []
    for c in sampled_comments:
        depth_label = " (reply)" if c.depth > 0 else ""
        header = f"[u/{c.author} | score: {c.score}{depth_label}]"
        formatted_comments.append(f"{header}\n{c.body}")

    comments_text = "\n\n".join(formatted_comments) if formatted_comments else "(No comments)"

    return f"""You are an expert financial analyst specialising in social media sentiment analysis.

Analyse the following Reddit discussion thread about stocks/investing. The thread is from r/{thread.subreddit}.

=== POST ===
Title: {thread.title}
Author: u/{thread.author}
Score: {thread.score}

{thread.selftext}

=== COMMENTS ({len(sampled_comments)} total{truncation_note}) ===
{comments_text}

Based on the above discussion, provide your analysis. Identify any stock tickers mentioned. Summarise the key discussion points. List the pros (bullish arguments) and cons (bearish arguments) for the stock(s).

IMPORTANT: For EVERY SINGLE commenter shown above, you MUST classify their overall sentiment toward the stock(s) being discussed as positive, negative, or neutral, with a brief reason. Do not skip any commenter - analyze all {len(sampled_comments)} comments above. If a user has multiple comments, combine their sentiment into one entry. If there are no comments, return an empty list for commenter_sentiments."""


def analyse_thread(thread: RedditThread) -> AnalysisResult:
    """Send the thread to Gemini and return structured analysis.

    Raises:
        RuntimeError: If Gemini API fails after retries.
    """
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    prompt = build_prompt(thread)

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AnalysisResult,
                ),
            )
            if not response.text:
                raise RuntimeError("Gemini returned an empty response")
            return AnalysisResult.model_validate_json(response.text)
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY_SECONDS)

    raise RuntimeError(
        f"Gemini API failed after {MAX_RETRIES} attempts: {last_error}"
    )


def _truncate_comments(thread: RedditThread) -> tuple[list, bool, int]:
    """Truncate comments to fit within MAX_COMMENT_CHARS.

    Comments are already sorted by score descending from reddit_client,
    so truncation naturally keeps the highest-value comments.

    Returns:
        (comments, was_truncated, original_count)
    """
    original_count = len(thread.comments)
    max_chars = config.MAX_COMMENT_CHARS

    post_chars = len(thread.title) + len(thread.selftext)
    remaining_chars = max_chars - post_chars

    if remaining_chars <= 0:
        return [], True, original_count

    kept_comments = []
    current_chars = 0

    for comment in thread.comments:
        comment_chars = len(comment.author) + len(comment.body) + 50
        if current_chars + comment_chars > remaining_chars:
            return kept_comments, True, original_count
        kept_comments.append(comment)
        current_chars += comment_chars

    return kept_comments, False, original_count
