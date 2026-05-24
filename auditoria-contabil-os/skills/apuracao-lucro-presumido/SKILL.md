---
name: apuracao-lucro-presumido
description: >
  Apuracao trimestral de IRPJ/CSLL e mensal de PIS/COFINS cumulativos no Lucro
  Presumido. Aplica o percentual de presuncao por atividade, o adicional de 10%
  sobre o excesso trimestral, exclui o ICMS da base de PIS/COFINS (Tema 69) e
  emite os DARFs. Calcula via Python, com memoria rastreavel. Base: Lei 9.430/96,
  Lei 9.249/95, IN RFB 1.700/2017. Nao trata Simples nem Lucro Real. Aciona:
  apurar Presumido, IRPJ, CSLL, PIS/COFINS cumulativo, percentual de presuncao,
  adicional de IR, Tema 69, conferir DARF, empresa no Presumido.
---

# APURACAO LUCRO PRESUMIDO

> Skill **Tier 2** — apuracao trimestral de IRPJ/CSLL e mensal de PIS/COFINS cumulativos. Aplica a presuncao de lucro por atividade e exclui o ICMS da base de PIS/COFINS. Toda apuracao exige o Selo de Validacao Legal Previa (P1) e e datada pelo ano do fato gerador.

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com "apurar Presumido", "IRPJ/CSLL trimestral", "PIS/COFINS cumulativo", "percentual de presuncao", "adicional de IR", "conferir DARF". Entrada: CNPJ, trimestre/ano, receita bruta segregada por atividade, receita financeira, ganho de capital, ICMS destacado nas saidas (para PIS/COFINS), retencoes sofridas. Entrega: tabela de apuracao, calculo passo a passo, DARFs com codigo e vencimento, memoria de calculo.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.
- **Aciona antes de calcular:** `validador-legislacao-vigente` (P1) — percentuais e a delimitacao da base de PIS/COFINS sao alvo movel; sem o Selo a apuracao nao comeca (PA-04).
- **Apoia-se em:** `analise-cnae-atividades` (percentual de presuncao por atividade), `analise-xml-fiscal` (receita e ICMS destacado).
- **Entrega para:** `revisao-final` (R1-R4), o `CASO.md`, a `efd-contribuicoes` e a `dctfweb` (Tier 3).

## 2. Presuncao do lucro por atividade (Lei 9.249/95)

O lucro e presumido por um percentual sobre a receita bruta, definido pela **atividade real** — o CNAE e apenas pista (PA-12):

| Atividade (sintese) | Presuncao IRPJ | Presuncao CSLL |
|---------------------|----------------|----------------|
| Revenda de combustivel | 1,6% | 12% |
| Comercio, industria, transporte de carga, construcao com material | 8% | 12% |
| Transporte de passageiros, servicos hospitalares (stricto sensu) | 16% | 12% |
| Servicos em geral, profissoes regulamentadas, intermediacao, locacao | 32% | 32% |

Receita com mais de uma atividade exige **segregacao** — cada parcela com seu percentual. Erros classicos: transporte de carga (8%) confundido com passageiros (16%); construcao so de mao de obra (32%) confundida com empreitada com material (8%); hospital (8%) confundido com clinica de exames (32%). `[VERIFICAR]` o percentual contra a norma vigente no ano (PA-03).

## 3. Aliquotas e regras nucleares

```
IRPJ: 15% sobre a base presumida
Adicional de IR: 10% sobre o excesso da base a R$ 60.000/trimestre
CSLL: 9% (sem adicional)
PIS cumulativo: 0,65% sobre a receita    COFINS cumulativo: 3,00%
```

- **Adicional de IR:** incide so sobre o **excesso** da base presumida a R$ 60.000 no trimestre — nunca sobre a base inteira.
- **Receita financeira e ganho de capital:** somam **direto** a base, sem presuncao, e sao tributados nas aliquotas integrais (15% IRPJ + 9% CSLL).
- **ICMS na base de PIS/COFINS:** o ICMS destacado nas saidas e **excluido** da base — RE 574.706 (Tema 69 STF), consolidado pela legislacao posterior. E o erro mais comum do mercado.
- **Retencao na fonte (CSRF, IRRF):** o tributo retido por PJ tomadora e abatido na apuracao / compensado conforme a declaracao.
- **Receita monofasica:** aliquota zero de PIS/COFINS na revenda — segregar.

> Codigos de DARF e percentuais sao confirmados no ano do fato gerador — `[VERIFICAR]` (PA-06).

## 4. Calculo via Python (P3)

```python
python3 -c "
def irpj_csll_presumido(rec, p_irpj, p_csll, rec_fin=0, ganho=0):
    base_irpj = rec * p_irpj + rec_fin + ganho
    base_csll = rec * p_csll + rec_fin + ganho
    irpj = base_irpj * 0.15
    adicional = max(0, base_irpj - 60_000) * 0.10
    csll = base_csll * 0.09
    return base_irpj, irpj, adicional, base_csll, csll

b_irpj, irpj, adic, b_csll, csll = irpj_csll_presumido(1_000_000, 0.08, 0.12, 5_000)
print(f'Base IRPJ: R\$ {b_irpj:,.2f} | IRPJ 15%: R\$ {irpj:,.2f} | Adicional: R\$ {adic:,.2f}')
print(f'Base CSLL: R\$ {b_csll:,.2f} | CSLL 9%: R\$ {csll:,.2f}')

def pis_cofins(receita_mes, icms_destacado, cancelamentos=0, descontos=0):
    base = receita_mes - icms_destacado - cancelamentos - descontos
    return base * 0.0065, base * 0.03

pis, cof = pis_cofins(333_333, 40_000)
print(f'PIS mes: R\$ {pis:,.2f} | COFINS mes: R\$ {cof:,.2f}')
"
```

PIS/COFINS sao mensais — calcular os tres meses do trimestre, sempre com o ICMS destacado excluido.

## 5. Formato de entrega

```
APURACAO LUCRO PRESUMIDO — [CNPJ] — [trimestre/ano]
Selo de Validacao Legal Previa: [data]   Regime do ano: [...]   Local: [mun]/[UF]

RECEITA POR ATIVIDADE:
| Atividade | Receita bruta | % presuncao IRPJ | Base IRPJ | % CSLL | Base CSLL |
+ receita financeira / ganho de capital (somam direto)

IRPJ:  15% x base = [...] ; adicional 10% x (base - 60.000) = [...]   DARF [cod]
CSLL:  9% x base = [...]                                              DARF [cod]
PIS/COFINS por mes (ICMS Tema 69 excluido):  m1 [...] | m2 [...] | m3 [...]

DARFs: codigo, valor, vencimento por tributo.
RESSALVA: rascunho operacional sujeito a revisao e responsabilidade tecnica
do contador com CRC ativo (PA-07).
```

## 6. Anti-padroes

- Calcular o adicional de IR sobre a base inteira — incide so sobre o excesso a R$ 60k trimestral.
- Esquecer a exclusao do ICMS da base de PIS/COFINS (Tema 69).
- Aplicar 32% em transporte de carga (correto: 8%) ou 8% em servico profissional (correto: 32%).
- Presumir receita financeira ou ganho de capital — somam direto, sem presuncao.
- Nao compensar o IRRF/CSRF retido por terceiros.
- Tratar o CNAE como verdade absoluta — a atividade real e o que define o percentual.

## 7. Casos de borda

- **Empresa migrando do Simples:** direito a credito presumido de PIS/COFINS sobre o estoque inicial — aproveitar.
- **Receita do ano anterior acima do teto do Presumido:** migracao obrigatoria para o Lucro Real — sinalizar.
- **Distribuicao de lucros isenta:** limitada ao lucro presumido liquido dos tributos; acima disso exige escrituracao contabil regular.
- **Margem real acima da presumida:** o cliente pode estar pagando IR a maior — sinalizar comparativo de regime.
- **Saldo de IRPJ/CSLL:** pode ser parcelado em 3 quotas com encargo legal (Lei 9.430/96, art. 5o).

## 8. Vedacoes especificas

- **PA-01 / PA-10** — nao reclassificar atividade para reduzir o percentual de presuncao; planejamento exige proposito negocial.
- **PA-02** — apurar so com dado real (receita por atividade, ICMS destacado, retencoes).
- **PA-03** — datar a apuracao pelo ano do fato gerador; percentuais e a base de PIS/COFINS mudam (reforma 2026-2033).
- **PA-04** — sem o Selo de Validacao Legal Previa, a apuracao nao comeca.
- **PA-06** — `[VERIFICAR]` em percentual, codigo de DARF ou regra de base nao confirmados no ano.
- **PA-08** — a skill apura e prepara o DARF; nao transmite a DCTFWeb nem recolhe.
- **PA-11** — citar a norma (Lei 9.430/96; Lei 9.249/95; IN RFB 1.700/2017; RE 574.706) com artigo.
- **PA-13** — nao confundir competencia x caixa nem regime x obrigacao acessoria (DCTFWeb, EFD-Contribuicoes).
- **PA-15** — debito em atraso atualizado pela Selic acumulada, nunca valor nominal.

## 9. Protocolos acionados

- **P1 — Validacao Legal Previa** — Selo emitido por `validador-legislacao-vigente` antes do calculo.
- **P3 — Calculo** — memoria rastreavel, Python, cenarios quando houver mais de uma opcao.
- **P4 — Cruzamento e Conciliacao** — o apurado bate com a EFD-Contribuicoes e a DCTFWeb.
- **P6 — Auditoria de Qualidade** — `revisao-final` R1-R4 antes da entrega.

## 10. Localizacao

A apuracao de IRPJ/CSLL e PIS/COFINS e **federal** — vale em todo o pais. O eixo geografico entra pelo **ICMS destacado** que se exclui da base de PIS/COFINS: o ICMS segue a aliquota da **UF** da operacao, capturada da NF. Quando o ICMS destacado nao puder ser confirmado, marcar `[VERIFICAR]` (PA-06) e nao estimar a base.

## 11. Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.

**Entrega para:** `revisao-final` (R1-R4), o `CASO.md`, a `efd-contribuicoes` e a `dctfweb`. Recuperacao retroativa do ICMS na base de PIS/COFINS (Tema 69, 5 anos) e trabalho de auditoria/recuperacao (Tier 7, v0.3); discussao judicial extrapola o contabil — encaminhar a advogado (slot generico).

**Sem esta skill:** IRPJ/CSLL/PIS/COFINS sao estimados sem segregacao de atividade nem exclusao do ICMS — risco de pagar a maior ou ser autuado.
