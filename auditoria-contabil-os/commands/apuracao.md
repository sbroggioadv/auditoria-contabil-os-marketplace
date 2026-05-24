---
description: Roteia para as skills de apuracao tributaria (Tier 2) — Simples Nacional, Lucro Presumido, Lucro Real, MEI, ICMS/ICMS-ST, IPI, ISS, PIS/COFINS, IRRF folha, INSS empresa e retencoes do tomador.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint: [demanda de apuracao — ex: apurar o Simples do mes, ICMS-ST, PIS/COFINS]
---

Voce foi acionado pelo comando `/apuracao` do plugin Auditoria Contabil OS.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** rotear a demanda de apuracao tributaria para a skill Tier 2 adequada.

## PROTOCOLO

1. **Verificar** se o `CASO.md` esta criado. Se nao, acionar `triagem-contabil` primeiro (sujeito PJ/PF, frente, localizacao, regime, competencia).
2. **Ingestao de arquivos** — se a apuracao depende de XML/OFX/CSV/SPED, acionar antes `analise-xml-fiscal`, `analise-extratos-ofx-csv` ou `leitura-arquivos-sped` (Protocolo 2 — parsing deterministico).
3. **Selo de Validacao Legal (PA-04)** — verificar se foi emitido. Se nao, acionar `validador-legislacao-vigente` antes de qualquer calculo. Atentar ao ano do fato gerador e a transicao da reforma tributaria (CBS/IBS em coexistencia por ano — PA-03).
4. **Identificar** a demanda e rotear:

| Demanda | Skill |
|---------|-------|
| Apuracao do Simples Nacional, anexos, fator R, sublimites | `apuracao-simples-nacional` |
| IRPJ/CSLL no Lucro Presumido, presuncao por atividade | `apuracao-lucro-presumido` |
| IRPJ/CSLL no Lucro Real, LALUR, adicoes/exclusoes | `apuracao-lucro-real` |
| Apuracao do MEI, DAS-MEI, DASN-SIMEI | `apuracao-mei` |
| ICMS proprio, ICMS-ST, MVA, DIFAL | `calculo-icms-st` |
| IPI — enquadramento na TIPI, creditos | `calculo-ipi` |
| ISS — base, aliquota e local de incidencia (municipal) | `calculo-iss` |
| PIS/COFINS no regime cumulativo | `pis-cofins-cumulativo` |
| PIS/COFINS no regime nao-cumulativo, creditos | `pis-cofins-nao-cumulativo` |
| IRRF sobre a folha de pagamento | `irrf-folha` |
| INSS patronal, RAT, FAP, terceiros | `inss-empresa` |
| Retencoes na fonte do tomador de servico | `retencoes-tomador` |

5. Toda apuracao usa **memoria de calculo rastreavel** (Protocolo 3, via `estilo-entrega-contabil`) e atualizacao pela Selic acumulada quando houver atraso (PA-15).
6. Ao concluir, acionar `revisao-final` (R1-R4) antes de entregar.

**Skills do Tier 2:** `apuracao-simples-nacional`, `apuracao-lucro-presumido`, `apuracao-lucro-real`, `apuracao-mei`, `calculo-icms-st`, `calculo-ipi`, `calculo-iss`, `pis-cofins-cumulativo`, `pis-cofins-nao-cumulativo`, `irrf-folha`, `inss-empresa`, `retencoes-tomador`.
