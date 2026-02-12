import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise SystemExit(
        "Error: Required environment variable 'GEMINI_API_KEY' is not set.\n"
        "Set it in your shell: export GEMINI_API_KEY='your-key'"
    )

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
MAX_COMMENT_CHARS = int(os.getenv("MAX_COMMENT_CHARS", "800000"))
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
