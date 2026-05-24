---
name: calculo-icms-st
description: >
  Apuracao de ICMS proprio e ICMS-ST em operacoes internas e interestaduais — MVA
  ajustada, DIFAL pos LC 190/2022, antecipacao tributaria, aliquota de 4% para
  importado e regra do remetente do Simples. Calcula via Python, NF a NF, com
  memoria rastreavel e GNRE. Base: LC 87/96, LC 190/2022, Convenio ICMS 142/2018,
  RICMS de cada UF. Aciona: calcular ICMS, ICMS-ST, MVA ajustada, DIFAL,
  substituicao tributaria, GNRE, NF interestadual, antecipacao de ICMS, aliquota
  interna, 4% importado.
---

# CALCULO ICMS / ICMS-ST

> Skill **Tier 2** — apuracao de ICMS proprio e ICMS-ST nas operacoes internas e interestaduais. O ICMS e estadual: cada UF tem aliquota interna, MVA, beneficios e RICMS proprios. Toda apuracao exige o Selo de Validacao Legal Previa (P1) e e datada pelo ano do fato gerador.

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com "calcular ICMS", "ICMS-ST", "MVA ajustada", "DIFAL", "substituicao tributaria", "GNRE", "NF interestadual", "antecipacao de ICMS". Entrada: UF de origem e de destino, NCM, valor da mercadoria, frete, seguro, outras despesas, IPI, perfil do destinatario (contribuinte ou nao), regime do remetente, MVA original. Entrega: calculo passo a passo NF a NF, memoria de calculo, GNRE e checklist de conformidade contra autuacao da SEFAZ.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.
- **Aciona antes de calcular:** `validador-legislacao-vigente` (P1) — aliquotas internas, MVA e protocolos sao alvo movel e variam por UF; sem o Selo a apuracao nao comeca (PA-04).
- **Apoia-se em:** `analise-xml-fiscal` (dados da NF: NCM, CFOP, CST, valores), `analise-cnae-atividades` (incidencia ICMS x ISS).
- **Entrega para:** `revisao-final` (R1-R4), o `CASO.md` e a `efd-icms-ipi` (Tier 3 — registros C170/C190/E110).

## 2. Aliquotas — interestaduais e internas

```
ALIQUOTAS INTERESTADUAIS (Resolucao do Senado)
 4% — produtos importados com Conteudo de Importacao > 40% (FCI atualizada)
 7% — remetente das regioes Sul/Sudeste (exceto ES) -> Norte/Nordeste/Centro-Oeste/ES
12% — demais combinacoes
```

As **aliquotas internas** (em regra entre 17% e 25%, com adicionais de fundo de combate a pobreza em algumas UFs e aliquotas reduzidas para itens essenciais) variam por **UF** e por mercadoria — sempre confirmar a aliquota interna da UF de destino na lei estadual vigente. Cravar aliquota interna de memoria e fonte de autuacao — `[VERIFICAR]` (PA-05/PA-06).

## 3. ICMS proprio e regra da base

```
Base ICMS proprio = valor da mercadoria + frete + seguro + outras despesas
ICMS proprio = base x aliquota (interna ou interestadual conforme a operacao)
```

- **IPI na base do ICMS:** o IPI integra a base do ICMS quando o destinatario for **nao-contribuinte** ou a mercadoria for para uso/consumo (LC 87/96, art. 13, §2o). Para contribuinte que revende, o IPI nao integra.
- **Remetente do Simples:** a aliquota e a regra do anexo do Simples — nao se usa 7%/12% do regime normal; o credito do destinatario segue a aliquota informada na NF (CGSN 140/2018).

## 4. ICMS-ST e MVA ajustada

Na substituicao tributaria, o remetente recolhe antecipadamente o ICMS de toda a cadeia ate o consumidor. A base presumida usa a **MVA ajustada** — nunca a MVA original em operacao interestadual:

```
MVA ajustada = [(1 + MVA orig) x (1 - Aliq inter) / (1 - Aliq interna destino)] - 1
Base ST      = base ICMS proprio x (1 + MVA ajustada)
ICMS-ST devido = (Base ST x Aliq interna destino) - ICMS proprio
```

O ICMS-ST devido **subtrai** o ICMS proprio — sem isso o valor sai dobrado. A MVA original vem do Convenio ICMS 142/2018 ou do protocolo bilateral entre as UFs envolvidas — `[VERIFICAR]` o NCM no Convenio e no protocolo da dupla de estados.

## 5. DIFAL, antecipacao e 4% importado

- **DIFAL — venda a nao-contribuinte (LC 190/2022):** recolhe-se o ICMS interestadual para a origem e o diferencial de aliquota (aliquota interna do destino menos a interestadual) para a UF de destino, pela base "por dentro"; GNRE para o destino antes da saida.
- **Antecipacao tributaria:** varias UFs exigem antecipacao do ICMS na entrada de mercadoria de outra UF — regra propria de cada estado; sempre verificar a legislacao da UF de destino.
- **4% para importado:** Resolucao do Senado, condicionada a FCI (Ficha de Conteudo de Importacao) com Conteudo de Importacao acima de 40%; sem FCI ou abaixo do limite, aplica-se a aliquota normal.

## 6. Calculo via Python (P3)

```python
python3 -c "
def icms_proprio(merc, frete, seguro, outras, ipi, aliq, dest_contrib=True):
    base = merc + frete + seguro + outras + (0 if dest_contrib else ipi)
    return base, base * aliq

def mva_ajustada(mva, aliq_inter, aliq_int_dest):
    return ((1 + mva) * (1 - aliq_inter) / (1 - aliq_int_dest)) - 1

def icms_st(base_prop, mva_aj, aliq_int_dest, icms_prop):
    base_st = base_prop * (1 + mva_aj)
    return base_st, base_st * aliq_int_dest - icms_prop

base, icms_p = icms_proprio(10_000, 500, 0, 0, 0, 0.07)   # SP->BA, 7%
mva_aj = mva_ajustada(0.35, 0.07, 0.19)                   # aliq interna BA [VERIFICAR]
base_st, st = icms_st(base, mva_aj, 0.19, icms_p)
print(f'ICMS proprio: R\$ {icms_p:,.2f} | MVA ajustada: {mva_aj:.4%}')
print(f'Base ST: R\$ {base_st:,.2f} | ICMS-ST devido: R\$ {st:,.2f}')
"
```

## 7. Formato de entrega

```
CALCULO ICMS / ICMS-ST — NF [n] — [UF orig] -> [UF dest]
Selo de Validacao Legal Previa: [data]   Destinatario: [contribuinte/nao]

Base ICMS proprio = mercadoria + frete + seguro + outras (+ IPI se nao-contribuinte)
ICMS proprio = base x aliquota interestadual
MVA original [Convenio 142/2018 / protocolo] -> MVA ajustada
Base ST = base x (1 + MVA ajustada)   ICMS-ST = Base ST x aliq interna - ICMS proprio
DIFAL (se nao-contribuinte): (aliq interna destino - aliq interestadual) por dentro

GNRE para a UF de destino — antes da saida da mercadoria.
RESSALVA: rascunho operacional sujeito a revisao e responsabilidade tecnica
do contador com CRC ativo (PA-07).
```

## 8. Anti-padroes

- Usar a MVA original em operacao interestadual — sempre a ajustada.
- Calcular o ICMS-ST sem subtrair o ICMS proprio — resultado dobrado.
- Nao incluir o IPI na base do ICMS quando o destinatario for nao-contribuinte.
- Esquecer o DIFAL na venda a nao-contribuinte.
- Aplicar 4% sem FCI atualizada ou com Conteudo de Importacao abaixo de 40%.
- Tratar o remetente do Simples como regime normal.
- Esquecer a antecipacao tributaria exigida pela UF de destino.
- Emitir/pagar a GNRE depois da saida da mercadoria — autuacao na fronteira.
- Cravar aliquota interna ou MVA de memoria — `[VERIFICAR]` na lei da UF.

## 9. Casos de borda

- **Devolucao de mercadoria sob ST:** CFOP de devolucao com creditos espelho; o ICMS-ST e devolvido ao destinatario original.
- **Empresa em regime especial estadual:** pode ter aliquota reduzida ou credito presumido — verificar o decreto da UF.
- **Venda a consumidor final nao-contribuinte (ex.: construtor):** o DIFAL se aplica.
- **NF cancelada apos o pagamento da GNRE:** pedido de ressarcimento a SEFAZ de destino — processo demorado.
- **Recuperacao de ICMS-ST pago a maior** (preco final menor que a base presumida): trabalho de auditoria/recuperacao (Tier 7, v0.3).

## 10. Vedacoes especificas

- **PA-01** — nao orientar subfaturamento de base nem MVA artificial para reduzir o ICMS-ST.
- **PA-02** — calcular so com dado real da NF (NCM, valores, UFs, perfil do destinatario).
- **PA-03** — datar a apuracao pelo ano do fato gerador (reforma 2026-2033 — transicao para o IBS).
- **PA-04** — sem o Selo de Validacao Legal Previa, a apuracao nao comeca.
- **PA-05** — aliquota interna, MVA e ICMS-ST sempre da **UF** do caso — nunca aliquota generica.
- **PA-06** — `[VERIFICAR]` em aliquota interna, MVA, protocolo bilateral ou regra de antecipacao nao confirmados.
- **PA-08** — a skill calcula e prepara a GNRE; nao transmite nem recolhe.
- **PA-11** — citar a norma (LC 87/96; LC 190/2022; Convenio ICMS 142/2018; RICMS da UF) com artigo.
- **PA-15** — ICMS em atraso atualizado pelo encargo legal da UF, nunca valor nominal.

## 11. Protocolos acionados

- **P1 — Validacao Legal Previa** — Selo emitido por `validador-legislacao-vigente`, com a aliquota da UF.
- **P2 — Ingestao** — dados da NF vindos de `analise-xml-fiscal`.
- **P3 — Calculo** — memoria rastreavel NF a NF, MVA ajustada em Python.
- **P5 — Localizacao** — eixo central desta skill: cada UF define aliquota, MVA, beneficio e RICMS.
- **P6 — Auditoria de Qualidade** — `revisao-final` R1-R4 antes da entrega.

## 12. Localizacao

O ICMS e tributo **estadual** — esta e a skill mais sensivel ao eixo geografico. A **UF de destino** define a aliquota interna, a MVA aplicavel, a existencia de antecipacao tributaria, os beneficios fiscais e o RICMS; a **UF de origem** define a aliquota interestadual e a apuracao do ICMS proprio. O protocolo de ST e bilateral — depende da dupla origem/destino. Toda regra estadual nao confirmada e marcada `[VERIFICAR — norma estadual]` (PA-06); nunca inventar aliquota, MVA ou codigo de receita da GNRE.

## 13. Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.

**Entrega para:** `revisao-final` (R1-R4), o `CASO.md` e a `efd-icms-ipi`. Recuperacao retroativa de ICMS-ST pago a maior e trabalho de auditoria (Tier 7, v0.3); autuacao da SEFAZ a contestar em juizo extrapola o contabil — encaminhar a advogado (slot generico).

**Sem esta skill:** o ICMS interestadual e estimado sem MVA ajustada nem DIFAL — risco de autuacao na fronteira e de GNRE incorreta.
