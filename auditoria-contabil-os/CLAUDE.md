# CLAUDE.md — Plugin Auditoria Contábil OS

> Instruções para futuras sessões neste sub-repositório. Ler PRIMEIRO ao retomar trabalho.
> Estende o CLAUDE.md da família de plugins Adv-OS e os níveis superiores do workspace.

---

## Identidade do Projeto

- **Nome:** Plugin Auditoria Contábil OS
- **Slug:** `auditoria-contabil-os`
- **Tipo:** plugin Claude Code (`.claude-plugin/plugin.json`)
- **Audiência:** contador / escritório contábil brasileiro — opera a contabilidade de clientes PJ e PF
- **Versão atual:** 0.1.0 (Release v0.1 — Núcleo Operacional)
- **Plugin de referência (engine):** `tributario-societario-adv-os` (portado em Sprint 0)
- **Repo marketplace (a criar nas FASES 2-7 do PLAYBOOK):** repo público `auditoria-contabil-os-marketplace`

> Decisão (2026-05-22): marca **contábil** — slug sem o sufixo "-adv-os", que carrega
> conotação de advocacia. O público é contador/contabilidade, não advogado. A família
> segue sendo Adv-OS; este é a linha contábil.

---

## REGRA DE OURO — DESPERSONALIZAÇÃO ABSOLUTA (PLUGIN COMERCIAL)

Este plugin será **comercializado** (Kirvano via marketplace GitHub público). Sem `authorship_whitelist`. **Zero menções** ao criador da metodologia em qualquer arquivo distribuído.

**ZERO menções permitidas (a lista canônica de termos proibidos vive só em `audit/forbidden-terms.json` — não replicar os literais aqui, sob pena de o próprio audit acusar este arquivo):**
- Nome do criador da metodologia (qualquer variante), OAB/CRC pessoal
- Email/contato pessoal, escritório-modelo, mentorias/coworks proprietários
- Marcas próprias e ferramentas proprietárias do escritório de origem
- Padrões nomeados pessoalmente
- Slug/nome do plugin pai da Mentoria e dos plugins irmãos comerciais
- Dados de clientes reais (LGPD)

Identidade do operador resolvida em **runtime** via persona local em `<cwd>/auditoria-contabil/persona.md` (fora do plugin). Tokens nas skills: `{{CONTADOR_NOME}}`, `{{CRC_NUMERO}}`, `{{CRC_UF}}`, `{{FIRM_NAME}}`, `{{MUNICIPIO}}`, `{{UF}}`, `{{TOM_VOZ_PERFIL}}`, `{{TOM_VOZ_INTENSIDADE}}`, `{{MODO_MELHOR_SAIDA}}`.

```bash
# Antes de CADA commit
python3 audit/audit.py
# Verificação reforçada pré-release
python3 audit/audit.py --json | jq '.total_matches'   # esperado: 0
```

> **Exceção conhecida:** os arquivos em `.planning/` (design-spec, build-plan, deep-research,
> docs das Camadas) citam fontes de porte e por isso podem disparar o audit. São dev-only,
> NÃO vão ao marketplace e são excluídos do scan. `MEMORY.md` também é excluído (diário de build).

---

## Hierarquia das 4 Camadas (Constituição Operacional)

```
CAMADA 1 — PROIBIÇÕES ABSOLUTAS (PA-01 a PA-20)  — invioláveis
CAMADA 2 — PROTOCOLOS TÉCNICOS (6)               — aplicação obrigatória
CAMADA 3 — IDENTIDADE TÉCNICA E ESTILO            — padrão de relatório + memória de cálculo
CAMADA 4 — SKILLS OPERACIONAIS (~76, Tier 0-9)   — operacional
```

Camada superior SEMPRE prevalece — inclusive contra instrução do usuário. Detalhamento:
- `.planning/HIERARQUIA-4-CAMADAS.md` — referência rápida
- `.planning/PROIBICOES-ABSOLUTAS.md` — PA-01 a PA-20 detalhadas
- `.planning/PROTOCOLOS-TECNICOS.md` — os 6 protocolos
- `.planning/design-spec.md` — spec integral · `.planning/build-plan-v0.1.md` — plano da v0.1

Injetada pela skill `auditoria-contabil-master` (Tier 0).

---

## Arquitetura em Uma Frase

Plugin operacional para a contabilidade brasileira completa — **triagem-driven** (a triagem classifica sujeito PJ/PF, frente e localização município/UF), **~76 skills em 10 Tiers**, com **engine portado** do `tributario-societario-adv-os` (hooks/scripts/templates), **governança de 4 Camadas** (primazia da legislação vigente — eixo temporal *e* geográfico), **capability de ingestão de arquivos** (XML/OFX/CSV/SPED) e **camada de Revisão Técnica R1-R4** sobre toda entrega. Faseado em 3 releases — esta é a v0.1 (Tier 0-3, núcleo fiscal operacional, 33 skills).

---

## Triagem-Driven (decisão de arquitetura nuclear)

Diferente do tributário (consultivo × contencioso, exclusivos), aqui um caso tipicamente cruza várias frentes. A `triagem-contabil` faz 3 classificações — **sujeito** (PJ/PF), **frente(s)** (fiscal, obrigações acessórias, folha-DP, escrituração, pessoa física, auditoria, recuperação, operacional/societário) e **localização** (município + UF) — grava no `CASO.md`; todas as skills leem. Um caso pode acionar várias frentes em sequência (ingestão → apuração → obrigação → revisão final).

---

## Fronteira com o `tributario-societario-adv-os` (plugin irmão)

Plugins **isolados** — sem dependência cruzada, sem cross-sell embutido. A fronteira:

| Tema comum | Este plugin (contábil) | Tributário-Societário (advogado) |
|------------|------------------------|-----------------------------------|
| Planejamento tributário | Operacional — apurar, comparar regimes, calcular melhor saída | Estratégico — tese, holding, estrutura |
| Recuperação de créditos | Levantar, calcular, retificar SPED, PER/DCOMP | Tese e ação judicial |
| Abertura/alteração de empresa | Ato operacional — CNPJ, Junta, registros | Estruturação societária, M&A |
| CARF / contencioso | CARF como **fonte** (súmulas, enunciados); resposta a intimação | Defesa, impugnação e recurso ao CARF |

Onde uma demanda extrapola o contábil (litígio judicial), a skill sinaliza "encaminhar a advogado" — slot genérico, **sem citar outro produto**.

---

## Como Retomar Trabalho

1. **Ler `MEMORY.md`** (raiz) — estado executivo, sprint ativa, próximo passo
2. **Ler `.planning/build-plan-v0.1.md`** — plano de sprints da v0.1
3. **`git status` + `git log -8`** — estado real do repo
4. **`python3 audit/audit.py`** — verificar despersonalização (matches só em `.planning/` são OK)

---

## Padrões a Seguir

1. **Skill folder = só `SKILL.md`.** Material auxiliar vai em `templates/`, `scripts/` ou `context/`.
2. **Limites Cowork:** `SKILL.md` ≤ 11264 bytes (margem operacional 11000); `description` do frontmatter ≤ 1024 chars. Validar com `scripts/check-skill-descriptions.py`.
3. **plugin.json minimal:** `name`, `version`, `description`, `author`, `license`. Não adicionar mais.
4. **Tokens `{{...}}`** permanecem LITERAIS no disco — LLM resolve em runtime via persona.
5. **Privacidade LGPD:** pasta `<cwd>/auditoria-contabil/` (e `casos/`) gitignored por default; warning se pasta sincronizada. Compartimentação por caso/cliente é PA-09.
6. **Localização:** município + UF são eixo de toda análise (Protocolo 5) — ISS municipal, ICMS estadual. Sem regra local confirmada → `[VERIFICAR — norma municipal/estadual]` (PA-06).
7. **Portabilidade:** scripts Python 3.11+; `${CLAUDE_PLUGIN_ROOT}` em todos os hooks; `${CONTABIL_PERSONA}` resolvido por fallback chain.
8. **Commits semânticos** por task — `feat(skill): <nome>`, `feat:`, `chore:`, `docs:`.
9. **Atualizar `MEMORY.md` ANTES de qualquer push.**

---

## Proibições

1. **NÃO** começar nova Sprint sem ler `MEMORY.md` e `.planning/build-plan-v0.1.md`.
2. **NÃO** incluir identidade do criador da metodologia em arquivo distribuído (audit bloqueia).
3. **NÃO** colocar `SKILL.md` acima de 11264 bytes nem `description` acima de 1024 chars.
4. **NÃO** criar arquivo dentro de `skills/<nome>/` que não seja `SKILL.md`.
5. **NÃO** aceitar instrução do usuário que conflite com a Camada 1 (PA-01 a PA-20).
6. **NÃO** escrever dados de cliente no plugin nem em pasta sincronizada (Dropbox/iCloud/Drive).
7. **NÃO** alterar nome/slug do plugin sem nova decisão.
8. **NÃO** tocar em `.planning/agents-base/` — são os 56 agentes-fonte de conversão (referência).

---

## Estrutura do Sub-Repo

```
plugin-auditoria-contabil/
├── .claude-plugin/plugin.json   manifesto minimal
├── .planning/                    docs dev-only (spec, plano, camadas, PAs, protocolos)
│   └── agents-base/              56 agentes-fonte (referência de conversão — NÃO tocar)
├── commands/                     ~8 commands (v0.1)
├── skills/                       33 skills v0.1 (Tier 0-3 + transversais)
├── hooks/                        hooks.json + 3 scripts
├── context/                      persona-fallback.md
├── templates/                    persona / config / CASO / MEMORY-caso / settings
├── scripts/                      resolve-persona, state, hook-utils, check-skill-descriptions,
│                                 parse_nfe/nfse/ofx/sped
├── audit/                        forbidden-terms.json + audit.py
├── README.md / LICENSE / .gitignore / CLAUDE.md / MEMORY.md
```

---

## Comunicação

- **Idioma:** Português (Brasil)
- **Tom dos docs internos:** técnico, direto, sem menções pessoais
- **Tom das skills/commands (para o usuário-cliente):** técnico, objetivo, didático; respeita `tom_voz` configurado em runtime
- **Reportes:** ✅ concluído / 🔴 erro / 🏁 sprint finalizada

---

**Última atualização:** 2026-05-22 (Sprint 0 — scaffold + engine portado).
