#!/usr/bin/env python3
"""
parse_nfe.py — Parser deterministico de XML fiscal de PRODUTO/TRANSPORTE.

Le NF-e (modelo 55), NFC-e (modelo 65) e CT-e e extrai os campos-chave
de cada documento e de cada item, sem depender do LLM ler nota a nota.
Ferramenta auxiliar do Protocolo 2 (Ingestao e Conferencia de Arquivos)
da skill `analise-xml-fiscal`.

USO:
    python3 scripts/parse_nfe.py <arquivo-ou-pasta> [--json] [--itens]

    <arquivo-ou-pasta>  XML unico ou diretorio (varre *.xml recursivamente).
    --json              Saida em JSON estruturado (default: resumo legivel).
    --itens             Inclui o detalhamento item a item no resumo.

SAIDA:
    Resumo por documento (modelo, chave, emitente, destinatario, valores,
    tributos destacados) + totalizador. Em --json, lista de dicts.

EXIT:
    0 = ok            1 = nenhum XML valido encontrado
    2 = erro de uso

Stdlib apenas (Python 3.11+). Parsing namespace-agnostico — o XML fiscal
brasileiro usa namespace padrao da SEFAZ, mas a tag local basta.
"""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def _local(tag: str) -> str:
    """Remove o namespace de uma tag ({uri}tag -> tag)."""
    return tag.rsplit("}", 1)[-1]


def _find(node, *names):
    """Busca o primeiro descendente cuja tag local esta em names."""
    target = set(names)
    for child in node.iter():
        if _local(child.tag) in target:
            return child
    return None


def _text(node, *names, default=""):
    el = _find(node, *names) if node is not None else None
    if el is None or el.text is None:
        return default
    return el.text.strip()


def _num(node, *names, default=0.0):
    raw = _text(node, *names, default="")
    if not raw:
        return default
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        return default


def _detect_modelo(root) -> str:
    """Identifica o tipo de documento pela estrutura/tag-raiz."""
    tag = _local(root.tag)
    if tag in ("cteProc", "CTe", "cteOS", "CTeOS"):
        return "CT-e"
    mod = _text(root, "mod", default="")
    if mod == "65":
        return "NFC-e (mod. 65)"
    if mod == "55":
        return "NF-e (mod. 55)"
    return "NF-e/NFC-e"


def parse_nfe_file(path: Path) -> dict | None:
    """Extrai os campos-chave de um XML fiscal de produto/transporte."""
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return {"arquivo": str(path), "erro": f"XML invalido: {exc}"}

    modelo = _detect_modelo(root)
    inf = _find(root, "infNFe", "infCte")
    chave = ""
    if inf is not None:
        chave = (inf.get("Id") or "").replace("NFe", "").replace("CTe", "")

    ide = _find(root, "ide")
    emit = _find(root, "emit")
    dest = _find(root, "dest")
    total = _find(root, "ICMSTot", "vPrest", "total")

    itens = []
    for det in root.iter():
        if _local(det.tag) != "det":
            continue
        prod = _find(det, "prod")
        imp = _find(det, "imposto")
        itens.append({
            "codigo": _text(prod, "cProd"),
            "descricao": _text(prod, "xProd"),
            "ncm": _text(prod, "NCM"),
            "cfop": _text(prod, "CFOP"),
            "cest": _text(prod, "CEST"),
            "quantidade": _num(prod, "qCom"),
            "valor": _num(prod, "vProd"),
            "cst_icms": _text(imp, "CST", "CSOSN"),
            "vbc_icms": _num(imp, "vBC"),
            "aliq_icms": _num(imp, "pICMS"),
            "valor_icms": _num(imp, "vICMS"),
            "cst_ipi": _text(imp, "CST", default=""),
            "valor_ipi": _num(imp, "vIPI"),
            "valor_pis": _num(imp, "vPIS"),
            "valor_cofins": _num(imp, "vCOFINS"),
        })

    return {
        "arquivo": str(path),
        "modelo": modelo,
        "chave_acesso": chave,
        "numero": _text(ide, "nNF", "nCT"),
        "serie": _text(ide, "serie"),
        "data_emissao": _text(ide, "dhEmi", "dEmi"),
        "natureza_operacao": _text(ide, "natOp"),
        "emitente": {
            "cnpj_cpf": _text(emit, "CNPJ", "CPF"),
            "nome": _text(emit, "xNome"),
            "uf": _text(emit, "UF"),
            "municipio": _text(emit, "xMun"),
        },
        "destinatario": {
            "cnpj_cpf": _text(dest, "CNPJ", "CPF"),
            "nome": _text(dest, "xNome"),
            "uf": _text(dest, "UF"),
            "municipio": _text(dest, "xMun"),
        },
        "totais": {
            "valor_produtos": _num(total, "vProd", "vTPrest"),
            "valor_nota": _num(total, "vNF", "vTPrest"),
            "valor_bc_icms": _num(total, "vBC"),
            "valor_icms": _num(total, "vICMS"),
            "valor_icms_st": _num(total, "vST", "vICMSST"),
            "valor_ipi": _num(total, "vIPI"),
            "valor_pis": _num(total, "vPIS"),
            "valor_cofins": _num(total, "vCOFINS"),
            "valor_frete": _num(total, "vFrete"),
        },
        "qtd_itens": len(itens),
        "itens": itens,
    }


def coletar(alvo: Path) -> list[Path]:
    if alvo.is_file():
        return [alvo]
    if alvo.is_dir():
        return sorted(alvo.rglob("*.xml"))
    return []


def imprimir_resumo(docs: list[dict], com_itens: bool) -> None:
    soma_nota = soma_icms = soma_st = soma_ipi = 0.0
    validos = 0
    for d in docs:
        if "erro" in d:
            print(f"[ERRO] {d['arquivo']}: {d['erro']}")
            continue
        validos += 1
        t = d["totais"]
        soma_nota += t["valor_nota"]
        soma_icms += t["valor_icms"]
        soma_st += t["valor_icms_st"]
        soma_ipi += t["valor_ipi"]
        print(f"\n=== {d['modelo']} n. {d['numero']}/{d['serie']} ===")
        print(f"  Chave: {d['chave_acesso']}")
        print(f"  Emissao: {d['data_emissao']}  Natureza: {d['natureza_operacao']}")
        print(f"  Emitente: {d['emitente']['nome']} "
              f"({d['emitente']['municipio']}/{d['emitente']['uf']})")
        print(f"  Destinatario: {d['destinatario']['nome']} "
              f"({d['destinatario']['municipio']}/{d['destinatario']['uf']})")
        print(f"  Valor da nota: R$ {t['valor_nota']:.2f}  "
              f"ICMS: R$ {t['valor_icms']:.2f}  ICMS-ST: R$ {t['valor_icms_st']:.2f}")
        print(f"  IPI: R$ {t['valor_ipi']:.2f}  PIS: R$ {t['valor_pis']:.2f}  "
              f"COFINS: R$ {t['valor_cofins']:.2f}  Itens: {d['qtd_itens']}")
        if com_itens:
            for it in d["itens"]:
                print(f"    - {it['descricao'][:40]:40} NCM {it['ncm']:10} "
                      f"CFOP {it['cfop']:5} CST {it['cst_icms']:4} "
                      f"R$ {it['valor']:.2f}")

    print(f"\n--- TOTALIZADOR ({validos} documento(s)) ---")
    print(f"  Valor total das notas: R$ {soma_nota:.2f}")
    print(f"  ICMS destacado: R$ {soma_icms:.2f}")
    print(f"  ICMS-ST: R$ {soma_st:.2f}")
    print(f"  IPI: R$ {soma_ipi:.2f}")
    print("  CONFERIR: totais batem com a apuracao; sem nota duplicada (P2).")


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if args else 2

    como_json = "--json" in args
    com_itens = "--itens" in args
    alvos = [a for a in args if not a.startswith("--")]
    if not alvos:
        print("ERRO: informe um arquivo XML ou uma pasta.", file=sys.stderr)
        return 2

    arquivos = coletar(Path(alvos[0]))
    if not arquivos:
        print(f"ERRO: nenhum XML encontrado em {alvos[0]}", file=sys.stderr)
        return 1

    docs = [parse_nfe_file(p) for p in arquivos]
    if como_json:
        print(json.dumps(docs, indent=2, ensure_ascii=False))
    else:
        imprimir_resumo(docs, com_itens)
    return 0


if __name__ == "__main__":
    sys.exit(main())
