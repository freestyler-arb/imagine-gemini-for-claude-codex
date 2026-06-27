#!/usr/bin/env python3
"""proxy_state.py — counter for the gemini-proxy protocol.

Single source of truth for "how many upcoming prompts are still covered by the protocol".
Pure stdlib. The on-disk write is atomic (temp + os.replace), and the read-modify-write in consume()
is serialized with an advisory file lock (fcntl.flock) so two concurrent consumers can't lose a
decrement — that keeps the "exactly N" guarantee under parallel/rapid prompts. The lock is best-effort:
if fcntl is unavailable or locking fails, operations still proceed (fail-open). Reads are fail-safe
(missing/corrupt/negative → 0 = off).

State file precedence:
  1. $GEMINI_PROXY_STATE   (explicit override; tests use this)
  2. ~/.gemini_proxy_state.json   (per-user default — works no matter where the skill is installed)

API:
  enable(n=10) -> int     turn the protocol on for n prompts; returns n
  peek()       -> int     prompts still covered (0 = off); does NOT mutate, takes no lock
  consume()    -> dict     spend one prompt -> {active, was, now}. active=True iff the counter was >0
                           on entry (this prompt is covered). Lock-serialized read-modify-write.
  disable()    -> None     turn off immediately (counter = 0)

CLI: python3 proxy_state.py [peek|enable N|consume|disable]
"""
from __future__ import annotations
import contextlib
import json
import os
from pathlib import Path

try:
    import fcntl  # POSIX only (macOS/Linux — this pack targets those); absent on Windows.
except ImportError:  # pragma: no cover
    fcntl = None

DEFAULT_PROMPTS = 10


def _state_path() -> Path:
    env = os.getenv("GEMINI_PROXY_STATE")
    if env:
        return Path(env)
    return Path.home() / ".gemini_proxy_state.json"


@contextlib.contextmanager
def _lock():
    """Advisory exclusive lock around a read-modify-write. Best-effort: yields exactly once whether or
    not the lock was acquired, so a caller is never blocked by a locking failure (fail-open)."""
    f = None
    if fcntl is not None:
        try:
            lockf = Path(str(_state_path()) + ".lock")
            lockf.parent.mkdir(parents=True, exist_ok=True)
            f = open(lockf, "w")
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        except Exception:
            if f is not None:
                try:
                    f.close()
                except Exception:
                    pass
            f = None
    try:
        yield
    finally:
        if f is not None:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            except Exception:
                pass
            try:
                f.close()
            except Exception:
                pass


def _read_raw() -> int:
    """Read remaining count, fail-safe: any error / garbage / negative → 0."""
    try:
        data = json.loads(_state_path().read_text(encoding="utf-8"))
        n = int(data.get("remaining", 0))
        return n if n > 0 else 0
    except Exception:
        return 0


def _write_raw(n: int) -> None:
    """Atomic write (temp in the same dir + os.replace) so a reader never sees a half file."""
    p = _state_path()
    n = max(0, int(n))
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(p.suffix + f".tmp{os.getpid()}")
        tmp.write_text(json.dumps({"remaining": n}), encoding="utf-8")
        os.replace(tmp, p)
    except Exception:
        # Fail-open: never raise into a caller (a hook must stay non-blocking).
        pass


def enable(n: int = DEFAULT_PROMPTS) -> int:
    n = max(1, int(n))
    with _lock():
        _write_raw(n)
    return n


def peek() -> int:
    return _read_raw()


def consume() -> dict:
    with _lock():
        was = _read_raw()
        if was <= 0:
            return {"active": False, "was": 0, "now": 0}
        now = was - 1
        _write_raw(now)
        return {"active": True, "was": was, "now": now}


def disable() -> None:
    with _lock():
        _write_raw(0)


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    if cmd == "enable":
        print(enable(int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PROMPTS))
    elif cmd == "consume":
        print(json.dumps(consume()))
    elif cmd == "disable":
        disable(); print(0)
    else:
        print(peek())
