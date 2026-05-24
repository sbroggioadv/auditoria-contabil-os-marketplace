#!/usr/bin/env python3
"""
Hook PreCompact — snapshot de estado antes da compaction de contexto.

Objetivo: quando o Claude Code esta prestes a compactar o historico da sessao,
salvar um snapshot minimo do estado dos MEMORY.md do COWORK para
<COWORK>/auditoria-contabil/.snapshots/pre-compact-<timestamp>.md.

Isso permite retomada posterior se a compaction apagar contexto critico.

Criterios:
- Snapshot soh e feito se houver COWORK detectavel (via env COWORK_PATH ou cwd ancestor).
- Snapshot inclui: MEMORY.md da raiz + MEMORY.md de cada area (se existirem) + timestamp.
- Se COWORK tiver > 10 areas, snapshot limita a 10 MEMORY.md mais recentemente modificados.
- Diretorio `.snapshots/` e criado se nao existir.
- Retencao: manter max 20 snapshots mais recentes (auto-pruning).

Stdlib only. Exit 0 sempre (nao bloquear compaction se falhar).
"""

from __future__ import annotations

import datetime as dt
import io
import json
import os
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

import importlib.util
spec = importlib.util.spec_from_file_location("hook_utils", PLUGIN_ROOT / "scripts" / "hook-utils.py")
hook_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook_utils)


MAX_AREAS = 10
MAX_SNAPSHOTS_RETAINED = 20


def _resolve_cowork() -> Path | None:
    env = os.environ.get("CONTABIL_COWORK_PATH") or os.environ.get("COWORK_PATH")
    if env:
        p = Path(env)
        if (p / "auditoria-contabil" / "cowork-state.json").exists():
            return p
    return hook_utils.find_cowork(Path.cwd())


def _collect_memories(cowork: Path) -> list[tuple[str, Path]]:
    """Lista (label, path) de MEMORY.md a incluir no snapshot."""
    results: list[tuple[str, Path]] = []
    root_memory = cowork / "MEMORY.md"
    if root_memory.exists():
        results.append(("(root)", root_memory))

    # Areas: primeiro nivel de subpastas (exclui auditoria-contabil e dot-dirs)
    area_memories: list[tuple[Path, float]] = []
    for sub in cowork.iterdir():
        if not sub.is_dir() or sub.name.startswith("."):
            continue
        mm = sub / "MEMORY.md"
        if mm.exists():
            area_memories.append((mm, mm.stat().st_mtime))

    area_memories.sort(key=lambda t: t[1], reverse=True)
    for mm, _ in area_memories[:MAX_AREAS]:
        label = mm.parent.name
        results.append((label, mm))

    return results


def _build_snapshot(cowork: Path, items: list[tuple[str, Path]]) -> str:
    lines: list[str] = []
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines.append(f"# PreCompact Snapshot — {now}")
    lines.append("")
    lines.append(f"COWORK: `{cowork}`")
    lines.append(f"Arquivos incluidos: {len(items)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    for label, path in items:
        lines.append(f"## MEMORY.md — {label}")
        lines.append(f"_source: `{path.relative_to(cowork)}`_")
        lines.append("")
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as e:
            lines.append(f"_[erro ao ler: {e}]_")
        else:
            lines.append(text.rstrip())
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines) + "\n"


def _prune_snapshots(snapshots_dir: Path, keep: int) -> int:
    files = sorted(
        (p for p in snapshots_dir.iterdir() if p.is_file() and p.name.startswith("pre-compact-")),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    removed = 0
    for p in files[keep:]:
        try:
            p.unlink()
            removed += 1
        except Exception:
            pass
    return removed


def main() -> int:
    cowork = _resolve_cowork()
    if cowork is None:
        sys.stderr.write("[pre-compact] skip: sem COWORK detectado\n")
        return 0

    items = _collect_memories(cowork)
    if not items:
        sys.stderr.write("[pre-compact] skip: nenhum MEMORY.md encontrado\n")
        return 0

    snapshots_dir = cowork / "auditoria-contabil" / ".snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = snapshots_dir / f"pre-compact-{ts}.md"
    out.write_text(_build_snapshot(cowork, items), encoding="utf-8")

    pruned = _prune_snapshots(snapshots_dir, MAX_SNAPSHOTS_RETAINED)
    sys.stderr.write(f"[pre-compact] snapshot OK em {out} ({len(items)} arquivos; pruned={pruned})\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
