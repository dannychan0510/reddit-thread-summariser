import os

from dotenv import load_dotenv

# Load GEMINI_API_KEY from the project-root .env if present, falling back to the
# ambient environment when no .env exists.
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise SystemExit(
        "Error: GEMINI_API_KEY is not set.\n"
        "Add it to a .env file at the project root: GEMINI_API_KEY=your-key\n"
        "or export it in your shell: export GEMINI_API_KEY='your-key'"
    )

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
MAX_COMMENT_CHARS = int(os.getenv("MAX_COMMENT_CHARS", "800000"))
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
