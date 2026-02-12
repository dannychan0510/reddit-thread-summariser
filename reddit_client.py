from __future__ import annotations

import re
from typing import Optional, Tuple

import requests
from bs4 import BeautifulSoup

import config
from models import RedditComment, RedditThread

REDDIT_URL_PATTERN = re.compile(
    r"https?://(?:www\.)?(?:old\.)?reddit\.com/r/(\w+)/comments/(\w+)"
)


def _parse_url(url: str) -> Tuple[str, str]:
    """Validate URL and return (old_reddit_url, subreddit). Raises ValueError."""
    url = url.strip().rstrip("/")
    match = REDDIT_URL_PATTERN.search(url)
    if not match:
        raise ValueError(
            f"Invalid Reddit post URL: {url}\n"
            "Expected format: https://www.reddit.com/r/<subreddit>/comments/<id>/..."
        )
    subreddit = match.group(1)
    old_url = re.sub(
        r"https?://(?:www\.)?reddit\.com", "https://old.reddit.com", url
    )
    return old_url, subreddit


def _is_valid_comment(div: BeautifulSoup) -> bool:
    """Return True if a comment div should be included."""
    if "deleted" in div.get("class", []):
        return False
    author_tag = div.find("a", class_="author")
    if not author_tag:
        return False
    if author_tag.get_text(strip=True) == "AutoModerator":
        return False
    md_div = div.find("div", class_="md")
    if not md_div:
        return False
    body = md_div.get_text(separator="\n", strip=True)
    return body not in ("[removed]", "[deleted]")


def fetch_thread(url: str) -> RedditThread:
    """Fetch a Reddit thread by scraping old.reddit.com.

    Raises:
        ValueError: If the URL is invalid.
        ConnectionError: If Reddit is unreachable.
        PermissionError: If the post is private/removed.
    """
    old_url, subreddit = _parse_url(url)

    try:
        response = requests.get(
            old_url,
            params={"limit": 500},
            headers={"User-Agent": config.USER_AGENT},
            timeout=30,
        )
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to connect to Reddit: {e}")

    if response.status_code == 404:
        raise ValueError(f"Reddit post not found: {url}")
    if response.status_code == 403:
        raise PermissionError(f"Reddit post is private or removed: {url}")
    if not response.ok:
        raise ConnectionError(f"Reddit returned HTTP {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    title = _extract_title(soup)
    selftext = _extract_selftext(soup)
    author = _extract_post_author(soup)
    score = _extract_post_score(soup)
    comments = _extract_comments(soup)
    comments.sort(key=lambda c: c.score, reverse=True)

    return RedditThread(
        title=title,
        selftext=selftext,
        author=author,
        score=score,
        url=url,
        subreddit=subreddit,
        num_comments=len(comments),
        comments=comments,
    )


def _extract_title(soup: BeautifulSoup) -> str:
    tag = soup.find("a", class_="title")
    return tag.get_text(strip=True) if tag else "(no title)"


def _extract_selftext(soup: BeautifulSoup) -> str:
    expando = soup.find("div", class_="expando")
    if not expando:
        return ""
    md_div = expando.find("div", class_="md")
    if not md_div:
        return ""
    return md_div.get_text(separator="\n", strip=True)


def _extract_post_author(soup: BeautifulSoup) -> str:
    tag = soup.find("div", id="siteTable")
    if tag:
        author_tag = tag.find("a", class_="author")
        if author_tag:
            return author_tag.get_text(strip=True)
    return "[deleted]"


def _parse_score(text: str) -> Optional[int]:
    """Parse a score string like '1234', '1,234', '1.2k', or '42 points' into an int."""
    text = text.strip().replace(",", "")
    # Strip common suffixes like " points" or " point"
    text = re.sub(r"\s*points?\s*$", "", text, flags=re.IGNORECASE)
    try:
        return int(text)
    except ValueError:
        pass
    match = re.match(r"^(-?[\d.]+)k$", text, re.IGNORECASE)
    if match:
        try:
            return int(float(match.group(1)) * 1000)
        except ValueError:
            pass
    return None


def _extract_post_score(soup: BeautifulSoup) -> int:
    site_table = soup.find("div", id="siteTable")
    search_root = site_table if site_table else soup

    # Try score divs/spans within the post area
    for tag in search_root.find_all(["div", "span"], class_="score"):
        # Try title attribute first, then text content
        for source in (tag.get("title", ""), tag.get_text(strip=True)):
            if source:
                score = _parse_score(source)
                if score is not None:
                    return score

    return 0


def _extract_comments(soup: BeautifulSoup) -> list[RedditComment]:
    """Extract all comments from the page."""
    comment_area = soup.find("div", class_="commentarea")
    if not comment_area:
        return []

    comments = []
    comment_divs = comment_area.find_all("div", class_="comment", id=True)

    for div in comment_divs:
        if not _is_valid_comment(div):
            continue

        author = div.find("a", class_="author").get_text(strip=True)
        body = div.find("div", class_="md").get_text(separator="\n", strip=True)

        score = 1
        score_tag = div.find("span", class_="score")
        if score_tag:
            parsed = _parse_score(score_tag.get("title", "1"))
            if parsed is not None:
                score = parsed

        depth = 0
        parent = div.parent
        while parent:
            if parent.name == "div" and "comment" in parent.get("class", []):
                depth += 1
            parent = parent.parent

        comment_id = div.get("data-fullname", div.get("id", ""))
        parent_id = div.get("data-parent", "")

        comments.append(
            RedditComment(
                author=author,
                body=body,
                score=score,
                depth=depth,
                comment_id=comment_id,
                parent_id=parent_id,
            )
        )

    return comments
