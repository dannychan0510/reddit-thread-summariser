import sys
import warnings

warnings.filterwarnings("ignore", category=FutureWarning, module=r"google\.")
warnings.filterwarnings("ignore", message=".*urllib3.*OpenSSL.*")

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from models import AnalysisResult, RedditThread, Sentiment, SENTIMENT_COLORS
from reddit_client import fetch_thread
from summariser import analyse_thread

console = Console()


def display_results(thread: RedditThread, analysis: AnalysisResult) -> None:
    """Render the analysis results in a formatted CLI output."""
    console.print()
    _display_header(thread, analysis.tickers)
    _display_summary(analysis.summary)
    _display_pros_cons(analysis.pros, analysis.cons)
    _display_sentiment(analysis.commenter_sentiments)
    console.print()


def _display_header(thread: RedditThread, tickers: list[str]) -> None:
    """Display post title and ticker badges."""
    ticker_text = Text()
    for ticker in tickers:
        ticker_text.append(f" ${ticker} ", style="bold white on blue")
        ticker_text.append(" ")

    subtitle = (
        f"r/{thread.subreddit}  |  Score: {thread.score}  "
        f"|  {thread.num_comments} comments"
    )

    header_content = Text()
    if tickers:
        header_content.append_text(ticker_text)
        header_content.append("\n")
    header_content.append(thread.title, style="bold")

    console.print(Panel(header_content, subtitle=subtitle, border_style="cyan"))


def _display_summary(summary: str) -> None:
    """Display the discussion summary in a panel."""
    console.print(Panel(summary, title="Discussion Summary", border_style="green"))


def _display_pros_cons(pros: list[str], cons: list[str]) -> None:
    """Display pros and cons in a two-column table."""
    table = Table(title="Pros & Cons", show_lines=True, border_style="yellow")
    table.add_column("Pros (Bullish)", style="green", ratio=1)
    table.add_column("Cons (Bearish)", style="red", ratio=1)

    max_rows = max(len(pros), len(cons))
    for i in range(max_rows):
        pro = f"+ {pros[i]}" if i < len(pros) else ""
        con = f"- {cons[i]}" if i < len(cons) else ""
        table.add_row(pro, con)

    console.print(table)


def _display_sentiment(sentiments: list) -> None:
    """Display sentiment breakdown with counts, percentages, and detail table."""
    total = len(sentiments)
    if total == 0:
        console.print("[dim]No commenter sentiments to display.[/dim]")
        return

    positive = sum(1 for s in sentiments if s.sentiment == Sentiment.POSITIVE)
    negative = sum(1 for s in sentiments if s.sentiment == Sentiment.NEGATIVE)
    neutral = sum(1 for s in sentiments if s.sentiment == Sentiment.NEUTRAL)

    console.print()
    console.print("[bold]Sentiment Breakdown[/bold]")
    console.print()

    bar_width = 30
    _print_bar("Positive", positive, total, bar_width, SENTIMENT_COLORS[Sentiment.POSITIVE])
    _print_bar("Negative", negative, total, bar_width, SENTIMENT_COLORS[Sentiment.NEGATIVE])
    _print_bar("Neutral", neutral, total, bar_width, SENTIMENT_COLORS[Sentiment.NEUTRAL])

    console.print()

    # Detail table - sorted by sentiment (positive, negative, neutral)
    table = Table(title="Per-Commenter Sentiment", show_lines=True)
    table.add_column("Author", style="bold")
    table.add_column("Sentiment")
    table.add_column("Reason", ratio=2)

    sentiment_order = {Sentiment.POSITIVE: 0, Sentiment.NEGATIVE: 1, Sentiment.NEUTRAL: 2}
    sorted_sentiments = sorted(sentiments, key=lambda s: sentiment_order[s.sentiment])

    for s in sorted_sentiments:
        colour = SENTIMENT_COLORS[s.sentiment]
        table.add_row(
            f"u/{s.author}",
            Text(s.sentiment.value.upper(), style=f"bold {colour}"),
            s.reason,
        )

    console.print(table)


def _print_bar(label: str, count: int, total: int, width: int, colour: str) -> None:
    """Print a single sentiment bar."""
    pct = (count / total * 100) if total > 0 else 0
    filled = int(width * count / total) if total > 0 else 0
    bar = "\u2588" * filled + "\u2591" * (width - filled)
    console.print(
        f"  [{colour}]{label:>8}[/]: {count:>3} ({pct:>5.1f}%)  [{colour}]{bar}[/]"
    )


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        console.print("[bold red]Usage:[/] python main.py <reddit_post_url>")
        console.print()
        console.print("Example:")
        console.print(
            "  python main.py https://www.reddit.com/r/ValueInvesting/comments/abc123/..."
        )
        sys.exit(1)

    url = sys.argv[1]

    try:
        with console.status("[bold green]Fetching Reddit thread..."):
            thread = fetch_thread(url)
        console.print(
            f"[green]Fetched {len(thread.comments)} comments "
            f"from r/{thread.subreddit}[/green]"
        )

        with console.status("[bold green]Analysing with Gemini..."):
            analysis = analyse_thread(thread)

        display_results(thread, analysis)

    except ValueError as e:
        console.print(f"[bold red]Invalid URL:[/] {e}")
        sys.exit(1)
    except ConnectionError as e:
        console.print(f"[bold red]Connection error:[/] {e}")
        sys.exit(1)
    except PermissionError as e:
        console.print(f"[bold red]Access denied:[/] {e}")
        sys.exit(1)
    except RuntimeError as e:
        console.print(f"[bold red]Analysis failed:[/] {e}")
        console.print("[dim]Check your GEMINI_API_KEY and API quota.[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()
