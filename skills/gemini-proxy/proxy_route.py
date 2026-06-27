#!/usr/bin/env python3
"""proxy_route.py — one-shot router for gemini-proxy.

Does the whole routed-prompt step in ONE call so the counter can't desync (Gemini's review flagged that
leaving `consume` to the agent is fragile — LLMs forget service calls):
  resolve rules file → call the `gemini` wrapper to polish the operator's message into a sharper FIRST-
  PERSON version → decrement the counter ONCE → print the improved message to stdout.

Fallback: if `gemini` is missing, errors, times out, or returns empty, it prints the RAW message unchanged
prefixed with a marker line and does NOT decrement — so the agent answers the raw message and tells the
operator Gemini was unavailable. Never hangs the agent.

Usage:  python3 proxy_route.py "<raw operator message>"
Rules precedence: $GEMINI_PROXY_RULES | ./.gemini-proxy-rules.txt | ./.claude/gemini-proxy-rules.txt
                  | <this skill dir>/prompt-rules.template.txt
gemini binary: $GEMINI_BIN | `gemini` on PATH | ~/.local/bin/gemini
Security: only the rules file + the raw message are sent to Gemini — keep real secret VALUES out of both.
"""
from __future__ import annotations
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FALLBACK_MARKER = "[[gemini-proxy: FALLBACK — Gemini unavailable, answer the raw message and tell the operator]]"
_TIMEOUT = float(os.getenv("GEMINI_PROXY_TIMEOUT", "150"))
_INSTRUCTION = ("You are a senior prompt engineer. Rewrite the operator's message into a sharper, more "
                "detailed FIRST-PERSON version (their own voice), per the context. Output ONLY the "
                "improved message.")


def _rules_path() -> Path:
    for cand in (os.getenv("GEMINI_PROXY_RULES"), "./.gemini-proxy-rules.txt", "./.claude/gemini-proxy-rules.txt"):
        if cand and Path(cand).is_file():
            return Path(cand)
    return HERE / "prompt-rules.template.txt"


def _gemini_bin() -> str | None:
    env = os.getenv("GEMINI_BIN")
    if env and (Path(env).is_file() or shutil.which(env)):
        return env
    found = shutil.which("gemini")
    if found:
        return found
    home = Path.home() / ".local/bin/gemini"
    return str(home) if home.is_file() else None


def _polish(raw: str) -> tuple[str, bool]:
    """Return (text, improved?). improved=False means fallback to the raw message."""
    gbin = _gemini_bin()
    if not gbin:
        return raw, False
    try:
        rules = _rules_path().read_text(encoding="utf-8")
    except Exception:
        rules = ""
    stdin = rules + "\n" + raw
    try:
        p = subprocess.run([gbin, _INSTRUCTION], input=stdin, capture_output=True,
                           text=True, timeout=_TIMEOUT)
    except Exception:
        return raw, False
    out = (p.stdout or "").strip()
    if p.returncode != 0 or not out:
        return raw, False
    return out, True


def main(argv) -> int:
    raw = argv[1] if len(argv) > 1 else sys.stdin.read()
    raw = (raw or "").strip()
    if not raw:
        print("usage: proxy_route.py \"<raw operator message>\"", file=sys.stderr)
        return 2

    text, improved = _polish(raw)
    if improved:
        # consume the counter exactly once — only on a real routed prompt
        try:
            import proxy_state
            res = proxy_state.consume()
            left = res.get("now", "?")
        except Exception:
            left = "?"
        print(text)
        print(f"[gemini-proxy] routed via Gemini; prompts remaining: {left}", file=sys.stderr)
    else:
        # fallback: do NOT consume; signal the agent to answer the raw message directly
        print(FALLBACK_MARKER)
        print(text)
        print("[gemini-proxy] FALLBACK: Gemini unavailable — counter NOT decremented", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
