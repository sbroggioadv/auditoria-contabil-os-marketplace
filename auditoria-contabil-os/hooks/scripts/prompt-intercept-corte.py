#!/usr/bin/env python3
"""
Hook UserPromptSubmit do plugin Auditoria Contabil OS.

Logica (ativacao automatica por contexto):
1. Le o prompt via stdin (JSON padrao Claude Code hooks).
2. Detecta bypass explicito: flags `--no-revisao`, `--quick`, `--no-corte`, `/revisao off`.
3. Detecta GATILHO CONTABIL via keywords (3 niveis):
   - Gatilho 1: prompt contem palavras do dominio contabil/fiscal
   - Gatilho 2: keywords fortes do dominio (DAS, Simples, Lucro Real, SPED, ECD,
     ECF, EFD, ICMS, ISS, PIS/COFINS, folha, eSocial, balancete, DRE, etc.)
   - Gatilho 3: comandos `/start-auditoria-contabil`, `/contabil-master`, etc.
4. Se gatilho dispara:
   - Verifica se `auditoria-contabil/cowork-state.json` existe no path atual
   - SIM: injeta protocolo Revisao Tecnica R1-R4 + aponta para skill
     `auditoria-contabil-master`
   - NAO: sugere `/start-auditoria-contabil` ao usuario (mas nao bloqueia)
5. Se ha bypass: reafirma em stdout que o bypass foi aceito (transparencia).
6. Se nao eh tarefa contabil/fiscal: silencio (exit 0 sem output).

Tambem respeita state.json: se `revisao_tecnica.enabled = false`, nunca injeta R1-R4.

Stdlib only.
"""

from __future__ import annotations

import io
import json
import os
import re
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


# Gatilho 1: palavras do dominio contabil (case insensitive)
TRIGGER_CONTABIL = [
    r"\bcontabil\b",
    r"\bcontábil\b",
    r"\bcontabilidade\b",
    r"\bauditoria\s+contabil\b",
    r"\bauditoria\s+contábil\b",
    r"\bfiscal\b",
    r"\btributacao\b",
    r"\btributação\b",
    r"\bescrituracao\b",
    r"\bescrituração\b",
    r"\bdepartamento\s+pessoal\b",
]

# Gatilho 2: keywords fortes do dominio contabil-fiscal brasileiro
DOMAIN_KEYWORDS = [
    # Apuracao e regimes tributarios
    r"\bapuracao\b", r"\bapuração\b",
    r"\bDAS\b", r"\bDASN\b", r"\bDAS-MEI\b",
    r"\bSimples\s+Nacional\b", r"\bSimples\b",
    r"\bLucro\s+Real\b", r"\bLucro\s+Presumido\b", r"\bLucro\s+Arbitrado\b",
    r"\bMEI\b", r"\bregime\s+tributario\b", r"\bregime\s+tributário\b",
    r"\benquadramento\s+fiscal\b",
    # Tributos e contribuicoes
    r"\bICMS\b", r"\bICMS-ST\b", r"\bISS\b", r"\bIPI\b",
    r"\bIRPJ\b", r"\bCSLL\b", r"\bIRPF\b", r"\bIRRF\b",
    r"\bPIS\b", r"\bCOFINS\b", r"\bPIS/COFINS\b",
    r"\bINSS\b", r"\bFGTS\b", r"\bICMS\s+ST\b",
    r"\bcredito\s+tributario\b", r"\bcrédito\s+tributário\b",
    r"\brecuperacao\s+de\s+credito\b", r"\brecuperação\s+de\s+crédito\b",
    # SPED e obrigacoes acessorias
    r"\bSPED\b", r"\bECD\b", r"\bECF\b", r"\bEFD\b",
    r"\bEFD-Contribuicoes\b", r"\bEFD-Contribuições\b",
    r"\bEFD-Reinf\b", r"\bEFD\s+ICMS\b",
    r"\bDCTFWeb\b", r"\bDCTF\b", r"\bDIRF\b", r"\bDIMOB\b", r"\bDMED\b",
    r"\bobrigacao\s+acessoria\b", r"\bobrigação\s+acessória\b",
    r"\bobrigacoes\s+acessorias\b", r"\bobrigações\s+acessórias\b",
    # Folha e DP / eSocial
    r"\beSocial\b", r"\bfolha\s+de\s+pagamento\b", r"\bfolha\b",
    r"\brescisao\b", r"\brescisão\b", r"\bferias\b", r"\bférias\b",
    r"\bdecimo\s+terceiro\b", r"\bdécimo\s+terceiro\b", r"\b13o\b",
    r"\badmissao\b", r"\badmissão\b", r"\bafastamento\b",
    r"\bFAP\b", r"\bRAT\b",
    # Escrituracao e fechamento
    r"\bbalancete\b", r"\bbalanco\b", r"\bbalanço\b",
    r"\bDRE\b", r"\bplano\s+de\s+contas\b",
    r"\bconciliacao\s+bancaria\b", r"\bconciliação\s+bancária\b",
    r"\bconciliacao\b", r"\bconciliação\b",
    r"\bfechamento\s+contabil\b", r"\bfechamento\s+contábil\b",
    r"\blancamento\s+contabil\b", r"\blançamento\s+contábil\b",
    r"\bfluxo\s+de\s+caixa\b", r"\bdepreciacao\b", r"\bdepreciação\b",
    r"\bimobilizado\b", r"\bCPC\b",
    # Documentos e arquivos fiscais
    r"\bNF-e\b", r"\bNFC-e\b", r"\bNFS-e\b", r"\bCT-e\b",
    r"\bnota\s+fiscal\b", r"\barquivo\s+XML\b", r"\bXML\b",
    r"\bOFX\b", r"\bextrato\s+bancario\b", r"\bextrato\s+bancário\b",
    r"\bCNAE\b", r"\bcarne-leao\b", r"\bcarnê-leão\b",
    r"\bganho\s+de\s+capital\b",
    # Diagnostico e auditoria
    r"\bmalha\s+fina\b", r"\bdue\s+diligence\s+contabil\b",
    r"\bvaluation\b", r"\bparcelamento\b",
    r"\babertura\s+de\s+empresa\b", r"\bCNPJ\b",
    r"\balteracao\s+contratual\b", r"\balteração\s+contratual\b",
    r"\bcalendario\s+fiscal\b", r"\bcalendário\s+fiscal\b",
    r"\bmelhor\s+saida\s+fiscal\b", r"\bmelhor\s+saída\s+fiscal\b",
]

# Gatilho 3: commands prefixados do plugin
PLUGIN_COMMANDS = [
    "/start-auditoria-contabil",
    "/contabil-master",
    "/caso-contabil",
    "/apuracao",
    "/obrigacoes",
    "/regime",
    "/revisao-final",
    "/status-contabil",
]

# Keywords contabeis gerais (fallback — se prompt e contabil mas nao casa
# com keyword forte, ainda aplica protocolo cauteloso de Revisao Tecnica)
CONTABIL_KEYWORDS_GENERAL = [
    r"\brelatorio\s+contabil\b", r"\brelatório\s+contábil\b",
    r"\bdemonstracoes\s+contabeis\b", r"\bdemonstrações\s+contábeis\b",
    r"\bcompetencia\b", r"\bcompetência\b",
    r"\balíquota\b", r"\baliquota\b",
    r"\bcontador\b", r"\bescritorio\s+contabil\b", r"\bescritório\s+contábil\b",
]

BYPASS_TOKENS = [
    "--no-revisao",
    "--no-corte",
    "--quick",
    "/revisao off",
    "/revisao-off",
]


def _load_input() -> dict:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {}


def _matches_any(text: str, patterns: list[str]) -> bool:
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


def _is_contabil(prompt: str) -> bool:
    """Detecta se o prompt e do dominio contabil-fiscal (gatilhos 1, 2 ou 3)."""
    if _matches_any(prompt, TRIGGER_CONTABIL):
        return True
    if _matches_any(prompt, DOMAIN_KEYWORDS):
        return True
    low = prompt.lower()
    for cmd in PLUGIN_COMMANDS:
        if cmd.lower() in low:
            return True
    return False


def _is_contabil_general(prompt: str) -> bool:
    """Detecta se e tarefa contabil em geral (mesmo sem keyword forte)."""
    return _matches_any(prompt, CONTABIL_KEYWORDS_GENERAL)


def _has_bypass(prompt: str) -> str | None:
    low = prompt.lower()
    for token in BYPASS_TOKENS:
        if token in low:
            return token
    return None


def _has_contabil_state(cowork: Path | None) -> bool:
    """Verifica se existe `auditoria-contabil/cowork-state.json` no path."""
    if cowork is None:
        return False
    return (cowork / "auditoria-contabil" / "cowork-state.json").exists()


def _revisao_tecnica_enabled(cowork: Path | None) -> bool:
    """Le state.json e verifica revisao_tecnica.enabled. Default true se ausente."""
    if cowork is None:
        return True
    sf = cowork / "auditoria-contabil" / "cowork-state.json"
    if not sf.exists():
        return True
    try:
        state = json.loads(sf.read_text(encoding="utf-8"))
        return bool(state.get("revisao_tecnica", {}).get("enabled", True))
    except Exception:
        return True


def _resolve_cowork() -> Path | None:
    """Resolve COWORK root via env CONTABIL_COWORK_PATH ou cwd ancestral."""
    env = os.environ.get("CONTABIL_COWORK_PATH") or os.environ.get("COWORK_PATH")
    if env:
        p = Path(env)
        if (p / "auditoria-contabil" / "cowork-state.json").exists():
            return p
    return hook_utils.find_cowork(Path.cwd())


def main() -> int:
    payload = _load_input()
    prompt = payload.get("prompt") or payload.get("user_prompt") or ""
    if not isinstance(prompt, str) or not prompt.strip():
        return 0

    cowork = _resolve_cowork()
    bypass = _has_bypass(prompt)

    is_contabil = _is_contabil(prompt)
    is_contabil_other = _is_contabil_general(prompt) and not is_contabil

    # Caso 1: bypass explicito
    if bypass and (is_contabil or is_contabil_other):
        sys.stdout.write(
            f"[auditoria-contabil-os] Bypass detectado ({bypass}). "
            "Apuracoes, relatorios e pareceres serao entregues SEM a "
            "Revisao Tecnica R1-R4. Use por sua conta e risco.\n"
        )
        return 0

    # Caso 2: tarefa contabil + plugin configurado
    if is_contabil and _has_contabil_state(cowork):
        if not _revisao_tecnica_enabled(cowork):
            sys.stdout.write(
                "[auditoria-contabil-os] Demanda contabil/fiscal detectada. "
                "Revisao Tecnica DESATIVADA na configuracao. Aciono apenas a cadeia de skills.\n"
                "Acionar skill: auditoria-contabil-master.\n"
            )
        else:
            sys.stdout.write(
                "[auditoria-contabil-os] Demanda contabil/fiscal detectada. Plugin ativado.\n"
                "\n"
                "PROTOCOLO AUTOMATICO:\n"
                "1. Acionar skill `auditoria-contabil-master` (Tier 0 — sempre ativa)\n"
                "2. Aplicar Hierarquia das 4 Camadas (1-Proibicoes, 2-Protocolos, 3-Estilo, 4-Skills)\n"
                "3. Verificar as 20 Proibicoes Absolutas (PA-01 a PA-20), com atencao especial:\n"
                "   - PA-01: nao orientar nem viabilizar sonegacao, fraude ou simulacao\n"
                "   - PA-02: exigir dado real do cliente (CNPJ/CPF, receita, competencia, atividade)\n"
                "   - PA-04: Selo de Validacao Legal Previa antes de qualquer calculo (P1)\n"
                "   - PA-05: ISS/ICMS sempre com base no municipio/UF do caso (P5)\n"
                "   - PA-03: datar apuracao e parecer pelo ano do fato gerador (reforma 2026-2033)\n"
                "   - PA-07: a saida e rascunho operacional — responsabilidade tecnica do contador (CRC)\n"
                "4. Acionar os 6 Protocolos da Camada 2 conforme demanda\n"
                "5. Antes de entregar: Revisao Tecnica R1->R2->R3->R4 (skill `revisao-final`)\n"
                "\n"
                "Bypass disponivel: `--no-revisao`, `--quick`, `/revisao off`.\n"
            )
        return 0

    # Caso 3: tarefa contabil mas plugin NAO configurado
    if is_contabil and not _has_contabil_state(cowork):
        sys.stdout.write(
            "[auditoria-contabil-os] Detectei demanda contabil/fiscal, mas o plugin "
            "ainda nao foi configurado neste diretorio.\n"
            "\n"
            "RECOMENDACAO: rode /start-auditoria-contabil para configurar (~5 min).\n"
            "Vou criar uma pasta `auditoria-contabil/` aqui com a identidade do "
            "contador/escritorio, CRC, municipio/UF, frentes de atuacao, tom de voz "
            "e configuracao das skills.\n"
            "\n"
            "Caso queira prosseguir SEM configurar, trabalho em modo fallback generico "
            "(persona neutra, qualidade reduzida). Apenas avise.\n"
        )
        return 0

    # Caso 4: tarefa contabil geral — protocolo cauteloso
    if is_contabil_other:
        sys.stdout.write(
            "[auditoria-contabil-os] Tarefa contabil detectada (sem frente especifica). "
            "Aplique protocolo padrao:\n"
            "1. Questionamento previo (sem suposicoes silenciosas — exigir dado real).\n"
            "2. Apresentar estrutura + premissas antes de calcular ou redigir.\n"
            "3. Aguardar confirmacao do usuario.\n"
            "4. Antes de entregar: executar Revisao Tecnica R1-R4 se aplicavel.\n"
            "Bypass: `--no-revisao`, `--quick`, `/revisao off`.\n"
        )
        return 0

    # Caso default: nao e tarefa contabil — silencio
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
