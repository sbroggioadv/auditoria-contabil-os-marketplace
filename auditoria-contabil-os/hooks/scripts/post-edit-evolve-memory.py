#!/usr/bin/env python3
"""
Hook PostToolUse(Edit|Write) — anti-flap.

Objetivo: detectar edicao de arquivo dentro de um COWORK e gravar sinalizacao em
<COWORK>/auditoria-contabil/.memory-evolver-pending.json. A SKILL `memory-evolver` e a que
efetivamente consolida o MEMORY.md (LLM aplica regras de admissao + bloat). Este
hook apenas registra o evento de forma silenciosa e debounced.

Entrada (via stdin como JSON no padrao Claude Code hooks):
{
  "tool_name": "Edit" | "Write",
  "tool_input": { "file_path": "<abs path>", ... },
  "tool_response": { ... }  (opcional)
}

Regras anti-flap:
- Skip se arquivo NAO esta dentro de um COWORK (sem cowork-state.json).
- Skip se arquivo e o proprio MEMORY.md (evita loop auto-referente).
- Skip se arquivo e .hook-state.json, AUTO-DEPLOY.md, cowork-state.json (internos).
- Skip se ultimo disparo no mesmo path foi ha < 60s.
- Skip se a tool_response indicar falha.

Output: sempre exit 0 (nao bloqueia fluxo). Imprime uma linha informativa em stderr
se pulou + razao (debug-friendly).

Este hook NAO invoca LLM. Apenas marca pending. A consolidacao da memoria
acontece quando o usuario ou outra skill invocar memory-evolver/cowork-doctor.
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

try:
    from importlib import import_module
    hook_utils = import_module("hook-utils".replace("-", "_"))
except ImportError:
    # hook-utils.py tem hifen no nome; import direto via spec
    import importlib.util
    spec = importlib.util.spec_from_file_location("hook_utils", PLUGIN_ROOT / "scripts" / "hook-utils.py")
    hook_utils = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hook_utils)


DEBOUNCE_SECONDS = 60
MIN_DIFF_CHARS = 50
INTERNAL_FILENAMES = {
    ".hook-state.json",
    "AUTO-DEPLOY.md",
    "cowork-state.json",
    ".memory-evolver-pending.json",
    "persona.md",
}


def _load_input() -> dict:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {}


def main() -> int:
    payload = _load_input()
    tool_input = payload.get("tool_input") or {}
    tool_response = payload.get("tool_response") or {}

    # Skip se a edicao falhou
    if isinstance(tool_response, dict):
        if tool_response.get("success") is False:
            sys.stderr.write("[post-edit] skip: tool_response.success=False\n")
            return 0

    file_path_raw = tool_input.get("file_path") or tool_input.get("filePath") or tool_input.get("path")
    if not file_path_raw:
        sys.stderr.write("[post-edit] skip: sem file_path no tool_input\n")
        return 0

    file_path = Path(file_path_raw)
    if not file_path.is_absolute():
        sys.stderr.write(f"[post-edit] skip: path nao absoluto ({file_path})\n")
        return 0

    # Skip arquivos internos do plugin
    if file_path.name in INTERNAL_FILENAMES:
        sys.stderr.write(f"[post-edit] skip: arquivo interno ({file_path.name})\n")
        return 0
    if file_path.name == "MEMORY.md":
        sys.stderr.write("[post-edit] skip: MEMORY.md (evita loop)\n")
        return 0

    cowork = hook_utils.is_inside_cowork(file_path)
    if cowork is None:
        # Edicao fora de qualquer COWORK → silencioso
        return 0

    # Escape session-only: se memory_evolver_session_muted for True, hook e silencioso
    state_file = cowork / "auditoria-contabil" / "cowork-state.json"
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
            if state.get("preferences", {}).get("memory_evolver_session_muted"):
                sys.stderr.write("[post-edit] skip: memory-evolver mutado na sessao\n")
                return 0
        except Exception:
            pass

    area = hook_utils.area_of(file_path, cowork)
    key = f"post-edit:{file_path}"

    if hook_utils.should_debounce(cowork, key, DEBOUNCE_SECONDS):
        sys.stderr.write(f"[post-edit] skip: debounce ativo ({DEBOUNCE_SECONDS}s) para {file_path}\n")
        return 0

    # Registrar pending (memory-evolver le e processa depois)
    pending_path = cowork / "auditoria-contabil" / ".memory-evolver-pending.json"
    pending_path.parent.mkdir(parents=True, exist_ok=True)
    pending: list = []
    if pending_path.exists():
        try:
            pending = json.loads(pending_path.read_text(encoding="utf-8"))
            if not isinstance(pending, list):
                pending = []
        except Exception:
            pending = []

    # Evitar duplicata literal (mesmo path nao processado)
    if not any(e.get("file_path") == str(file_path) for e in pending):
        pending.append({
            "file_path": str(file_path),
            "area": area,
            "at": hook_utils.dt.datetime.now(hook_utils.dt.timezone.utc).isoformat().replace("+00:00", "Z"),
            "tool": payload.get("tool_name"),
        })
        tmp = pending_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(pending, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(pending_path)

    hook_utils.mark_fired(cowork, key, {"file": str(file_path), "area": area})
    sys.stderr.write(f"[post-edit] pending registrado: {file_path} (area={area})\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
