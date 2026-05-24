---
name: calendario-fiscal
description: >
  Mapa de obrigacoes e prazos contabil-fiscais por ente — federal, estadual e municipal — conforme o regime tributario e as frentes do cliente. Lista apuracoes, declaracoes e SPED com competencia, vencimento, ente competente e penalidade por atraso. Sinaliza prazos criticos: opcao de regime (prazo anual), decadencia e prescricao de 5 anos (CTN arts. 173 e 174), e vencimentos proximos. Datado pelo ano do fato gerador. Aciona: calendario fiscal, prazos, vencimentos, quando vence, obrigacoes do mes, agenda tributaria, prazo de entrega, decadencia, prescricao, prazo de opcao de regime, o que entregar.
---

# CALENDARIO FISCAL

> Skill **Tier 1** — mapa de obrigacoes e prazos por ente (federal, estadual, municipal), conforme regime e frente. Sinaliza prazos criticos. O escritorio contabil vive de prazos: a perda de um deles gera multa, perda de credito ou trava de regime.

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com "calendario fiscal", "prazos", "quando vence", "obrigacoes do mes", "agenda tributaria", "prazo de opcao de regime". Entrada: regime tributario, frentes, localizacao e competencia do `CASO.md`. Entrega: lista de obrigacoes e prazos do cliente, com prazos criticos destacados.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.
- **Aciona:** `validador-legislacao-vigente` (P1) quando um prazo depender de norma de alvo movel ou de regra local.
- **Entrega para:** o `CASO.md` (secao "Prazos e obrigacoes"), as skills de apuracao (Tier 2) e de obrigacoes acessorias (Tier 3).

## 2. Os tres niveis de obrigacao

| Nivel | Competencia | Exemplos |
|-------|-------------|----------|
| **Federal** | Receita Federal | DAS (Simples), DARF de IRPJ/CSLL/PIS/COFINS/IRRF/INSS, EFD-Contribuicoes, ECD, ECF, EFD-Reinf, DCTFWeb, DIMOB, DMED |
| **Estadual** | SEFAZ da UF | Guia de ICMS, GIA / apuracao estadual, EFD ICMS/IPI, ICMS-ST, DIFAL |
| **Municipal** | Prefeitura | Guia de ISS, declaracao mensal de servicos (NFS-e), obrigacoes municipais |

O conjunto de obrigacoes **depende do regime** (PA-13): o Simples concentra tributos no DAS e tem a DEFIS; o Presumido/Real tem EFD-Contribuicoes, ECD, ECF, apuracoes mensais/trimestrais separadas.

## 3. Obrigacoes por regime — visao operacional

### Simples Nacional
- **DAS** — apuracao mensal unica (federal + ICMS/ISS, salvo acima do sublimite).
- **DEFIS** — declaracao anual de informacoes socioeconomicas e fiscais.
- Acima do **sublimite** (R$ 3,6 mi — Portaria CGSN; `[VERIFICAR]` o valor do ano): ICMS/ISS recolhidos "por fora", com as obrigacoes do regime normal.
- MEI: DAS-MEI mensal e declaracao anual (DASN-SIMEI).

### Lucro Presumido / Lucro Real
- IRPJ e CSLL — apuracao trimestral (Presumido) ou trimestral/anual (Real).
- PIS/COFINS — apuracao mensal; **EFD-Contribuicoes** mensal.
- **ECD** e **ECF** — escrituracao contabil e fiscal, anuais.
- Obrigacoes de ICMS/IPI (EFD ICMS/IPI) e ISS conforme a atividade.

> Os vencimentos exatos sao definidos por ato infralegal que muda ano a ano — sempre `[VERIFICAR]` a data contra a norma vigente; nunca cravar dia de memoria (PA-06).

## 4. Obrigacoes acessorias e SPED (Tier 3)

| Obrigacao | Periodicidade | Ente | A quem se aplica |
|-----------|---------------|------|------------------|
| ECD | Anual | Federal | PJ obrigada a escriturar (Presumido/Real e parte do Simples) |
| ECF | Anual | Federal | PJ nao optante pelo Simples |
| EFD-Contribuicoes | Mensal | Federal | PJ do regime nao-cumulativo/cumulativo |
| EFD ICMS/IPI | Mensal | Estadual | Contribuinte de ICMS/IPI |
| EFD-Reinf | Mensal | Federal | PJ com retencoes e receitas a declarar |
| DCTFWeb | Mensal | Federal | Confissao de debitos previdenciarios e demais |
| DIMOB | Anual | Federal | Atividade imobiliaria |
| DMED | Anual | Federal | Servicos de saude |

Cada obrigacao tem competencia, prazo, layout e penalidade por atraso. A skill **mapeia** o prazo; a preparacao e das skills do Tier 3.

## 5. Prazos criticos a sinalizar (PA-18)

| Prazo | Base legal | Risco se perdido |
|-------|-----------|-------------------|
| **Opcao de regime tributario** | LC 123/2006 (Simples); legislacao do IRPJ | Trava o enquadramento por todo o ano-calendario |
| **Decadencia** | CTN art. 173 (e art. 150 §4o) — 5 anos | Extingue o direito de a Fazenda lancar; e o limite para recuperar credito |
| **Prescricao** | CTN art. 174 — 5 anos | Extingue a cobranca do credito ja constituido |
| **Obrigacoes acessorias** | Atos infralegais | Multa por atraso/omissao |
| **Parcelamentos** | Norma do parcelamento | Rescisao por falta de pagamento de parcelas |

> Decadencia/prescricao: **nunca** cravar a data sem ressalva de suspensoes e interrupcoes — anotar como estimativa marcada `[VERIFICAR]`. O prazo de **opcao de regime** e oportunidade que se perde: destacar quando proximo.

## 6. Datacao pelo ano do fato gerador (PA-03)

O calendario e datado pelo **ano do fato gerador / competencia**, nao pelo ano corrente. Na transicao da reforma (2026-2033), surgem obrigacoes novas ligadas a CBS/IBS e mudam prazos — sempre validar o calendario do ano correto com `validador-legislacao-vigente`. Marcar `[VERIFICAR — norma em transicao]` em obrigacao afetada pela reforma.

## 7. Formato de entrega

```
CALENDARIO FISCAL — [cliente] — [competencia]
Regime: [Simples | Presumido | Real | MEI]   Localizacao: [municipio]/[UF]

OBRIGACOES DO PERIODO:
| Obrigacao | Competencia | Vencimento | Ente | Penalidade por atraso |
|-----------|-------------|------------|------|------------------------|
| [...]     | [MM/AAAA]   | [DD/MM] [VERIFICAR] | [F/E/M] | [...] |

PRAZOS CRITICOS:
- Opcao de regime: [janela do ano] [VERIFICAR]
- Decadencia (fato gerador + 5 anos): [estimativa, VERIFICAR suspensoes]
- [prazo proximo destacado]

RESSALVA: as datas dependem de ato infralegal do ano e de regra local —
confirmar cada vencimento na fonte oficial. Rascunho operacional sujeito a
revisao e responsabilidade tecnica do contador com CRC ativo (PA-07).
```

## 8. Vedacoes especificas

- **PA-03** — o calendario e do ano do fato gerador; nao aplicar prazo de um ano a competencia de outro.
- **PA-06** — vencimentos exatos dependem de ato infralegal anual e de regra local — `[VERIFICAR]`, nunca cravar de memoria.
- **PA-08** — a skill mapeia e alerta; nao transmite nem entrega obrigacao.
- **PA-12** — distinguir obrigacao (mandatoria) de opcao (regime, beneficio facultativo).
- **PA-13** — o conjunto de obrigacoes depende do regime — nao listar obrigacao de outro regime.
- **PA-18** — sinalizar decadencia, prescricao e prazo de opcao de regime; nunca cravar prazo decadencial sem ressalva de interrupcoes.

## 9. Protocolos acionados

- **P1 — Validacao Legal Previa** — acionar `validador-legislacao-vigente` para confirmar prazos de alvo movel.
- **P5 — Localizacao** — prazos estaduais e municipais dependem do ente.

## 10. Localizacao

Os prazos **federais** valem em todo o pais. Os **estaduais** (ICMS, EFD, GIA) variam por UF; os **municipais** (ISS, declaracao de servicos) variam por municipio. A skill usa a localizacao do `CASO.md` para listar as obrigacoes do ente correto. Quando o vencimento estadual ou municipal nao puder ser confirmado, marcar `[VERIFICAR — norma municipal/estadual]` (PA-06).

## 11. Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.

**Entrega para:** o `CASO.md` (secao "Prazos e obrigacoes"), as apuracoes do Tier 2 e as obrigacoes acessorias do Tier 3. A entrega final passa por `revisao-final` (R1-R4).

**Sem esta skill:** o caso opera sem mapa de prazos — risco de perder a opcao de regime, deixar obrigacao acessoria vencer ou perder o prazo de recuperacao de credito por decadencia.
