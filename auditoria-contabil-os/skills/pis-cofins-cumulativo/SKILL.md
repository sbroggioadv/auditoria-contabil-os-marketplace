---
name: pis-cofins-cumulativo
description: >
  Apuracao mensal de PIS e COFINS no regime cumulativo (Lucro Presumido e
  atividades excepcionalmente cumulativas no Real) — exclusao obrigatoria do
  ICMS destacado da base (Tema 69 STF, RE 574.706, Lei 14.592/2023), receitas
  monofasicas com aliquota zero na revenda, demais exclusoes legais, CSRF
  retida por terceiros e regra das atividades cumulativas da Lei 10.833.
  Calcula via Python, mes a mes, com memoria rastreavel e DARFs. Base: Lei
  9.715/98, LC 70/91, IN RFB 2.121/2022. Aciona: PIS COFINS cumulativo, Lucro
  Presumido, Tema 69, exclusao do ICMS, receita monofasica, DARF 8109 ou 2172.
---

# PIS / COFINS CUMULATIVO

> Skill **Tier 2** — apuracao mensal de PIS e COFINS no regime cumulativo, tipico do Lucro Presumido. No cumulativo nao ha credito; o ponto critico e a **base de calculo** — toda exclusao legal aplicada corretamente. Exige o Selo de Validacao Legal Previa (P1) e e datada pelo ano do fato gerador (PA-03). Atencao: a reforma tributaria extingue PIS e COFINS, substituidos pela CBS, ao longo da transicao 2026-2033.

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com "PIS COFINS cumulativo", "Lucro Presumido", "Tema 69", "exclusao do ICMS", "receita monofasica", "DARF 8109", "DARF 2172". Entrada: CNPJ, competencia, faturamento bruto do mes, ICMS destacado nas saidas, IPI e ICMS-ST destacados, vendas canceladas e descontos incondicionais, receitas de exportacao, receitas monofasicas, CSRF retida por terceiros, atividade (para a regra de cumulatividade no Real). Entrega: apuracao mensal com a base depurada, memoria de calculo, DARFs e checklist de conformidade.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, `apuracao-lucro-presumido`, operador direto.
- **Aciona antes de calcular:** `validador-legislacao-vigente` (P1) — aliquotas, hipoteses de exclusao e o cronograma da reforma sao alvo movel; sem o Selo a apuracao nao comeca (PA-04).
- **Apoia-se em:** `analise-xml-fiscal` (ICMS destacado nas saidas), `leitura-arquivos-sped` (EFD-Contribuicoes).
- **Entrega para:** `revisao-final` (R1-R4), o `CASO.md` e a `efd-contribuicoes` (Tier 3).

## 2. Aliquotas e codigos do regime cumulativo

```
ALIQUOTAS (regime cumulativo)
  PIS .... 0,65%
  COFINS . 3,00%
  Total .. 3,65% sobre a base depurada

CODIGOS DARF
  PIS cumulativo ..... 8109   — vencimento dia 25 do mes seguinte
  COFINS cumulativo .. 2172   — vencimento dia 25 do mes seguinte
  CSRF retida (tomador) 5952  — ultimo dia util da quinzena seguinte ao pagamento
```

As aliquotas nominais sao estaveis no regime atual, mas a **vigencia do regime** e alvo movel: confirmar com o Selo (P1) se a competencia esta sob PIS/COFINS ou ja sob a CBS na transicao da reforma.

## 3. Base de calculo — exclusoes obrigatorias

```
Receita bruta total
(-) ICMS destacado nas saidas .......... Tema 69 STF / Lei 14.592/2023
(-) IPI destacado
(-) ICMS-ST destacado
(-) Vendas canceladas e devolucoes
(-) Descontos incondicionais
(-) Receitas de exportacao ............. aliquota zero
(-) Receitas monofasicas (revenda) ..... aliquota zero
(-) Receitas isentas / nao tributadas
(=) BASE PIS/COFINS CUMULATIVO
```

**Tema 69 (STF, RE 574.706, j. 15/03/2017):** o ICMS destacado nas saidas nao compoe a base de PIS/COFINS; a modulacao fixou efeitos a partir de 15/03/2017 (antes, para quem ja tinha acao). A Lei 14.592/2023 consolidou a exclusao do ICMS destacado. Nao excluir o ICMS e o erro mais caro do mercado — a empresa recolhe sobre ~100% da receita quando deveria recolher sobre ~82%.

## 4. Receitas monofasicas — aliquota zero na revenda

Nos regimes monofasicos, a tributacao concentra-se no produtor/importador; na revenda (atacado e varejo) a receita tem **aliquota zero**. Setores: combustiveis, autopecas (NCMs especificos), cosmeticos, bebidas frias — cada um com lei propria. Erro frequente: o varejista recolher 3,65% sobre a venda de produto monofasico. A receita monofasica deve ser **segregada** da base tributada.

## 5. Receita financeira e CSRF retida

- **Receita financeira no cumulativo:** o STF declarou inconstitucional o alargamento da base promovido pela Lei 9.718/98 (RE 585.235). Em PJ nao-financeira, a receita financeira nao compoe a base do cumulativo; em instituicao financeira, e receita operacional tributada.
- **CSRF retida por terceiros:** quando o cliente teve CSRF (4,65%) retida em pagamentos que recebeu, a parcela de PIS e de COFINS retida e compensada na apuracao, na proporcao (0,65/4,65 para o PIS e 3,00/4,65 para a COFINS).

## 6. Calculo via Python (P3)

```python
python3 -c "
def pis_cofins_cumulativo(receita, icms_destacado, vendas_canc=0, descontos=0,
                          ipi=0, icms_st=0, exportacao=0, monofasica=0, csrf_retida=0):
    base = (receita - icms_destacado - vendas_canc - descontos - ipi
            - icms_st - exportacao - monofasica)
    pis, cofins = base * 0.0065, base * 0.03
    return {
        'base': base,
        'pis_a_recolher': max(0, pis - csrf_retida * (0.65/4.65)),
        'cofins_a_recolher': max(0, cofins - csrf_retida * (3.0/4.65)),
    }

for k, v in pis_cofins_cumulativo(800_000, 96_000, vendas_canc=5_000).items():
    print(f'{k}: R\$ {v:,.2f}')
"
```

## 7. Formato de entrega

```
PIS/COFINS CUMULATIVO — competencia [MM/AAAA] — CNPJ [...]
Selo de Validacao Legal Previa: [data]   Regime do ano: [...]

Receita bruta total ................ [...]
(-) Vendas canceladas .............. [...]
(-) IPI / ICMS-ST destacados ....... [...]
(-) ICMS destacado (Tema 69) ....... [...]
(-) Exportacao / monofasicas ....... [...]
(=) Base PIS/COFINS ................ [...]
PIS (0,65%) ........................ [...]
COFINS (3,00%) ..................... [...]
(-) CSRF retida por terceiros ...... [...]
PIS a recolher (DARF 8109) ......... [...]   Vencimento: dia 25/MM+1
COFINS a recolher (DARF 2172) ...... [...]   Vencimento: dia 25/MM+1

Recuperacao retroativa do ICMS (Tema 69) — ate 5 anos: avaliar como
trabalho de auditoria/recuperacao (Tier 7, v0.3).
RESSALVA: rascunho operacional sujeito a revisao e responsabilidade tecnica
do contador com CRC ativo (PA-07).
```

## 8. Anti-padroes

- Nao excluir o ICMS destacado da base (Tema 69) — recolhimento sobre receita inflada.
- Tratar receita monofasica como tributada — recolhimento a maior na revenda.
- Esquecer a compensacao da CSRF retida por terceiros, na proporcao correta.
- Empresa ainda no Presumido aplicando o regime nao-cumulativo por engano.
- Tributar receita financeira de PJ nao-financeira no cumulativo (RE 585.235).
- Deixar IPI ou ICMS-ST destacados fora das exclusoes.

## 9. Casos de borda

- **Transicao Simples para Presumido:** PIS/COFINS cumulativo so a partir do mes de inicio do regime Presumido.
- **Atividades excepcionalmente cumulativas no Real (Lei 10.833, art. 10):** hospitais, transporte de passageiros, telecom, jornais — mantem o cumulativo nessas receitas, mesmo a empresa sendo do Lucro Real.
- **Receita imobiliaria (incorporacao):** regime especial RET ou Presumido normal, conforme a opcao.
- **Receita de exportacao:** aliquota zero; eventual saldo a recuperar via PER/DCOMP.
- **Indenizacao recebida:** nao e receita — nao compoe a base.

## Vedacoes especificas

- **PA-01** — nao orientar omissao de receita nem segregacao artificial como monofasica.
- **PA-02** — calcular so com dado real (faturamento, ICMS destacado, competencia).
- **PA-03** — datar pelo ano do fato gerador; PIS/COFINS sao substituidos pela CBS na transicao 2026-2033.
- **PA-04** — sem o Selo de Validacao Legal Previa, a apuracao nao comeca.
- **PA-11** — citar a norma (Lei 9.715/98; LC 70/91; RE 574.706; Lei 14.592/2023; IN RFB 2.121/2022) com artigo.
- **PA-13** — nao confundir regime de apuracao (cumulativo x nao-cumulativo) com a obrigacao acessoria.
- **PA-14** — em recuperacao do Tema 69, retificar a EFD-Contribuicoes antes de compensar — nunca o inverso.
- **PA-15** — PIS/COFINS em atraso atualizado pela Selic acumulada, nunca valor nominal.

## Protocolos acionados

- **P1 — Validacao Legal Previa** — Selo emitido por `validador-legislacao-vigente`, com o regime do ano travado.
- **P2 — Ingestao** — receita e ICMS destacado conferidos via `analise-xml-fiscal` / `leitura-arquivos-sped`.
- **P3 — Calculo** — memoria rastreavel mes a mes, calculo em Python.
- **P4 — Cruzamento** — apurado x EFD-Contribuicoes x DCTFWeb.
- **P6 — Auditoria de Qualidade** — `revisao-final` R1-R4 antes da entrega.

## Localizacao

PIS e COFINS sao tributos **federais** — aliquotas e regras sao uniformes em todo o territorio nacional, sem variacao por municipio ou UF. O eixo de localizacao incide de forma indireta: o **ICMS destacado** a excluir da base (Tema 69) depende da aliquota da UF de origem das saidas, apurada na `calculo-icms-st`. A reforma tributaria muda esse quadro — a CBS, que substitui PIS/COFINS, e federal, mas o desenho IBS/CBS unifica a tributacao do consumo; confirmar no Selo (P1) o estagio da transicao no ano do fato gerador.

## Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, `apuracao-lucro-presumido`, operador direto.

**Entrega para:** `revisao-final` (R1-R4), o `CASO.md` e a `efd-contribuicoes`. A recuperacao retroativa do ICMS na base (Tema 69, ate 5 anos) e trabalho de auditoria/recuperacao (Tier 7, v0.3). A migracao para o Lucro Real aciona a `pis-cofins-nao-cumulativo` e o comparativo de regime. Autuacao da Receita a contestar em juizo extrapola o contabil — encaminhar a advogado (slot generico, PA-16).

**Sem esta skill:** PIS/COFINS sao apurados sobre a receita bruta sem depurar a base — recolhimento a maior e perda do Tema 69.
