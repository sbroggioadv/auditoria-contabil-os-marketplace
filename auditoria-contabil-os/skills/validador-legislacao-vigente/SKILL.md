---
name: validador-legislacao-vigente
description: >
  Protocolo 1 do plugin. Valida se cada norma (lei, LC, decreto, IN, solucao de consulta) citada esta vigente e na redacao correta para o ANO DO FATO GERADOR (eixo temporal — reforma tributaria 2026-2033, transicao CBS/IBS/IS) E no ENTE correto (eixo geografico — federal, estadual de ICMS, municipal de ISS). Considera jurisprudencia, sumulas e enunciados do CARF. Emite o Selo de Validacao Legal Previa — pre-requisito de toda apuracao, calculo e parecer. Marca [VERIFICAR] quando a norma e alvo movel ou a regra local nao esta confirmada. Aciona: validar legislacao, lei vigente, a norma ainda vale, checar legislacao, reforma tributaria, qual regime se aplica, datar fato gerador, emitir o Selo.
---

# VALIDADOR DE LEGISLACAO VIGENTE

> Skill **Tier 0** — o Protocolo 1 em operacao. Pre-requisito absoluto de toda skill de calculo/apuracao (Tier 1-9). Emite o **Selo de Validacao Legal Previa**. Implementa PA-03, PA-04, PA-05, PA-06 e PA-11.

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master` antes de qualquer apuracao, ou diretamente pelo operador com `/regime`, "validar a legislacao", "qual regra se aplica", "a reforma impacta este caso", "datar o fato gerador". Recebe: norma(s) citada(s), tipo de caso, ano/competencia do fato gerador, municipio e UF. Entrega: laudo de vigencia nos dois eixos + o Selo de Validacao Legal Previa, registrado no `CASO.md`.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master` (obrigatorio antes de Tier 1-9 de calculo), `triagem-contabil`, qualquer skill que precise confirmar norma.
- **Entrega para:** a skill de apuracao/calculo solicitante + campo `Selo de Validacao Legal` no `CASO.md`.
- **Dependencia (PA-04):** **nenhuma apuracao opera sem o Selo.**

## 2. Os dois eixos do alvo movel

A legislacao tributaria muda em duas dimensoes:

- **Eixo temporal** — a reforma tributaria (EC 132/2023 + LC 214/2025) cria uma transicao 2026-2033 com coexistencia de CBS/IBS/IS e PIS/COFINS/ICMS/ISS. Aliquotas, anexos do Simples, limites de faturamento e regras mudam por exercicio.
- **Eixo geografico** — o **ISS** e municipal (aliquota 2% a 5%, lista de servicos e NFS-e variam por municipio — LC 116/2003); o **ICMS** e estadual (aliquotas internas, ICMS-ST, MVA, beneficios e RICMS variam por UF).

A norma aplicavel e sempre a vigente **no ano do fato gerador** e **no ente competente** — nunca a redacao de hoje, nunca uma aliquota generica.

## 3. Os 8 passos do Protocolo 1

### Passo 1 — Datar o fato gerador
Identificar o ano/competencia exata do evento tributavel. Esta data e o marco para determinar qual redacao da norma se aplica (PA-03). Se nao informado, perguntar: "Qual a competencia do fato gerador? Ex.: 03/2026."

### Passo 2 — Inventariar as normas nos 3 niveis
Listar todas as normas relevantes:
- **Federal** — LC e lei ordinaria, decreto regulamentador, IN RFB, Solucao de Consulta COSIT, Ato Declaratorio Interpretativo.
- **Estadual** — RICMS, decretos estaduais, convenios e protocolos CONFAZ (ICMS, ICMS-ST).
- **Municipal** — LC 116/2003 + lei e decreto municipal de ISS, portaria da NFS-e.

### Passo 3 — Validar vigencia
Para cada norma: data de publicacao (DOU), vacatio legis, inicio da vigencia efetiva, revogacao expressa ou tacita anterior ao fato gerador. Classificar: **VIGENTE** / **ALTERADA** / **REVOGADA** / **VACATIO** / **INDETERMINADO**. Norma INDETERMINADO → sinalizar e pedir orientacao antes de prosseguir.

### Passo 4 — Checar a redacao efetiva no ano
A norma pode ter sido alterada por multiplas leis/MPs apos a edicao original. Verificar a redacao vigente no ano do fato gerador, nao a atual. Indicar a versao usada. Ex.: a LC 123/2006 (Simples Nacional) tem multiplas alteracoes — confirmar a redacao do exercicio.

### Passo 5 — Travar o regime tributario do ano
Critico na transicao da reforma (referencia: EC 132/2023 + LC 214/2025 — regulamentacao infralegal pendente, reverificar a cada uso):

| Ano do fato gerador | Regime aplicavel |
|---------------------|-----------------|
| ate 2025 | PIS/COFINS/ICMS/ISS integrais |
| 2026 | Ano-teste: CBS 0,9% + IBS 0,1% (informativo, sem arrecadacao efetiva). PIS/COFINS/ICMS/ISS seguem normais. NF ja discrimina os novos tributos |
| 2027 | PIS e COFINS extintos; CBS em aliquota cheia. IS cobrado. IPI reduzido (salvo ZFM) — [VERIFICAR percentuais] |
| 2029-2032 | Transicao gradual: ICMS e ISS reduzem, IBS sobe progressivamente — [VERIFICAR percentuais de cada ano na LC 214/2025] |
| 2033+ | ICMS e ISS extintos. Modelo pleno CBS + IBS + IS |

### Passo 6 — Verificar infralegais e regras locais
IN RFB vigente; **RICMS da UF** do contribuinte (aliquotas, ST, beneficios); **lei e portaria municipal de ISS** (aliquota, lista de servicos, NFS-e). A lei pode ser federal, mas a regulamentacao e a aliquota sao locais (Protocolo 5).

### Passo 7 — Rastrear PL/MP pendente
Verificar proposta legislativa ou medida provisoria relevante em tramitacao (regulamentacao pendente da LC 214/2025, ajustes de aliquota, alteracao de anexos do Simples) e sinalizar ao operador.

### Passo 8 — Emitir o Selo de Validacao Legal Previa
Ao final dos 7 passos, emitir o Selo.

## 4. Jurisprudencia, sumulas e enunciados do CARF

O CARF e tratado como **fonte** — nao como instancia de litigio (PA-16). Ao validar a base legal:
- Confirmar se ha **Sumula CARF** vinculante sobre a materia (efeito vinculante para a propria administracao).
- Verificar **enunciados** e jurisprudencia consolidada do CARF que orientem a apuracao ou a recuperacao de credito.
- Sinalizar quando a interpretacao for controversa ou houver divergencia entre turmas.
- Para teses de credito (ex.: Tema 69 STF — ICMS fora da base de PIS/COFINS), classificar a situacao e marcar `[VERIFICAR]` o que depender de transito em julgado ou modulacao.

> **PA-11 / PA-06 — zero alucinacao:** sem certeza do numero de lei, artigo, sumula, tema ou enunciado, marcar `[VERIFICAR — confirmar na fonte oficial]` e indicar o caminho de busca. Nunca inventar ou aproximar referencia, aliquota, prazo ou codigo de receita.

## 5. Formato do Selo de Validacao Legal Previa

```
SELO DE VALIDACAO LEGAL PREVIA
Data-base: [DD/MM/AAAA]
Fato gerador datado: [competencia/ano]
Localizacao: [municipio] / [UF]
Normas validadas (3 niveis):
  Federal:   [norma] — VIGENTE — redacao de [data]
  Estadual:  [RICMS/UF] — [VIGENTE | VERIFICAR]
  Municipal: [lei ISS] — [VIGENTE | VERIFICAR — norma municipal]
Regime tributario travado: [PIS/COFINS/ICMS/ISS | ano-teste 2026 | transicao CBS/IBS X%]
Jurisprudencia/CARF: [sumulas, enunciados, temas aplicaveis — ou "nao aplicavel"]
Alertas: [PL/MP pendente; norma de alvo movel; regra local nao confirmada]
Validade: reflete a legislacao na data-base. Reverificar se o caso for fechado
          apos [data-base + 60 dias].
```

O Selo e registrado no `CASO.md` (campo `Selo de Validacao Legal`). Qualquer skill de calculo que receba demanda sem Selo aciona esta skill primeiro.

## 6. Flag de norma desatualizada

```
[ALERTA NORMATIVO]
A norma citada ([ex.: art. X da Lei Y]) nao se aplica ao fato gerador de [ano].
Motivo: [revogada por / alterada por / substituida por]
Norma aplicavel ao periodo: [Z]
Acao recomendada: [substituir a referencia / verificar texto vigente / aguardar regulamentacao]
```

Nunca prosseguir com norma sinalizada como REVOGADA sem confirmacao expressa do operador.

## 7. Vedacoes especificas

- **PA-03** — a redacao atual nao substitui a redacao vigente no ano do fato gerador.
- **PA-04** — Selo nao emitido = apuracao bloqueada.
- **PA-05** — ISS validado contra a lei do municipio; ICMS contra o RICMS da UF — nunca aliquota generica.
- **PA-06** — norma de alvo movel ou regra local nao confirmada → `[VERIFICAR]`.
- **PA-11** — toda norma citada com lei, artigo, inciso — nada de "a lei diz".
- Nunca emitir o Selo sem completar os 8 passos. Nunca afirmar vigencia sem checar fonte oficial.

## 8. Protocolos acionados

- **P1 — Validacao Legal Previa** — esta skill **e** o Protocolo 1.
- **P5 — Localizacao** — o Passo 6 aplica o eixo geografico (ISS municipal, ICMS estadual).

## 9. Localizacao

A localizacao e parte estrutural da validacao. Le municipio + UF da persona e do `CASO.md` (a `triagem-contabil` pode ter sobrescrito por caso). O Selo so e emitido com a localizacao identificada — o eixo geografico determina qual RICMS e qual lei municipal de ISS validar. Regra local nao confirmada → `[VERIFICAR — norma municipal/estadual]` no Selo (PA-06); a cobertura de NFS-e municipal e reconhecidamente fragmentada.

## 10. Integracao

**Chamada por:** `auditoria-contabil-master` (obrigatorio antes de qualquer Tier 1-9 de calculo), `triagem-contabil`, qualquer skill que receba citacao de norma.

**Entrega para:** a skill de apuracao/calculo que aguarda o Selo + campo `Selo de Validacao Legal` no `CASO.md`. A entrega final passa por `revisao-final` (R1-R4).

**Sem esta skill:** nenhuma apuracao, comparativo de regime, recuperacao ou parecer pode prosseguir (PA-04 + Protocolo 1). E invariante (nao-removivel).
