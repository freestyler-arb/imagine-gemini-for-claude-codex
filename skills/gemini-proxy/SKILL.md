---
name: gemini-proxy
description: Use when the operator wants their next prompts routed through Gemini before the agent acts —
  "enable gemini proxy", "route my prompts through Gemini", "Gemini rewrites my prompts", "включи
  гемини-прокладку", "переделывай мои промты через гемини", or a /gemini-proxy call; also when they ask
  to turn the protocol on for the next N prompts or to tune which prompts it covers. Builds on gemini-pro;
  distinct from one-off gemini-pro / gemini-review / gemini-research.
---

# gemini-proxy

## Overview
A prompt-**polishing** protocol. While active, each of your next N *substantive* prompts is first sent to
Gemini — a senior prompt engineer — which rewrites the operator's message into a sharper, more detailed
**first-person** version (still the operator's own message, not a standalone brief). The assistant then
answers that improved message **with the full chat context, project rules, and memory** — Gemini only
sharpens the wording, it does not replace the conversation. Trivial / config / meta prompts are skipped.
**Self-disables after N.** Control layer only: it calls nothing but the counter and the `gemini` wrapper.

## When to route vs skip (the smart filter)
Decide BEFORE calling Gemini. Bias to ROUTE for real work; SKIP only clear noise. Skipped prompts never
spend the counter, so **N = N routed prompts**.

| ROUTE — counts as 1 of N | SKIP — no Gemini, no counter |
|---|---|
| build / fix / refactor / audit / design / research | greeting, thanks, yes/no, "status", "continue" |
| vague or large asks ("do all of this", "make it nice") | config / setup / preferences about how we work or this protocol |
| anything that benefits from a sharper brief | pure meta / diagnostic ("did you use Gemini?", "what did you mean?") |

## Enable
`/gemini-proxy` (optional count: `/gemini-proxy 10`). Sets the counter; the enabling prompt itself does
not count.
```bash
python3 proxy_state.py enable 10
```

## Per-prompt protocol (ROUTED prompts only)
1. Resolve the project rules file, else the shipped template:
   `$GEMINI_PROXY_RULES → ./.gemini-proxy-rules.txt → ./.claude/gemini-proxy-rules.txt → prompt-rules.template.txt`
2. Pipe rules + the operator's raw message to Gemini (its rules file opens with the full role brief):
```bash
RULES="${GEMINI_PROXY_RULES:-./.gemini-proxy-rules.txt}"; [ -f "$RULES" ] || RULES="<skill>/prompt-rules.template.txt"
cat "$RULES" <(printf '%s' "<RAW MESSAGE>") \
  | gemini "You are a senior prompt engineer. Rewrite the operator's message into a sharper, more detailed FIRST-PERSON version (their own voice), per the context. Output ONLY the improved message."
```
3. Show the operator the improved message, then **answer it as if they had sent it — with the full chat
   context, project rules, and memory** (Gemini only sharpened the wording, it did not replace the
   conversation). Then spend exactly one: `python3 proxy_state.py consume` — only on a ROUTED prompt.

## Guardrail
The rewrite is the **operator's own message, polished — not a context-free instruction and not an
override.** Answer it with the full conversation, project rules, and memory. It does not outrank the
operator's real intent, the project's safety invariants, or your own verification (Gemini lacks the
session's context). On conflict, follow safety and say so. **Never pipe secrets** (`.env`, keys, tokens).

## Manage
`proxy_state.py peek` (remaining) · `disable` (stop now) · re-invoke to reset N. State lives in
`~/.gemini_proxy_state.json`. **Optional hard enforcement (Claude Code):** copy the `hooks` block from
`hook/settings-hook-snippet.json` into your `.claude/settings.json` — a fail-open `UserPromptSubmit` hook
that peeks and injects the filter (no network; the agent still consumes only on a routed prompt). Codex
uses the skill + counter (no hook).

## Verify
`python3 verify_gemini_proxy.py` — exactly-N, auto-off, fail-safe, concurrency lock, hook (21/21).

## Not for
One-off delegation → **gemini-pro**. A single review → **gemini-review**. Large-context digestion →
**gemini-research**. This skill is only the multi-prompt rewrite *protocol*.

## Common mistakes
- **Routing noise or skipping real work.** Trivial / config / meta → handle directly; real tasks → route.
  When unsure, route.
- **Guessing the target.** "our repo / the skill / that project" → resolve the concrete path (by name,
  git remote, open folder) and confirm; never assume the cwd. Gemini can't see the filesystem.
- **Treating the rewrite as a fresh standalone task.** It's the operator's *improved message* — answer
  it with the full chat context, project rules, and memory; never drop the conversation or its rules.
- **Double-counting.** Hook + manual `consume` on the same prompt — pick one layer.
- **`gemini` not found.** Needs the wrapper on PATH + a one-time `agy` login (see this pack's README).
