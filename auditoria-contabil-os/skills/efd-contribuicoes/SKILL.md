---
name: efd-contribuicoes
description: >
  Preparacao e conferencia da EFD-Contribuicoes mensal — escrituracao de PIS/COFINS por
  CST (Tabela 4.3.3), bloco M de apuracao (M100/M200/M500/M600), F500 (regime caixa do
  Presumido), F600 (CSRF sofrida), bloco P (CPRB) e conciliacao com a DCTFWeb. Base:
  IN RFB 1.252/2012, IN RFB 2.121/2022, Lei 14.592/2023, Decreto 8.426/2015. Aciona:
  preparar EFD-Contribuicoes, SPED PIS/COFINS, bloco M, CST 50/04/49, F500, F600, CPRB,
  conciliar com DCTFWeb, erro no PVA EFD-Contribuicoes.
---

# EFD-CONTRIBUICOES

> Skill **Tier 3** — obrigacao acessoria federal. Prepara e confere a EFD-Contribuicoes:
> consolida a apuracao de PIS e COFINS do mes. Exige o Selo de Validacao Legal Previa
> (P1) e e datada pelo ano do fato gerador. O plugin **prepara**; a transmissao e a
> responsabilidade tecnica sao do contador com CRC ativo (PA-07, PA-08).

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com
"preparar EFD-Contribuicoes", "SPED PIS/COFINS", "bloco M", "F500", "F600", "CPRB",
"conciliar com DCTFWeb". Entrada: CNPJ, competencia, regime (Real nao-cumulativo,
Presumido cumulativo, CPRB), XMLs de entrada/saida e NFS-e, apuracao interna de
PIS/COFINS, receitas monofasicas/exportacao/retencoes CSRF. Entrega: conferencia por
amostragem de notas, apuracao consolidada do bloco M, cruzamento com a DCTFWeb,
checklist de pre-validacao.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.
- **Aciona antes:** `validador-legislacao-vigente` (P1) — leiaute, Manual e a Tabela
  4.3.3 mudam; sem o Selo a preparacao nao comeca (PA-04).
- **Apoia-se em:** `analise-xml-fiscal` (CST PIS/COFINS por item), `leitura-arquivos-sped`
  (bloco M do TXT), `pis-cofins-cumulativo` e `pis-cofins-nao-cumulativo` (a apuracao
  interna que a EFD consolida).
- **Entrega para:** `dctfweb`, `revisao-final` (R1-R4) e o `CASO.md`.

## 2. Estrutura da EFD-Contribuicoes — blocos

```
0  Cadastros: 0140 estabelecimentos (regime), 0150 participantes,
   0200 itens (NCM, aliquotas), 0500 contas contabeis vinculadas a ECD
A  Servicos tomados/prestados (NFS-e)
C  Documentos de mercadoria (C170 com CST PIS/COFINS por item)
D  CT-e e similares
F  F500 receita por regime caixa, F550, F600 retencoes (CSRF), F700 deducoes
I  Operacoes financeiras
M  Apuracao: M100/M105 creditos de PIS, M200/M210 PIS devido por codigo de receita;
   M500/M505 creditos de COFINS, M600/M610 COFINS devida
P  Apuracao da CPRB (P100, P200)
1  1010, 1100, 1500 — retencoes complementares
9  Encerramento
```

**Prazo de entrega:** em regra ate o dia 10 (util) do segundo mes subsequente ao do
fato gerador — `[VERIFICAR]` o prazo do ano (IN RFB 1.252/2012 e atualizacoes).

## 3. CST de PIS/COFINS — Tabela 4.3.3

```
SAIDA (regime nao-cumulativo)
01 tributada aliquota basica   02 aliquota diferenciada   04 aliquota zero
05 substituicao tributaria     06 isenta                  07 suspensao
08 sem incidencia              09 diferimento             49 outras saidas

ENTRADA (creditos no nao-cumulativo)
50 com direito a credito (insumo, MP, energia)
51 vinculado a receita nao tributada     52 vinculado a exportacao
53 vinculado a tributada e nao tributada (rateio)
70 entrada com aliquota zero             98/99 outras
```

A Tabela 4.3.3 e atualizada — `[VERIFICAR]` a versao vigente (PA-06).

## 4. Bloco M — apuracao

- **M100/M105:** detalhamento dos creditos por tipo — insumo, energia eletrica,
  aluguel, depreciacao, frete na venda; o conceito de insumo segue o Tema 779 do STJ
  (essencialidade e relevancia). Cada credito identifica a fonte (CST 50/51/52/53).
- **M200/M210 e M600/M610:** PIS e COFINS devidos por codigo de receita.
- **Exclusao do ICMS (Tema 69 — RE 574.706):** o ICMS destacado e excluido da base de
  PIS/COFINS; a base do bloco M tem de refletir essa exclusao.
- **Receita financeira (Decreto 8.426/2015):** no nao-cumulativo, PIS 0,65% e COFINS 4%
  — nao e aliquota zero.

## 5. F500 (regime caixa) e F600 (retencoes)

- **F500:** receita das empresas do Presumido que optaram pelo regime de caixa.
- **F600:** retencoes de CSRF sofridas — quando o cliente PJ reteve PIS/COFINS/CSLL
  sobre o servico que a empresa prestou; essas retencoes sao compensadas no apurado.

## 6. Conferencia e cruzamento (P4)

- Cadastros 0140/0150/0200/0500 atualizados.
- CST de PIS/COFINS por item revisado contra a Tabela 4.3.3 (amostragem).
- Bloco M batendo com a apuracao interna (`pis-cofins-cumulativo`/`nao-cumulativo`).
- ICMS excluido da base (Tema 69).
- F500/F600 preenchidos.
- **Cruzamento com a DCTFWeb:** o PIS/COFINS do bloco M deve bater com os debitos
  confessados na DCTFWeb; divergencia relevante exige retificacao.

## 7. Anti-padroes

- CST de PIS/COFINS divergente entre a nota e o bloco M (entrada CST 50 sem o credito
  escriturado no M105).
- ICMS nao excluido da base (Tema 69) — divergencia com a DCTFWeb.
- F600 nao preenchido — perde a compensacao das retencoes sofridas.
- Tratar a receita financeira do nao-cumulativo como aliquota zero (Decreto 8.426/2015
  fixou 0,65% / 4%).
- Empresa cumulativa lancando creditos no bloco M100 (vedado no regime cumulativo).
- Esquecer o bloco P quando a empresa optou pela CPRB.
- Cravar prazo ou versao da Tabela 4.3.3 de memoria — `[VERIFICAR]`.

## 8. Casos de borda

- **Migracao Presumido → Real:** credito presumido sobre o estoque de abertura
  (Lei 10.637/2002, art. 11; Lei 10.833/2003, art. 12) escriturado no bloco M/F.
- **PJ do Real com atividades cumulativas** (Lei 10.833/2003, art. 10 — hospitais,
  transporte de passageiros, telecom): manter o regime cumulativo nessas receitas,
  com a codificacao correta.
- **CPRB em transicao:** a desoneracao da folha esta em encerramento progressivo
  (Lei 14.973/2024) — `[VERIFICAR]` se o bloco P ainda se aplica no ano.
- **Reforma tributaria:** PIS e COFINS serao substituidos pela CBS na transicao
  2026-2033; a EFD-Contribuicoes acompanha — `[VERIFICAR]` o regime do ano.

## 9. Vedacoes especificas

- **PA-01** — nao orientar credito indevido nem CST que mascare a operacao real.
- **PA-02** — preparar so com dado real (XMLs do mes, apuracao interna, retencoes).
- **PA-03** — datar a EFD pelo ano do fato gerador; PIS/COFINS estao em transicao para
  a CBS.
- **PA-04** — sem o Selo de Validacao Legal Previa, a preparacao nao comeca.
- **PA-06** — `[VERIFICAR]` no prazo, na versao da Tabela 4.3.3 e na vigencia da CPRB.
- **PA-07** — a saida e rascunho operacional; a responsabilidade tecnica e do contador
  com CRC ativo.
- **PA-08** — a skill prepara e confere; nao transmite a EFD nem recolhe o DARF.
- **PA-11** — citar a norma com artigo (IN RFB 1.252/2012; IN RFB 2.121/2022;
  Lei 14.592/2023; Decreto 8.426/2015; RE 574.706/STF — Tema 69).
- **PA-13** — nao confundir a apuracao de PIS/COFINS com a obrigacao acessoria EFD.

## 10. Protocolos acionados

- **P1 — Validacao Legal Previa** — Selo emitido por `validador-legislacao-vigente`,
  com o Manual da EFD-Contribuicoes do ano.
- **P2 — Ingestao** — XMLs via `analise-xml-fiscal`/`parse_nfe.py`/`parse_nfse.py`;
  TXT da EFD via `leitura-arquivos-sped`.
- **P4 — Cruzamento e Conciliacao** — bloco M × apuracao interna × DCTFWeb; em
  recuperacao, retificar o SPED antes de compensar (PA-14).
- **P6 — Auditoria de Qualidade** — `revisao-final` R1-R4 antes da entrega.

## 11. Localizacao

A EFD-Contribuicoes e obrigacao **federal** — leiaute, prazo e aliquotas de PIS/COFINS
valem em todo o pais e nao variam por municipio ou UF. O eixo geografico aparece de
forma indireta: o ICMS excluido da base (Tema 69) e estadual; a CBS, que substituira o
PIS/COFINS na reforma, tera reparticao federativa. Sem regra confirmada, `[VERIFICAR]`.

## 12. Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.

**Entrega para:** `dctfweb`, `revisao-final` (R1-R4) e o `CASO.md`. Os XMLs sao
conferidos por `analise-xml-fiscal`; o TXT da EFD e lido por `leitura-arquivos-sped`;
a apuracao consolidada vem de `pis-cofins-cumulativo` e `pis-cofins-nao-cumulativo`. A
recuperacao retroativa de PIS/COFINS pago a maior e trabalho de auditoria (Tier 7, v0.3).

**Sem esta skill:** a EFD-Contribuicoes e montada sem conferencia de CST nem cruzamento
com a DCTFWeb — risco de bloqueio no PVA, credito perdido e divergencia de malha PJ.
