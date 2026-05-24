---
name: dmed
description: >
  Preparacao e conferencia da DMED — declaracao anual de prestadores de servicos
  de saude (hospitais, clinicas, laboratorios, medicos PJ) e de operadoras de
  plano de saude. E o espelho da deducao de saude do paciente no IRPF —
  divergencia gera malha fina. Conhece as operacoes (01 prestador, 02 operadora),
  a validacao no PGD, a exigencia de CPF do paciente e os requisitos do recibo
  medico. Base: IN RFB 985/2009, IN RFB 1.228/2011, RIR/2018 art. 73. Aciona:
  preparar DMED, cliente medico/hospital/operadora, PGD DMED, recibo medico com
  CPF, contribuicoes e reembolsos de plano de saude.
---

# DMED

> Skill **Tier 3** — obrigacao acessoria federal anual do setor de saude.
> Prepara e confere a DMED: declara pagamentos recebidos por servicos de saude.
> A DMED e o **espelho** da deducao de saude no IRPF do paciente — divergencia
> atrai malha fina. Exige o Selo de Validacao Legal Previa (P1) e e datada pelo
> ano-calendario do fato gerador. O plugin **prepara**; a transmissao e a
> responsabilidade tecnica sao do contador com CRC ativo (PA-07, PA-08).

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com
"preparar DMED", "cliente medico", "cliente hospital", "operadora de plano de
saude", "PGD DMED", "recibo medico com CPF", "contribuicoes e reembolsos de
plano". Entrada: ano-calendario, CNPJ, tipo (prestador ou operadora), exportacao
do sistema de gestao com pacientes pagantes (CPF + valor anual), contribuicoes e
reembolsos no caso de operadora, verificacao amostral de recibos com CPF.
Entrega: lista consolidada de pagamentos por beneficiario, diagnostico para o
PGD, checklist de validacao, alerta ao cliente sobre o CPF nos recibos.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.
- **Aciona antes:** `validador-legislacao-vigente` (P1) — o leiaute do PGD DMED e
  o prazo mudam por ano; sem o Selo a preparacao nao comeca (PA-04).
- **Apoia-se em:** `analise-extratos-ofx-csv` (conferencia do CSV exportado do
  sistema de gestao do prestador/operadora).
- **Entrega para:** `revisao-final` (R1-R4) e o `CASO.md`.

## 2. Operacoes da DMED

```
01  Prestador  hospital, clinica, laboratorio, medico PJ — declara o que
                recebeu de PF particular (pagamento direto do paciente)
02  Operadora  plano de saude, seguro saude — contribuicoes recebidas dos
                titulares + reembolsos pagos por procedimento
```

Estao obrigados, em regra, os prestadores de servico de saude pessoas juridicas
e as operadoras de plano de saude. O prazo era, em regra, o ultimo dia util de
fevereiro do ano seguinte — `[VERIFICAR]` o prazo, a multa e o piso do ano
(IN RFB 985/2009, IN RFB 1.228/2011; PA-06, PA-11).

## 3. Prestador — Operacao 01

- Declara **apenas** os valores recebidos da PF diretamente (pagamento
  particular).
- **Excluir** os pacientes que pagaram com plano de saude — esses valores vao na
  DMED da **operadora**, nao na do prestador. Lancar o paciente do plano na DMED
  do prestador gera duplicidade.
- Cada lancamento: CPF do titular do pagamento + valor anual.

## 4. Operadora — Operacao 02

- Contribuicoes mensais por titular do contrato.
- Reembolsos pagos por procedimento, com o CPF do beneficiario — mesmo quando o
  beneficiario for dependente do titular.

## 5. Recibo medico valido (orientacao ao prestador)

Para o paciente conseguir deduzir a despesa de saude no IRPF, o recibo precisa
de: **CPF do paciente** (nao basta o CPF do titular do contrato), valor pago e
data, identificacao do profissional (registro no conselho de classe) ou CNPJ do
prestador, e assinatura. Recibo sem o CPF do paciente nao sustenta a deducao.

## 6. Entregavel — lista consolidada

```
DMED — ANO ____ — CNPJ ____ — Prestador / Operadora

Beneficiario            CPF                 Valor anual
__________              ___.___.___-__      R$ ______
... (lista completa)

Total: R$ ______
```

A partir da lista, o contador gera o arquivo para o PGD DMED (extraido do
sistema e ajustado) e transmite (PA-08).

## 7. Conferencia e cruzamento (P4)

- Lista de pagamentos de PF do ano coletada e CPFs validados.
- Prestador: pacientes do plano **excluidos** da Operacao 01.
- Operadora: contribuicoes e reembolsos incluidos; dependentes vinculados ao
  titular.
- Validador do PGD com zero erros.
- Verificacao amostral: recibos com o CPF do paciente.
- **Cruzamento:** a DMED e o espelho da deducao de saude do paciente no IRPF
  (RIR/2018, art. 73) — valor incompativel entre o que a empresa declara e o que
  o paciente deduz atrai a malha fina do paciente.

## 8. Alerta obrigatorio ao cliente

Quando houver pacientes recorrentes sem CPF no recibo, alertar o cliente: a
Receita nao aceita a deducao de saude sem o CPF do paciente — recomendar a
exigencia do CPF em todo recibo como politica do estabelecimento, sob pena de o
paciente nao conseguir deduzir no IRPF.

## 9. Anti-padroes

- Lancar pacientes que pagaram com plano na DMED do prestador — eles vao so na
  DMED da operadora.
- Trocar o CPF do titular pelo CPF do dependente — o IRPF acusa malha por valor
  incompativel.
- A operadora esquecer os reembolsos pagos por procedimento.
- Tratar o medico autonomo PF (sem CNPJ) como obrigado a DMED — ele e
  dispensado; os tomadores PJ que pagaram a ele e que declaram (EFD-Reinf/DIRF).
- Cravar prazo, multa ou leiaute de memoria — `[VERIFICAR]`.

## 10. Casos de borda

- **Medico que atende particular e plano:** a DMED da PJ cobre so os
  particulares; a operadora declara os pacientes do plano pelo CPF do
  beneficiario.
- **Cooperativa de trabalho medico:** DMED propria + repasse aos cooperados;
  cada cooperado que atende particular pode ter sua propria DMED.
- **Servico de saude estetico:** segue sendo DMED — qualquer servico de saude
  entra.
- **Paciente que cair na malha:** o diagnostico da malha de PF e da frente de
  pessoa fisica (Tier futuro); a DMED corrigida e a fonte para reconciliar.

## 11. Vedacoes especificas

- **PA-01** — nao orientar omissao de pagamento recebido nem valor a menor.
- **PA-02** — preparar so com dado real (lista de pacientes pagantes do ano).
- **PA-03** — datar a DMED pelo ano-calendario do fato gerador.
- **PA-04** — sem o Selo de Validacao Legal Previa, a preparacao nao comeca.
- **PA-06** — `[VERIFICAR]` no prazo, na multa e no leiaute do PGD DMED.
- **PA-07** — a saida e rascunho operacional; a responsabilidade tecnica e do
  contador com CRC ativo.
- **PA-08** — a skill prepara e confere; nao transmite a DMED nem assina.
- **PA-09** — CPF e valores de saude sao dados sensiveis — compartimentados no
  caso, sem mistura de clientes (LGPD).
- **PA-11** — citar a norma com artigo (IN RFB 985/2009; IN RFB 1.228/2011;
  RIR/2018, art. 73).
- **PA-13** — nao confundir a obrigacao acessoria (DMED) com a apuracao de
  tributo do prestador de saude.
- **PA-18** — sinalizar o prazo de entrega da DMED.

## 12. Protocolos acionados

- **P1 — Validacao Legal Previa** — Selo emitido por `validador-legislacao-vigente`,
  com o leiaute do PGD DMED e o prazo do ano.
- **P2 — Ingestao** — conferencia do CSV exportado do sistema de gestao via
  `analise-extratos-ofx-csv`.
- **P4 — Cruzamento e Conciliacao** — DMED x deducao de saude do paciente no
  IRPF; prestador x operadora (sem duplicidade do mesmo paciente).
- **P6 — Auditoria de Qualidade** — `revisao-final` R1-R4 antes da entrega.

## 13. Localizacao

A DMED e obrigacao **federal** — leiaute, operacoes e prazo valem em todo o pais
e nao variam por municipio ou UF. O eixo geografico nao incide diretamente;
quando uma regra acessoria nao puder ser confirmada, marcar `[VERIFICAR]`
(PA-06).

## 14. Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.

**Entrega para:** `revisao-final` (R1-R4) e o `CASO.md`. O CSV do sistema de
gestao do prestador/operadora e conferido por `analise-extratos-ofx-csv`. A DMED
e o espelho da deducao de saude do paciente — a frente de pessoa fisica (Tier
futuro) usa a DMED para reconciliar a declaracao de IRPF e diagnosticar malha.

**Sem esta skill:** os pagamentos de saude sao declarados sem segregacao
prestador/operadora nem checklist de CPF — risco de duplicidade, malha fina do
paciente e multa por atraso.
