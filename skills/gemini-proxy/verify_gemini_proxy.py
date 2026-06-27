#!/usr/bin/env python3
"""verify_gemini_proxy.py — TDD lock for the gemini-proxy counter + hook.

Proves the core requirement: "exactly N prompts, then off". Isolated (own temp state file via
GEMINI_PROXY_STATE) — never touches the real counter. No network.
Run: python3 verify_gemini_proxy.py
"""
from __future__ import annotations
import importlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

fails = []
def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        fails.append(name)

_tmp = tempfile.mkdtemp(prefix="gemini_proxy_test_")
STATE = os.path.join(_tmp, "state.json")
os.environ["GEMINI_PROXY_STATE"] = STATE

import proxy_state  # noqa: E402
importlib.reload(proxy_state)

# 1. off by default (no file → 0)
check("default-off", proxy_state.peek() == 0)

# 2. enable(10) → 10
check("enable-10", proxy_state.enable(10) == 10 and proxy_state.peek() == 10)

# 3. EXACTLY 10 consumes: was 10→1, now 9→0, active all 10
seq_ok = True
for i in range(10):
    r = proxy_state.consume()
    if not (r["active"] and r["was"] == 10 - i and r["now"] == 9 - i):
        seq_ok = False; print(f"   step {i+1}: {r}")
check("exactly-10-consumes", seq_ok)
check("zero-after-10", proxy_state.peek() == 0)

# 4. 11th consume inactive (not 11 prompts)
r11 = proxy_state.consume()
check("11th-inactive", r11["active"] is False and r11["was"] == 0)

# 5. custom N=3 → exactly 3
proxy_state.enable(3)
acts = [proxy_state.consume()["active"] for _ in range(4)]
check("custom-N-3", acts == [True, True, True, False], f"{acts}")

# 6. disable() immediate
proxy_state.enable(10); proxy_state.disable()
check("disable-now", proxy_state.peek() == 0)

# 7. fail-safe: corrupt / negative → 0 (never stuck on)
Path(STATE).write_text("{ not json", encoding="utf-8")
check("corrupt-safe", proxy_state.peek() == 0)
Path(STATE).write_text(json.dumps({"remaining": -5}), encoding="utf-8")
check("negative-safe", proxy_state.peek() == 0)

# 8. enable clamps up to min 1
check("enable-clamp", proxy_state.enable(0) == 1)
proxy_state.disable()

# 9. HOOK end-to-end: active → injects + decrements; off → silent; always exit 0
HOOK = HERE / "hook" / "gemini_proxy_hook.py"
def run_hook():
    env = dict(os.environ); env["GEMINI_PROXY_STATE"] = STATE
    return subprocess.run([sys.executable, str(HOOK)], input='{"prompt":"x"}',
                          capture_output=True, text=True, env=env, timeout=15)

check("hook-exists", HOOK.exists(), str(HOOK))
proxy_state.disable()
p_off = run_hook()
check("hook-silent-off", p_off.returncode == 0 and p_off.stdout.strip() == "",
      f"rc={p_off.returncode} out={p_off.stdout[:60]!r}")
# Hook PEEKS only — it injects the smart-filter instruction but does NOT decrement (the agent consumes
# itself, and only on a routed prompt, so trivial/config prompts don't spend the counter).
proxy_state.enable(2)
p1 = run_hook()
check("hook-active-injects", "gemini-proxy protocol ACTIVE" in p1.stdout)
check("hook-no-decrement", proxy_state.peek() == 2, f"хук не трогает счётчик (peek={proxy_state.peek()})")
try:
    inj = json.loads(p1.stdout)["hookSpecificOutput"]["additionalContext"]
    check("hook-json-shape", "gemini" in inj.lower())
    check("hook-mentions-filter", "SMART FILTER" in inj and "ROUTE" in inj)
except Exception as e:
    check("hook-json-shape", False, f"{e}")
# The AGENT consumes (only when it routes). Hook keeps injecting while remaining > 0, silent at 0.
proxy_state.consume()
check("agent-consume-decrements", proxy_state.peek() == 1)
p2 = run_hook()
check("hook-active-still", ("ACTIVE" in p2.stdout) and proxy_state.peek() == 1)
proxy_state.consume()  # -> 0
p3 = run_hook()
check("hook-silent-at-zero", p3.stdout.strip() == "" and proxy_state.peek() == 0)
check("hook-failopen-rc", all(p.returncode == 0 for p in (p_off, p1, p2, p3)))

# 10. CONCURRENCY: N threads each consume once on enable(N) → exactly N active, 0 left.
#     Without the fcntl lock the read-modify-write races and loses decrements (TOCTOU).
import threading
proxy_state.enable(20)
_actives = []
_rlock = threading.Lock()
def _worker():
    r = proxy_state.consume()
    with _rlock:
        _actives.append(bool(r["active"]))
_threads = [threading.Thread(target=_worker) for _ in range(20)]
for t in _threads: t.start()
for t in _threads: t.join()
check("concurrency-exact-N", sum(_actives) == 20 and proxy_state.peek() == 0,
      f"active={sum(_actives)}/20, left={proxy_state.peek()} (TOCTOU lock holds)")
proxy_state.disable()

import shutil
shutil.rmtree(_tmp, ignore_errors=True)

print()
if fails:
    print(f"❌ FAILED ({len(fails)}): {fails}"); sys.exit(1)
print("✅ ALL PASS — gemini-proxy counter: off by default, EXACTLY N consumes, auto-off after N, "
      "fail-safe on garbage, concurrency-locked; hook peeks+injects the smart filter (agent consumes "
      "only on routed prompts) and is always fail-open.")
