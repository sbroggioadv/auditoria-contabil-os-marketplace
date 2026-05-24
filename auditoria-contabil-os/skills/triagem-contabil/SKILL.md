---
name: triagem-contabil
description: >
  Porta de entrada de todo caso contabil-fiscal. Conduz entrevista estruturada e faz 3 classificacoes: sujeito (PJ ou PF), frente(s) de trabalho (fiscal, obrigacoes-acessorias, folha-dp, escrituracao, pessoa-fisica, auditoria, recuperacao, operacional-societario) e localizacao (municipio + UF — eixo de ISS e ICMS). Identifica regime tributario, CNAE, competencia do fato gerador e prazos em curso. Grava tudo no CASO.md e roteia ao Tier correto. Sem triagem concluida nenhuma skill de calculo opera com contexto. Aciona: novo caso, triagem, abrir caso, /caso-contabil, cliente novo, analisar demanda contabil, comecar atendimento, qual regime, onde se enquadra.
---

# TRIAGEM CONTABIL

> Skill **Tier 1** — porta de entrada obrigatoria de toda demanda contabil-fiscal. Executa entrevista estruturada, faz 3 classificacoes (sujeito, frente, localizacao), identifica regime/CNAE/competencia/prazos e grava o `CASO.md`. Triagem-driven: um caso cruza varias frentes em sequencia.

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master` ao receber demanda nova, por `/caso-contabil`, ou pelo operador com "novo caso", "triagem", "abrir caso", "cliente novo". Entrega: `CASO.md` preenchido (sujeito, frente(s), localizacao, regime, CNAE, competencia, prazos) + roteamento ao Tier correto. Nao executa calculo — classifica e encaminha.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master` (Tier 0) ao abrir demanda.
- **Aciona em seguida:** `analise-cnae-atividades` e `calendario-fiscal` (Tier 1) para completar o diagnostico; `validador-legislacao-vigente` (P1, Tier 0) antes de qualquer calculo.
- **Entrega para:** o `CASO.md` (gravacao) e as skills de Tier 1-9 conforme roteamento.
- **Pre-requisito de:** toda skill de apuracao/obrigacao — sem `CASO.md`, a skill opera sem contexto de sujeito, frente e localizacao.

## 2. Entrevista estruturada

Conduzir em ate 6 perguntas objetivas, na ordem. Adaptar conforme as respostas. Nao supor fato — registrar `[INFORMAR]` no `CASO.md` quando incerto.

```
1. Nome / razao social do cliente. (Sem CPF/CNPJ de cliente real durante a
   triagem se o workspace estiver em pasta sincronizada — PA-09.)
2. E pessoa juridica ou pessoa fisica?
3. Qual a demanda em termos praticos? (Ex.: apurar o Simples do mes,
   preparar a EFD-Contribuicoes, conciliar o banco, declarar o IRPF,
   revisar a apuracao, abrir empresa, responder a uma intimacao.)
4. Para PJ: qual o regime tributario e o CNAE/atividade principal?
   Para PF: qual a origem dos rendimentos (salario, aluguel, autonomo,
   ganho de capital, bolsa)?
5. Qual o municipio e a UF do cliente? (Eixo critico — ISS e municipal,
   ICMS e estadual. Pode diferir da sede do escritorio.)
6. Qual a competencia / periodo do fato gerador? Ha algum prazo,
   intimacao ou obrigacao vencendo?
```

## 3. Classificacao 1 — Sujeito

| Sujeito | Indicadores |
|---------|-------------|
| **PJ** | CNPJ, regime (Simples/Presumido/Real/MEI), faturamento empresarial, folha, obrigacoes acessorias de PJ |
| **PF** | CPF, rendimentos de pessoa fisica, IRPF, carne-leao, ganho de capital, aluguel, investimentos |

Registrar `Sujeito: PJ | PF` no `CASO.md`. Um cliente pode ter as duas dimensoes (socio PJ + IRPF do socio) — registrar ambas e tratar em casos separados (compartimentacao — PA-09).

## 4. Classificacao 2 — Frente(s) de trabalho

Diferente de um modo exclusivo: um caso tipicamente aciona **varias frentes em sequencia**.

| Frente | O que abrange | Tier |
|--------|---------------|------|
| **fiscal** | Apuracao de tributos por regime (Simples, Presumido, Real, MEI, ICMS, IPI, ISS, PIS/COFINS, INSS, IRRF, retencoes) | 2 |
| **obrigacoes-acessorias** | SPED (ECD/ECF/EFD), DCTFWeb, DIRF, DIMOB, DMED | 3 |
| **folha-dp** | Folha, eSocial, ferias/13o, rescisao, FGTS | 4 (v0.2) |
| **escrituracao** | Plano de contas, lancamentos, conciliacoes, balancete, DRE, fechamento | 5 (v0.2) |
| **pessoa-fisica** | IRPF, carne-leao, ganho de capital, investimentos | 6 (v0.2) |
| **auditoria** | Revisao e diagnostico da contabilidade operada | 7 (v0.3) |
| **recuperacao** | Levantamento e recuperacao de creditos tributarios | 7 (v0.3) |
| **operacional-societario** | Abertura, alteracao, baixa de empresa, parcelamento, resposta a fiscalizacao | 8 (v0.3) |

Registrar `Frente(s): [lista]` no `CASO.md`. Demanda de Tier ainda nao liberado na v0.1 (4-9) → sinalizar ao operador e cobrir o possivel com Tier 0-3.

## 5. Classificacao 3 — Localizacao (Protocolo 5)

Capturar **municipio** e **UF** do cliente — eixo de toda apuracao de ISS e ICMS.

- O **ISS** e municipal: aliquota (2% a 5%, LC 116/2003), lista de servicos e NFS-e variam por municipio.
- O **ICMS** e estadual: aliquotas internas, ICMS-ST, MVA, beneficios e RICMS variam por UF.
- A localizacao **do cliente** pode diferir da sede do escritorio (persona). A triagem **sobrescreve** a localizacao-padrao quando o cliente atua em outra praca.

Registrar `Municipio` e `UF` no `CASO.md`. Sem confirmacao da regra local → as skills marcam `[VERIFICAR — norma municipal/estadual]` (PA-06).

## 6. Marcos do caso — regime, CNAE, fato gerador

- **Regime tributario** (PJ): Simples Nacional, Lucro Presumido, Lucro Real, MEI — define quais apuracoes e obrigacoes se aplicam (PA-13). CNAE → acionar `analise-cnae-atividades` para confirmar regime permitido, anexo do Simples / presuncao e incidencia ISS×ICMS.
- **Competencia / ano do fato gerador**: marco que determina a legislacao aplicavel (PA-03) — critico na transicao da reforma 2026-2033.
- **Prazos em curso**: opcao de regime (prazo anual), obrigacoes acessorias, decadencia/prescricao 5 anos (CTN arts. 173/174) — acionar `calendario-fiscal` (PA-18).

## 7. Gravacao no CASO.md

Concluida a triagem, gerar/atualizar o `CASO.md` (template `templates/CASO.md.tpl`):

```markdown
# CASO — [cliente]

## Triagem do caso
- Sujeito: [PJ | PF]
- Frente(s): [lista]
- Tipo de tarefa: [descricao curta]

## Localizacao (Protocolo 5)
- Municipio do cliente: [municipio]
- UF do cliente: [UF]

## Dados do cliente
- Regime tributario: [Simples | Presumido | Real | MEI | PF]
- CNAE / Atividade: [codigo + descricao ou INFORMAR]
- Competencia / periodo: [competencia]

## Marco intertemporal
- Ano / data do fato gerador: [AAAA ou INFORMAR]

## Selo de Validacao Legal Previa
- Status: PENDENTE  (acionar validador-legislacao-vigente)

## Historico de updates
- [DD/MM/AAAA]: Triagem inicial concluida.
```

## 8. Roteamento pos-triagem

| Classificacao | Proxima skill |
|---------------|---------------|
| Ha arquivos a processar (XML/OFX/CSV/SPED) | `analise-xml-fiscal` / `analise-extratos-ofx-csv` / `leitura-arquivos-sped` |
| PJ + regime a confirmar | `analise-cnae-atividades` |
| Qualquer caso | `calendario-fiscal` (prazos) + `validador-legislacao-vigente` (Selo) |
| Frente fiscal | Tier 2 — apuracao do regime correto, **so apos o Selo** |
| Frente obrigacoes-acessorias | Tier 3 — SPED/declaracoes |

**Sempre** acionar `validador-legislacao-vigente` antes de qualquer apuracao — nenhum calculo roda sem o Selo (PA-04).

## 9. Vedacoes especificas

- **PA-02** — nao iniciar apuracao sem regime, CNAE, receita e competencia reais; o que faltar fica `[INFORMAR]`.
- **PA-05** — concluir a triagem sem municipio e UF deixa ISS/ICMS sem eixo — campo obrigatorio.
- **PA-09** — nao coletar nem registrar CPF/CNPJ de cliente real se o workspace estiver em pasta sincronizada; nunca misturar dados de clientes diferentes no mesmo `CASO.md`.
- **PA-13** — nao confundir regime tributario com obrigacao acessoria; nao confundir competencia com caixa.
- **PA-16** — demanda de litigio judicial → registrar e sinalizar "encaminhar a advogado" (slot generico).
- Nao supor sujeito, frente ou regime — perguntar; registrar `[INFORMAR]` se incerto.

## 10. Protocolos acionados

- **P5 — Localizacao** — a captura de municipio + UF e o ponto de origem do eixo geografico de todo o caso.
- **P1 — Validacao Legal Previa** — acionar `validador-legislacao-vigente` logo apos a triagem, antes de qualquer calculo.
- **P2 — Ingestao de Arquivos** — quando houver arquivos, rotear para as skills de ingestao do Tier 1.

## 11. Localizacao

A localizacao e a terceira classificacao da triagem e a mais sensivel. Esta skill **captura** municipio + UF do cliente e os grava no `CASO.md`, podendo **sobrescrever** a localizacao-sede do escritorio (persona) quando o cliente atua em outra praca. A partir daqui, `validador-legislacao-vigente` sabe qual RICMS (UF) e qual lei municipal de ISS validar, e toda apuracao de ISS/ICMS usa o ente correto (PA-05).

## 12. Integracao

**Chamada por:** `auditoria-contabil-master`, `/caso-contabil`, operador direto.

**Entrega para:** `CASO.md` (gravacao das 3 classificacoes + marcos) e as skills de Tier 1-9 via roteamento. A entrega final de qualquer caso passa por `revisao-final` (R1-R4).

**Sem esta skill:** as skills de apuracao operam sem sujeito, frente nem localizacao — analise inadequada e risco de aplicar a regra do ente errado.
