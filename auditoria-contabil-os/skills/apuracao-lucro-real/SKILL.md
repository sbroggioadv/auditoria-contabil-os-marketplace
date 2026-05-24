---
name: apuracao-lucro-real
description: >
  Apuracao trimestral ou anual no Lucro Real — parte do LAIR contabil, executa as
  adicoes e exclusoes da Parte A do LALUR, controla o prejuizo fiscal com limite
  de 30%, gera IRPJ/CSLL e atualiza a Parte B. Calcula via Python, com memoria
  rastreavel. Base: Decreto 9.580/2018 (RIR), Lei 8.981/95, Lei 9.249/95, Lei
  12.973/2014. Nao trata Simples nem Lucro Presumido. Aciona: apurar Lucro Real,
  LALUR, prejuizo fiscal, Parte B, adicoes e exclusoes, JCP dedutivel, estimativa
  mensal, balancete de suspensao, IRPJ/CSLL no Real.
---

# APURACAO LUCRO REAL

> Skill **Tier 2** — apuracao trimestral ou anual com estimativa no Lucro Real. Parte do LAIR contabil, ajusta pelo LALUR e controla o prejuizo fiscal. Toda apuracao exige o Selo de Validacao Legal Previa (P1) e e datada pelo ano do fato gerador.

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com "apurar Lucro Real", "LALUR", "prejuizo fiscal", "adicoes e exclusoes", "Parte B", "estimativa mensal", "balancete de suspensao". Entrada: CNPJ, periodo, opcao (trimestral ou anual com estimativa), LAIR contabil, saldo de prejuizo fiscal e base negativa de CSLL, eventos a ajustar. Entrega: LALUR Parte A, calculo passo a passo, Parte B atualizada, DARFs com vencimento, memoria de calculo.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.
- **Aciona antes de calcular:** `validador-legislacao-vigente` (P1) — sem o Selo a apuracao nao comeca (PA-04).
- **Apoia-se em:** o balancete fechado (`fechamento-mensal`, v0.2) — sem LAIR nao ha Real; `leitura-arquivos-sped` (ECD do ano-base).
- **Entrega para:** `revisao-final` (R1-R4), o `CASO.md`, a `ecf` e a `efd-contribuicoes` (Tier 3).

## 2. Aliquotas e periodicidade

```
IRPJ: 15% sobre o lucro real
Adicional de IR: 10% sobre o excesso a R$ 60.000/trimestre OU R$ 240.000/ano
CSLL: 9% (instituicoes financeiras com aliquota majorada)
```

- **Real Trimestral:** apuracao definitiva a cada trimestre — 4 apuracoes no ano.
- **Real Anual:** estimativa mensal (percentual de presuncao sobre a receita) + balancete de suspensao/reducao + ajuste anual em 31/12.

> Codigos de DARF e prazos sao confirmados no ano do fato gerador — `[VERIFICAR]` (PA-06).

## 3. LALUR Parte A — adicoes (Decreto 9.580/2018)

Despesas/perdas contabeis **indedutiveis** voltam a base via adicao:

| Adicao | Base legal (referencia) |
|--------|-------------------------|
| Multas punitivas (penais, nao compensatorias) | RIR/2018 |
| Provisoes nao autorizadas (salvo ferias, 13o, perdas Lei 9.430/96) | RIR/2018 |
| Equivalencia patrimonial negativa | Lei 12.973/2014 |
| Doacoes sem incentivo legal e brindes | RIR/2018 |
| Despesas com socios/administradores fora do limite | RIR/2018 |
| Tributos discutidos em juizo sem deposito | RIR/2018 |
| JCP excedente ao limite legal | Lei 9.249/95, art. 9o |
| Ajustes de preco de transferencia | Lei 14.596/2023 |
| Despesas nao comprovadas | RIR/2018 |

## 4. LALUR Parte A — exclusoes

Receitas tributadas contabilmente que **nao** compoem o lucro real:

| Exclusao | Base legal (referencia) |
|----------|-------------------------|
| Reversao de provisoes antes adicionadas | RIR/2018 |
| Equivalencia patrimonial positiva (controlada no Brasil) | Lei 12.973/2014 |
| Dividendos recebidos (PJ -> PJ no Brasil) | Lei 9.249/95, art. 10 |
| Variacao cambial diferida (regime caixa por opcao) | MP 2.158-35/2001 |
| IPI/ICMS recuperaveis na compra de imobilizado | CPC 27 |
| Subvencao para investimento | regime vigente no ano [VERIFICAR] |

> Atencao: lucros de filial/controlada **no exterior** sao tributados (Lei 12.973/2014) — nao excluir.

## 5. Prejuizo fiscal — limite de 30% (Lei 8.981/95, art. 42)

A compensacao do prejuizo fiscal e limitada a **30% do lucro liquido ajustado** (apos adicoes e exclusoes, antes da compensacao). Cada compensacao reduz o saldo da Parte B. Exemplo: prejuizo acumulado de R$ 1.000.000 e lucro ajustado de R$ 100.000 — limite = 30% x 100.000 = R$ 30.000 compensados; saldo remanescente R$ 970.000. **Prejuizo fiscal (IRPJ) e base negativa de CSLL sao contas separadas** — controle independente.

## 6. JCP e estimativa mensal

**JCP** (Lei 9.249/95, art. 9o): juros sobre capital proprio limitados a TJLP/TLP x Patrimonio Liquido ajustado, com tetos adicionais sobre o lucro ou as reservas. E **despesa dedutivel** para a PJ (economia de IRPJ + CSLL), com IRRF na fonte do socio. Exige ata de aprovacao.

**Estimativa mensal** (Real Anual): estimativa = receita do mes x percentual de presuncao x 15% + adicional. A **suspensao/reducao** (IN RFB 1.700/2017) permite levantar balancete acumulado e provar lucro real menor que a estimativa — suspende ou reduz o recolhimento.

## 7. Calculo via Python (P3)

```python
python3 -c "
def lucro_real(lair, adicoes, exclusoes, prej_acum, teto_adic=60_000):
    ajustado = lair + adicoes - exclusoes
    prej_comp = min(prej_acum, ajustado * 0.30)
    real = ajustado - prej_comp
    irpj = real * 0.15
    adicional = max(0, real - teto_adic) * 0.10
    return ajustado, prej_comp, real, irpj, adicional, real * 0.09

aj, pc, lr, irpj, adic, csll = lucro_real(500_000, 80_000, 30_000, 200_000)
print(f'Lucro ajustado: R\$ {aj:,.2f} | Prej. compensado: R\$ {pc:,.2f}')
print(f'Lucro real: R\$ {lr:,.2f}')
print(f'IRPJ 15%: R\$ {irpj:,.2f} | Adicional: R\$ {adic:,.2f} | CSLL 9%: R\$ {csll:,.2f}')
"
```

## 8. Formato de entrega

```
APURACAO LUCRO REAL — [CNPJ] — [periodo]
Selo de Validacao Legal Previa: [data]   Regime do ano: [...]   Local: [mun]/[UF]

LALUR PARTE A:
  LAIR contabil ........................... [...]
  (+) Adicoes (cada uma com documento e norma) [...]
  (-) Exclusoes (cada uma com fundamento legal) [...]
  = Lucro liquido ajustado ................ [...]
  (-) Prejuizo fiscal compensado (limite 30%) [...]
  = LUCRO REAL ............................ [...]
  IRPJ 15% + adicional 10% .. [...]   CSLL 9% .. [...]

PARTE B: saldo de prejuizo fiscal e base negativa de CSLL atualizados.
DARFs: codigo, valor, vencimento.
RESSALVA: rascunho operacional sujeito a revisao e responsabilidade tecnica
do contador com CRC ativo (PA-07).
```

## 9. Anti-padroes

- Compensar prejuizo fiscal acima de 30% do lucro liquido ajustado.
- Misturar prejuizo fiscal (IRPJ) com base negativa de CSLL — contas separadas.
- Excluir dividendos/lucros de controlada **no exterior** — sao tributados.
- Calcular o adicional sobre o lucro inteiro — incide so sobre o excesso.
- JCP sem TJLP/TLP atualizada ou sem ata de aprovacao.
- Distribuir lucro do Real sem escrituracao contabil regular.
- Adotar regime antigo de subvencao para investimento sem checar a norma vigente.

## 10. Casos de borda

- **Lucro real abaixo do figurado no Presumido:** o cliente pode estar pagando a maior — sinalizar comparativo de regime.
- **Operacoes com partes relacionadas no exterior:** Lei 14.596/2023 — exige laudo de preco de transferencia.
- **Empresa recem-saida do Simples:** credito presumido de PIS/COFINS sobre o estoque inicial.
- **Variacao cambial:** a opcao pelo regime de caixa e anual e irretratavel — formalizar.

## 11. Vedacoes especificas

- **PA-01 / PA-10** — nao construir adicao/exclusao artificial; cada ajuste tem documento e norma.
- **PA-02** — apurar so com dado real (LAIR do balancete, saldo de prejuizo, eventos).
- **PA-03** — datar a apuracao pelo ano do fato gerador (reforma 2026-2033 e alteracoes anuais).
- **PA-04** — sem o Selo de Validacao Legal Previa, a apuracao nao comeca.
- **PA-06** — `[VERIFICAR]` em codigo de DARF, regime de subvencao ou regra nao confirmada no ano.
- **PA-08** — a skill apura e prepara o DARF; nao transmite a ECF/DCTFWeb nem recolhe.
- **PA-11** — citar a norma (RIR/2018; Lei 8.981/95, art. 42; Lei 9.249/95, art. 9o-10) com artigo.
- **PA-13** — nao confundir competencia x caixa nem regime x obrigacao acessoria.
- **PA-15** — debito em atraso atualizado pela Selic acumulada, nunca valor nominal.
- **PA-16** — recuperacao judicial e contencioso judicial extrapolam o contabil — encaminhar a advogado.

## 12. Protocolos acionados

- **P1 — Validacao Legal Previa** — Selo emitido por `validador-legislacao-vigente`.
- **P3 — Calculo** — memoria rastreavel, Python, cenarios.
- **P4 — Cruzamento** — o lucro real bate com a ECF, a ECD e a EFD-Contribuicoes.
- **P6 — Auditoria de Qualidade** — `revisao-final` R1-R4 antes da entrega.

## 13. Localizacao

A apuracao de IRPJ/CSLL no Lucro Real e **federal** — vale em todo o pais. O eixo geografico entra de forma indireta, via IPI/ICMS recuperaveis (exclusao na compra de imobilizado) e via benefícios estaduais que se refletem no resultado. Quando uma regra que depende de norma estadual nao puder ser confirmada, marcar `[VERIFICAR — norma estadual]` (PA-06).

## 14. Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.

**Entrega para:** `revisao-final` (R1-R4), o `CASO.md`, a `ecf` e a `efd-contribuicoes`. Recuperacao retroativa e cruzamento profundo de SPED sao trabalho de auditoria (Tier 7, v0.3); litigio judicial extrapola o contabil — encaminhar a advogado (slot generico).

**Sem esta skill:** o LALUR e montado sem controle de adicoes/exclusoes nem do limite de 30% — risco de IRPJ/CSLL incorretos e glosa de prejuizo.
