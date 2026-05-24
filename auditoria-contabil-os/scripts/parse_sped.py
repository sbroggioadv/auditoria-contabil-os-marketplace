#!/usr/bin/env python3
"""
parse_sped.py — Parser deterministico de arquivos SPED em texto.

Le os arquivos SPED no formato texto (registros delimitados por pipe `|`):
EFD-Contribuicoes, EFD ICMS/IPI e ECD. Identifica o tipo pela estrutura
do registro 0000, conta os registros por bloco e extrai os totais
relevantes. Ferramenta auxiliar do Protocolo 2 / Protocolo 4 da skill
`leitura-arquivos-sped` — evita o LLM ler arquivos com milhares de linhas.

USO:
    python3 scripts/parse_sped.py <arquivo.txt> [--json] [--registros R0150,...]

    --json        Saida em JSON estruturado (default: resumo legivel).
    --registros   Lista os registros indicados (csv de codigos, ex. C100,D100).

SAIDA:
    Tipo do SPED, identificacao do contribuinte, periodo, contagem de
    registros por bloco e por codigo, e conferencia (registro 9999 x
    linhas lidas).

EXIT:
    0 = ok            1 = arquivo invalido / vazio
    2 = erro de uso

Stdlib apenas (Python 3.11+). Cada linha SPED: |REG|campo1|campo2|...|
O primeiro campo apos o pipe inicial e o codigo do registro.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

# Assinatura do tipo de SPED pelo registro 0000 (posicao e conteudo variam).
# Heuristica: tokens caracteristicos presentes no 0000 ou nos blocos.


def _ler_linhas(path: Path) -> list[str]:
    raw = path.read_bytes()
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            texto = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        texto = raw.decode("utf-8", errors="replace")
    return [ln for ln in texto.splitlines() if ln.strip()]


def _campos(linha: str) -> list[str]:
    """|REG|a|b|  ->  ['REG','a','b']."""
    return linha.strip().strip("|").split("|")


def _detectar_tipo(reg0000: list[str]) -> str:
    """Identifica o SPED pelo conteudo do registro 0000."""
    joined = "|".join(reg0000).upper()
    # ECD: 0000 traz LECD; EFD-Contribuicoes traz indicador de PIS/COFINS;
    # EFD ICMS/IPI traz a versao do leiaute fiscal.
    if "LECD" in joined:
        return "ECD (Escrituracao Contabil Digital)"
    if "LECF" in joined:
        return "ECF (Escrituracao Contabil Fiscal)"
    # EFD-Contribuicoes: registro 0000 tem campo COD_INC_TRIB / TIPO_ESCRIT.
    if len(reg0000) >= 3 and reg0000[1] in ("LECF",):
        return "ECF (Escrituracao Contabil Fiscal)"
    # Diferenciacao EFD ICMS/IPI x EFD-Contribuicoes pela presenca de blocos.
    return "EFD (ICMS/IPI ou Contribuicoes) [confirmar pelo bloco]"


def _refinar_tipo(blocos: set[str], tipo: str) -> str:
    if "[confirmar" not in tipo:
        return tipo
    # Bloco M = apuracao de PIS/COFINS (EFD-Contribuicoes).
    # Bloco E = apuracao de ICMS/IPI (EFD ICMS/IPI).
    if "M" in blocos and "E" not in blocos:
        return "EFD-Contribuicoes (PIS/COFINS)"
    if "E" in blocos and "M" not in blocos:
        return "EFD ICMS/IPI"
    if "M" in blocos and "E" in blocos:
        return "EFD ICMS/IPI + apuracao [VERIFICAR]"
    return tipo


def parse_sped_file(path: Path) -> dict:
    linhas = _ler_linhas(path)
    if not linhas:
        return {"arquivo": str(path), "erro": "arquivo vazio"}

    reg0000 = None
    contagem: Counter = Counter()
    blocos: Counter = Counter()
    reg9999 = None
    registros_capturados: dict[str, list[list[str]]] = {}

    for linha in linhas:
        c = _campos(linha)
        if not c or not c[0]:
            continue
        cod = c[0]
        contagem[cod] += 1
        if cod and cod[0].isalpha() or (cod and cod[0].isdigit()):
            blocos[cod[0]] += 1
        if cod == "0000" and reg0000 is None:
            reg0000 = c
        if cod == "9999":
            reg9999 = c

    if reg0000 is None:
        return {"arquivo": str(path),
                "erro": "registro 0000 ausente — nao e SPED valido"}

    tipo = _refinar_tipo(set(blocos), _detectar_tipo(reg0000))

    # Identificacao do contribuinte: o CNPJ/nome estao em posicoes
    # diferentes conforme o SPED — varrer por padrao de CNPJ (14 digitos).
    cnpj = nome = ""
    for campo in reg0000:
        so_dig = campo.replace(".", "").replace("/", "").replace("-", "")
        if so_dig.isdigit() and len(so_dig) == 14:
            cnpj = campo
        elif len(campo) > 4 and not campo.replace(" ", "").isdigit() \
                and not nome and campo not in ("LECD", "LECF"):
            nome = campo

    total_9999 = None
    if reg9999 and len(reg9999) >= 2 and reg9999[1].isdigit():
        total_9999 = int(reg9999[1])

    resultado = {
        "arquivo": str(path),
        "tipo": tipo,
        "contribuinte": {"cnpj": cnpj, "nome": nome},
        "linhas_lidas": len(linhas),
        "total_registros_9999": total_9999,
        "integridade_ok": (total_9999 == len(linhas)) if total_9999 else None,
        "qtd_blocos": dict(sorted(blocos.items())),
        "qtd_por_registro": dict(sorted(contagem.items())),
    }

    if registros_capturados:
        resultado["registros"] = registros_capturados
    return resultado


def _capturar_registros(path: Path, codigos: list[str]) -> dict:
    alvo = {c.strip().upper() for c in codigos if c.strip()}
    capt: dict[str, list[list[str]]] = {c: [] for c in alvo}
    for linha in _ler_linhas(path):
        c = _campos(linha)
        if c and c[0].upper() in alvo:
            capt[c[0].upper()].append(c)
    return capt


def imprimir_resumo(d: dict) -> None:
    if "erro" in d:
        print(f"[ERRO] {d['arquivo']}: {d['erro']}")
        return
    print(f"=== ARQUIVO SPED — {d['tipo']} ===")
    print(f"  Contribuinte: {d['contribuinte']['nome']} "
          f"(CNPJ {d['contribuinte']['cnpj'] or '[VERIFICAR]'})")
    print(f"  Linhas lidas: {d['linhas_lidas']}")
    if d["total_registros_9999"] is not None:
        ok = "OK" if d["integridade_ok"] else "DIVERGENCIA"
        print(f"  Registro 9999 (total declarado): "
              f"{d['total_registros_9999']} -> integridade: {ok}")
    else:
        print("  Registro 9999 ausente — [VERIFICAR integridade]")
    print("  Registros por bloco:")
    for bloco, qtd in d["qtd_blocos"].items():
        print(f"    Bloco {bloco}: {qtd} registro(s)")
    print("  Registros mais relevantes:")
    for cod, qtd in d["qtd_por_registro"].items():
        if qtd > 1 or cod in ("0000", "9999", "9990", "0001"):
            print(f"    {cod}: {qtd}")
    if "registros" in d:
        for cod, linhas in d["registros"].items():
            print(f"  --- registro {cod} ({len(linhas)}) ---")
            for ln in linhas[:20]:
                print(f"    {'|'.join(ln)}")
            if len(linhas) > 20:
                print(f"    ... (+{len(linhas) - 20} linhas)")
    print("  CONFERIR: o escriturado bate com o apurado e o declarado (P4).")


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if args else 2

    como_json = "--json" in args
    codigos: list[str] = []
    if "--registros" in args:
        idx = args.index("--registros")
        if idx + 1 < len(args):
            codigos = args[idx + 1].split(",")

    alvos = [a for a in args if not a.startswith("--")
             and a not in codigos and "," not in a]
    if not alvos:
        print("ERRO: informe um arquivo SPED (.txt)", file=sys.stderr)
        return 2

    path = Path(alvos[0])
    if not path.is_file():
        print(f"ERRO: arquivo nao encontrado: {path}", file=sys.stderr)
        return 1

    d = parse_sped_file(path)
    if codigos and "erro" not in d:
        d["registros"] = _capturar_registros(path, codigos)
    if como_json:
        print(json.dumps(d, indent=2, ensure_ascii=False))
    else:
        imprimir_resumo(d)
    return 1 if "erro" in d else 0


if __name__ == "__main__":
    sys.exit(main())
