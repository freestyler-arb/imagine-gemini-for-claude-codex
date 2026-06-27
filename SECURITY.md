# Security & Privacy

Read this before using the tool — it sends your data to a third party by design.

## What the tool does with your data

Every call to `gemini` (or the skills that wrap it) sends your **prompt and any piped context** to **Google Gemini** through the Antigravity CLI (`agy`), using your Google AI Pro / Ultra subscription. Treat each call as **handing that text to Google**.

- **Never pipe secrets.** Strip API keys, tokens, passwords, `.env` files, private keys, and personal data before piping a file to `gemini`. The wrapper does **not** filter content — whatever you pipe is sent verbatim.
- **Treat Gemini's output as untrusted.** It can be wrong, and a file you pipe in for review may contain text that tries to steer the model (prompt injection). **Never run commands or code Gemini returns without reading them first.**
- **No credentials live in this repo.** The wrapper holds no keys. Auth lives only in your local `agy` login under `~/.gemini/…`, which is never part of this repository.

## A note on `gemini-proxy`

The `gemini-proxy` skill sends **every prompt in its active window** (the next N, default 10) to Google
Gemini for rewriting — a larger, more continuous data flow than the one-shot skills. Keep the same rule:
**never include secrets in those prompts or in the project rules file** they're piped with. The protocol
self-disables after N, and `proxy_state.py disable` stops it immediately. Its optional Claude Code hook
(`skills/gemini-proxy/hook/`) is **opt-in** (you add it to your own `.claude/settings.json`), runs on
every prompt while enabled, makes **no network calls**, touches no credentials, and is fail-open (any
error → it does nothing and cannot block your prompt).

## The install script

`install.sh` only copies files into your own `~/.local/bin` and agent skill directories. It runs **no `sudo`, no network calls, and no telemetry**. It is ~45 lines of plain Bash — read it before running. `bin/gemini` is a thin wrapper that quotes all inputs and never `eval`s them, so piped content cannot inject shell commands.

## Keep your own setup safe

- Don't commit your shell history, `~/.gemini/`, or any `agy` tokens.
- If you fork and publish, configure git to use a **GitHub no-reply email** so your real address doesn't end up in public commit metadata:
  ```bash
  git config user.email "<your-username>@users.noreply.github.com"
  ```

## Reporting a vulnerability

Open a GitHub issue for non-sensitive reports, or use **GitHub Security Advisories** on this repository for anything that should stay private until fixed.
