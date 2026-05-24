#!/usr/bin/env python3
"""
resolve-persona.py — Resolve qual persona carregar no hook SessionStart.

Fallback chain (ordem de prioridade):
1. Env var CONTABIL_PERSONA aponta para arquivo existente
2. <CWD>/.claude/settings.local.json contem env.CONTABIL_PERSONA
3. ~/.config/auditoria-contabil-os/active-cowork.json contem persona_path
4. Fallback para <PLUGIN_ROOT>/context/persona-fallback.md

Imprime o CONTEUDO da persona resolvida em stdout (consumido pelo hook).
Se nenhuma persona for encontrada, imprime a fallback.
"""

from __future__ import annotations

import io
import json
import os
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def _plugin_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _fallback_path() -> Path:
    return _plugin_root() / "context" / "persona-fallback.md"


def _try_env_var() -> Path | None:
    p = os.environ.get("CONTABIL_PERSONA")
    if p:
        path = Path(p).expanduser()
        if path.exists() and path.is_file():
            return path
    return None


def _try_settings_local() -> Path | None:
    cwd = Path.cwd()
    # Busca ate 4 niveis acima do CWD
    for _ in range(5):
        settings = cwd / ".claude" / "settings.local.json"
        if settings.exists():
            try:
                data = json.loads(settings.read_text(encoding="utf-8"))
                env = data.get("env", {}) if isinstance(data, dict) else {}
                p = env.get("CONTABIL_PERSONA")
                if p:
                    path = Path(p).expanduser()
                    if path.exists() and path.is_file():
                        return path
            except (json.JSONDecodeError, PermissionError):
                pass
        if cwd.parent == cwd:
            break
        cwd = cwd.parent
    return None


def _try_active_cowork_config() -> Path | None:
    home = Path.home()
    for config_path in (
        home / ".config" / "auditoria-contabil-os" / "active-cowork.json",
        home / ".auditoria-contabil-os" / "active-cowork.json",
    ):
        if config_path.exists():
            try:
                data = json.loads(config_path.read_text(encoding="utf-8"))
                p = data.get("persona_path")
                if p:
                    path = Path(p).expanduser()
                    if path.exists() and path.is_file():
                        return path
            except (json.JSONDecodeError, PermissionError):
                pass
    return None


def resolve_persona() -> tuple[Path, str]:
    """Resolve persona via fallback chain. Retorna (path, source_tag)."""
    for fn, tag in (
        (_try_env_var, "env:CONTABIL_PERSONA"),
        (_try_settings_local, "settings.local.json"),
        (_try_active_cowork_config, "active-cowork.json"),
    ):
        try:
            p = fn()
            if p:
                return p, tag
        except Exception:
            continue

    return _fallback_path(), "fallback"


def main() -> int:
    path, source = resolve_persona()
    try:
        content = path.read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError) as e:
        print(f"# Persona nao encontrada\n\nErro ao ler {path}: {e}", file=sys.stderr)
        return 1

    # Header de diagnostico no comeco (nao interfere com markdown renderizado)
    if source == "fallback":
        sys.stderr.write(f"[auditoria-contabil-os] Persona: FALLBACK (nenhuma persona configurada, rode /start)\n")
    else:
        sys.stderr.write(f"[auditoria-contabil-os] Persona carregada de {source}: {path}\n")

    print(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
