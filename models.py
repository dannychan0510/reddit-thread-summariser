from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


# ---------- Internal data models ----------


class RedditComment(BaseModel):
    """A single flattened comment from the thread."""

    author: str
    body: str
    score: int
    depth: int
    comment_id: str
    parent_id: str


class RedditThread(BaseModel):
    """The complete fetched thread data."""

    title: str
    selftext: str
    author: str
    score: int
    url: str
    subreddit: str
    num_comments: int
    comments: list[RedditComment]


# ---------- Gemini response schema ----------


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


SENTIMENT_COLORS = {
    Sentiment.POSITIVE: "green",
    Sentiment.NEGATIVE: "red",
    Sentiment.NEUTRAL: "yellow",
}


class CommenterSentiment(BaseModel):
    """Sentiment classification for a single commenter."""

    author: str = Field(description="Reddit username of the commenter")
    sentiment: Sentiment = Field(
        description="Overall sentiment of this commenter toward the stock(s)"
    )
    reason: str = Field(
        description="Brief one-sentence reason for the classification"
    )


class AnalysisResult(BaseModel):
    """Complete analysis of a Reddit stock discussion thread."""

    tickers: list[str] = Field(
        description="Stock ticker symbols mentioned in the discussion (e.g. ['AAPL', 'TSLA'])"
    )
    summary: str = Field(
        description="A 3-5 sentence summary of the overall discussion and key points"
    )
    pros: list[str] = Field(
        description="List of bullish arguments and pros mentioned about the stock(s)"
    )
    cons: list[str] = Field(
        description="List of bearish arguments and cons mentioned about the stock(s)"
    )
    commenter_sentiments: list[CommenterSentiment] = Field(
        description="Sentiment classification for EVERY SINGLE commenter in the thread. Do not skip any - include all commenters from the provided comments section."
    )
