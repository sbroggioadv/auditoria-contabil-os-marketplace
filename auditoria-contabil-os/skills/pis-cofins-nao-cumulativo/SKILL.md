---
name: pis-cofins-nao-cumulativo
description: >
  Apuracao mensal de PIS e COFINS no regime nao-cumulativo (Lucro Real) —
  debitos x creditos, identificacao ampla de creditos sob o conceito de insumo
  do Tema 779 STJ (essencial ou relevante), exclusao do ICMS da base e dos
  creditos (Tema 69, Lei 14.592/2023), receita financeira tributada (Decreto
  8.426/2015), manutencao de creditos da exportacao e credito presumido sobre
  estoque na migracao de regime. Calcula via Python, com memoria rastreavel,
  apuracao de saldo credor e DARFs. Base: Lei 10.637/02, Lei 10.833/03, IN RFB
  2.121/2022. Aciona: PIS COFINS nao-cumulativo, Lucro Real, Tema 779, creditos
  de insumo, exclusao do ICMS, saldo credor, DARF 6912 ou 5856.
---

# PIS / COFINS NAO-CUMULATIVO

> Skill **Tier 2** — apuracao mensal de PIS e COFINS no regime nao-cumulativo, tipico do Lucro Real. O regime e de debito x credito; o ponto critico e identificar **todos os creditos cabiveis** sob o conceito de insumo do Tema 779. Exige o Selo de Validacao Legal Previa (P1) e e datada pelo ano do fato gerador (PA-03). Atencao: a reforma tributaria extingue PIS e COFINS, substituidos pela CBS, na transicao 2026-2033.

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com "PIS COFINS nao-cumulativo", "Lucro Real", "Tema 779", "creditos de insumo", "exclusao do ICMS", "saldo credor", "DARF 6912", "DARF 5856". Entrada: CNPJ, competencia, receita bruta segregada (vendas, servicos, financeiras, locacao), ICMS destacado nas saidas, notas de entrada com PIS/COFINS destacado, despesas geradoras de credito (energia, aluguel PJ, depreciacao, frete, insumos), receitas de exportacao e monofasicas, saldo credor anterior. Entrega: apuracao debito x credito, analise de creditos por categoria, saldo credor, memoria de calculo, DARFs e checklist.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, `apuracao-lucro-real`, operador direto.
- **Aciona antes de calcular:** `validador-legislacao-vigente` (P1) — aliquotas, hipoteses de credito e o cronograma da reforma sao alvo movel; sem o Selo a apuracao nao comeca (PA-04).
- **Apoia-se em:** `analise-xml-fiscal` (notas de entrada — creditos), `leitura-arquivos-sped` (EFD-Contribuicoes — blocos M e F).
- **Entrega para:** `revisao-final` (R1-R4), o `CASO.md` e a `efd-contribuicoes` (Tier 3).

## 2. Aliquotas e codigos do regime nao-cumulativo

```
ALIQUOTAS (regime nao-cumulativo)
  PIS .... 1,65%
  COFINS . 7,60%
  Total debito ... 9,25% sobre a receita tributada

RECEITA FINANCEIRA (Decreto 8.426/2015)
  PIS .... 0,65%   COFINS . 4,00%   (nao e mais aliquota zero)

CODIGOS DARF
  PIS nao-cumulativo ..... 6912 (ou 8109 conforme o caso)
  COFINS nao-cumulativo .. 5856 (ou 2172 conforme o caso)
  Vencimento ............. dia 25 do mes seguinte
```

As aliquotas nominais sao estaveis no regime atual; a **vigencia do regime** e alvo movel — confirmar com o Selo (P1) se a competencia ja esta sob a CBS na transicao da reforma.

## 3. Debitos — base e exclusoes

```
Receita bruta tributavel
(-) ICMS destacado nas saidas .......... Tema 69 / Lei 14.592/2023
(-) Vendas canceladas e devolucoes
(-) Receitas de aliquota zero / monofasicas
(-) Receitas de exportacao ............. aliquota zero, mantem creditos
(=) Base do debito -> PIS 1,65% + COFINS 7,60%
(+) Receita financeira -> PIS 0,65% + COFINS 4,00%
```

A Lei 14.592/2023 exclui o ICMS destacado **tanto do debito quanto da base de creditos** — erro comum e excluir so do debito.

## 4. Creditos — conceito de insumo do Tema 779

O Tema 779 (STJ, REsp 1.221.170) firmou que **insumo e o bem ou servico essencial ou relevante** a atividade — nao basta "incorporar ao produto".

```
CREDITOS CLASSICOS
  materia-prima, embalagem, bens para revenda
  energia eletrica e termica
  aluguel de predios, maquinas e equipamentos de PJ
  arrendamento mercantil de PJ
  depreciacao do imobilizado de producao (1/12 ou 1/48)
  edificacao da atividade (1/300 ao mes)
  frete na operacao de venda

CREDITOS DEFENSAVEIS PELO TEMA 779
  vale-transporte e vale-refeicao quando obrigatorios
  EPI obrigatorio por NR
  fardamento contratual, treinamento tecnico essencial
  manutencao preventiva de maquinas, software essencial a producao
  frete entre estabelecimentos, combustiveis da frota da atividade

VEDADOS
  mao de obra de pessoa fisica (Lei 10.833 art. 3o, §2o, II)
  aquisicoes de optante do Simples (regra com excecoes — IN 2.121 art. 174)
  aquisicoes de aliquota zero, suspensao ou monofasicas (sem tributacao na origem)
```

Creditos do Tema 779 exigem **fundamentacao tecnica documentada** — util para defesa em fiscalizacao.

## 5. Exportacao e credito presumido sobre estoque

- **Manutencao de creditos da exportacao (Lei 10.833, art. 6o):** a receita de exportacao tem aliquota zero e **mantem os creditos** dos insumos; o saldo credor acumulado pode ser objeto de PER/DCOMP ou ressarcimento.
- **Credito presumido sobre estoque (Lei 10.637, art. 11):** empresa que migra do Presumido para o Real toma credito presumido sobre o estoque inicial (0,65% de PIS + 3% de COFINS = 3,65%). Frequentemente esquecido — sempre checar se houve migracao de regime.

## 6. Calculo via Python (P3)

```python
python3 -c "
def pis_cofins_nc(receita_trib, exclusoes, base_creditos, rec_financ=0, saldo_ant=0):
    base_db = receita_trib - exclusoes
    pis_db = base_db * 0.0165 + rec_financ * 0.0065
    cof_db = base_db * 0.076 + rec_financ * 0.04
    pis_cr, cof_cr = base_creditos * 0.0165, base_creditos * 0.076
    pis_dev, cof_dev = pis_db - pis_cr - saldo_ant, cof_db - cof_cr - saldo_ant
    return {
        'pis_a_recolher': max(0, pis_dev), 'cof_a_recolher': max(0, cof_dev),
        'saldo_credor': max(0, -pis_dev) + max(0, -cof_dev),
    }

for k, v in pis_cofins_nc(2_000_000, 240_000, 940_000).items():
    print(f'{k}: R\$ {v:,.2f}')
"
```

## 7. Formato de entrega

```
PIS/COFINS NAO-CUMULATIVO — competencia [MM/AAAA] — CNPJ [...]
Selo de Validacao Legal Previa: [data]   Regime do ano: [...]

DEBITOS
  Receita tributavel ............. [...]
  (-) ICMS (Tema 69) ............. [...]
  (=) Base do debito ............. [...]
  PIS 1,65% / COFINS 7,60% ....... [...]
CREDITOS (Tema 779)
  insumos / energia / aluguel / depreciacao / frete / EPI-VT . [...]
  Base de credito ................ [...]
  PIS 1,65% / COFINS 7,60% ....... [...]
SALDO
  PIS a recolher (DARF 6912) ..... [...]   Vencimento: dia 25/MM+1
  COFINS a recolher (DARF 5856) .. [...]   Vencimento: dia 25/MM+1
  Saldo credor (se houver) ....... [...]   -> PER/DCOMP via e-CAC

RESSALVA: rascunho operacional sujeito a revisao e responsabilidade tecnica
do contador com CRC ativo (PA-07).
```

## 8. Anti-padroes

- Nao aproveitar os creditos amplos do Tema 779 — deixa credito legitimo na mesa.
- Tomar credito de aquisicao monofasica/aliquota zero — vedado, nao houve tributacao na origem.
- Excluir o ICMS so do debito e nao dos creditos (Lei 14.592/2023 exclui de ambos).
- Lancar 100% da depreciacao no mes — o correto e 1/12 ou 1/48.
- Tratar receita financeira como aliquota zero — o Decreto 8.426/2015 a tornou tributada.
- Esquecer a manutencao de creditos da exportacao e o credito presumido sobre estoque na migracao.

## 9. Casos de borda

- **Empresa importadora:** PIS/COFINS-importacao devido na entrada, com direito a credito.
- **Exportadora com saldo credor cronico:** ressarcimento via PER/DCOMP — processo longo.
- **Atividades cumulativas no Real (Lei 10.833, art. 10):** hospitais, transporte de passageiros, telecom — essas receitas seguem o regime cumulativo, apuradas pela skill irma.
- **Empresa na Zona Franca de Manaus:** PIS/COFINS suspensos na compra de produtor da ZFM — nao gera credito.
- **Software adquirido:** credito sobre licenca essencial a producao (Tema 779) — defensavel com fundamentacao.

## Vedacoes especificas

- **PA-01** — nao orientar credito sobre despesa sem suporte legal nem fictio de insumo.
- **PA-02** — calcular so com dado real (receita segregada, notas de entrada, competencia).
- **PA-03** — datar pelo ano do fato gerador; PIS/COFINS sao substituidos pela CBS na transicao 2026-2033.
- **PA-04** — sem o Selo de Validacao Legal Previa, a apuracao nao comeca.
- **PA-11** — citar a norma (Lei 10.637/02; Lei 10.833/03; REsp 1.221.170; RE 574.706; Lei 14.592/2023; Decreto 8.426/2015) com artigo.
- **PA-13** — nao confundir regime de apuracao com a obrigacao acessoria.
- **PA-14** — em recuperacao, retificar a EFD-Contribuicoes antes de compensar — nunca o inverso.
- **PA-15** — PIS/COFINS em atraso atualizado pela Selic acumulada, nunca valor nominal.
- **PA-17** — conservadorismo no credito do Tema 779 — nao inflar a base recuperavel; cada credito com fundamentacao.

## Protocolos acionados

- **P1 — Validacao Legal Previa** — Selo emitido por `validador-legislacao-vigente`, com o regime do ano travado.
- **P2 — Ingestao** — notas de entrada e receita conferidas via `analise-xml-fiscal` / `leitura-arquivos-sped`.
- **P3 — Calculo** — memoria rastreavel debito x credito, calculo em Python.
- **P4 — Cruzamento** — apurado x EFD-Contribuicoes (blocos M/F) x DCTFWeb.
- **P6 — Auditoria de Qualidade** — `revisao-final` R1-R4 antes da entrega.

## Localizacao

PIS e COFINS sao tributos **federais** — aliquotas, hipoteses de credito e regras sao uniformes em todo o territorio nacional, sem variacao por municipio ou UF. O eixo de localizacao incide de forma indireta: o **ICMS destacado** a excluir da base e dos creditos (Tema 69) depende da aliquota da UF de origem, apurada na `calculo-icms-st`. A reforma tributaria altera o quadro — a CBS, federal, substitui PIS/COFINS no desenho IBS/CBS de tributacao do consumo; confirmar no Selo (P1) o estagio da transicao no ano do fato gerador.

## Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, `apuracao-lucro-real`, operador direto.

**Entrega para:** `revisao-final` (R1-R4), o `CASO.md` e a `efd-contribuicoes`. A recuperacao retroativa de creditos do Tema 779 (ate 5 anos) e o levantamento de saldo credor sao trabalho de auditoria/recuperacao (Tier 7, v0.3). O comparativo entre Real e Presumido aciona o comparativo de regime. Defesa em autuacao da Receita extrapola o contabil — encaminhar a advogado (slot generico, PA-16).

**Sem esta skill:** PIS/COFINS sao apurados sem identificar os creditos cabiveis — recolhimento a maior e perda dos creditos do Tema 779.
