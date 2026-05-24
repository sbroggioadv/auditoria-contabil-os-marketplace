---
name: analise-cnae-atividades
description: >
  Analise de CNAE e atividades economicas. Cruza o CNAE com o regime tributario permitido (vedacoes ao Simples Nacional), o anexo do Simples e o Fator R, o percentual de presuncao no Lucro Presumido, a incidencia de ISS versus ICMS, e o enquadramento de risco para folha (FAP e RAT/GIIL-RAT). Diagnostica se a atividade declarada e compativel com o objeto social e com a operacao real. Insumo da escolha de regime e da apuracao. Aciona: analisar CNAE, qual o anexo do Simples, vedacao ao Simples, atividade permite o regime, ISS ou ICMS, percentual de presuncao, Fator R, RAT/FAP, enquadramento de atividade, classificacao economica.
---

# ANALISE DE CNAE E ATIVIDADES

> Skill **Tier 1** — diagnostico da atividade economica. O CNAE determina regime permitido, anexo/presuncao, incidencia ISS×ICMS e risco de folha. Insumo direto da escolha de regime e de toda apuracao. Toda conclusao de regime exige o Selo de Validacao Legal Previa (P1).

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com "analisar CNAE", "qual o anexo do Simples", "essa atividade permite o regime", "ISS ou ICMS", "Fator R", "RAT/FAP". Entrada: CNAE(s) do cliente, objeto social, descricao da operacao real, localizacao. Entrega: ficha de enquadramento da atividade — regime permitido, anexo/presuncao, incidencia, risco de folha.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil` (apos identificar o regime), operador direto.
- **Aciona:** `validador-legislacao-vigente` (P1) antes de cravar regime ou anexo — a vedacao ao Simples e os anexos sao norma de alvo movel.
- **Entrega para:** apuracoes do Tier 2 (Simples, Presumido, Real), `calculo-iss`, `calculo-icms-st`, `calendario-fiscal` e a futura `planejamento-melhor-saida-fiscal`.

## 2. O que o CNAE determina

| Dimensao | O CNAE define |
|----------|---------------|
| **Regime permitido** | Atividades vedadas ao Simples (LC 123/2006, art. 17) e ao Lucro Presumido |
| **Anexo do Simples** | Anexo I a V — qual tabela de aliquotas e progressao se aplica |
| **Fator R** | Se folha/receita >= 28%, atividade do Anexo V pode migrar ao Anexo III |
| **Presuncao (Presumido)** | Percentual de presuncao do lucro por atividade (1,6% / 8% / 16% / 32%) |
| **ISS x ICMS** | Servico (ISS, municipal) x circulacao de mercadoria (ICMS, estadual) |
| **Risco de folha** | RAT/GIIL-RAT (1%, 2% ou 3%) e FAP (multiplicador 0,5 a 2,0) |
| **Obrigacoes acessorias** | Quais SPED e declaracoes a atividade exige |

## 3. Vedacoes ao Simples Nacional

A LC 123/2006 (art. 17) lista atividades **vedadas** ao Simples — entre elas, atividades financeiras, cessao/locacao de mao de obra, producao/venda de cigarros, importacao de combustiveis, certas atividades de assessoria creditoria. Outras atividades sao permitidas mas exigem o **Fator R** ou tem ressalvas.

Regra de conduta:
- Confirmar o CNAE contra a lista de vedacoes **vigente no ano** (alvo movel — PA-03/PA-06).
- Um CNAE vedado impede a opcao pelo Simples — registrar e rotear para Presumido/Real.
- **Multiplos CNAE**: se qualquer atividade exercida for vedada, a vedacao alcanca a empresa.
- `[VERIFICAR]` quando a inclusao do CNAE na lista de vedacao nao puder ser confirmada — nunca afirmar de memoria.

## 4. Anexos do Simples e Fator R

O Simples tem **5 anexos** (LC 123/2006, anexos I-V), cada um com sua tabela de aliquotas e faixas:
- **Anexo I** — comercio. **Anexo II** — industria.
- **Anexos III, IV e V** — servicos, conforme a atividade.
- **Anexo IV** — atividades de servico cuja folha **nao** integra a base do CPP no DAS (recolhe INSS patronal por fora).

**Fator R** = folha de salarios dos 12 meses anteriores ÷ receita bruta dos 12 meses anteriores. Atividades sujeitas ao Fator R: se o Fator R >= **28%**, tributam pelo **Anexo III** (geralmente mais favoravel); abaixo de 28%, pelo **Anexo V**. O calculo do Fator R e refeito mes a mes.

> O anexo aplicavel e dado de entrada da `apuracao-simples-nacional` — esta skill o **diagnostica**; a apuracao **calcula**.

## 5. Presuncao no Lucro Presumido

No Lucro Presumido, o lucro e presumido por um percentual sobre a receita bruta, definido pela atividade (Lei 9.249/1995):

| Atividade (sintese) | Presuncao IRPJ | Presuncao CSLL |
|---------------------|----------------|----------------|
| Revenda de combustivel | 1,6% | 12% |
| Comercio, industria, transporte de carga | 8% | 12% |
| Servico de transporte (exceto carga), serv. hospitalares | 16% | 12% |
| Servicos em geral, profissoes regulamentadas, intermediacao | 32% | 32% |

A atividade pode ter mais de uma receita com presuncoes diferentes — segregar por tipo de receita. `[VERIFICAR]` o percentual contra a norma vigente no ano do fato gerador (PA-03).

## 6. ISS x ICMS — qual tributo incide

| Operacao | Tributo | Ente | Norma-base |
|----------|---------|------|------------|
| Prestacao de servico | **ISS** | Municipio | LC 116/2003 |
| Circulacao de mercadoria | **ICMS** | UF | LC 87/1996 |
| Operacao mista (mercadoria + servico) | Conforme a lista da LC 116/2003 | Municipio e/ou UF | Servico na lista → ISS; fora da lista → ICMS sobre o todo |

O CNAE e o **item da lista de servicos** indicam se a atividade gera ISS ou ICMS. Atividade de servico na lista anexa da LC 116/2003 → ISS no municipio; circulacao de mercadoria → ICMS na UF. Operacoes mistas exigem segregacao — sinalizar.

## 7. Risco de folha — RAT/FAP

A atividade preponderante (CNAE) define a aliquota **RAT** (Risco Ambiental do Trabalho / GIIL-RAT — 1%, 2% ou 3% sobre a folha), ajustada pelo **FAP** (Fator Acidentario de Prevencao — multiplicador de 0,5 a 2,0, divulgado anualmente). RAT × FAP = aliquota efetiva da contribuicao para o financiamento dos beneficios acidentarios. Esta skill **diagnostica** o enquadramento; o calculo e da skill de INSS/folha (Tier 2/4).

## 8. Compatibilidade CNAE × objeto × operacao real

Diagnosticar se o CNAE declarado reflete a operacao real e o objeto social:
- CNAE incompativel com a operacao distorce regime, anexo, presuncao e risco de folha.
- Atividade exercida sem CNAE correspondente registrado e irregularidade — recomendar inclusao do CNAE (ato operacional, Tier 8).
- **Nunca** orientar a manter um CNAE incorreto para reduzir tributo (PA-01, PA-10) — isso e simulacao.

## 9. Vedacoes especificas

- **PA-01 / PA-10** — nao orientar enquadramento de CNAE artificial para caber no Simples ou reduzir presuncao; planejamento exige proposito negocial real.
- **PA-03 / PA-06** — vedacoes, anexos e percentuais sao alvo movel — `[VERIFICAR]` contra a norma vigente no ano.
- **PA-05** — a incidencia de ISS depende do municipio; a de ICMS, da UF — confirmar a localizacao.
- **PA-11** — citar a norma (LC 123/2006 art. 17, anexos; Lei 9.249/1995; LC 116/2003) com artigo.
- **PA-12** — distinguir o que e vedacao legal (obrigatorio) do que e opcao de regime do contribuinte.
- Nao calcular o tributo aqui — diagnosticar o enquadramento; o calculo e do Tier 2.

## 10. Protocolos acionados

- **P1 — Validacao Legal Previa** — acionar `validador-legislacao-vigente` antes de cravar regime, anexo ou presuncao.
- **P5 — Localizacao** — a incidencia ISS×ICMS e o risco de folha tem eixo geografico.

## 11. Localizacao

A incidencia de **ISS** depende do **municipio** (lista de servicos e aliquota da LC 116/2003 regulamentada localmente) e a de **ICMS**, da **UF**. O mesmo CNAE pode ter tratamento de ISS distinto entre municipios. Quando a regra municipal de incidencia ou a aliquota nao puder ser confirmada, marcar `[VERIFICAR — norma municipal/estadual]` (PA-06).

## 12. Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.

**Entrega para:** as apuracoes do Tier 2, `calculo-iss`, `calculo-icms-st`, `calendario-fiscal` e a `planejamento-melhor-saida-fiscal` (v0.3). A entrega final passa por `revisao-final` (R1-R4).

**Sem esta skill:** a escolha de regime e a apuracao operam sem diagnostico da atividade — risco de optar por regime vedado, aplicar o anexo errado ou trocar ISS por ICMS.
