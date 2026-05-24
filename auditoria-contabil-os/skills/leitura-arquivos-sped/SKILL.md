---
name: leitura-arquivos-sped
description: >
  Leitura de arquivos SPED em texto: EFD-Contribuicoes (PIS/COFINS), EFD ICMS/IPI e ECD (Escrituracao Contabil Digital). Identifica o tipo pelo registro 0000, conhece os blocos e registros principais de cada SPED (0, A-K, M, 9), extrai contribuinte, periodo e totais de apuracao, e confere integridade (registro 9999 versus linhas lidas). Base do cruzamento SPED x apurado x pago x declarado. Para volume, orienta o script parse_sped.py — parsing deterministico de arquivos com milhares de registros. Aciona: ler SPED, analisar EFD, EFD-Contribuicoes, EFD ICMS/IPI, ECD, arquivo da escrituracao digital, registros do SPED, conferir SPED, importar SPED.
---

# LEITURA DE ARQUIVOS SPED

> Skill **Tier 1** — Protocolo 2 (Ingestao) aplicado aos arquivos SPED em texto. Le e interpreta EFD-Contribuicoes, EFD ICMS/IPI e ECD; conhece os blocos e registros; confere integridade. Em volume, apoia-se no script `parse_sped.py`.

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com "ler SPED", "analisar EFD", "conferir o SPED", "registros do arquivo". Entrada: arquivo SPED em texto (`.txt`). Entrega: identificacao do tipo, contribuinte, periodo, contagem de registros por bloco e totais de apuracao — insumo para cruzamento e revisao fiscal.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.
- **Entrega para:** skills de obrigacoes acessorias do Tier 3 (`ecd`, `efd-icms-ipi`, `efd-contribuicoes`), apuracoes do Tier 2 (cruzamento), skills de recuperacao e auditoria (Tier 7, v0.3) e o `CASO.md`.
- **Le e confere** — a geracao/retificacao do SPED e das skills do Tier 3; a transmissao e do contador (PA-08).

## 2. Estrutura de um arquivo SPED

O SPED e um arquivo-texto com registros delimitados por pipe: `|REG|campo1|campo2|...|`. O primeiro campo de cada linha e o **codigo do registro**. Registros se organizam em **blocos** (1a letra/digito do codigo). Estrutura comum:

- **Bloco 0** — abertura, identificacao do contribuinte, tabelas (participantes, itens, contas).
- **Blocos intermediarios** — escrituracao propriamente dita (varia por tipo de SPED).
- **Bloco 9** — encerramento; registro **9999** declara o total de linhas do arquivo.

## 3. Os tres tipos de SPED cobertos

### EFD-Contribuicoes (PIS/COFINS)
Escrituracao de PIS e COFINS. Blocos principais:
- **A** — documentos de servico (NFS-e); **C** — documentos de mercadoria (NF-e/NFC-e); **D** — servico de transporte/comunicacao; **F** — demais documentos e operacoes.
- **M** — **apuracao** da contribuicao: M100/M105 (PIS), M500/M505 (COFINS), creditos e debitos.
- O bloco M e onde o PIS/COFINS apurado aparece — ponto-chave do cruzamento.

### EFD ICMS/IPI
Escrituracao fiscal de ICMS e IPI. Blocos principais:
- **C** — documentos fiscais de mercadoria; **D** — servico de transporte/comunicacao.
- **E** — **apuracao** do ICMS (E110) e do IPI (E520).
- **G** — ativo imobilizado (CIAP); **H** — inventario; **K** — producao e estoque (Bloco K).

### ECD (Escrituracao Contabil Digital)
Escrituracao contabil — substitui os livros Diario e Razao. Blocos principais:
- **I** — escrituracao contabil: I050 (plano de contas), I150 (saldos periodicos), I200/I250 (lancamentos contabeis).
- **J** — demonstracoes: J100 (balanco patrimonial), J150 (DRE).
- Registro 0000 da ECD traz o indicador `LECD`.

## 4. Identificacao do tipo

O `parse_sped.py` identifica o tipo pelo registro 0000 e pelos blocos presentes:
- 0000 com `LECD` → ECD; com `LECF` → ECF.
- Presenca do bloco **M** sem bloco E → EFD-Contribuicoes.
- Presenca do bloco **E** → EFD ICMS/IPI.
Quando a estrutura for ambigua, marcar `[VERIFICAR]` e confirmar com o operador.

## 5. Uso do script de parsing (volume)

Arquivos SPED tem facilmente milhares a centenas de milhares de linhas — **nunca** ler linha a linha no LLM. Usar o script:

```bash
# Resumo: tipo, contribuinte, periodo, contagem por bloco, integridade
python3 scripts/parse_sped.py casos/<slug>/arquivos/sped.txt
python3 scripts/parse_sped.py casos/<slug>/arquivos/sped.txt --json

# Capturar registros especificos (ex.: apuracao do ICMS e do PIS)
python3 scripts/parse_sped.py casos/<slug>/arquivos/sped.txt --registros E110,M100,M500
```

O script conta registros por bloco, identifica o tipo e confere o 9999. O LLM consome o resultado e pede apenas os registros relevantes via `--registros`.

## 6. Conferencia de integridade (Protocolo 2)

- **Registro 9999** — o total declarado bate com as linhas efetivamente lidas. Divergencia indica arquivo truncado ou corrompido.
- **Periodo** — as datas do registro 0000 cobrem a competencia esperada (PA-13).
- **Contribuinte** — CNPJ do 0000 e o do caso.
- **Blocos esperados presentes** — um EFD-Contribuicoes sem bloco M esta incompleto; uma EFD ICMS/IPI sem bloco E nao tem apuracao.
- Divergencia de integridade e apontada **antes** de qualquer cruzamento ou apuracao.

## 7. Cruzamento (Protocolo 4)

O SPED e a ponta de escrituracao do cruzamento fiscal:
- **SPED × apurado** — o ICMS no E110 / o PIS-COFINS no bloco M batem com a apuracao calculada pelas skills do Tier 2.
- **SPED × pago** — o apurado bate com o efetivamente recolhido (guia/DARF).
- **SPED × declarado** — o SPED bate com a DCTFWeb e demais declaracoes.
- Em **recuperacao de credito**, a ordem e: cruzar → **retificar o SPED** → so depois compensar via PER/DCOMP — nunca o inverso (PA-14).

## 8. Vedacoes especificas

- **PA-02** — usar apenas os registros reais do arquivo; nao presumir registro ausente.
- **PA-08** — esta skill le e confere; nao gera, nao retifica e nunca transmite o SPED (atos do Tier 3 e do contador).
- **PA-09** — arquivos SPED ficam em `casos/<slug>/arquivos/`, gitignored; sem mistura de clientes.
- **PA-13** — distinguir o regime de apuracao escriturado do que e obrigacao acessoria; respeitar a competencia.
- **PA-14** — em recuperacao, retificar o SPED antes de compensar.
- Nao ler arquivo SPED grande linha a linha — usar `parse_sped.py`.

## 9. Protocolos acionados

- **P2 — Ingestao e Conferencia de Arquivos** — esta skill **executa** o P2 para SPED.
- **P4 — Cruzamento e Conciliacao** — os dados de apuracao do SPED alimentam o cruzamento × apurado × pago × declarado.

## 10. Localizacao

A EFD ICMS/IPI e estadual — seu leiaute, registros e obrigatoriedade seguem o RICMS da **UF** do contribuinte (PA-05); o Bloco K e a EFD podem ter exigencias especificas por estado. A EFD-Contribuicoes e a ECD sao federais. Quando uma regra de obrigatoriedade ou de registro depender de norma estadual nao confirmada, marcar `[VERIFICAR — norma estadual]` (PA-06).

## 11. Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.

**Entrega para:** skills de obrigacoes acessorias do Tier 3, apuracoes do Tier 2 (cruzamento), skills de recuperacao e auditoria (v0.3) e o `CASO.md`. A entrega final passa por `revisao-final` (R1-R4).

**Sem esta skill:** o cruzamento e a revisao fiscal operam sem leitura conferida do SPED — risco de divergencia entre escriturado, apurado e declarado passar despercebida.
