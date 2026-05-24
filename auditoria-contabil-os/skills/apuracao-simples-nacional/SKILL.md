---
name: apuracao-simples-nacional
description: >
  Apuracao mensal do DAS no Simples Nacional — segregacao de receitas por anexo,
  aliquota efetiva sobre RBT12, Fator R, sublimite estadual, ICMS-ST/monofasico e
  exportacao. Calcula via Python, com memoria rastreavel e conferencia contra o
  PGDAS-D. Base: LC 123/2006, LC 155/2016, Resolucao CGSN 140/2018. Nao trata MEI
  (ver apuracao-mei). Aciona: apurar Simples, calcular DAS, PGDAS-D, aliquota
  efetiva, RBT12, Anexo I a V, Fator R, sublimite, conferir DAS, empresa optante.
---

# APURACAO SIMPLES NACIONAL

> Skill **Tier 2** — apuracao mensal do DAS de empresa optante (ME/EPP). Segrega receitas por anexo, calcula a aliquota efetiva sobre o RBT12 e consolida o DAS. Toda apuracao exige o Selo de Validacao Legal Previa (P1) e e datada pelo ano do fato gerador.

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com "apurar Simples", "calcular DAS", "PGDAS-D", "aliquota efetiva", "Fator R", "conferir DAS". Entrada: CNPJ, competencia, receita bruta do mes segregada por atividade, RBT12, folha de 12 meses (se Anexo III/V), localizacao. Entrega: tabela de receitas segregadas, calculo passo a passo, DAS por anexo e consolidado, memoria de calculo e checklist de conferencia contra o PGDAS-D.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.
- **Aciona antes de calcular:** `validador-legislacao-vigente` (P1) — anexos, faixas e sublimites sao alvo movel; sem o Selo a apuracao nao comeca (PA-04).
- **Apoia-se em:** `analise-cnae-atividades` (anexo/Fator R aplicavel), `analise-xml-fiscal` (receita por XML), `calendario-fiscal` (vencimento).
- **Entrega para:** `revisao-final` (R1-R4), o `CASO.md` e as obrigacoes do Tier 3 (DEFIS, EFD do regime).

## 2. Premissa de calculo — aliquota efetiva, nunca nominal

O DAS nao usa a aliquota nominal da faixa. Aplica-se a **aliquota efetiva** (LC 123/2006, art. 18, §1o):

```
Aliquota efetiva = ((RBT12 x Aliq nominal) - Parcela a Deduzir) / RBT12
DAS = Receita do mes x Aliquota efetiva
```

- **RBT12** = receita bruta acumulada dos **12 meses anteriores** ao periodo de apuracao — nunca o acumulado do ano nem a receita do proprio mes.
- Empresa com menos de 12 meses: proporcionalizar (CGSN 140, art. 26, §1o) — RBT12 estimada = (receita real / meses ativos) x 12.
- Multiplos anexos: calcular cada anexo em separado e somar os DAS.

## 3. Anexos, Fator R e sublimite

O Simples tem 5 anexos (LC 123/2006, anexos I-V), cada um com 6 faixas de RBT12 (ate R$ 4,8 mi anuais). Anexo I — comercio; II — industria; III/IV/V — servicos. No **Anexo IV** a CPP (INSS patronal) e recolhida por fora, em guia propria, nao no DAS.

**Fator R** (CGSN 140, art. 26): atividades de servico intelectual (TI, consultoria, profissoes regulamentadas, saude, engenharia, marketing, pericia) tributam pelo **Anexo III** se a folha dos 12 meses anteriores (salario + pro-labore + 13o + INSS patronal) ÷ RBT12 >= **28%**; abaixo disso, pelo **Anexo V**. O Fator R e recalculado mes a mes — diagnostico detalhado fica em `analise-cnae-atividades`.

**Sublimite estadual:** acima do sublimite anual de ICMS/ISS, esses tributos passam ao regime normal estadual/municipal; o PGDAS-D segue para os demais tributos com flag "acima do sublimite". O valor do sublimite e dado de alvo movel — `[VERIFICAR]` contra a norma vigente. Sublimite e por estabelecimento; filial em outra UF pode ter situacao distinta da matriz.

## 4. Tratamentos especiais

- **ICMS-ST e monofasicos** (combustiveis, autopecas, cosmeticos, bebidas frias): segregar a receita do produto e, na aliquota efetiva, **excluir** o percentual do ICMS (no ST) ou de PIS+COFINS (no monofasico), conforme a tabela de partilha do Anexo VII da Resolucao CGSN 140/2018. Sem segregar, a receita e tributada em duplicidade.
- **Exportacao:** aliquota efetiva sem ICMS, ISS, PIS, COFINS e IPI — segregar a receita de exportacao.
- **ISS retido pelo tomador:** nao alterar a base; calcular o DAS normal e abater o ISS retido em campo proprio do PGDAS-D (CGSN 140, art. 27).
- **Programa social / auxilio:** repasse de programa social nao compoe a receita bruta.

## 5. Calculo via Python (P3)

Todo calculo roda em Python — memoria rastreavel, nunca conta de cabeca.

```python
python3 -c "
def aliq_efetiva(rbt12, aliq_nom, parc_deduzir):
    return ((rbt12 * aliq_nom) - parc_deduzir) / rbt12

# Exemplo: servico Anexo III, faixa 4 (RBT12 R\$ 1.800.000)
rbt12 = 1_800_000
ae = aliq_efetiva(rbt12, 0.16, 35_640)   # aliq nominal e parcela [VERIFICAR ano]
receita_mes = 150_000
das = receita_mes * ae
print(f'Aliquota efetiva: {ae:.4%}')
print(f'DAS: R\$ {das:,.2f}')
"
```

A aliquota efetiva sai com 4 casas decimais; valores monetarios em formato brasileiro. Aliquota nominal e parcela a deduzir de cada faixa/anexo sao confirmadas com `validador-legislacao-vigente` no ano do fato gerador.

## 6. Formato de entrega

```
APURACAO SIMPLES NACIONAL — [CNPJ] — competencia [MM/AAAA]
Selo de Validacao Legal Previa: [data]   Regime do ano: [...]   Local: [mun]/[UF]

RECEITAS SEGREGADAS:
| Tipo de receita | Valor | Anexo | RBT12 | Tratamento |
|-----------------|-------|-------|-------|------------|

MEMORIA DE CALCULO (por anexo):
| Anexo | Faixa | Aliq nominal | Parcela deduzir | Aliq efetiva | Receita | DAS |
|-------|-------|--------------|-----------------|--------------|---------|-----|

DAS CONSOLIDADO: R$ [...]   Vencimento: [DD/MM/AAAA] [VERIFICAR]

CONFERENCIA PGDAS-D: lancar no portal e comparar (tolerancia R$ 0,01).
RESSALVA: rascunho operacional sujeito a revisao e responsabilidade tecnica
do contador com CRC ativo (PA-07).
```

## 7. Anti-padroes

- Usar a receita do mes (ou o acumulado do ano) como RBT12 — RBT12 sao os 12 meses **anteriores**.
- Aplicar a aliquota nominal direto sobre a receita — sempre a efetiva.
- Misturar receita sob ST/monofasica com a base normal.
- Esquecer o Fator R em servico intelectual ou nao incluir o pro-labore no calculo.
- Empresa nova: comparar periodo parcial sem proporcionalizar (CGSN 140, art. 26, §1o).
- Calcular sem confirmar que a empresa ainda e optante (pode ter sido excluida).
- Cravar aliquota, faixa ou sublimite de memoria — `[VERIFICAR]` no ano (PA-06).

## 8. Casos de borda

- **Troca de anexo no meio do ano** (entrada/saida do Fator R): apurar por competencia, sem retroagir.
- **RBT12 proximo de R$ 4,8 mi:** alertar — exclusao iminente; encaminhar a comparativo de regime.
- **DAS do PGDAS-D divergente do calculo:** revisar primeiro o input (classificacao, RBT12, Fator R).
- **Transmissao em atraso:** o PGDAS-D aceita com multa (minimo legal ou percentual por dia, ate o teto); sinalizar.
- **Estouro do limite de R$ 4,8 mi:** migracao obrigatoria para Lucro Presumido/Real — sinalizar para comparativo de regime.

## 9. Vedacoes especificas

- **PA-01 / PA-10** — nao segregar receita artificialmente nem fracionar empresa para caber no Simples; planejamento exige proposito negocial.
- **PA-02** — apurar so com dado real do cliente (CNPJ, receita, RBT12, folha); dado faltante e solicitado.
- **PA-03** — datar a apuracao pelo ano do fato gerador; anexos e sublimites mudam por exercicio (reforma 2026-2033).
- **PA-04** — sem o Selo de Validacao Legal Previa, a apuracao nao comeca.
- **PA-06** — `[VERIFICAR]` em aliquota, faixa, sublimite ou limite nao confirmados no ano.
- **PA-08** — a skill apura e prepara o DAS; nao transmite o PGDAS-D nem recolhe.
- **PA-11** — citar a norma (LC 123/2006, art. 18; CGSN 140/2018, art. 26-27) com artigo.
- **PA-13** — nao confundir regime (Simples) com obrigacao acessoria (DEFIS); respeitar a competencia.
- **PA-15** — DAS em atraso atualizado pelo encargo legal do ano, nunca valor nominal.

## 10. Protocolos acionados

- **P1 — Validacao Legal Previa** — Selo emitido por `validador-legislacao-vigente` antes do calculo.
- **P3 — Calculo** — memoria rastreavel, Python, aliquota efetiva com 4 casas.
- **P5 — Localizacao** — sublimite e ICMS/ISS dependem do ente.
- **P6 — Auditoria de Qualidade** — `revisao-final` R1-R4 antes da entrega.

## 11. Localizacao

O Simples concentra ICMS e ISS no DAS — mas a posicao da empresa em relacao ao **sublimite** depende da **UF** do estabelecimento, e a parcela de ICMS (UF) e de ISS (municipio) acima do sublimite passa ao regime normal local. ICMS-ST segue o RICMS da UF. Filial em outra UF e apurada por estabelecimento. Quando o sublimite do estado ou a regra municipal nao puder ser confirmada, marcar `[VERIFICAR — norma estadual/municipal]` (PA-05/PA-06).

## 12. Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.

**Entrega para:** `revisao-final` (R1-R4), o `CASO.md` e as obrigacoes do Tier 3. Demanda de litigio judicial (ex.: discussao judicial de exclusao) extrapola o contabil — encaminhar a advogado (slot generico).

**Sem esta skill:** o DAS e estimado sem segregacao de receita nem aliquota efetiva — risco de autuacao por DAS incorreto.
