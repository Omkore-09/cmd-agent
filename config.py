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
    # ── LLM Provider ─────────────────────────────────────────────
    # Options: "gemini"  |  "groq"  |  "ollama"
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")

    # ── Google Gemini (FREE) ──────────────────────────────────────
    # Key  → https://aistudio.google.com/apikey
    # Docs → https://ai.google.dev/gemini-api/docs
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL:   str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    #  Other free models: gemini-1.5-flash-8b  |  gemini-2.0-flash-exp

    # ── Groq (FREE) ───────────────────────────────────────────────
    # Key  → https://console.groq.com/keys
    # Docs → https://console.groq.com/docs/openai
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL:   str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    #  Other free Groq models: llama-3.1-8b-instant  |  mixtral-8x7b-32768
    #                          gemma2-9b-it

    # ── Ollama (local, 100 % FREE) ────────────────────────────────
    # Install → https://ollama.com/download
    # Pull    → run:  ollama pull llama3.2
    # Models  → https://ollama.com/library
    OLLAMA_HOST:  str = os.getenv("OLLAMA_HOST",  "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    #  Other good local models: mistral  |  qwen2.5  |  phi3  |  codellama

    # ── Agent Behaviour ───────────────────────────────────────────
    # SAFE_MODE=true  → confirms before risky/destructive commands
    SAFE_MODE:       bool = os.getenv("SAFE_MODE", "true").lower() == "true"
    MAX_HISTORY:     int  = int(os.getenv("MAX_HISTORY", "20"))   # messages kept
    COMMAND_TIMEOUT: int  = int(os.getenv("COMMAND_TIMEOUT", "30"))  # seconds

    # ─────────────────────────────────────────────────────────────

    def get_model(self) -> str:
        mapping = {
            "gemini": self.GEMINI_MODEL,
            "groq":   self.GROQ_MODEL,
            "ollama": self.OLLAMA_MODEL,
        }
        return mapping.get(self.LLM_PROVIDER, "unknown")

    def validate(self) -> list:
        """Return list of error strings; empty list means config is valid."""
        errors = []
        p = self.LLM_PROVIDER.lower()

        if p not in ("gemini", "groq", "ollama"):
            errors.append(f"LLM_PROVIDER must be gemini, groq, or ollama (got '{p}')")

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
