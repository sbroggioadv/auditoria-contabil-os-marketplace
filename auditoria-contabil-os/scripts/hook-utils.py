#!/usr/bin/env python3
"""
hook-utils.py — Utilitarios compartilhados pelos hooks do plugin.

Nao e executado diretamente — importado pelos scripts em hooks/scripts/.

Funcoes:
- find_cowork(path)       → descobre COWORK root procurando auditoria-contabil/ acima
- hook_state_load/save    → gerencia auditoria-contabil/.hook-state.json (debounce anti-flap)
- should_debounce(path, key, seconds=60) → True se ultimo disparo < seconds
- is_inside_cowork(path)  → bool
- area_of(path, cowork)   → slug da area (primeiro segmento apos cowork)
- log_warn(msg)           → imprime warning em stderr (nao bloqueia hook)

Stdlib only.
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

STATE_DIR = "auditoria-contabil"
HOOK_STATE_FILENAME = ".hook-state.json"


def find_cowork(start: Path) -> Path | None:
    """Procura uma pasta ancestral de `start` que contenha <dir>/auditoria-contabil/cowork-state.json."""
    start = start.resolve()
    candidates = [start] + list(start.parents)
    for c in candidates:
        if (c / STATE_DIR / "cowork-state.json").exists():
            return c
    return None


def is_inside_cowork(path: Path) -> Path | None:
    """Retorna o COWORK root se `path` estiver dentro, None caso contrario."""
    try:
        resolved = path.resolve()
    except Exception:
        return None
    if not resolved.exists():
        parent = path.parent.resolve()
        if parent.exists():
            resolved = parent
        else:
            return None
    return find_cowork(resolved)


def area_of(path: Path, cowork: Path) -> str | None:
    """Determina o slug da area (primeiro segmento do path relativo ao COWORK) ou None se raiz."""
    try:
        rel = path.resolve().relative_to(cowork.resolve())
    except ValueError:
        return None
    parts = rel.parts
    if not parts:
        return None
    first = parts[0]
    # Ignorar dirs internos e arquivos na raiz do cowork
    if first.startswith(".") or first in {"CLAUDE.md", "MEMORY.md", "README.md"}:
        return None
    return first


def _hook_state_path(cowork: Path) -> Path:
    return cowork / STATE_DIR / HOOK_STATE_FILENAME


def hook_state_load(cowork: Path) -> dict:
    p = _hook_state_path(cowork)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def hook_state_save(cowork: Path, state: dict) -> None:
    p = _hook_state_path(cowork)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)


def should_debounce(cowork: Path, key: str, seconds: int = 60) -> bool:
    """True se o ultimo disparo com o mesmo `key` foi ha < `seconds` segundos."""
    state = hook_state_load(cowork)
    entry = state.get(key)
    if not entry:
        return False
    try:
        last_iso = entry.get("last_at")
        if not last_iso:
            return False
        last = dt.datetime.fromisoformat(last_iso.replace("Z", "+00:00"))
        now = dt.datetime.now(dt.timezone.utc)
        return (now - last).total_seconds() < seconds
    except Exception:
        return False


def mark_fired(cowork: Path, key: str, meta: dict | None = None) -> None:
    state = hook_state_load(cowork)
    state[key] = {"last_at": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"), **(meta or {})}
    hook_state_save(cowork, state)


def log_warn(msg: str) -> None:
    sys.stderr.write(f"[hook-warn] {msg}\n")
