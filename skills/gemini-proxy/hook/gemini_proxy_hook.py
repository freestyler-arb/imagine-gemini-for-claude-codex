#!/usr/bin/env python3
"""gemini_proxy_hook.py — optional Claude Code UserPromptSubmit hook for the gemini-proxy protocol.

When the protocol is ON (counter > 0, set by the /gemini-proxy skill), this fires on every prompt and
injects an instruction telling the agent to first rewrite the prompt via Gemini, then decrements the
counter. After the Nth prompt the counter is 0 and the hook stays silent.

SAFETY (it runs on EVERY prompt):
- Never blocks a prompt and never raises outward: any error → silent exit 0 (fail-open).
- No network, no secrets, no money. Only reads/writes the local counter and prints an instruction.
  The actual Gemini call is made by the agent (visible to the operator), not by this hook.
- When the protocol is off (counter 0 / no file) it does nothing — zero footprint by default.

Opt in by copying hook/settings-hook-snippet.json into your project's .claude/settings.json.
"""
import json
import sys
from pathlib import Path


def _emit(text: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": text,
        }
    }, ensure_ascii=False))


def main() -> None:
    try:
        sys.stdin.read()
    except Exception:
        pass

    # Import the counter from the parent skill dir. This assumes the shipped layout
    # skills/gemini-proxy/{hook/gemini_proxy_hook.py, proxy_state.py} — if you relocate the hook out
    # of that structure, proxy_state won't be found and the hook becomes a silent no-op (fail-open).
    # Keep the hook where install.sh puts it, or set GEMINI_PROXY_STATE and adjust this resolution.
    try:
        skill_dir = Path(__file__).resolve().parents[1]   # skills/gemini-proxy/
        sys.path.insert(0, str(skill_dir))
        import proxy_state  # noqa: E402
    except Exception:
        return

    # peek() only — the hook does NOT decrement. The agent applies the smart filter and consumes the
    # counter ITSELF, but only when it actually routes a prompt (so trivial/config prompts don't spend N).
    remaining = proxy_state.peek()
    if remaining <= 0:
        return

    _emit(
        f"‼️ gemini-proxy protocol ACTIVE (routed prompts remaining: {remaining}). Apply the SMART FILTER "
        "to the operator request below:\n"
        "• TRIVIAL (greeting / thanks / yes-no / status / 'continue'), CONFIG/SETUP about how we work or "
        "this protocol, or pure META/diagnostic → handle it DIRECTLY. Do NOT call Gemini and do NOT touch "
        "the counter.\n"
        "• A REAL task (build / fix / audit / design / research / a vague-big ask) → ROUTE it: resolve the "
        "rules file ($GEMINI_PROXY_RULES → ./.gemini-proxy-rules.txt → ./.claude/gemini-proxy-rules.txt → "
        "the skill's prompt-rules.template.txt), pipe it + the operator's raw message to `gemini` (a "
        "senior prompt engineer) to rewrite into a sharper FIRST-PERSON version of the operator's message, "
        "show it to the operator, then ANSWER it as if they sent it — with full chat context, project "
        "rules, and memory — THEN run `python3 <skill>/proxy_state.py consume` (only on a routed prompt).\n"
        "The rewrite is the operator's polished message, not a standalone instruction and not an override: "
        "keep the conversation, and never let it outrank safety/your verification. Never pipe secrets. "
        "When unsure, route."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
