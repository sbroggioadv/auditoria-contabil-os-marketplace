#!/usr/bin/env python3
"""
parse_nfse.py — Parser deterministico de XML de NFS-e (nota de servico).

Le NFS-e no padrao nacional (DPS/NFS-e — Lei Complementar 116/2003,
sistema nacional) e tolera variacoes de layout municipal legado, que
ainda sao fragmentadas. Extrai prestador, tomador, servico, valores e
o ISS destacado/retido. Ferramenta auxiliar do Protocolo 2 da skill
`analise-xml-fiscal`.

USO:
    python3 scripts/parse_nfse.py <arquivo-ou-pasta> [--json]

    <arquivo-ou-pasta>  XML unico ou diretorio (varre *.xml recursivamente).
    --json              Saida em JSON estruturado (default: resumo legivel).

SAIDA:
    Resumo por NFS-e (numero, prestador, tomador, item da lista de
    servicos, municipio de incidencia, base, aliquota, ISS) + totalizador
    com alerta de layout municipal nao reconhecido.

EXIT:
    0 = ok            1 = nenhum XML valido encontrado
    2 = erro de uso

Stdlib apenas (Python 3.11+). Busca namespace-agnostica por tag local —
cobre tanto o XSD nacional quanto as muitas variacoes municipais.
"""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Tags equivalentes entre o padrao nacional e os layouts municipais.
# A primeira encontrada vale.
NUMERO = ("nNFSe", "Numero", "numeroNfse", "NumeroNfse")
DATA = ("dhProc", "dhEmi", "DataEmissao", "dataEmissao")
VALOR_SERV = ("vServ", "ValorServicos", "valorServicos", "vServPrest")
VALOR_ISS = ("vISS", "ValorIss", "valorIss", "vTotTrib")
BASE_ISS = ("vBC", "BaseCalculo", "baseCalculo", "vBCISS")
ALIQ_ISS = ("pAliqAplic", "Aliquota", "aliquota", "pAliq")
ISS_RETIDO = ("tpRetISSQN", "IssRetido", "issRetido", "vISSRet")
ITEM_LISTA = ("cServ", "cTribNac", "ItemListaServico", "itemListaServico",
              "codigoTributacaoMunicipio")
DISCRIMINACAO = ("xDescServ", "Discriminacao", "discriminacao", "xServ")
MUN_INCID = ("cLocIncid", "cMunPrestacao", "MunicipioIncidencia", "cMun")


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _grab(root, names, default=""):
    target = set(names)
    for el in root.iter():
        if _local(el.tag) in target and el.text and el.text.strip():
            return el.text.strip()
    return default


def _num(root, names) -> float:
    raw = _grab(root, names, default="")
    if not raw:
        return 0.0
    try:
        return float(raw.replace(".", "").replace(",", ".")) if "," in raw \
            else float(raw)
    except ValueError:
        return 0.0


def _party(root, *containers):
    """Extrai um participante (prestador/tomador) pelo container."""
    target = set(containers)
    for el in root.iter():
        if _local(el.tag) in target:
            return {
                "cnpj_cpf": _grab(el, ("CNPJ", "Cpf", "CpfCnpj", "nCpfCnpj",
                                       "CPF")),
                "nome": _grab(el, ("xNome", "RazaoSocial", "razaoSocial",
                                   "NomeRazaoSocial")),
                "municipio": _grab(el, ("xMun", "cMun", "CodigoMunicipio")),
                "uf": _grab(el, ("UF", "Uf", "uf")),
            }
    return {"cnpj_cpf": "", "nome": "", "municipio": "", "uf": ""}


def parse_nfse_file(path: Path) -> dict:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return {"arquivo": str(path), "erro": f"XML invalido: {exc}"}

    layout = "nacional"
    tags = {_local(e.tag) for e in root.iter()}
    if not ({"nNFSe", "infNFSe", "DPS", "infDPS"} & tags):
        layout = "municipal-legado [VERIFICAR layout]"

    return {
        "arquivo": str(path),
        "layout": layout,
        "numero": _grab(root, NUMERO),
        "data_emissao": _grab(root, DATA),
        "prestador": _party(root, "prest", "Prestador", "prestador",
                            "PrestadorServico"),
        "tomador": _party(root, "toma", "Tomador", "tomador",
                          "TomadorServico"),
        "item_lista_servico": _grab(root, ITEM_LISTA),
        "discriminacao": _grab(root, DISCRIMINACAO)[:160],
        "municipio_incidencia": _grab(root, MUN_INCID),
        "valor_servico": _num(root, VALOR_SERV),
        "base_calculo_iss": _num(root, BASE_ISS),
        "aliquota_iss": _num(root, ALIQ_ISS),
        "valor_iss": _num(root, VALOR_ISS),
        "iss_retido_flag": _grab(root, ISS_RETIDO),
    }


def coletar(alvo: Path) -> list[Path]:
    if alvo.is_file():
        return [alvo]
    if alvo.is_dir():
        return sorted(alvo.rglob("*.xml"))
    return []


def imprimir_resumo(docs: list[dict]) -> None:
    soma_serv = soma_iss = 0.0
    validos = legados = 0
    for d in docs:
        if "erro" in d:
            print(f"[ERRO] {d['arquivo']}: {d['erro']}")
            continue
        validos += 1
        if "municipal-legado" in d["layout"]:
            legados += 1
        soma_serv += d["valor_servico"]
        soma_iss += d["valor_iss"]
        print(f"\n=== NFS-e n. {d['numero']}  [{d['layout']}] ===")
        print(f"  Emissao: {d['data_emissao']}")
        print(f"  Prestador: {d['prestador']['nome']} "
              f"({d['prestador']['municipio']}/{d['prestador']['uf']})")
        print(f"  Tomador: {d['tomador']['nome']}")
        print(f"  Item lista de servico (LC 116/2003): "
              f"{d['item_lista_servico'] or '[VERIFICAR]'}")
        print(f"  Municipio de incidencia do ISS: "
              f"{d['municipio_incidencia'] or '[VERIFICAR]'}")
        print(f"  Valor do servico: R$ {d['valor_servico']:.2f}  "
              f"Base ISS: R$ {d['base_calculo_iss']:.2f}")
        print(f"  Aliquota ISS: {d['aliquota_iss']:.2f}%  "
              f"ISS: R$ {d['valor_iss']:.2f}  "
              f"Retido: {d['iss_retido_flag'] or 'nao informado'}")

    print(f"\n--- TOTALIZADOR ({validos} NFS-e) ---")
    print(f"  Valor total de servicos: R$ {soma_serv:.2f}")
    print(f"  ISS destacado: R$ {soma_iss:.2f}")
    if legados:
        print(f"  ATENCAO: {legados} nota(s) em layout municipal legado — "
              f"conferir campos marcados [VERIFICAR] (PA-06).")
    print("  CONFERIR: municipio de incidencia define a aliquota (PA-05).")


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if args else 2

    como_json = "--json" in args
    alvos = [a for a in args if not a.startswith("--")]
    if not alvos:
        print("ERRO: informe um arquivo XML ou uma pasta.", file=sys.stderr)
        return 2

    arquivos = coletar(Path(alvos[0]))
    if not arquivos:
        print(f"ERRO: nenhum XML encontrado em {alvos[0]}", file=sys.stderr)
        return 1

    docs = [parse_nfse_file(p) for p in arquivos]
    if como_json:
        print(json.dumps(docs, indent=2, ensure_ascii=False))
    else:
        imprimir_resumo(docs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
