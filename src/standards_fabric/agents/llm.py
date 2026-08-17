"""Optional LLM writer. Provider is swappable by env var; the deterministic report never depends on it.

  SF_LLM=none        (default) — no model call; the report is the collected findings, grouped.
  SF_LLM=anthropic   uses ANTHROPIC_API_KEY, model SF_MODEL (default claude-haiku-4-5-20251001 — cheapest that reads Swedish well)
  SF_LLM=ollama      uses OLLAMA_URL (default http://localhost:11434) and SF_MODEL (default qwen2.5:14b)

Only stdlib. The prompt is versioned in prompts/summarise.md (single source of truth), never inline.
"""
from __future__ import annotations

import json
import os
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PROMPT_PATH = os.path.join(ROOT, "prompts", "summarise.md")


def load_prompt() -> str:
    with open(PROMPT_PATH, encoding="utf-8") as f:
        return f.read()


def summarise(findings_md: str, cadence: str) -> str | None:
    provider = os.environ.get("SF_LLM", "none").lower()
    if provider == "none":
        return None
    prompt = load_prompt().replace("{cadence}", cadence) + "\n\n---\n\n" + findings_md
    if provider == "anthropic":
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            return None
        model = os.environ.get("SF_MODEL", "claude-haiku-4-5-20251001")
        body = json.dumps({"model": model, "max_tokens": 1800,
                           "messages": [{"role": "user", "content": prompt}]}).encode()
        req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, headers={
            "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.load(r)
        return "".join(b.get("text", "") for b in d.get("content", []))
    if provider == "ollama":
        url = os.environ.get("OLLAMA_URL", "http://localhost:11434").rstrip("/") + "/api/generate"
        model = os.environ.get("SF_MODEL", "qwen2.5:14b")
        body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
        req = urllib.request.Request(url, data=body, headers={"content-type": "application/json"})
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.load(r).get("response")
    raise ValueError(f"unknown SF_LLM provider {provider}")
