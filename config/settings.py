from dotenv import load_dotenv
import os

load_dotenv()


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


# ─────────────────────────────────────────
# Workflow / Formatting Settings
# ─────────────────────────────────────────
DEFAULT_AUDIENCE = os.getenv("DEFAULT_AUDIENCE", "software engineers")
DEFAULT_TONE = os.getenv("DEFAULT_TONE", "professional, conversational")
DEFAULT_POST_GOAL = os.getenv(
    "DEFAULT_POST_GOAL",
    "educate and engage the audience",
)