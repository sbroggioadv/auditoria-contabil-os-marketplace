---
name: dirf
description: >
  Skill de transicao/legado da DIRF. A DIRF foi EXTINTA para fatos geradores a
  partir de 2024 (IN RFB 2.060/2021) — absorvida pelos eventos R-4010/R-4020 da
  EFD-Reinf e pela DCTFWeb. Esta skill cobre apenas o legado: retificacao de
  DIRF de anos-calendario ate 2023, fiscalizacao e malha de periodos anteriores,
  regularizacao retroativa e emissao de comprovante de rendimentos do periodo.
  Para fatos geradores a partir de 2024, redireciona para `efd-reinf` e
  `dctfweb`. Aciona: retificar DIRF de ano <= 2023, codigo 0561/1708/3208/5952,
  Quadro 12 plano de saude, comprovante de rendimentos retroativo, pendencia de
  DIRF antiga, migracao DIRF para EFD-Reinf.
---

# DIRF — OBRIGACAO LEGADO

> Skill **Tier 3** — obrigacao acessoria **legado**. A DIRF foi extinta para
> fatos geradores a partir de 2024 (`[VERIFICAR]` o ano exato de corte na
> legislacao vigente). Esta skill atua so no periodo anterior — retificacao,
> malha e regularizacao de anos-calendario ate 2023. Exige o Selo de Validacao
> Legal Previa (P1) e e datada pelo ano-calendario do fato gerador. O plugin
> **prepara**; a transmissao e a responsabilidade tecnica sao do contador com
> CRC ativo (PA-07, PA-08).

---

## 0. Escopo e acionamento

A DIRF **deixou de existir** para fatos geradores a partir de 2024
(`[VERIFICAR]` o ano de corte — IN RFB 2.060/2021). As informacoes de
rendimentos e retencoes na fonte migraram para a EFD-Reinf (eventos R-4010 e
R-4020) e para a DCTFWeb.

Esta skill **so trata o legado**. Acionada por `auditoria-contabil-master`,
`triagem-contabil` ou diretamente com "retificar DIRF de [ano <= 2023]",
"pendencia de DIRF antiga", "DIRF na malha", "comprovante de rendimentos
retroativo", "Quadro 12 plano de saude". Use-a quando o fato gerador for de
ano-calendario **ate 2023**. Para fato gerador **a partir de 2024**, esta skill
**nao se aplica** — redireciona para `efd-reinf` (R-4010/R-4020/R-4099) e
`dctfweb`.

Entrada: ano-calendario (<= 2023), CNPJ, se e retificacao ou original atrasada,
levantamento de IRRF/CSRF retidos no ano, plano de saude com dependentes.
Entrega: DIRF retificadora/original do ano antigo, comprovante de rendimentos do
periodo, ou — se o ano for >= 2024 — encaminhamento para `efd-reinf` + `dctfweb`.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.
- **Aciona antes:** `validador-legislacao-vigente` (P1) — confirmar o ano de
  corte da extincao e o regulamento da DIRF do ano antigo; sem o Selo a
  preparacao nao comeca (PA-04).
- **Apoia-se em:** `irrf-folha` (IRRF retido sobre folha/pro-labore do ano),
  `retencoes-tomador` (IRRF/CSRF de NFs de servico do ano).
- **Entrega para:** `efd-reinf` e `dctfweb` quando o fato gerador for >= 2024
  (substituicao); `revisao-final` (R1-R4) e o `CASO.md` no caso legado.

## 2. Status — extincao e substituicao

```
ANO-CALENDARIO <= 2023   DIRF tradicional via PGD — esta skill atua
ANO-CALENDARIO >= 2024   EXTINTA — substituida por:
                         R-4010 (pagamentos a PF) — EFD-Reinf
                         R-4020 (pagamentos a PJ) — EFD-Reinf
                         R-4099 (fechamento) — EFD-Reinf
                         debitos confessados na DCTFWeb
```

`[VERIFICAR]` o ano-calendario exato de corte e o cronograma de transicao na
legislacao vigente — IN RFB 2.060/2021 e atualizacoes. A regra-mae da
substituicao deve ser confirmada pelo `validador-legislacao-vigente` antes de
qualquer trabalho (PA-03, PA-06).

## 3. Codigos de natureza (legado DIRF)

```
0561  trabalho assalariado / pro-labore / 13o
0588  servicos profissionais a PF (autonomo)
1708  servicos profissionais a PJ
3208  aluguel pago a PF / juros pagos a PF
5952  CSRF (PIS+COFINS+CSLL)
0473  JCP
5706  IRRF sobre rendimentos pagos ao exterior
```

A EFD-Reinf (R-4010/R-4020) usa a mesma tabela de codigos de natureza — o que
muda e o veiculo da declaracao, nao a classificacao do rendimento.

## 4. DIRF retificadora ou original atrasada (anos <= 2023)

Quando aparece pendencia de DIRF de ano antigo, levantar:

- IRRF retido em folha de cada mes do ano (cod 0561).
- IRRF/CSRF de NFs de servico (1708, 5952).
- IRRF de aluguel pago a PF (3208) e de autonomo PF (0588).
- Plano de saude — **Quadro 12**: dependentes informados e valor anual
  reembolsado por beneficiario.
- Pagamentos ao exterior (5706).

O prazo da DIRF era o ultimo dia util de fevereiro do ano seguinte; o
comprovante de rendimentos era entregue a cada beneficiario ate 28/02.
`[VERIFICAR]` o prazo, a multa por atraso e o piso do ano (PA-06, PA-11).

## 5. Validacao no PGD DIRF (ano legado)

O programa validador da DIRF aponta, em regra: CPF invalido, soma mensal
diferente do total anual, beneficiario sem ao menos um mes de rendimento, plano
de saude com dependente sem CPF. Corrigir antes de transmitir.

## 6. Comprovante de rendimentos (ano legado)

O comprovante de rendimentos pagos e de imposto retido na fonte do ano antigo
identifica: beneficiario e CPF, pagador e CNPJ, rendimentos tributaveis (cod
0561), rendimentos isentos, IRRF retido, INSS pago, pensao alimenticia paga e os
dependentes do plano de saude com CPF e valor. Sem detalhar os dependentes do
plano, o beneficiario nao consegue deduzir no IRPF do periodo.

## 7. Fato gerador a partir de 2024 — redirecionamento

Se o caso for de ano-calendario **>= 2024**, esta skill **nao prepara DIRF**.
O fluxo correto:

1. **Pagamentos a PF com IRRF** — evento **R-4010** da EFD-Reinf (mensal, em
   regra ate o dia 15 do mes seguinte) — ver `efd-reinf`.
2. **Pagamentos a PJ com IRRF/CSRF** — evento **R-4020** da EFD-Reinf — ver
   `efd-reinf`.
3. **Fechamento da serie R-4000** — evento **R-4099** — ver `efd-reinf`.
4. **Confissao dos debitos federais** — `dctfweb`.

A skill devolve esse roteiro e encerra; nao gera arquivo de DIRF para ano
posterior ao corte.

## 8. Anti-padroes

- Preparar DIRF para fato gerador a partir de 2024 — a obrigacao foi extinta;
  usar `efd-reinf` + `dctfweb`.
- Manter a DIRF junto da EFD-Reinf no mesmo ano — dupla declaracao.
- Nao bater a soma do IRRF retido com a DCTF/DCTFWeb do periodo.
- Esquecer o informe de dependentes do plano de saude — o beneficiario perde a
  deducao no IRPF.
- Comprovante sem detalhar os dependentes informados.
- Cravar o ano de corte, o prazo ou a multa de memoria — `[VERIFICAR]`.

## 9. Casos de borda

- **Multiplos vinculos:** cada pagador entrega sua propria declaracao do ano.
- **Pagamento a residente no exterior:** cod 5706, regime proprio.
- **Pagamento a falecido:** ate a data do obito; depois, ao espolio (CPF do
  espolio).
- **DIRF de espolio / encerramento de PJ:** regime proprio no ano legado.
- **Fiscalizacao de periodo antigo:** a DIRF retificada e a fonte; demanda
  judicial e `encaminhar a advogado` (PA-16).

## 10. Vedacoes especificas

- **PA-01** — nao orientar omissao de rendimento nem retencao a menor.
- **PA-02** — preparar so com dado real do ano (IRRF retido, NFs, plano de saude).
- **PA-03** — datar pelo ano-calendario do fato gerador; o ano define DIRF
  (<= 2023) ou EFD-Reinf (>= 2024).
- **PA-04** — sem o Selo de Validacao Legal Previa, a preparacao nao comeca.
- **PA-06** — `[VERIFICAR]` no ano exato de corte, no prazo, na multa e no piso.
- **PA-07** — a saida e rascunho operacional; a responsabilidade tecnica e do
  contador com CRC ativo.
- **PA-08** — a skill prepara; nao transmite a DIRF nem assina.
- **PA-11** — citar a norma com artigo (IN RFB 2.060/2021; RIR/2018).
- **PA-13** — nao confundir a obrigacao acessoria (DIRF/EFD-Reinf) com a
  apuracao do IRRF.
- **PA-16** — fiscalizacao com desdobramento judicial e `encaminhar a advogado`.
- **PA-18** — sinalizar a decadencia de 5 anos (CTN art. 173) sobre o periodo
  legado e os prazos da migracao.

## 11. Protocolos acionados

- **P1 — Validacao Legal Previa** — Selo emitido por `validador-legislacao-vigente`,
  confirmando o ano de corte e o regulamento do ano legado.
- **P3 — Calculo** — soma anual de IRRF/CSRF como memoria rastreavel.
- **P4 — Cruzamento e Conciliacao** — DIRF/comprovante x DCTF/DCTFWeb do periodo;
  soma mensal x total anual.
- **P6 — Auditoria de Qualidade** — `revisao-final` R1-R4 antes da entrega.

## 12. Localizacao

A DIRF era obrigacao **federal** — regras valiam em todo o pais e nao variavam
por municipio ou UF. O eixo geografico nao incide diretamente; quando uma regra
acessoria nao puder ser confirmada, marcar `[VERIFICAR]` (PA-06).

## 13. Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.

**Entrega para:** no caso legado (ano <= 2023), `revisao-final` (R1-R4) e o
`CASO.md`; no caso de fato gerador a partir de 2024, **redireciona** para
`efd-reinf` (R-4010/R-4020/R-4099) e `dctfweb`. O IRRF de folha vem de
`irrf-folha`; o IRRF/CSRF de servicos tomados vem de `retencoes-tomador`. A
malha de PF de periodo antigo e tratada na frente de pessoa fisica (Tier futuro).

**Sem esta skill:** uma pendencia de DIRF de ano antigo e tratada sem checklist
de retificacao, e ha risco de preparar DIRF para ano em que ela ja nao existe.
