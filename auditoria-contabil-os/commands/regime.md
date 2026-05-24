---
description: Comparativo basico de regime tributario (melhor saida fiscal) — orquestra as skills de apuracao do Tier 2 para confrontar Simples Nacional, Lucro Presumido e Lucro Real lado a lado. Comparativo completo (sensibilidade, deck) chega na v0.3.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint: [dados do contribuinte para o comparativo — receita, atividade, folha]
---

Voce foi acionado pelo comando `/regime` do plugin Auditoria Contabil OS.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** produzir um **comparativo basico de regime tributario** — confrontar Simples Nacional, Lucro Presumido e Lucro Real para o contribuinte, apontando a saida fiscal mais economica.

> **Escopo na v0.1:** comparativo basico — apura cada regime com as skills do Tier 2 e confronta os totais. A skill dedicada `planejamento-melhor-saida-fiscal` (analise de sensibilidade, projecao multi-cenario, deck de apresentacao, modo `recomendar-e-listar` vs `apenas-listar` configuravel) chega na **v0.3**. Sinalizar isso ao operador.

## PROTOCOLO

1. **Verificar** se o `CASO.md` esta criado. Se nao, acionar `triagem-contabil` — o comparativo depende de sujeito (PJ), CNAE/atividade, faturamento e folha.
2. **Conferir dados de entrada** — sao necessarios (PA-02): receita bruta (12 meses ou projecao), atividade/CNAE, folha de pagamento, margem, despesas dedutiveis. Dado faltante → `[INFORMAR]`, nunca presumir.
3. **Selo de Validacao Legal (PA-04)** — acionar `validador-legislacao-vigente`. Atencao a transicao da reforma tributaria (CBS/IBS por ano do fato gerador — PA-03) e ao eixo de localizacao (ISS municipal, ICMS estadual — PA-05).
4. **Apurar cada regime** acionando as skills do Tier 2, com a mesma base de dados:
   - `apuracao-simples-nacional` — DAS por anexo, fator R, sublimites.
   - `apuracao-lucro-presumido` — IRPJ/CSLL por presuncao + PIS/COFINS cumulativo (`pis-cofins-cumulativo`) + ICMS/ISS aplicaveis.
   - `apuracao-lucro-real` — IRPJ/CSLL sobre o lucro + PIS/COFINS nao-cumulativo (`pis-cofins-nao-cumulativo`) + ICMS/ISS aplicaveis.
   - Considerar tambem `inss-empresa` (carga patronal varia entre regimes).
5. **Verificar vedacoes de enquadramento** com `analise-cnae-atividades` — nem toda atividade pode optar por todos os regimes (PA-12 — distinguir obrigatorio de opcao).
6. **Consolidar o comparativo** via `estilo-entrega-contabil` — tabela lado a lado: regime, carga tributaria total, premissas de cada cenario, memoria de calculo rastreavel de cada um (P3). Numeros so do que vem de memoria verificavel (PA-20).
7. **Apontar** o regime de menor carga, com as ressalvas: a opcao tem prazo legal (PA-18), ha proposito negocial a observar (PA-10), e a decisao e do contador com CRC ativo (PA-07).
8. Ao concluir, acionar `revisao-final` (R1-R4) antes de entregar.

**Skills orquestradas:** `triagem-contabil`, `validador-legislacao-vigente`, `analise-cnae-atividades`, `apuracao-simples-nacional`, `apuracao-lucro-presumido`, `apuracao-lucro-real`, `pis-cofins-cumulativo`, `pis-cofins-nao-cumulativo`, `inss-empresa`, `estilo-entrega-contabil`, `revisao-final`.
