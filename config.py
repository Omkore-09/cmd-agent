"""
Configuration — loaded from .env file
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed yet; will still read os.environ


class Config:
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")

    # ── Google Gemini  ──────────────────────────────────────
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL:   str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # ── Groq  ───────────────────────────────────────────────
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL:   str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
   
    SAFE_MODE:       bool = os.getenv("SAFE_MODE", "true").lower() == "true"
    MAX_HISTORY:     int  = int(os.getenv("MAX_HISTORY", "20"))   # messages kept
    COMMAND_TIMEOUT: int  = int(os.getenv("COMMAND_TIMEOUT", "30"))  # seconds

    # ─────────────────────────────────────────────────────────────

    def get_model(self) -> str:
        mapping = {
            "gemini": self.GEMINI_MODEL,
            "groq":   self.GROQ_MODEL,
        }
        return mapping.get(self.LLM_PROVIDER, "unknown")

    def validate(self) -> list:
        """Return list of error strings; empty list means config is valid."""
        errors = []
        p = self.LLM_PROVIDER.lower()

        if p not in ("gemini", "groq"):
            errors.append(f"LLM_PROVIDER must be gemini, groq (got '{p}')")

        if p == "gemini" and not self.GEMINI_API_KEY:
            errors.append(
                "GEMINI_API_KEY is not set. "
                "Get a free key at https://aistudio.google.com/apikey"
            )

        if p == "groq" and not self.GROQ_API_KEY:
            errors.append(
                "GROQ_API_KEY is not set. "
                "Get a free key at https://console.groq.com/keys"
            )

        return errors
