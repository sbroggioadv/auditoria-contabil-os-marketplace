#!/usr/bin/env python3
"""
state.py — Maquina de estados do cowork-state.json.

Responsabilidades:
- load()      le e valida cowork-state.json
- save()      valida e escreve com backup automatico
- create_empty() cria state inicial com defaults
- validate()  valida contra JSON Schema (com fallback sem jsonschema lib)
- migrate()   migra entre versoes de schema

CLI:
    python scripts/state.py init <cowork_path>
    python scripts/state.py validate <cowork_path>
    python scripts/state.py show <cowork_path>
    python scripts/state.py set <cowork_path> <json_path> <value>
    python scripts/state.py migrate <cowork_path>

Nao depende de bibliotecas externas obrigatorias. Se 'jsonschema' estiver
instalado, validacao e completa; senao, validacao minima (campos obrigatorios +
tipos basicos).
"""

from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import shutil
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

SCHEMA_VERSION = "1.2.0"
STATE_FILENAME = "cowork-state.json"
STATE_DIR = "auditoria-contabil"

try:
    import jsonschema  # type: ignore
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _schema_path() -> Path:
    return Path(__file__).parent / "state-schema.json"


def _state_file(cowork_path: Path) -> Path:
    return cowork_path / STATE_DIR / STATE_FILENAME


def _backup_file(cowork_path: Path) -> Path:
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return cowork_path / STATE_DIR / ".backup" / f"cowork-state.{ts}.json"


# ---------------------------------------------------------------------------
# Core API
# ---------------------------------------------------------------------------

def load(cowork_path: Path) -> dict:
    """Le cowork-state.json. Valida. Retorna dict."""
    sf = _state_file(cowork_path)
    if not sf.exists():
        raise FileNotFoundError(f"Arquivo de estado nao encontrado: {sf}")
    state = json.loads(sf.read_text(encoding="utf-8"))
    errors = validate(state)
    if errors:
        raise ValueError(f"State invalido em {sf}:\n  " + "\n  ".join(errors))
    return state


def save(cowork_path: Path, state: dict, *, create_backup: bool = True) -> Path:
    """Valida state, cria backup do anterior, escreve atomicamente."""
    errors = validate(state)
    if errors:
        raise ValueError(f"State invalido — nao salvo:\n  " + "\n  ".join(errors))

    state["updated_at"] = _now_iso()

    sf = _state_file(cowork_path)
    sf.parent.mkdir(parents=True, exist_ok=True)

    if create_backup and sf.exists():
        bf = _backup_file(cowork_path)
        bf.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(sf, bf)

    tmp = sf.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(sf)
    return sf


def create_empty(cowork_path: Path, *, firm_name: str, firm_slug: str,
                 contador_nome: str, plugin_version: str = "0.1.0-alpha.0") -> dict:
    """Cria state inicial com defaults. Nao salva em disco."""
    now = _now_iso()
    return {
        "schema_version": SCHEMA_VERSION,
        "plugin_version": plugin_version,
        "created_at": now,
        "updated_at": now,
        "identity": {
            "firm_name": firm_name,
            "firm_slug": firm_slug,
            "contador_nome": contador_nome,
            "crc_numero": None,
            "crc_uf": None,
            "municipio": None,
            "uf": None,
            "email": None,
            "telefone": None,
            "endereco": None,
        },
        "cowork_path": str(cowork_path),
        "persona_path": str(cowork_path / STATE_DIR / "persona.md"),
        "tom_voz": {
            "perfil": "tecnico-objetivo",
            "intensidade_combativa": 4,
            "postura_default": "",
            "expressoes_assinatura": [],
            "termos_a_evitar": [],
        },
        "areas": [],
        "skills": {
            "invariants": [
                "auditoria-contabil-master",
                "validador-legislacao-vigente",
                "revisao-final",
                "estilo-entrega-contabil",
                "memoria-de-caso-contabil",
            ],
            "opt_in_active": [],
            "opt_in_inactive": [],
        },
        "revisao_tecnica": {
            "enabled": True,
            "bypass_threshold_words": 200,
            "auto_apply_to": ["apuracoes", "relatorios", "pareceres"],
        },
        "tools": {
            "sistema_contabil": None,
            "emissor_fiscal": None,
            "tarefas_projetos": None,
            "crm_leads": None,
            "email_provider": None,
            "banco_psp": None,
            "armazenamento_nuvem": None,
            "assinatura_digital": None,
            "outras": [],
        },
        "connectors": {
            "available": [],
            "notes": None,
        },
        "automations": {},
        "preferences": {
            "idioma": "pt-BR",
            "output_format_preferido": "docx",
            "modo_melhor_saida": "recomendar-e-listar",
            "papel_timbrado_path": None,
            "sync_folder_warning_acknowledged": False,
            "memory_evolver_session_muted": False,
            "cowork_sync_session_muted": False,
        },
        "wizard_state": {
            "completed": False,
            "current_step": "identity",
            "completed_steps": [],
            "last_interaction_at": now,
        },
    }


def validate(state: dict) -> list[str]:
    """Valida state contra schema. Retorna lista de erros (vazia = OK)."""
    errors: list[str] = []

    if HAS_JSONSCHEMA:
        try:
            schema = json.loads(_schema_path().read_text(encoding="utf-8"))
            validator = jsonschema.Draft202012Validator(schema)
            for err in sorted(validator.iter_errors(state), key=lambda e: e.path):
                path = " / ".join(str(p) for p in err.absolute_path) or "(root)"
                errors.append(f"{path}: {err.message}")
            return errors
        except Exception as e:
            errors.append(f"Validacao via jsonschema falhou ({e}); usando fallback minimo.")
            # cai no fallback abaixo

    # Fallback minimo: verifica campos obrigatorios top-level e alguns subcampos
    required_top = [
        "schema_version", "created_at", "updated_at", "identity",
        "cowork_path", "areas", "skills", "revisao_tecnica", "tom_voz"
    ]
    for field in required_top:
        if field not in state:
            errors.append(f"Campo obrigatorio ausente: {field}")

    if "identity" in state:
        for field in ("firm_name", "firm_slug", "contador_nome"):
            if field not in state["identity"] or not state["identity"][field]:
                errors.append(f"identity.{field}: obrigatorio e nao vazio")
        slug = state["identity"].get("firm_slug", "")
        import re
        if slug and not re.match(r"^[a-z0-9-]+$", slug):
            errors.append(f"identity.firm_slug: '{slug}' nao e slug valido (a-z, 0-9, hifen)")

    if "skills" in state:
        for field in ("invariants", "opt_in_active", "opt_in_inactive"):
            if field not in state["skills"]:
                errors.append(f"skills.{field}: obrigatorio")

    return errors


def migrate(state: dict) -> tuple[dict, bool]:
    """Migra state para SCHEMA_VERSION atual. Retorna (state_novo, mudou)."""
    from_v = state.get("schema_version", "0.0.0")
    if from_v == SCHEMA_VERSION:
        return state, False

    # v1.0.0 -> v1.1.0: adiciona blocos opcionais `tools` e `connectors`.
    if from_v in ("1.0.0",):
        state.setdefault("tools", {
            "sistema_contabil": None,
            "emissor_fiscal": None,
            "tarefas_projetos": None,
            "crm_leads": None,
            "email_provider": None,
            "banco_psp": None,
            "armazenamento_nuvem": None,
            "assinatura_digital": None,
            "outras": [],
        })
        state.setdefault("connectors", {
            "available": [],
            "notes": None,
        })

    # v1.1.0 -> v1.2.0: adiciona flags session-mute em preferences +
    # campo modo_melhor_saida.
    if from_v in ("1.0.0", "1.1.0"):
        prefs = state.setdefault("preferences", {})
        prefs.setdefault("memory_evolver_session_muted", False)
        prefs.setdefault("cowork_sync_session_muted", False)
        prefs.setdefault("modo_melhor_saida", "recomendar-e-listar")

    state["schema_version"] = SCHEMA_VERSION
    return state, True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cmd_init(args: argparse.Namespace) -> int:
    cp = Path(args.cowork_path).resolve()
    if _state_file(cp).exists() and not args.force:
        print(f"ERRO: {_state_file(cp)} ja existe. Use --force para sobrescrever.")
        return 1

    state = create_empty(
        cp,
        firm_name=args.firm_name or "[nao configurado]",
        firm_slug=args.firm_slug or "escritorio",
        contador_nome=args.contador or "[nao configurado]",
    )
    sf = save(cp, state, create_backup=False)
    print(f"State criado em: {sf}")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    cp = Path(args.cowork_path).resolve()
    try:
        load(cp)
        print("OK: state valido.")
        return 0
    except (FileNotFoundError, ValueError) as e:
        print(f"ERRO: {e}")
        return 1


def _cmd_show(args: argparse.Namespace) -> int:
    cp = Path(args.cowork_path).resolve()
    state = load(cp)
    print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


def _cmd_set(args: argparse.Namespace) -> int:
    cp = Path(args.cowork_path).resolve()
    state = load(cp)

    keys = args.json_path.split(".")
    node = state
    for k in keys[:-1]:
        if k not in node:
            node[k] = {}
        node = node[k]

    # tenta parsear como JSON, senao usa string
    try:
        value = json.loads(args.value)
    except json.JSONDecodeError:
        value = args.value

    node[keys[-1]] = value
    save(cp, state)
    print(f"OK: {args.json_path} = {value!r}")
    return 0


def _cmd_migrate(args: argparse.Namespace) -> int:
    cp = Path(args.cowork_path).resolve()
    state = json.loads(_state_file(cp).read_text(encoding="utf-8"))
    new_state, changed = migrate(state)
    if changed:
        save(cp, new_state)
        print(f"OK: migrado para schema {SCHEMA_VERSION}.")
    else:
        print(f"Ja na versao {SCHEMA_VERSION}, nada a fazer.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Maquina de estados cowork-state.json")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Cria state inicial.")
    p_init.add_argument("cowork_path")
    p_init.add_argument("--firm-name")
    p_init.add_argument("--firm-slug")
    p_init.add_argument("--contador")
    p_init.add_argument("--force", action="store_true")
    p_init.set_defaults(func=_cmd_init)

    p_validate = sub.add_parser("validate", help="Valida state existente.")
    p_validate.add_argument("cowork_path")
    p_validate.set_defaults(func=_cmd_validate)

    p_show = sub.add_parser("show", help="Imprime state como JSON.")
    p_show.add_argument("cowork_path")
    p_show.set_defaults(func=_cmd_show)

    p_set = sub.add_parser("set", help="Define campo do state. Ex: set /tmp/cw identity.crc_numero 12345")
    p_set.add_argument("cowork_path")
    p_set.add_argument("json_path", help="Ex: identity.crc_numero")
    p_set.add_argument("value", help="Valor (JSON ou string).")
    p_set.set_defaults(func=_cmd_set)

    p_migrate = sub.add_parser("migrate", help="Migra state para SCHEMA_VERSION atual.")
    p_migrate.add_argument("cowork_path")
    p_migrate.set_defaults(func=_cmd_migrate)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
