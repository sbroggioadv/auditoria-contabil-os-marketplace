#!/usr/bin/env python3
"""
parse_ofx.py — Parser deterministico de extrato bancario OFX.

Le arquivos OFX (Open Financial Exchange) — formato exportado por bancos
para extrato de conta. Cobre OFX 1.x (SGML, tags sem fechamento) e OFX
2.x (XML). Extrai os lancamentos, datas, valores e saldos para apoiar a
conciliacao bancaria. Ferramenta auxiliar do Protocolo 2 / Protocolo 4
da skill `analise-extratos-ofx-csv`.

USO:
    python3 scripts/parse_ofx.py <arquivo.ofx> [--json] [--lancamentos]

    --json          Saida em JSON estruturado (default: resumo legivel).
    --lancamentos   Lista cada lancamento no resumo.

SAIDA:
    Cabecalho da conta (banco, agencia, conta), periodo, saldo final,
    total de creditos e debitos, contagem de lancamentos e conferencia
    de integridade (saldo inicial + movimento = saldo final).

EXIT:
    0 = ok            1 = arquivo invalido / vazio
    2 = erro de uso

Stdlib apenas (Python 3.11+). O OFX 1.x SGML e tratado por regex linha a
linha — robusto para os exports mais comuns dos bancos brasileiros.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TAG_RE = re.compile(r"<([A-Z0-9.]+)>([^<\r\n]*)")


def _ler(path: Path) -> str:
    """Le o OFX tolerando latin-1 (comum em exports de banco BR)."""
    raw = path.read_bytes()
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _parse_valor(v: str) -> float:
    v = v.strip().replace(",", ".")
    try:
        return float(v)
    except ValueError:
        return 0.0


def _parse_data_ofx(v: str) -> str:
    """OFX usa AAAAMMDD[HHMMSS]. Devolve AAAA-MM-DD."""
    v = v.strip()[:8]
    if len(v) == 8 and v.isdigit():
        return f"{v[0:4]}-{v[4:6]}-{v[6:8]}"
    return v


def parse_ofx_file(path: Path) -> dict:
    texto = _ler(path)
    if "<OFX>" not in texto.upper():
        return {"arquivo": str(path), "erro": "nao parece um arquivo OFX"}

    # Coleta linear de tags com valor (cobre SGML 1.x e XML 2.x).
    pares = TAG_RE.findall(texto)
    campos: dict[str, str] = {}
    for tag, val in pares:
        if val.strip() and tag not in campos:
            campos[tag] = val.strip()

    # Lancamentos: cada bloco <STMTTRN> ... </STMTTRN>.
    lancamentos = []
    for bloco in re.findall(r"<STMTTRN>(.*?)</STMTTRN>", texto,
                            re.DOTALL | re.IGNORECASE):
        b = dict(TAG_RE.findall(bloco))
        lancamentos.append({
            "tipo": b.get("TRNTYPE", "").strip(),
            "data": _parse_data_ofx(b.get("DTPOSTED", "")),
            "valor": _parse_valor(b.get("TRNAMT", "0")),
            "id": b.get("FITID", "").strip(),
            "descricao": (b.get("MEMO", "") or b.get("NAME", "")).strip(),
        })

    creditos = sum(l["valor"] for l in lancamentos if l["valor"] > 0)
    debitos = sum(l["valor"] for l in lancamentos if l["valor"] < 0)
    saldo_final = _parse_valor(campos.get("BALAMT", "0"))
    movimento = creditos + debitos

    return {
        "arquivo": str(path),
        "versao": "OFX 2.x (XML)" if texto.lstrip().startswith("<?xml")
        else "OFX 1.x (SGML)",
        "banco_id": campos.get("BANKID", ""),
        "agencia": campos.get("BRANCHID", ""),
        "conta": campos.get("ACCTID", ""),
        "tipo_conta": campos.get("ACCTTYPE", ""),
        "moeda": campos.get("CURDEF", ""),
        "periodo_inicio": _parse_data_ofx(campos.get("DTSTART", "")),
        "periodo_fim": _parse_data_ofx(campos.get("DTEND", "")),
        "saldo_final_informado": saldo_final,
        "data_saldo": _parse_data_ofx(campos.get("DTASOF", "")),
        "qtd_lancamentos": len(lancamentos),
        "total_creditos": round(creditos, 2),
        "total_debitos": round(debitos, 2),
        "movimento_liquido": round(movimento, 2),
        "lancamentos": lancamentos,
    }


def imprimir_resumo(d: dict, com_lanc: bool) -> None:
    if "erro" in d:
        print(f"[ERRO] {d['arquivo']}: {d['erro']}")
        return
    print(f"=== EXTRATO OFX — {d['versao']} ===")
    print(f"  Banco: {d['banco_id']}  Agencia: {d['agencia']}  "
          f"Conta: {d['conta']} ({d['tipo_conta']})")
    print(f"  Periodo: {d['periodo_inicio']} a {d['periodo_fim']}  "
          f"Moeda: {d['moeda']}")
    print(f"  Lancamentos: {d['qtd_lancamentos']}")
    print(f"  Total de creditos: R$ {d['total_creditos']:.2f}")
    print(f"  Total de debitos:  R$ {d['total_debitos']:.2f}")
    print(f"  Movimento liquido: R$ {d['movimento_liquido']:.2f}")
    print(f"  Saldo final informado: R$ {d['saldo_final_informado']:.2f} "
          f"(em {d['data_saldo']})")
    if com_lanc:
        print("  --- lancamentos ---")
        for l in d["lancamentos"]:
            print(f"    {l['data']}  {l['valor']:>12.2f}  "
                  f"{l['tipo']:<8} {l['descricao'][:48]}")
    print("  CONFERIR: saldo inicial + movimento liquido = saldo final;")
    print("  cada lancamento deve ter contrapartida no razao (P4).")


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if args else 2

    como_json = "--json" in args
    com_lanc = "--lancamentos" in args
    alvos = [a for a in args if not a.startswith("--")]
    if not alvos:
        print("ERRO: informe um arquivo .ofx", file=sys.stderr)
        return 2

    path = Path(alvos[0])
    if not path.is_file():
        print(f"ERRO: arquivo nao encontrado: {path}", file=sys.stderr)
        return 1

    d = parse_ofx_file(path)
    if como_json:
        print(json.dumps(d, indent=2, ensure_ascii=False))
    else:
        imprimir_resumo(d, com_lanc)
    return 1 if "erro" in d else 0


if __name__ == "__main__":
    sys.exit(main())
