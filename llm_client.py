import json
import re
import requests


class LLMClient:
    def __init__(self, config):
        self.config = config



    def complete(self, system_prompt: str, messages: list) -> str:
        """Call the configured LLM and return raw text response."""
        provider = self.config.LLM_PROVIDER.lower()
        if provider == "gemini":
            return self._gemini(system_prompt, messages)
        elif provider == "groq":
            return self._groq(system_prompt, messages)
        elif provider == "ollama":
            return self._ollama(system_prompt, messages)
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: '{provider}'. Use gemini, groq, or ollama.")


    # ── Groq (FREE tier)

    def _groq(self, system_prompt: str, messages: list) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"

        all_msgs = [{"role": "system", "content": system_prompt}] + messages

        payload = {
            "model":       self.config.GROQ_MODEL,
            "messages":    all_msgs,
            "temperature": 0.1,
            "max_tokens":  2048,
        }

        resp = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {self.config.GROQ_API_KEY}",
                "Content-Type":  "application/json",
            },
            json=payload,
            timeout=40,
        )

        if resp.status_code != 200:
            raise RuntimeError(
                f"Groq API error {resp.status_code}: {resp.text[:300]}"
            )

        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError(f"Unexpected Groq response structure: {data}") from exc

    
