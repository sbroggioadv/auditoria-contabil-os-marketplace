---
name: efd-reinf
description: >
  Preparacao e conferencia da EFD-Reinf — eventos R-1000 (cadastro), R-2010/R-2020
  (retencao de INSS 11% sobre cessao de mao de obra), R-2050/R-2055 (rural), R-2099
  (fechamento periodico), R-4010/R-4020 (IRRF de PF e PJ, em substituicao a DIRF) e
  R-4099. Alimenta a geracao da DCTFWeb. Base: IN RFB 2.043/2021, IN RFB 2.060/2021,
  leiaute EFD-Reinf vigente. Aciona: preparar EFD-Reinf, eventos R-1000/R-2010/R-2099,
  R-4010/R-4020, retencao 11%, substituicao da DIRF, fechamento de competencia.
---

# EFD-REINF

> Skill **Tier 3** — obrigacao acessoria federal. Prepara e confere os eventos da
> EFD-Reinf: retencoes na fonte e pagamentos sujeitos a IRRF. Exige o Selo de Validacao
> Legal Previa (P1) e e datada pelo ano do fato gerador. O plugin **prepara**; a
> transmissao e a responsabilidade tecnica sao do contador com CRC ativo (PA-07, PA-08).

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com
"preparar EFD-Reinf", "evento R-1000", "R-2010", "R-2099", "R-4010", "retencao 11%",
"substituicao da DIRF", "fechar a competencia". Entrada: CNPJ, competencia, R-1000 do
ano, servicos tomados com retencao de INSS, pagamentos a PF/PJ com IRRF/CSRF, atividade
rural, opcao por CPRB, status do fechamento do eSocial. Entrega: sequencia de eventos
a transmitir, confirmacao de R-2099/R-4099, cruzamento com a DCTFWeb.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.
- **Aciona antes:** `validador-legislacao-vigente` (P1) — o leiaute da EFD-Reinf muda
  por versao; sem o Selo a preparacao nao comeca (PA-04).
- **Apoia-se em:** `retencoes-tomador` (lado do tomador — INSS 11%, IRRF, CSRF),
  `irrf-folha` (IRRF de pagamentos a PF).
- **Entrega para:** `dctfweb` (a EFD-Reinf alimenta a DCTFWeb), `revisao-final` (R1-R4)
  e o `CASO.md`.

## 2. Estrutura da EFD-Reinf — eventos

```
CADASTRAIS / TABELAS
R-1000 contribuinte (ano de inicio)   R-1050 comissoes   R-1070 processos

PERIODICOS (mensais — fecham no R-2099)
R-2010 retencao de INSS 11% sobre servico tomado com cessao de MO
R-2020 idem, lado prestador (espelho do R-2010)
R-2030/R-2040 recursos de/para associacao desportiva
R-2050 comercializacao de producao rural por PJ
R-2055 aquisicao de producao rural
R-2060 apuracao da CPRB
R-2098 reabertura      R-2099 FECHAMENTO PERIODICO

NAO PERIODICOS — substituem a DIRF (fatos geradores 2024+)
R-4010 pagamentos a PF (IRRF)
R-4020 pagamentos a PJ (IRRF, CSRF)
R-4040 beneficiario nao identificado
R-4080 retencao sofrida no recebimento
R-4099 FECHAMENTO da serie R-4000
```

**Prazo de entrega:** em regra ate o dia 15 do mes seguinte ao do fato gerador, para
os periodicos e o R-2099 — `[VERIFICAR]` o prazo do ano (IN RFB 2.043/2021).

## 3. Sequencia mensal de fechamento

1. Confirmar o R-1000 do ano em vigor; atualizar se houve mudanca cadastral.
2. R-1050 / R-1070, se aplicavel.
3. R-2010 — um evento por NF de servico tomado com retencao de INSS (cessao de MO).
4. R-2020 — lado prestador (espelho), se aplicavel.
5. R-2050 / R-2055 — atividade rural, se aplicavel.
6. R-2060 — CPRB, se a empresa optou e a desoneracao ainda vigorar (`[VERIFICAR]`).
7. R-4010 — pagamentos a PF com IRRF (aluguel a PF, RPA, autonomo).
8. R-4020 — pagamentos a PJ com IRRF/CSRF retidos.
9. **R-2099** — fecha os eventos periodicos.
10. **R-4099** — fecha a serie R-4000.
11. A DCTFWeb e gerada a partir dos fechamentos — ver `dctfweb`.

## 4. R-2010 — retencao de INSS 11% (cessao de mao de obra)

O R-2010 informa, por NF de servico tomado em cessao de MO: valor bruto, base de
retencao e o valor retido (em regra 11% — Lei 8.212/1991, art. 31). A retencao de INSS
incide **apenas** sobre cessao de mao de obra ou empreitada; servico comum nao gera
retencao. O `tpInsc` distingue CNPJ (1) de CPF (2).

## 5. Substituicao da DIRF (fatos geradores 2024+)

A DIRF foi extinta para fatos geradores a partir de 2024 (IN RFB 2.060/2021). As
informacoes de rendimentos e retencoes na fonte passaram para a EFD-Reinf:
- **R-4010:** pagamentos a PF com IRRF.
- **R-4020:** pagamentos a PJ com IRRF/CSRF retidos.
- **R-4080:** retencao sofrida no recebimento (a empresa e prestadora e o cliente PJ
  reteve).
- **R-4099:** fechamento da serie.

`[VERIFICAR]` o status e o ano de corte da migracao DIRF → EFD-Reinf na legislacao
vigente, e a articulacao da skill `dirf` no Tier 3 do plugin.

## 6. Conferencia e cruzamento (P4)

- R-1000 do ano transmitido e em vigor.
- Eventos R-2010/R-2020 para todos os tomadores/prestadores com retencao de INSS.
- R-4010/R-4020 para todos os pagamentos a PF e PJ com retencao na fonte.
- R-2099 e R-4099 fechados, com recibo.
- **Cruzamento com a DCTFWeb:** o INSS retido (R-2010/R-2020) e o IRRF (R-4010/R-4020)
  devem aparecer na DCTFWeb.
- Comprovantes de retencao entregues aos prestadores (eles precisam para a propria
  escrituracao).

## 7. Anti-padroes

- Nao fechar o R-2099 — a DCTFWeb nao e gerada e o debito nao e constituido.
- Enviar R-2010 sem o R-1000 do contribuinte.
- Esquecer o R-2055 (aquisicao de producao rural por PJ) — risco de glosa de credito
  presumido.
- Confundir o `tpInsc` (1 = CNPJ, 2 = CPF).
- Reter INSS 11% de prestador sem cessao de mao de obra — so a cessao gera retencao.
- Manter a DIRF para fatos geradores 2024+ junto da EFD-Reinf — dupla declaracao.
- Reabrir com R-2098 apos a DCTFWeb transmitida sem retificar a DCTFWeb.
- Cravar prazo ou versao do leiaute de memoria — `[VERIFICAR]`.

## 8. Casos de borda

- **Aluguel pago a PF mensalmente:** um R-4010 a cada pagamento.
- **Atividade rural agroindustrial:** R-2050 (comercializacao) + R-2055 (aquisicao).
- **Cooperativa de trabalho:** a contribuicao de INSS 15% sobre nota de cooperativa
  foi afastada pelo STF (RE 595.838) — nao se envia esse evento.
- **Pagamento a PJ no exterior** (royalties, juros, dividendos): R-4020 com regime
  proprio de IRRF — `[VERIFICAR]` a aliquota e o tratado.
- **Empresa do Simples sem cessao de MO:** sem CSRF e sem retencao de INSS — o R-4020
  e o R-2010 nao se aplicam aquela operacao.

## 9. Vedacoes especificas

- **PA-01** — nao orientar omissao de evento nem retencao a menor para reduzir debito.
- **PA-02** — preparar so com dado real (NFs com retencao, pagamentos do mes).
- **PA-03** — datar a competencia pelo ano do fato gerador; o corte DIRF → Reinf e
  por ano.
- **PA-04** — sem o Selo de Validacao Legal Previa, a preparacao nao comeca.
- **PA-06** — `[VERIFICAR]` no prazo, na versao do leiaute, na vigencia da CPRB e no
  status da migracao da DIRF.
- **PA-07** — a saida e rascunho operacional; a responsabilidade tecnica e do contador
  com CRC ativo.
- **PA-08** — a skill prepara e confere os eventos; nao transmite a EFD-Reinf nem
  recolhe a DCTFWeb.
- **PA-11** — citar a norma com artigo (IN RFB 2.043/2021; IN RFB 2.060/2021;
  Lei 8.212/1991, art. 31; RE 595.838/STF).
- **PA-13** — nao confundir a retencao na fonte (tema do tomador) com a obrigacao
  acessoria EFD-Reinf, que apenas a informa.

## 10. Protocolos acionados

- **P1 — Validacao Legal Previa** — Selo emitido por `validador-legislacao-vigente`,
  com o leiaute da EFD-Reinf do ano.
- **P2 — Ingestao** — NFs e comprovantes de retencao conferidos via `analise-xml-fiscal`.
- **P4 — Cruzamento e Conciliacao** — eventos da EFD-Reinf × DCTFWeb; em retificacao,
  ajustar a DCTFWeb na sequencia correta.
- **P6 — Auditoria de Qualidade** — `revisao-final` R1-R4 antes da entrega.

## 11. Localizacao

A EFD-Reinf e obrigacao **federal** — leiaute, eventos e prazo valem em todo o pais e
nao variam por municipio ou UF. O eixo geografico aparece de forma indireta no R-4010
(aluguel pago a PF, cujo imovel tem localizacao) e na obra de construcao civil
(`ideEstabObra`). Sem regra confirmada, marcar `[VERIFICAR]` (PA-06).

## 12. Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.

**Entrega para:** `dctfweb` (a EFD-Reinf, com o eSocial fechado, alimenta a geracao da
DCTFWeb), `revisao-final` (R1-R4) e o `CASO.md`. O lado do tomador (calculo das
retencoes) vem de `retencoes-tomador`; o IRRF dos pagamentos a PF vem de `irrf-folha`;
o status da DIRF e tratado pela skill `dirf`. A folha completa e do Tier 4 (v0.2).

**Sem esta skill:** os eventos de retencao nao sao fechados — a DCTFWeb nao e gerada,
o debito nao e constituido e ha risco de autuacao por declaracao em falta.
