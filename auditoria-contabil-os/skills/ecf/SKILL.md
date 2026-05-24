---
name: ecf
description: >
  Preparacao e conferencia da ECF anual (Escrituracao Contabil Fiscal) — apuracao de
  IRPJ/CSLL, LALUR/LACS Parte A (adicoes e exclusoes) e Parte B (controle de prejuizo
  fiscal e base negativa), recuperacao da ECD e blocos M/N/P/Q/T. Base: IN RFB
  2.004/2021, IN RFB 1.700/2017, Lei 12.973/2014, Lei 14.789/2023. Aciona: preparar
  ECF, e-Lalur, LALUR Parte A/B, recuperar ECD, prejuizo fiscal compensado, adicoes e
  exclusoes, plano referencial fiscal, JCP, blocos M/N/P/Q, erro no PVA da ECF.
---

# ECF — ESCRITURACAO CONTABIL FISCAL

> Skill **Tier 3** — obrigacao acessoria que consolida a apuracao de IRPJ/CSLL do
> exercicio. Exige o Selo de Validacao Legal Previa (P1) e e datada pelo ano do fato
> gerador. O plugin **prepara**; a transmissao e a responsabilidade tecnica sao do
> contador com CRC ativo (PA-07, PA-08).

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com
"preparar ECF", "e-Lalur", "LALUR Parte A", "recuperar ECD", "prejuizo fiscal
compensado", "adicoes e exclusoes". Entrada: ano-calendario, CNPJ, regime (Real
trimestral, Real anual, Presumido), ECD transmitida e autenticada, saldo da Parte B
(prejuizo fiscal e base negativa CSLL), adicoes/exclusoes levantadas, DARFs de IRPJ/CSLL
pagos. Entrega: checklist de pre-validacao, LALUR Parte A pronto, Parte B atualizada,
cruzamento ECF × ECD × EFD-Contribuicoes × DCTFWeb.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.
- **Aciona antes:** `validador-legislacao-vigente` (P1) — leiaute e Manual da ECF mudam
  por ano; sem o Selo a preparacao nao comeca (PA-04).
- **Pre-requisito absoluto:** `ecd` — sem ECD validada e autenticada, a ECF nao
  recupera dados.
- **Apoia-se em:** `apuracao-lucro-real` e `apuracao-lucro-presumido` (a apuracao de
  IRPJ/CSLL que a ECF consolida) e `leitura-arquivos-sped`.
- **Entrega para:** `revisao-final` (R1-R4) e o `CASO.md`.

## 2. Estrutura da ECF — blocos criticos

```
0  Identificacao do contribuinte
C  Recuperacao da ECD (botao "Recuperar ECD" no PVA)
E  Lancamentos da ECD recuperados
J  Plano de contas referencial
K  Saldos das contas referenciais
L  Lucro Liquido do periodo
M  e-Lalur / e-Lacs: M300 adicoes (M310 detalhamento), M350/M360 exclusoes
N  Calculo de IRPJ/CSLL — Real trimestral (N500-N635), Real anual (N640-N670)
P  Demonstracoes do Lucro Real     Q  Demonstracoes do Lucro Presumido
T  Lucros e dividendos pagos       U  SCP
W  Declaracao Pais-a-Pais          X  Operacoes com o exterior
Y  Informacoes gerais (creditos fiscais, P&D)     9  Encerramento
```

**Prazo de entrega:** ate o ultimo dia util de julho do ano seguinte ao do fato gerador
— `[VERIFICAR]` o prazo do ano (IN RFB 2.004/2021 e atualizacoes). Multa por atraso
conforme IN RFB vigente — `[VERIFICAR]` percentual e piso. A ECF e devida pelas PJ em
geral (Real, Presumido e imunes/isentas), nas hipoteses da IN — `[VERIFICAR]`.

## 3. Pre-requisito — ECD recuperada

Sem ECD validada e autenticada, a ECF nao recupera dados. No PVA da ECF, o botao
"Recuperar ECD" importa plano de contas, balancetes, lancamentos, BP e DRE. Conferir
que a recuperacao ocorreu sem erros antes de seguir. ECD pendente → acionar `ecd`.

## 4. LALUR Parte A — adicoes e exclusoes (blocos M300/M350)

A apuracao parte do **lucro liquido contabil** (LAIR) e o ajusta:

| Adicoes (despesas indedutiveis a somar) | Fundamento |
|------------------------------------------|------------|
| Multas punitivas | RIR/2018 |
| Provisoes nao autorizadas (exceto ferias, 13o, perdas dedutiveis) | Lei 9.430/96 |
| Equivalencia patrimonial negativa | Lei 12.973/2014 |
| Doacoes sem incentivo / brindes | RIR/2018 |
| Despesas indedutiveis com socios/administradores | RIR/2018 |
| JCP que excede o limite legal | Lei 9.249/1995, art. 9o |
| Ajustes de preco de transferencia | Lei 14.596/2023 |

| Exclusoes (a subtrair do lucro) | Fundamento |
|----------------------------------|------------|
| Reversao de provisoes antes adicionadas | Lei 12.973/2014 |
| Equivalencia patrimonial positiva (controlada no Brasil) | Lei 12.973/2014 |
| Dividendos recebidos PJ → PJ no Brasil | Lei 9.249/1995, art. 10 |

O LACS (CSLL) tem logica analoga, com diferencas pontuais de base.

## 5. Parte B — controle de prejuizo fiscal

O prejuizo fiscal e a base negativa de CSLL ficam estocados na Parte B por ano de
origem. Na compensacao, o limite anual e **30% do lucro liquido ajustado** (apos
adicoes/exclusoes) — Lei 8.981/1995, art. 42; Lei 9.065/1995. Cada compensacao reduz
o saldo da Parte B; o saldo nunca pode ficar negativo.

## 6. Calculo de IRPJ/CSLL (bloco N)

- **Real anual:** lucro real do ano com as estimativas mensais ja recolhidas vinculadas.
- **Real trimestral:** quatro trimestres apurados separadamente.
- **Presumido:** apuracao por percentual de presuncao (ver `apuracao-lucro-presumido`),
  refletida no bloco Q.

O calculo detalhado de IRPJ/CSLL e das apuracoes do Tier 2; a ECF consolida o resultado.

## 7. Conferencia antes do PVA (P4)

- ECD do ano transmitida e autenticada; recuperacao sem erros.
- Plano de contas 100% mapeado ao referencial fiscal.
- Adicoes e exclusoes com fundamento legal (lei + artigo).
- Compensacao de prejuizo dentro do limite de 30%.
- Parte B atualizada, com saldo por ano de origem.
- DARFs de IRPJ/CSLL do ano lancados e vinculados.
- Cruzamento ECF × DCTFWeb × EFD-Contribuicoes × ECD sem divergencia.

Erros frequentes do PVA: conta sem referencial, divergencia da DRE recuperada vs
balancete, prejuizo acima de 30%, receita da ECF ≠ EFD-Contribuicoes (alerta de malha).

## 8. Anti-padroes

- Iniciar a ECF sem recuperar a ECD.
- Conta contabil sem codigo referencial.
- Compensar prejuizo fiscal acima de 30% do lucro ajustado.
- Parte B com saldo negativo (impossivel).
- Divergencia de receita entre ECF e EFD-Contribuicoes.
- JCP excedente ao limite legal nao adicionado.
- Tratar subvencao para investimento pela sistematica antiga — a Lei 14.789/2023
  alterou o regime; `[VERIFICAR]` a regra vigente no ano do fato gerador.
- Cravar prazo, multa ou regra de subvencao de memoria — `[VERIFICAR]`.

## 9. Casos de borda

- **Partes relacionadas no exterior:** blocos W e X; preco de transferencia pela
  Lei 14.596/2023 (alinhamento OCDE).
- **PJ com mais de um regime no ano** (ex.: Presumido virou Real): a ECF reflete a
  apuracao de cada periodo.
- **Empresa em recuperacao judicial:** a ECF continua devida.
- **Subvencao para investimento:** regime alterado pela Lei 14.789/2023 — confirmar
  o tratamento (credito fiscal) vigente no ano (PA-03).

## 10. Vedacoes especificas

- **PA-02** — preparar so com dado real (ECD recuperada, adicoes/exclusoes, DARFs).
- **PA-03** — datar a ECF pelo ano do fato gerador; leiaute, Manual e regras de
  subvencao mudam por ano.
- **PA-04** — sem o Selo de Validacao Legal Previa, a preparacao nao comeca.
- **PA-06** — `[VERIFICAR]` no prazo, na multa, na obrigatoriedade e no regime da
  subvencao para investimento.
- **PA-07** — a saida e rascunho operacional; a responsabilidade tecnica e do contador
  com CRC ativo.
- **PA-08** — a skill prepara e confere; nao transmite nem assina a ECF.
- **PA-11** — citar a norma com artigo (IN RFB 2.004/2021; IN RFB 1.700/2017;
  Lei 12.973/2014; Lei 14.789/2023; Lei 8.981/1995, art. 42).
- **PA-13** — nao confundir a apuracao de IRPJ/CSLL (Tier 2) com a obrigacao acessoria
  ECF, que apenas a consolida.

## 11. Protocolos acionados

- **P1 — Validacao Legal Previa** — Selo emitido por `validador-legislacao-vigente`,
  com a IN e o Manual da ECF do ano.
- **P2 — Ingestao** — recuperacao da ECD e leitura de arquivos via `leitura-arquivos-sped`.
- **P4 — Cruzamento e Conciliacao** — ECF × ECD × EFD-Contribuicoes × DCTFWeb; toda
  divergencia apontada; em recuperacao, retificar antes de compensar (PA-14).
- **P6 — Auditoria de Qualidade** — `revisao-final` R1-R4 antes da entrega.

## 12. Localizacao

A ECF e obrigacao **federal** — leiaute, prazo e regras de IRPJ/CSLL valem em todo o
pais e nao variam por municipio ou UF. Quando uma regra de transicao ou de obrigacao
acessoria correlata depender de norma nao confirmada, marcar `[VERIFICAR]` (PA-06).

## 13. Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.

**Entrega para:** `revisao-final` (R1-R4) e o `CASO.md`. Tem `ecd` como pre-requisito
absoluto (a ECF recupera a ECD). As apuracoes de IRPJ/CSLL vem de `apuracao-lucro-real`
e `apuracao-lucro-presumido`; o cruzamento de divergencia detalhado e trabalho de
auditoria (Tier 7, v0.3). Quando a demanda for tese ou litigio judicial sobre o
resultado fiscal, encaminhar a advogado (PA-16).

**Sem esta skill:** a ECF e montada sem amarracao com a ECD nem checklist do LALUR —
risco de bloqueio no PVA, compensacao indevida de prejuizo e divergencia de malha.
