<div align="center">

# 🛰️ Imagine

### A second brain for your coding agent — Google Gemini inside Claude Code & Codex.

**Hand the hard thinking — reasoning, independent code review, deep research, and *automatic prompt-engineering* — to Google Gemini. It runs on your Google AI Pro / Ultra subscription (`agy`), *not* on your agent's tokens.**

⚡ One install · 4 skills · **Claude Code & Codex** · no API key · no extra bill — just your existing AI Pro plan.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-skill%20%2B%20plugin-orange)](#-install)
[![Codex](https://img.shields.io/badge/Codex-compatible-blue)](#-using-with-codex)
[![Shell](https://img.shields.io/badge/shell-bash-lightgrey)](bin/gemini)

</div>

> ⚠️ **Security:** every `gemini` call sends your prompt + piped files to Google verbatim. **Never pipe secrets** (`.env`, keys, tokens). **Never run Gemini's output unread** — piped files can carry prompt injection, and Gemini can be wrong. See **[SECURITY.md](SECURITY.md)**.

---

## Why Imagine

Your coding agent is brilliant — and it has three blind spots:

- 🪞 **It reviews its own code.** Same model, same blind spots. Before you merge, you want a genuinely *different* pair of eyes.
- 🔥 **Research burns your tokens.** Digesting a huge module or comparing five libraries chews through your agent's budget fast.
- 🎲 **It acts on whatever you typed.** A rushed, half-formed prompt → a rushed, half-formed result.

**Imagine fixes all three** by giving your agent a second, *independent* model — **Google Gemini** — to hand work to. And because generation runs through Google's **Antigravity CLI** on your **AI Pro / Ultra subscription**, that heavy thinking is effectively **free**: a flat monthly fee you already pay, never metered against your agent's tokens.

> **A second brain for your coding agent — that you've already paid for.**

## ✨ The four skills

| Skill | What it gives you | Just say… |
|-------|-------------------|-----------|
| 🧠 **`gemini-pro`** | One-shot delegation to Gemini (default **3.1 Pro, High**), with model selection via `-m`. Offload hard reasoning and save your agent's credits. | *"ask Gemini Pro to…"*, *"use Gemini"*, *"юзай Gemini"* |
| 🔍 **`gemini-review`** | An **independent, adversarial** review of code / a diff / a PR / a plan — a different model, different blind spots, severity-tagged findings. Catch what self-review can't. | *"let Gemini review this"*, *"second opinion before I merge"* |
| 📚 **`gemini-research`** | **Deep research & large-context digestion** — summaries, comparisons, "find X across all of this", sourced reports — without spending agent tokens on the reading. | *"have Gemini dig into this module"*, *"compare these options"* |
| ✨ **`gemini-proxy`** | **Automatic prompt-engineering.** For your next N prompts, Gemini quietly rewrites each message into a sharper version *before* your agent acts. | *"enable gemini proxy"*, *"polish my prompts"*, *"переделывай мои промты через гемини"* |

Plus **`bin/gemini`** — a dependency-free Bash wrapper over `agy -p` (model shortcuts + stdin context), and **`install.sh`** to wire it all up for **both** Claude Code and Codex.

## ⭐ The one people love: `gemini-proxy`

The other three skills are one-shot. **`gemini-proxy` turns Gemini into your agent's built-in prompt engineer.** Enable it, and for your **next N substantive prompts (default 10)** Gemini rewrites each message you type into a sharper, more detailed **first-person** version of *itself* — as a senior prompt engineer would — *before* your agent acts. Your agent still answers **with the full chat context, your project rules, and memory**; Gemini only sharpens the wording. A **smart filter** routes real work (build / fix / review / design) and skips trivial / config / meta chatter, so the counter only spends on substance. It **self-disables after N**.

**Ground it first — this is what makes it great.** Drop a rules file in your project (canon + safety invariants + standing expectations) and Gemini rewrites *with your project in mind*:

```bash
cp skills/gemini-proxy/prompt-rules.template.txt ./.gemini-proxy-rules.txt
# then fill in: PROJECT CANON · STANDING EXPECTATIONS (tracker, finish-to-plan,
#               use-the-right-skills, independent review on risky changes, goal-drift) · HARD GUARDRAILS
```

Resolution order: `$GEMINI_PROXY_RULES → ./.gemini-proxy-rules.txt → ./.claude/gemini-proxy-rules.txt → shipped template`. The richer that file, the sharper **and safer** every rewrite. The rewrite is a *brief, not an override* — it never outranks your real instructions, your project's safety rules, or your agent's own verification. **Never pipe secrets** into it.

```text
/gemini-proxy            # enable for the next 10 prompts (or /gemini-proxy <N>)
python3 ~/.claude/skills/gemini-proxy/proxy_state.py peek      # prompts remaining (0 = off)
python3 ~/.claude/skills/gemini-proxy/proxy_state.py disable   # stop early
python3 ~/.claude/skills/gemini-proxy/verify_gemini_proxy.py   # TDD: exactly-N, auto-off, fail-safe (21/21)
```

> **Optional hard enforcement (Claude Code):** opt in to the bundled `UserPromptSubmit` hook (copy the snippet from `skills/gemini-proxy/hook/settings-hook-snippet.json` into `.claude/settings.json`). It's fail-open and makes no network calls. Codex uses the skill + counter (no hook).

## 🧠 How it works

```
 You ─▶ Claude Code / Codex ─▶ /gemini-* skill ─▶ `gemini` wrapper ─▶ `agy -p` ─▶ Gemini (your AI Pro quota)
                                                                                      │
 You ◀── synthesised, verified answer ◀── your agent ◀───────────────────────────────┘
```

Your agent writes a self-contained prompt, optionally pipes files as context, runs the wrapper, sanity-checks the result, and relays it. Generation is billed to your Google subscription's **weekly compute quota** — not to your agent.

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
/plugin marketplace add freestyler-arb/imagine-gemini-for-claude-codex
/plugin install imagine@imagine-gemini-for-claude-codex
```

This loads the four skills. You still need the `agy` CLI (above) and the `gemini` wrapper — grab it from this repo, **read it** (it's short, mostly comments), then put it on your PATH:

```bash
# clone or download bin/gemini, review it, then:
mkdir -p ~/.local/bin && cp bin/gemini ~/.local/bin/gemini && chmod +x ~/.local/bin/gemini
```

> Don't `curl | bash` a script onto your PATH without reading it. Option B's `./install.sh` does the same copy after you've cloned and can inspect the source.

### Option B — script install (Claude Code **and** Codex)

```bash
git clone https://github.com/freestyler-arb/imagine-gemini-for-claude-codex.git
cd imagine-gemini-for-claude-codex
./install.sh
```

Installs the `gemini` wrapper to `~/.local/bin/` and the four skills to **both** `~/.claude/skills/` (Claude Code) and `~/.agents/skills/` (Codex). Override with `BIN_DIR=…` / `SKILLS_DIRS=…`.

### Then: one-time Antigravity login + PATH

```bash
agy                                                        # pick your Google AI Pro account (browser OAuth)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc    # or ~/.bashrc, if ~/.local/bin isn't on PATH
exec $SHELL
gemini "reply with one word: ok"                           # smoke test
```

In Claude Code / Codex the skills are **Agent Skills** — the model loads them automatically when your request matches their `description` (e.g. *"ask Gemini Pro to…"*). You can also name one: *"use the gemini-review skill on this diff."*

## 🛠 Usage

```bash
# Default = Gemini 3.1 Pro (High)
gemini "explain the trade-offs of optimistic vs pessimistic locking"

# Pipe a file (or several) as context
cat src/order_engine.py | gemini "review this for correctness bugs"
cat a.py b.py | gemini "trace the order flow across these two files"

# Cheaper / faster on the weekly quota
gemini -m flash "summarise this changelog in 5 bullets" < CHANGELOG.md
```

From your agent, just ask in natural language — the right skill fires on its own:

- *"Ask Gemini Pro to explain this regex."* → `gemini-pro`
- *"Let Gemini review this diff before I merge."* → `gemini-review`
- *"Have Gemini dig through this module and summarise the data flow."* → `gemini-research`

### Model selection (`-m`)

| Flag | Model | Use for |
|------|-------|---------|
| *(none)* / `-m pro` | Gemini 3.1 Pro (High) | Default. Hard reasoning, reviews, architecture. |
| `-m pro-low` | Gemini 3.1 Pro (Low) | Pro quality, lighter budget, faster. |
| `-m flash` | Gemini 3.5 Flash (High) | Fast & cheap; summaries, bulk tasks. |
| `-m flash-mid` / `-m flash-low` | Flash (Medium / Low) | Middle ground / cheapest. |
| `-m "<full name>"` | anything from `agy models` | e.g. `"Claude Opus 4.6"`, `"GPT-OSS 120B"`. |

Run `agy models` for everything your subscription exposes. Set a different default with `GEM_MODEL`; point at a non-standard binary with `AGY_BIN`.

## 🤖 Using with Codex

The skills are plain `SKILL.md` files, so the **same four work in Codex** unchanged: `./install.sh` copies them to `~/.agents/skills/`, Codex loads skills natively, and the `gemini` wrapper + `agy` login are shared across both agents — install once, use from either.

## 💸 Cost & where the usage shows up

- **Gemini runs on your Google AI Pro / Ultra subscription (the Antigravity weekly compute quota), NOT the pay-per-token Gemini API.** If you check **Gemini API** usage (AI Studio / Cloud console) you'll see **zero** — that's expected; nothing goes through the API.
- **`gemini-proxy` is a *quality* tool, not a token-saver.** The Gemini generation is free (your sub), but the proxy adds a small **agent-side** round-trip per routed prompt (~hundreds–few-thousand tokens to send + read the rewrite back). That's why the smart filter skips trivial / config / meta. The one-shot skills have no standing overhead — they fire only when asked.

| | Cost |
|---|---|
| **Gemini's generation** | **$0** of agent credits — billed to your AI Pro / Antigravity weekly quota |
| Extra agent tokens per *routed* proxy prompt | ~200–400 in + ~200–500 out (one round-trip + reading the rewrite) |
| ≈ extra agent spend per routed prompt | **~$0.02–0.05** |
| As **% over answering directly** | **~5–15%** (higher on tiny prompts, lower on big tasks) |
| Trivial / config / meta prompts | **$0** — skipped by the smart filter |

Tight on agent credits? `proxy_state.py disable` and write directly; enable the proxy only when a sharper prompt is worth the round-trip.

## 🔒 Security & privacy

This tool **sends your prompt and any piped context to Google Gemini** by design. Read **[SECURITY.md](SECURITY.md)**. The essentials:

- **Never pipe secrets.** Strip keys, tokens, `.env`, private data — the wrapper sends whatever you give it, verbatim.
- **Treat output as untrusted.** Gemini can be wrong, and a reviewed file can carry prompt injection. Never run returned commands/code without reading them.
- **No credentials in this repo.** Auth lives only in your local `agy` login; nothing sensitive is committed.
- **`install.sh`** makes no network calls, uses no `sudo`, and only copies files into your own home directory. Read it first — it's ~45 lines of plain Bash.

## 🧩 Writing a skill — and its `description`

Each skill is a folder with one `SKILL.md`: YAML frontmatter, then Markdown the agent reads on demand. **The `description` is the single most important line** — it's all the agent sees when deciding whether to load the skill.

- **Describe *when to use*, not *what it does*.** Start with **"Use when…"** and list concrete triggers. (Summarise the workflow here and the agent follows the one-liner instead of reading the skill.)
- **Third person** (it's injected into the system prompt), **packed with real trigger phrases** (multiple languages if you use them — these ship English **and** Russian), **name the technology**, and keep it **under ~500 chars** with **distinct** triggers so the right skill fires.

```yaml
# ❌ summarises the workflow → agent skips the body
description: Reviews code by piping it to Gemini and printing severity-tagged findings.
# ✅ triggers only → agent loads the skill and follows it
description: Use when the user wants an independent second-opinion review of code, a diff,
  a PR, or a plan from Gemini — "let Gemini review this", "second opinion before merge".
```

## 🗺 Repo layout

```
imagine-gemini-for-claude-codex/
├── .claude-plugin/{marketplace.json, plugin.json}   # Claude Code plugin + marketplace
├── .codex-plugin/plugin.json                        # Codex plugin manifest
├── skills/
│   ├── gemini-pro/SKILL.md
│   ├── gemini-review/SKILL.md
│   ├── gemini-research/SKILL.md
│   └── gemini-proxy/                                 # the N-prompt rewrite protocol
│       ├── SKILL.md
│       ├── proxy_state.py            # the counter (atomic, fail-safe, fcntl-locked)
│       ├── proxy_route.py            # one-shot route: rules → Gemini → consume once
│       ├── prompt-rules.template.txt # ground-it template (copy into your project)
│       ├── verify_gemini_proxy.py    # TDD: exactly-N, auto-off, fail-safe, concurrency (21/21)
│       └── hook/                     # optional Claude Code UserPromptSubmit hook (opt-in)
├── bin/gemini                        # the wrapper over `agy -p`
├── install.sh                        # installs wrapper + skills (Claude + Codex)
├── SECURITY.md · README.md · LICENSE
```

## 🤝 Contributing

Issues and PRs welcome — new model shortcuts as Google ships tiers, extra skills (`gemini-translate`, `gemini-explain`), and fixes to track `agy`. Keep skills focused and follow the `description` rules above.

## 📄 License

[MIT](LICENSE).

---

<details>
<summary>🇷🇺 Кратко по-русски</summary>

**Imagine** — второй мозг для твоего кодинг-агента: даёт **Claude Code** и **Codex** четыре навыка делегирования **Google Gemini** через Antigravity CLI (`agy`). Оплачивается подпиской **AI Pro**, а не токенами агента.

- **`gemini-pro`** — делегация + выбор модели (`-m flash|pro|…`).
- **`gemini-review`** — независимый разбор кода / диффа / плана (другая модель = другие слепые зоны).
- **`gemini-research`** — ресёрч и переваривание больших контекстов.
- **`gemini-proxy`** — авто-промт-инжиниринг: следующие **N промтов** (деф.10) Gemini переписывает в более чёткую версию ОТ ПЕРВОГО ЛИЦА перед тем, как агент их выполнит. Умный фильтр пропускает тривиал; сам выключается после N. **Заземли** его файлом `./.gemini-proxy-rules.txt` (канон + standing-правила + гайдрейлы) — это и делает прокси по-настоящему полезным.

**Установка:** плагином — `/plugin marketplace add freestyler-arb/imagine-gemini-for-claude-codex` → `/plugin install imagine@imagine-gemini-for-claude-codex`; скриптом (Claude + Codex) — `git clone …` → `./install.sh`. Дальше: `~/.local/bin` в `PATH`, один раз `agy` (вход в Google AI Pro), проверка `gemini "скажи ок"`.

⚠️ **Безопасность:** всё, что передаёшь в `gemini`, уходит в Google. Не передавай ключи/токены/`.env`; вывод считай непроверенным. Подробности — [SECURITY.md](SECURITY.md).

</details>
