---
description: Submete uma entrega contabil-fiscal a Revisao Tecnica R1-R4 antes da entrega — escopo e dados, tecnica (calculo e norma), conformidade (obrigacao, prazo, localizacao) e entrega (clareza, ressalva CRC).
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint: [entrega a auditar]
---

Voce foi acionado pelo comando `/revisao-final` do plugin Auditoria Contabil OS.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** auditar uma entrega contabil-fiscal pela Revisao Tecnica R1-R4 antes de devolver ao usuario.

## PROTOCOLO

1. **Acionar a skill `revisao-final`**.
2. Identificar a entrega a auditar (apuracao, obrigacao preparada, relatorio, parecer, deck) e o caso ativo (`CASO.md`).
3. Executar a sequencia obrigatoria:
   - **R1 — Escopo e dados:** o pedido foi entendido? Os dados de entrada sao reais (PA-02), completos e da competencia certa (PA-03)?
   - **R2 — Tecnica:** calculo correto? Norma vigente e datada pelo ano do fato gerador, citada com artigo/numero (PA-03, PA-11)? Memoria de calculo rastreavel (P3)? Selo de Validacao Legal emitido (PA-04)?
   - **R3 — Conformidade:** obrigacao certa para o regime (PA-13)? Prazos corretos e sinalizados (PA-18)? Localizacao aplicada — ISS do municipio, ICMS da UF (PA-05)? Cruzamentos feitos (P4)?
   - **R4 — Entrega:** estrutura canonica? Ressalva de responsabilidade tecnica do contador (PA-07)? Numeros batendo com a memoria de calculo (PA-20)?
4. Cada rodada emite `APROVADO` / `APROVADO COM RESSALVAS` / `REPROVADO`. Reprovacao bloqueia as seguintes e devolve ao produtor.
5. Apresentar o relatorio final consolidado com o resultado de cada rodada e o veredito: `APROVADO` / `REVISAR` / `BLOQUEADO`.

Bypass disponivel: `--no-revisao` (registra waiver), `--quick` (R1+R2 apenas, para rascunhos internos) ou `/revisao off` (session toggle) — usado com transparencia, sob responsabilidade do operador.

**Skill a acionar:** `revisao-final`.
