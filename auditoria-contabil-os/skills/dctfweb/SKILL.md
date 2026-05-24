---
name: dctfweb
description: >
  Preparacao e conferencia da DCTFWeb — declaracao que confessa os debitos
  federais (INSS empresa CPP/RAT/Terceiros, INSS retido, IRRF folha, IRRF de
  PF/PJ, CSRF, IRPJ/CSLL, PIS/COFINS, IPI), vincula DARFs pagos e PER/DCOMP, e
  trata suspensao judicial. Conhece as modalidades (mensal, 13o, afericao de
  obra, reclamatoria trabalhista), os debitos importados do eSocial/EFD-Reinf e
  os lancamentos manuais. Base: IN RFB 2.005/2021, Lei 11.941/2009, Decreto
  70.235/1972. Aciona: preparar DCTFWeb, confessar debitos federais, DCTFWeb
  mensal/13o/afericao, lancamento manual de IRPJ/CSLL/PIS/COFINS/IPI, vincular
  DARF/PER-DCOMP, retificar DCTFWeb apos ajuste em eSocial/Reinf.
---

# DCTFWEB

> Skill **Tier 3** — obrigacao acessoria federal. Prepara e confere a DCTFWeb:
> a declaracao que **confessa** os debitos tributarios federais. Exige o Selo de
> Validacao Legal Previa (P1) e e datada pela competencia do fato gerador. O
> plugin **prepara**; a transmissao e a responsabilidade tecnica sao do contador
> com CRC ativo (PA-07, PA-08).

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com
"preparar DCTFWeb", "confessar debitos federais", "DCTFWeb mensal", "DCTFWeb do
13o", "afericao de obra", "lancar IRPJ manualmente", "vincular DARF", "retificar
DCTFWeb". Entrada: CNPJ, competencia, status do fechamento do eSocial (S-1299) e
da EFD-Reinf (R-2099/R-4099), apuracoes de IRPJ/CSLL/PIS/COFINS/IPI prontas,
DARFs ja pagos, PER/DCOMP em uso, processos com suspensao judicial. Entrega:
tabela de debitos esperados x confessados, lista de DARFs por codigo, plano de
retificacao se houver divergencia.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.
- **Aciona antes:** `validador-legislacao-vigente` (P1) — codigos de receita e
  regras mudam por ato; sem o Selo a preparacao nao comeca (PA-04).
- **Apoia-se em:** `efd-reinf` (R-2010/R-2020/R-4010/R-4020/R-2099/R-4099 — a
  EFD-Reinf alimenta a DCTFWeb), `inss-empresa` (CPP/RAT/Terceiros), `irrf-folha`
  (IRRF sobre folha e pro-labore), `retencoes-tomador` (INSS retido, CSRF) e nas
  apuracoes do Tier 2 (IRPJ/CSLL/PIS/COFINS/IPI lancados manualmente).
- **Entrega para:** `revisao-final` (R1-R4) e o `CASO.md`.

## 2. Modalidades da DCTFWeb

```
Mensal           todos os debitos federais a partir de 2024
13o salario      apenas o 13o (anual — competencia anual/dezembro)
Afericao de obra construcao civil — vinculada ao CNO
RT               decorrente de reclamatoria trabalhista (por sentenca)
```

A DCTFWeb absorveu as informacoes da antiga DCTF e da GFIP para os tributos
nela declarados. `[VERIFICAR]` o cronograma de obrigatoriedade por publico e o
prazo do ano (IN RFB 2.005/2021 e atualizacoes).

## 3. Pre-requisitos absolutos

A DCTFWeb e a **ultima etapa** da cadeia mensal. Antes de prepara-la:

- eSocial **S-1299** (fechamento) da competencia transmitido e aceito.
- EFD-Reinf **R-2099** e **R-4099** transmitidos e aceitos.
- Apuracoes de IRPJ/CSLL/PIS/COFINS/IPI da competencia fechadas (sao lancamentos
  manuais — nao vem de eventos).
- DARFs ja pagos no mes identificados (data, numero, valor).
- PER/DCOMP em uso identificadas.
- Processos com suspensao judicial mapeados.

Transmitir a DCTFWeb antes de fechar o eSocial/Reinf significa declarar com
debitos faltando.

## 4. Origem dos debitos — importados x lancados manualmente

```
IMPORTADOS automaticamente do eSocial/EFD-Reinf:
  CPP empresa, RAT x FAP, Terceiros (INSS empresa)   — eSocial
  INSS retido sobre cessao de mao de obra            — EFD-Reinf R-2010/R-2020
  IRRF folha, IRRF de PF/PJ, CSRF                    — EFD-Reinf R-4010/R-4020

LANCADOS MANUALMENTE (nao vem de eventos):
  IRPJ apuracao (trimestral ou anual)
  CSLL apuracao
  PIS                COFINS
  IPI
```

O codigo de receita de cada debito manual e definido pela apuracao
correspondente — `[VERIFICAR]` o codigo vigente no ano (PA-06, PA-11). Esquecer
um debito manual (IPI, PIS/COFINS, IRPJ) e o erro mais comum: ele nao chega via
evento e some da declaracao.

## 5. Sequencia de preparacao

1. Confirmar eSocial S-1299, EFD-Reinf R-2099 e R-4099 fechados e aceitos.
2. Acessar a DCTFWeb no e-CAC; conferir os debitos importados de eSocial/Reinf.
3. Lancar manualmente IRPJ/CSLL/PIS/COFINS/IPI da competencia.
4. Vincular os DARFs ja pagos (data, numero, valor) aos debitos correspondentes.
5. Vincular as PER/DCOMP em uso (numero, data).
6. Informar as suspensoes judiciais (numero do processo).
7. Conferir o saldo a pagar resultante.
8. O contador transmite a declaracao e emite os DARFs do saldo (PA-08).

## 6. Vencimentos dos tributos confessados

```
INSS empresa, INSS retido, IRRF folha      em regra dia 20 do mes seguinte
CSRF retida                                 quinzena seguinte ao pagamento
PIS / COFINS                                 em regra dia 25 do mes seguinte
IRPJ/CSLL Presumido (trimestral)             ultimo dia util do mes seguinte
IRPJ/CSLL Real estimativa                    ultimo dia util do mes seguinte
IPI                                          em regra dia 25 do mes seguinte
```

`[VERIFICAR]` cada vencimento no ano do fato gerador — datas e antecipacoes por
feriado mudam por exercicio (PA-06, PA-18). A DCTFWeb confessa; o vencimento do
DARF segue o tributo, nao a data de entrega da declaracao.

## 7. Conferencia e cruzamento (P4)

- eSocial S-1299, EFD-Reinf R-2099 e R-4099 fechados antes de gerar a DCTFWeb.
- Cada debito esperado presente: importados (eSocial/Reinf) + manuais.
- DARFs pagos e PER/DCOMP vinculados aos debitos certos (mesma competencia).
- Suspensoes judiciais com numero de processo informado.
- Saldo a pagar coerente com debitos menos vinculacoes.
- **Cruzamento:** o INSS e o IRRF confessados na DCTFWeb batem com a EFD-Reinf e
  o eSocial; IRPJ/CSLL/PIS/COFINS/IPI batem com as apuracoes do Tier 2.

## 8. Retificacao

Quando ha ajuste em evento antecedente (eSocial ou EFD-Reinf), a ordem e:

1. Retificar primeiro o evento eSocial/Reinf antecedente.
2. Aguardar o novo fechamento (S-1299 / R-2099 / R-4099).
3. So entao retificar a DCTFWeb — ela recebe o debito ajustado.
4. Recolher a diferenca com a atualizacao pela Selic acumulada (PA-15), se
   aplicavel.

Retificar a EFD-Reinf sem retificar a DCTFWeb correspondente deixa a declaracao
divergente do evento.

## 9. Anti-padroes

- Transmitir a DCTFWeb antes de fechar o eSocial/Reinf — debitos faltam.
- Esquecer um debito manual (IPI, PIS/COFINS, IRPJ) — nao vem de evento.
- Vincular DARF de outra competencia.
- Retificar a EFD-Reinf e nao retificar a DCTFWeb.
- Tratar a DCTFWeb transmitida como tributo pago — confessar nao e recolher.
- Cravar codigo de receita, prazo ou valor de multa de memoria — `[VERIFICAR]`.

## 10. Casos de borda

- **Empresa em recuperacao judicial** (Lei 14.112/2020): os debitos antigos
  seguem o plano de RJ; os debitos correntes vao na DCTFWeb normal.
- **Cliente em parcelamento** (Lei 10.522/2002): o debito original e confessado;
  as parcelas mensais sao recolhidas a parte.
- **Suspensao por liminar** (mandado de seguranca, anulatoria): informar o
  processo; o debito fica suspenso ate decisao definitiva — `encaminhar a
  advogado` o acompanhamento judicial (PA-16).
- **Empresa com filiais:** DCTFWeb consolidada — o CNPJ matriz aglutina.
- **Reclamatoria trabalhista paga:** gera DCTFWeb especifica na modalidade RT.
- **Empresa em CPRB:** a opcao pela desoneracao afeta o totalizador — confirmar
  a vigencia da CPRB no ano (`[VERIFICAR]`).

## 11. Vedacoes especificas

- **PA-01** — nao orientar omissao de debito nem confissao a menor.
- **PA-02** — preparar so com dado real (apuracoes, eventos fechados, DARFs).
- **PA-03** — datar a DCTFWeb pela competencia do fato gerador.
- **PA-04** — sem o Selo de Validacao Legal Previa, a preparacao nao comeca.
- **PA-06** — `[VERIFICAR]` no codigo de receita, no prazo, na multa e na
  vigencia da CPRB.
- **PA-07** — a saida e rascunho operacional; a responsabilidade tecnica e do
  contador com CRC ativo.
- **PA-08** — a skill prepara e confere; nao transmite a DCTFWeb nem recolhe os
  DARFs (atos do contador com certificado digital).
- **PA-11** — citar a norma com artigo (IN RFB 2.005/2021; Lei 11.941/2009;
  Decreto 70.235/1972).
- **PA-13** — nao confundir a confissao de debito (DCTFWeb) com a apuracao do
  tributo nem com o recolhimento.
- **PA-15** — diferenca de retificacao atualizada pela Selic acumulada.
- **PA-16** — acompanhamento de suspensao judicial e `encaminhar a advogado`.
- **PA-18** — sinalizar o prazo de entrega e os vencimentos dos DARFs.

## 12. Protocolos acionados

- **P1 — Validacao Legal Previa** — Selo emitido por `validador-legislacao-vigente`,
  com codigos de receita e regras da DCTFWeb do ano.
- **P3 — Calculo** — o saldo a pagar (debitos menos vinculacoes) e a diferenca de
  retificacao com Selic sao memoria rastreavel.
- **P4 — Cruzamento e Conciliacao** — DCTFWeb x eSocial x EFD-Reinf x apuracoes;
  apurado x declarado x pago.
- **P6 — Auditoria de Qualidade** — `revisao-final` R1-R4 antes da entrega.

## 13. Localizacao

A DCTFWeb e obrigacao **federal** — codigos, prazo e regras valem em todo o pais
e nao variam por municipio ou UF. O eixo geografico nao incide diretamente;
quando uma regra acessoria nao puder ser confirmada, marcar `[VERIFICAR]`
(PA-06).

## 14. Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.

**Entrega para:** `revisao-final` (R1-R4) e o `CASO.md`. A DCTFWeb e alimentada
pela `efd-reinf` (eventos de retencao) e pelo eSocial fechado; o INSS empresa vem
de `inss-empresa`, o IRRF de `irrf-folha`, as retencoes (INSS retido, CSRF) de
`retencoes-tomador`, e os debitos manuais de IRPJ/CSLL/PIS/COFINS/IPI das
apuracoes do Tier 2. O acompanhamento de suspensao judicial e o parcelamento
contencioso sao `encaminhar a advogado`.

**Sem esta skill:** os debitos federais sao confessados sem checklist de
pre-requisitos nem conferencia — risco de debito faltando, multa por atraso e
divergencia entre o declarado e os eventos.
