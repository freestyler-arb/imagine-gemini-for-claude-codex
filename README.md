<div align="center">

# 🛰️ Gemini for Claude Code & Codex

**Delegate reasoning, code review, and research to Google Gemini — from inside your coding agent.**

Paid for by your **Google AI Pro / Ultra** subscription via the Antigravity CLI (`agy`), *not* by your agent's tokens.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-skill%20%2B%20plugin-orange)](#-install)
[![Codex](https://img.shields.io/badge/Codex-compatible-blue)](#-using-with-codex)
[![Shell](https://img.shields.io/badge/shell-bash-lightgrey)](bin/gemini)

</div>

---

A small **skill pack + CLI wrapper** that lets Claude Code (or Codex) hand a task to Google Gemini and relay the answer. The heavy generation runs on Google's side through the **Antigravity CLI** (`agy`), so your agent only orchestrates the call. You get a strong, *independent* second model for second opinions, reviews, and large-context digestion — without spending agent credits on the generation.

## ✨ What you get

| Skill | What it does | Trigger examples |
|-------|--------------|------------------|
| **`gemini-pro`** | General one-shot delegation to Gemini (default **Gemini 3.1 Pro, High**) with **model selection** via `-m`. The freeform fallback. | *"ask Gemini Pro to…"*, *"use Gemini"*, *"юзай Gemini"* |
| **`gemini-review`** | Independent **adversarial review** of code, a diff, a PR, or a plan, with severity-tagged findings. | *"let Gemini review this"*, *"second opinion before merge"* |
| **`gemini-research`** | **Research / digestion** over large context — summaries, comparisons, "find X across all of this", structured sourced reports. | *"have Gemini dig into this module"*, *"compare these options"* |
| **`gemini-proxy`** | **Automatic prompt engineering**: for your **next N substantive prompts** (default 10), Gemini rewrites each message you type into a sharper first-person version before the assistant acts — which still answers with full chat context. Smart filter skips trivial/config/meta; self-disables after N. | *"enable gemini proxy"*, *"polish my prompts with Gemini"*, *"переделывай мои промты через гемини"* |

Plus **`bin/gemini`** — a dependency-free Bash wrapper over `agy -p` (model shortcuts + stdin context), and **`install.sh`** to put everything in place.

## 🧠 How it works

```
 You ─▶ Claude Code / Codex ─▶ /gemini-* skill ─▶ `gemini` wrapper ─▶ `agy -p` ─▶ Gemini (your AI Pro quota)
                                                                                      │
 You ◀── synthesised, verified answer ◀── your agent ◀───────────────────────────────┘
```

Your agent writes a self-contained prompt, optionally pipes files as context, runs the wrapper, sanity-checks the result, and relays it. Generation is billed to your Google subscription's **weekly compute quota**, not to your agent.

## 📦 Requirements

- **macOS or Linux** with `bash`.
- A **Google AI Pro or Ultra** subscription. *(The subscription quota is reached through Google's own CLI — a pay-per-token Gemini API key is a **different** thing and won't use your subscription.)*
- **Antigravity CLI** (`agy`) — Google's headless client:
  ```bash
  brew install --cask antigravity-cli
  ```
- A coding agent that loads skills: **Claude Code** (`~/.claude/skills/`) or **Codex** (`~/.agents/skills/`).

> **Why `agy` and not the old `gemini` CLI?** Google retired the consumer Gemini CLI for AI Pro/Ultra/free tiers in mid-2026 and replaced it with the Antigravity CLI (`agy`). Quota is now a **weekly compute cap**, not a daily request count.

## 🚀 Install

### Option A — as a Claude Code plugin (one command)

```text
/plugin marketplace add freestyler-arb/gemini-for-claude-and-codex
/plugin install gemini@gemini-for-claude-and-codex
```

This loads the three skills. You still need the `agy` CLI (above) and the `gemini` wrapper. Grab the wrapper from this repo, **read it** (it's short — mostly comments), then put it on your PATH:

```bash
# clone or download bin/gemini, review it, then:
mkdir -p ~/.local/bin && cp bin/gemini ~/.local/bin/gemini && chmod +x ~/.local/bin/gemini
```

> Don't `curl | bash` a script onto your PATH without reading it. Option B's `./install.sh` does the same copy after you've cloned and can inspect the source.

### Option B — script install (Claude Code **and** Codex)

```bash
git clone https://github.com/freestyler-arb/gemini-for-claude-and-codex.git
cd gemini-for-claude-and-codex
./install.sh
```

This installs the `gemini` wrapper to `~/.local/bin/` and the three skills to **both** `~/.claude/skills/` (Claude Code) and `~/.agents/skills/` (Codex). Override targets with `BIN_DIR=…` / `SKILLS_DIRS=…`.

### Then: one-time Antigravity login

The wrapper can't log in for you — it needs a real browser OAuth:

```bash
agy            # choose your Google AI Pro account when prompted
```

### Make sure `~/.local/bin` is on your PATH

A fresh macOS/Linux shell often doesn't include it, so `gemini` won't be found:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc   # or ~/.bashrc
exec $SHELL
```

### Smoke test

```bash
gemini "reply with one word: ok"
```

In Claude Code / Codex the skills are **Agent Skills**: the model loads them automatically when your request matches their `description` (e.g. *"ask Gemini Pro to…"*). You can also nudge it explicitly: *"use the gemini-review skill on this diff."*

## 🛠 Usage

### From the CLI

```bash
# Default = Gemini 3.1 Pro (High)
gemini "explain the trade-offs of optimistic vs pessimistic locking"

# Pipe a file as context
cat src/order_engine.py | gemini "review this for correctness bugs"

# Several files at once
cat a.py b.py | gemini "trace the order flow across these two files"

# Cheaper / faster on the weekly quota
gemini -m flash "summarise this changelog in 5 bullets" < CHANGELOG.md
```

### From your agent

Just ask in natural language — the right skill fires on its own:

- *"Ask Gemini Pro to explain this regex / rewrite this function."* → `gemini-pro`
- *"Let Gemini review this diff before I merge."* → `gemini-review`
- *"Have Gemini dig through this module and summarise the data flow."* → `gemini-research`

### Model selection (`-m`)

| Flag | Model | Use for |
|------|-------|---------|
| *(none)* / `-m pro` | Gemini 3.1 Pro (High) | Default. Hard reasoning, reviews, architecture. |
| `-m pro-low` | Gemini 3.1 Pro (Low) | Pro quality, lighter budget, faster. |
| `-m flash` | Gemini 3.5 Flash (High) | Fast & cheap; summaries, bulk tasks. |
| `-m flash-mid` | Gemini 3.5 Flash (Medium) | Middle ground. |
| `-m flash-low` | Gemini 3.5 Flash (Low) | Cheapest / fastest. |
| `-m "<full name>"` | anything from `agy models` | e.g. `"Claude Opus 4.6"`, `"GPT-OSS 120B"`. |

Run `agy models` to see everything your subscription exposes. Set a different default with `GEM_MODEL`, or point at a non-standard binary with `AGY_BIN`.

## 🤖 Using with Codex

The skills are plain `SKILL.md` files, so the **same three skills work in Codex** with no changes:

- `./install.sh` already copies them to `~/.agents/skills/` (Codex's personal-skills directory).
- Codex loads skills natively — just phrase your request to match a skill, or name it.
- The `gemini` wrapper and `agy` login are shared across both agents — install once, use from either.

## 🔁 `gemini-proxy` — automatic prompt engineering

The other three skills are one-shot delegation. **`gemini-proxy` turns Gemini into your prompt engineer.**
Enable it, and for your **next N substantive prompts (default 10)** Gemini quietly **rewrites each message
you type into a sharper, more detailed first-person version of itself** — as a senior prompt engineer
would — *before* your assistant acts on it. The assistant still answers **with the full chat context, your
project rules, and memory**; Gemini only polishes the wording, it does not replace the conversation. A
**smart filter** sends real tasks (build / fix / audit / design / research / vague-big asks) through and
skips trivial / config / meta chatter (greetings, "ok/thanks", settings), so the counter only spends on
real work. It **self-disables** after N.

```text
/gemini-proxy            # enable for the next 10 prompts (or /gemini-proxy <N>)
python3 ~/.claude/skills/gemini-proxy/proxy_state.py peek      # prompts remaining (0 = off)
python3 ~/.claude/skills/gemini-proxy/proxy_state.py disable   # stop early
python3 ~/.claude/skills/gemini-proxy/verify_gemini_proxy.py   # TDD: exactly N, auto-off, fail-safe (17/17)
```

- **Project rules.** The rewrite reads a project rules/canon file so Gemini knows your project:
  `$GEMINI_PROXY_RULES` → `./.gemini-proxy-rules.txt` → `./.claude/gemini-proxy-rules.txt`, else the
  shipped generic `prompt-rules.template.txt` (copy it and fill in your project's canon).
- **The rewrite is a brief, not an override.** It never outranks your real instructions, your project's
  safety rules, or the agent's own verification. **Never pipe secrets** into the rewrite.
- **Optional hard enforcement (Claude Code).** By default the agent just follows the skill + a counter.
  For deterministic per-prompt enforcement, opt in to the bundled `UserPromptSubmit` hook by copying the
  snippet from `skills/gemini-proxy/hook/settings-hook-snippet.json` into your `.claude/settings.json`.
  The hook is fail-open and makes no network calls. Codex uses the skill + counter (no hook).

## 🔒 Security & privacy

This tool **sends your prompt and any piped context to Google Gemini** by design. Before you use it — and especially before you fork and publish — read **[SECURITY.md](SECURITY.md)**. The essentials:

- **Never pipe secrets.** Strip API keys, tokens, `.env` files, and private data before piping — the wrapper sends whatever you give it, verbatim.
- **Treat output as untrusted.** Gemini can be wrong, and a reviewed file can carry prompt-injection. Never run commands/code it returns without reading them.
- **No credentials in this repo.** Auth lives only in your local `agy` login; nothing sensitive is committed.
- **The install script** makes no network calls, uses no `sudo`, and only copies files into your own home directory. Read it first — it's ~45 lines of plain Bash.

## 🧩 How to write a skill — and its `description`

Each skill is a folder with one `SKILL.md`: YAML frontmatter, then Markdown the agent reads on demand.

```markdown
---
name: gemini-review
description: Use when the user wants an independent second-opinion review of code, a diff,
  a PR, or a plan from Google Gemini — "let Gemini review this", "юзай Gemini для ревью".
---

# gemini-review
## Overview …      ← what it is, in 1–2 sentences
## How to invoke … ← the exact command(s)
## Steps …         ← the workflow
## When to use / Not for …
## Common mistakes …
```

**The `description` is the single most important line** — it's all the agent sees when deciding whether to load the skill. Rules these three skills follow:

- **Describe *when to use*, not *what it does*.** Start with **"Use when…"** and list concrete triggers/symptoms. If you summarise the workflow here, the agent tends to follow the one-liner instead of reading the full skill.
- **Write in the third person** — it's injected into the system prompt.
- **Pack in real trigger phrases and keywords** the user would actually say (multiple languages if you use them — these ship with English *and* Russian triggers).
- **Name the technology** when the skill is tool-specific (here: Google Gemini, Antigravity CLI).
- **Keep it under ~500 characters.** Make each skill's triggers **distinct** so the right one fires — a generic "fallback" skill should *defer* to the specialists in its own description.

```yaml
# ❌ summarises the workflow → agent skips the body
description: Reviews code by piping it to Gemini and printing severity-tagged findings.

# ✅ triggers only → agent loads the skill and follows it
description: Use when the user wants an independent second-opinion review of code, a diff,
  a PR, or a plan from Gemini — "let Gemini review this", "second opinion before merge".
```

## 🗺 Repo layout

```
gemini-for-claude-and-codex/
├── .claude-plugin/
│   ├── marketplace.json              # so others can /plugin marketplace add this repo
│   └── plugin.json                   # Claude Code plugin manifest
├── .codex-plugin/
│   └── plugin.json                   # Codex plugin manifest
├── .github/workflows/shellcheck.yml  # CI: shellcheck on bin/ + install.sh
├── skills/
│   ├── gemini-pro/SKILL.md
│   ├── gemini-review/SKILL.md
│   ├── gemini-research/SKILL.md
│   └── gemini-proxy/                 # the N-prompt rewrite protocol
│       ├── SKILL.md
│       ├── proxy_state.py            # the counter (atomic, fail-safe)
│       ├── prompt-rules.template.txt # generic rules template (copy into your project)
│       ├── verify_gemini_proxy.py    # TDD: exactly N, auto-off, fail-safe
│       └── hook/                     # optional Claude Code UserPromptSubmit hook (opt-in)
│           ├── gemini_proxy_hook.py
│           └── settings-hook-snippet.json
├── bin/gemini                        # the wrapper over `agy -p`
├── install.sh                        # installs wrapper + skills (Claude + Codex)
├── SECURITY.md
├── README.md
├── LICENSE
└── .gitignore
```

## 🤝 Contributing

Issues and PRs welcome. Good contributions: new model shortcuts as Google ships tiers, extra skills (e.g. `gemini-translate`, `gemini-explain`), and fixes to keep the wrapper working as `agy` evolves. Keep skills focused and follow the description rules above.

## 📄 License

[MIT](LICENSE).

---

<details>
<summary>🇷🇺 Кратко по-русски</summary>

Пакет даёт твоему агенту (**Claude Code** или **Codex**) три навыка для делегирования задач **Google Gemini** через Antigravity CLI (`agy`) — оплачивается подпиской **AI Pro**, а не токенами агента:

- **`gemini-pro`** — общая делегация + выбор модели (`-m flash|pro|…`).
- **`gemini-review`** — независимый разбор кода / диффа / плана.
- **`gemini-research`** — ресёрч и переваривание больших контекстов.
- **`gemini-proxy`** — протокол: твои **следующие N промтов** (деф.10) Gemini переписывает в детальный промт для агента, агент исполняет его. Сам выключается после N. Правила проекта — из локального файла (`./.gemini-proxy-rules.txt`).

**Установка (плагином):** `/plugin marketplace add freestyler-arb/gemini-for-claude-and-codex`, затем `/plugin install gemini@gemini-for-claude-and-codex`.
**Установка (скриптом, Claude + Codex):** `git clone …` → `./install.sh`.
Дальше: добавить `~/.local/bin` в `PATH`, один раз войти `agy` (Google AI Pro), проверка — `gemini "скажи ок"`.

⚠️ **Безопасность:** всё, что ты передаёшь в `gemini`, уходит в Google. Не передавай ключи/токены/`.env`. Вывод Gemini считай непроверенным — не запускай его код вслепую. Подробности — в [SECURITY.md](SECURITY.md).

</details>
