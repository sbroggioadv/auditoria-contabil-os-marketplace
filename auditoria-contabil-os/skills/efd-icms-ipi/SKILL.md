---
name: efd-icms-ipi
description: >
  Preparacao e conferencia da EFD ICMS/IPI mensal (SPED Fiscal) — escrituracao de
  documentos (C100/C170/C190, bloco D), apuracao do ICMS (E110/E111/E116) e do IPI
  (E520/E530), CIAP (bloco G), inventario (bloco H) e Livro de Producao (bloco K).
  Base: Convenio ICMS s/no 1970, Ajuste SINIEF 2/2009, LC 87/1996, LC 190/2022,
  Convenio 142/2018. Aciona: preparar EFD ICMS/IPI, SPED Fiscal, apuracao do ICMS,
  ajuste E111, Tabela 5.1.1, bloco K, CIAP, inventario anual, DIFAL, erro no PVA.
---

# EFD ICMS/IPI

> Skill **Tier 3** — obrigacao acessoria estadual. Prepara e confere a EFD ICMS/IPI:
> consolida os documentos fiscais e a apuracao de ICMS e IPI do mes. Exige o Selo de
> Validacao Legal Previa (P1) e e datada pelo ano do fato gerador. O plugin **prepara**;
> a transmissao e a responsabilidade tecnica sao do contador com CRC ativo (PA-07, PA-08).

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com
"preparar EFD ICMS/IPI", "SPED Fiscal", "ajuste E111", "Tabela 5.1.1", "bloco K",
"CIAP", "inventario anual", "DIFAL". Entrada: CNPJ, competencia, UF (matriz e filiais),
XMLs de entrada/saida e CT-e, tipo de atividade (industria/atacadista para o bloco K),
saldo credor anterior, beneficios fiscais, inventario de 31/12 quando for a competencia
de fevereiro. Entrega: conferencia dos XMLs, apuracao E110/E520, ajustes E111 com
codigo, checklist de pre-validacao.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.
- **Aciona antes:** `validador-legislacao-vigente` (P1) — leiaute, Manual, alíquotas e
  a Tabela 5.1.1 sao estaduais e mudam; sem o Selo a preparacao nao comeca (PA-04).
- **Apoia-se em:** `analise-xml-fiscal` (campos dos XMLs — CST, CFOP, NCM, valores),
  `leitura-arquivos-sped` (registros E110/E520 do TXT), `calculo-icms-st` e `calculo-ipi`
  (a EFD consolida o que foi apurado).
- **Entrega para:** `dctfweb`, `revisao-final` (R1-R4) e o `CASO.md`.

## 2. Estrutura da EFD ICMS/IPI — blocos

```
0  Cadastros: 0150 participantes, 0200 itens (NCM), 0300 ativo imobilizado
B  ISS — opcional, alguns estados
C  NF-e, NFC-e, modelos antigos: C100 cabecalho, C170 itens, C190 analitico
D  CT-e (frete) e documentos de comunicacao
E  Apuracao do ICMS: E110 ICMS proprio, E111 ajustes, E116 obrigacoes a recolher
   Apuracao do ICMS-ST: E200/E210 por UF     DIFAL: E300+ (pos LC 190/2022)
   Apuracao do IPI: E520, E530 ajustes
G  CIAP — credito de ICMS do imobilizado em 48 parcelas (G110, G125)
H  Inventario (H010, H020) — anual, na EFD de fevereiro
K  Livro de Producao: K200 estoque, K220 movimentacao, K230 producao,
   K235 insumos consumidos, K250 producao de terceiros — industria/atacadista
1  Outras informacoes (1200 creditos extemporaneos, 1300 combustiveis)
9  Encerramento
```

**Prazo de entrega:** em regra o dia 25 do mes seguinte, mas o calendario e definido
por **cada UF** — `[VERIFICAR — prazo estadual]` (PA-05/PA-06).

## 3. Conferencia dos documentos (C170/C190)

O C190 consolida por **CST + CFOP + aliquota**, base para a apuracao do E110/E116.
Conferir os XMLs do mes contra a EFD: quantidade de notas, CFOP e CST coerentes com a
operacao. Para volume, `analise-xml-fiscal` e `parse_nfe.py` extraem os campos.

## 4. Apuracao do ICMS (bloco E110)

```
DEBITOS  = debitos das NFs de saida (E110) + ajustes a debito (E111)
CREDITOS = creditos das NFs de entrada + ajustes a credito (E111)
SALDO APURADO = saldo anterior + creditos - debitos
Saldo devedor -> ICMS a recolher (E116)   Saldo credor -> carrega
```

Os ajustes do E111 exigem o **codigo da Tabela 5.1.1 da UF** — cada estado tem a sua
tabela de codigos de ajuste; `[VERIFICAR — Tabela 5.1.1 da UF]`. O DIFAL pos LC 190/2022
e escriturado no bloco E300.

## 5. CIAP (bloco G — 48 parcelas)

O ICMS do ativo imobilizado e creditado em 48 parcelas:

```
Credito mensal = (ICMS do imobilizado x receita tributada / receita total) / 48
```

G110 controla o bem; G125 registra a parcela mensal. NF de aquisicao de imobilizado
sem CIAP escriturado = credito perdido.

## 6. Inventario (bloco H) e Livro de Producao (bloco K)

- **Bloco H:** levantamento fisico de 31/12, entregue na EFD de **fevereiro** do ano
  seguinte. Cada item: NCM, unidade, quantidade, valor unitario e total.
- **Bloco K:** obrigatorio para industria e atacadista acima do limite estadual
  (`[VERIFICAR]`). K235 sem ficha tecnica do produto e consumo desproporcional a
  producao geram autuacao; o estoque do K200 deve bater com o inventario do H010.

## 7. Anti-padroes

- CFOP generico para operacao especifica (ex.: 5.949 onde cabe 5.102/5.405).
- CST/CSOSN incompativel com o regime do emitente (CSOSN so em emitente do Simples).
- Bloco K sem ficha tecnica do produto — autuacao.
- NF de imobilizado sem CIAP — perde o credito de 48 parcelas.
- Nao escriturar o CT-e — perde o credito de ICMS do frete.
- Inventario do bloco H nao entregue na competencia de fevereiro — multa.
- DIFAL pos LC 190/2022 escriturado fora do bloco E300.
- Cravar aliquota interna, prazo estadual ou codigo da Tabela 5.1.1 de memoria.

## 8. Casos de borda

- **Empresa em ZFM/ALC:** regime especifico de suspensao; tratar pela norma local.
- **Brindes/amostras:** CFOP 5.910/6.910, em regra sem ICMS.
- **Devolucoes:** CFOP da serie 1.201/2.201/5.201/6.201, com creditos espelho.
- **Transferencia entre estabelecimentos:** a transferencia interna entre filiais do
  mesmo titular nao gera ICMS (ADC 49 STF) — confirmar a regra da UF e a modulacao
  vigente (`[VERIFICAR]`).

## 9. Vedacoes especificas

- **PA-01** — nao orientar credito indevido nem CFOP/CST que mascare a operacao real.
- **PA-02** — preparar so com dado real (XMLs do mes, saldo anterior, inventario).
- **PA-03** — datar a EFD pelo ano do fato gerador; leiaute e tabelas mudam.
- **PA-04** — sem o Selo de Validacao Legal Previa, a preparacao nao comeca.
- **PA-05** — ICMS sempre com base na **UF** do estabelecimento; sem aliquota generica.
- **PA-06** — `[VERIFICAR]` no prazo estadual, no codigo da Tabela 5.1.1 e no limite
  estadual do bloco K.
- **PA-07** — a saida e rascunho operacional; a responsabilidade tecnica e do contador
  com CRC ativo.
- **PA-08** — a skill prepara e confere; nao transmite a EFD nem recolhe a guia.
- **PA-11** — citar a norma com artigo (LC 87/1996; LC 190/2022; Convenio 142/2018;
  Ajuste SINIEF 2/2009; RICMS da UF).
- **PA-13** — nao confundir a apuracao do ICMS/IPI com a obrigacao acessoria EFD.

## 10. Protocolos acionados

- **P1 — Validacao Legal Previa** — Selo emitido por `validador-legislacao-vigente`,
  com o Manual da EFD ICMS/IPI e a norma estadual do ano.
- **P2 — Ingestao** — XMLs via `analise-xml-fiscal`/`parse_nfe.py`; TXT da EFD via
  `leitura-arquivos-sped`.
- **P4 — Cruzamento e Conciliacao** — XMLs × C100/C170; apuracao E110/E520 × calculo
  do Tier 2 × DCTFWeb; estoque K200 × inventario H010.
- **P5 — Localizacao** — a EFD ICMS/IPI e estadual: prazo, aliquota, Tabela 5.1.1 e
  bloco K seguem a UF.
- **P6 — Auditoria de Qualidade** — `revisao-final` R1-R4 antes da entrega.

## 11. Localizacao

A EFD ICMS/IPI e obrigacao **estadual** — e o eixo geografico desta skill. Leiaute,
prazo de entrega, aliquotas internas, codigos de ajuste da Tabela 5.1.1, regras de
DIFAL e o limite de obrigatoriedade do bloco K sao definidos pelo RICMS de cada **UF**.
Para estabelecimentos em UFs diferentes (matriz e filiais), cada um segue a sua UF. O
IPI e federal — aliquota uniforme da TIPI. Sem regra estadual confirmada, marcar
`[VERIFICAR — norma estadual]` (PA-05/PA-06).

## 12. Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.

**Entrega para:** `dctfweb`, `revisao-final` (R1-R4) e o `CASO.md`. Os XMLs sao
conferidos por `analise-xml-fiscal`; o TXT da EFD e lido por `leitura-arquivos-sped`;
a apuracao consolidada vem de `calculo-icms-st` e `calculo-ipi`. A recuperacao
retroativa de ICMS pago a maior e trabalho de auditoria (Tier 7, v0.3).

**Sem esta skill:** a EFD ICMS/IPI e montada sem conferencia dos XMLs nem checklist de
CIAP/inventario/bloco K — risco de bloqueio no PVA, credito perdido e autuacao.
