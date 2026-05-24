---
name: dimob
description: >
  Preparacao e conferencia da DIMOB — declaracao anual de imobiliarias,
  construtoras, incorporadoras e administradoras de bens. Conhece as quatro
  operacoes (01 comercializacao, 02 locacao, 03 intermediacao, 04 construcao),
  a validacao no PGD, a consolidacao de vendas parceladas e o IRRF sobre
  comissao e aluguel pago a PF. Base: IN RFB 1.115/2010, IN RFB 1.711/2017,
  RIR/2018 (Decreto 9.580/2018). Aciona: preparar DIMOB, cliente imobiliario,
  PGD DIMOB, Operacao 01-04, aluguel repassado, venda parcelada, comissao com
  IRRF, comprovante de rendimentos a vendedor/locador PF.
---

# DIMOB

> Skill **Tier 3** — obrigacao acessoria federal anual do setor imobiliario.
> Prepara e confere a DIMOB: declara as operacoes de venda, locacao,
> intermediacao e construcao. Exige o Selo de Validacao Legal Previa (P1) e e
> datada pelo ano-calendario do fato gerador. O plugin **prepara**; a
> transmissao e a responsabilidade tecnica sao do contador com CRC ativo
> (PA-07, PA-08).

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com
"preparar DIMOB", "cliente imobiliario", "PGD DIMOB", "Operacao 01/02/03/04",
"aluguel repassado", "venda parcelada na DIMOB", "comissao com IRRF". Entrada:
ano-calendario, CNPJ, tipo de empresa (construtora/incorporadora, imobiliaria,
administradora de bens, cooperativa habitacional), operacoes por tipo no ano,
exportacao do CRM/sistema imobiliario, IRRF retido, enderecos completos dos
imoveis. Entrega: tabela consolidada de operacoes por tipo, diagnostico de
pendencias para o PGD, checklist de validacao, comprovantes de IRRF a
beneficiarios PF.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.
- **Aciona antes:** `validador-legislacao-vigente` (P1) — o leiaute do PGD DIMOB
  e o prazo mudam por ano; sem o Selo a preparacao nao comeca (PA-04).
- **Apoia-se em:** `analise-extratos-ofx-csv` (conferencia do CSV exportado do
  CRM imobiliario), `retencoes-tomador` e `irrf-folha` (IRRF retido sobre
  comissao e sobre aluguel pago a PF).
- **Entrega para:** `revisao-final` (R1-R4) e o `CASO.md`.

## 2. Operacoes da DIMOB

```
01  Comercializacao  venda direta — incorporadora vendendo unidade
02  Locacao          administradora — alugueis recebidos em nome do proprietario
03  Intermediacao    imobiliaria — comissao recebida por venda/locacao
04  Construcao       incorporacao por administracao, lotes urbanos
```

Estao obrigadas, em regra, as pessoas juridicas que comercializam, intermediam
ou administram bens imoveis. O prazo era, em regra, o ultimo dia util de
fevereiro do ano seguinte — `[VERIFICAR]` o prazo, a multa e o piso do ano
(IN RFB 1.115/2010, IN RFB 1.711/2017; PA-06, PA-11).

## 3. Levantamento por tipo de empresa

- **Construtora / incorporadora:** Operacao 01 (vendas de unidades) e Operacao
  04 (construcao por administracao).
- **Imobiliaria:** Operacao 03 (comissoes de intermediacao).
- **Administradora de bens:** Operacao 02 (alugueis recebidos e repassados em
  nome do proprietario).
- Uma empresa pode acumular operacoes (imobiliaria que tambem administra
  alugueis declara 02 e 03).

## 4. Validacao tecnica antes do PGD

- CPF/CNPJ de todos os adquirentes, locatarios e locadores validos.
- Enderecos completos dos imoveis (CEP, numero, complemento).
- Datas e valores conferindo com os contratos.
- **Vendas parceladas:** somar as parcelas efetivamente pagas no ano-calendario
  — declara-se o que foi pago no ano, nao o valor total do contrato.
- **Locacao ativa parcial no ano:** considerar os meses do contrato (12 meses ou
  o periodo conforme inicio/fim).

## 5. Entregavel — tabela consolidada por operacao

```
DIMOB — ANO ____ — CNPJ ____

Operacao 01 — VENDAS
  N operacoes | Valor total: R$ ____ | IRRF: R$ ____
Operacao 02 — LOCACOES (administradora repassando)
  M contratos | Valor total no ano: R$ ____
Operacao 03 — INTERMEDIACAO
  P comissoes | Valor: R$ ____ | IRRF retido: R$ ____
Operacao 04 — CONSTRUCAO
  Q empreendimentos | Valor: R$ ____
```

A partir da tabela, o contador gera o arquivo para o PGD DIMOB (extraido do CRM
e ajustado) e transmite (PA-08).

## 6. Conferencia e cruzamento (P4)

- Todas as vendas do ano conferidas com os contratos.
- Locacoes ativas e repassadas — a administradora nao esquece o aluguel que
  administra mas nao e dela.
- Comissoes com IRRF retido informadas.
- CPF/CNPJ validos; enderecos completos.
- Validador do PGD com zero erros.
- **Cruzamento:** o IRRF retido sobre comissao e sobre aluguel pago a PF deve
  bater com a EFD-Reinf (R-4010, fato gerador a partir de 2024 — ver `efd-reinf`)
  ou com a DIRF do periodo legado (ano <= 2023 — ver `dirf`).

## 7. Comprovante de rendimentos

A empresa entrega ao vendedor PF e ao locador PF o comprovante de rendimentos
pagos e de IRRF retido (em regra cod 1708 para servico/comissao a PJ ou 3208
para aluguel pago a PF) — o beneficiario precisa dele para a declaracao de IRPF.

## 8. Anti-padroes

- A administradora esquecer a locacao repassada — administra, mas nao declara os
  alugueis em nome do proprietario.
- CPF do comprador invalido ou trocado entre adquirente e vendedor.
- Declarar a venda de imovel financiado pelo SFH pelas parcelas pagas no ano —
  declarar conforme o efetivamente pago no ano-calendario.
- Imovel vendido na planta — confundir o ano da venda com o ano da entrega.
- Locacao de curto prazo (hospedagem por temporada): o tratamento pode ser de
  hospedagem — `[VERIFICAR]` a solucao de consulta aplicavel.
- Cravar prazo, multa ou leiaute de memoria — `[VERIFICAR]`.

## 9. Casos de borda

- **Imovel vendido na planta entregue depois de mais de um ano:** declarar
  conforme as parcelas pagas em cada ano-calendario; o ano da entrega nao e o
  ano da venda.
- **Distrato de venda:** declarar como devolucao no ano em que o distrato
  ocorreu.
- **Permuta de imoveis:** tratamento especifico (RIR/2018) — confirmar a regra
  vigente.
- **Cooperativa habitacional:** regime proprio.
- **Ganho de capital na venda pela PF:** tema da frente de pessoa fisica
  (Tier futuro) — a DIMOB e o espelho que alimenta o cruzamento com o IRPF do
  vendedor.

## 10. Vedacoes especificas

- **PA-01** — nao orientar omissao de operacao nem valor a menor.
- **PA-02** — preparar so com dado real (operacoes do ano, contratos, IRRF).
- **PA-03** — datar a DIMOB pelo ano-calendario do fato gerador.
- **PA-04** — sem o Selo de Validacao Legal Previa, a preparacao nao comeca.
- **PA-06** — `[VERIFICAR]` no prazo, na multa, no leiaute do PGD e no
  tratamento da locacao de curto prazo.
- **PA-07** — a saida e rascunho operacional; a responsabilidade tecnica e do
  contador com CRC ativo.
- **PA-08** — a skill prepara e confere; nao transmite a DIMOB nem assina.
- **PA-11** — citar a norma com artigo (IN RFB 1.115/2010; IN RFB 1.711/2017;
  RIR/2018).
- **PA-13** — nao confundir a obrigacao acessoria (DIMOB) com a apuracao de
  tributo das operacoes imobiliarias.
- **PA-18** — sinalizar o prazo de entrega da DIMOB e a entrega do comprovante.

## 11. Protocolos acionados

- **P1 — Validacao Legal Previa** — Selo emitido por `validador-legislacao-vigente`,
  com o leiaute do PGD DIMOB e o prazo do ano.
- **P2 — Ingestao** — conferencia do CSV exportado do CRM via
  `analise-extratos-ofx-csv`.
- **P3 — Calculo** — consolidacao de vendas parceladas por ano-calendario como
  memoria rastreavel.
- **P4 — Cruzamento e Conciliacao** — operacoes x contratos; IRRF retido x
  EFD-Reinf/DIRF.
- **P6 — Auditoria de Qualidade** — `revisao-final` R1-R4 antes da entrega.

## 12. Localizacao

A DIMOB e obrigacao **federal** — leiaute, operacoes e prazo valem em todo o
pais e nao variam por municipio ou UF. O eixo geografico aparece de forma
indireta no **endereco do imovel**, que e campo obrigatorio da declaracao (CEP,
numero, complemento), mas nao altera a regra da obrigacao. Quando uma regra
acessoria nao puder ser confirmada, marcar `[VERIFICAR]` (PA-06).

## 13. Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.

**Entrega para:** `revisao-final` (R1-R4) e o `CASO.md`. O CSV do CRM imobiliario
e conferido por `analise-extratos-ofx-csv`; o IRRF retido sobre comissao e
aluguel se articula com `retencoes-tomador` e `irrf-folha`, e com a EFD-Reinf
(`efd-reinf`, R-4010) ou a DIRF legado (`dirf`) para o cruzamento. O ganho de
capital e o aluguel da PF sao da frente de pessoa fisica (Tier futuro).

**Sem esta skill:** as operacoes imobiliarias sao declaradas sem segregacao por
tipo nem checklist de validacao — risco de locacao esquecida, CPF trocado e
multa por atraso.
