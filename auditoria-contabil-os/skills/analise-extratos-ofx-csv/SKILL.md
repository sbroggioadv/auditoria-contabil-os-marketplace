---
name: analise-extratos-ofx-csv
description: >
  Leitura de extrato bancario OFX e de arquivos CSV — extratos de conta, relatorios de adquirentes e credenciadoras de cartao, planilhas de movimento. Extrai lancamentos, datas, valores, saldos, creditos e debitos; identifica taxas de adquirente; confere integridade (saldo inicial mais movimento igual a saldo final). Base da conciliacao bancaria e de cartoes (banco x razao). Para volume, orienta o script parse_ofx.py — parsing deterministico de OFX 1.x SGML e 2.x XML. Aciona: analisar extrato, ler OFX, conciliacao bancaria, conciliar cartao, relatorio de adquirente, importar CSV, extrato de conta, movimento bancario, conferir banco.
---

# ANALISE DE EXTRATOS OFX E CSV

> Skill **Tier 1** — Protocolo 2 (Ingestao) e base do Protocolo 4 (Cruzamento) aplicados a extrato bancario OFX e a arquivos CSV. Le, estrutura e confere os lancamentos para conciliacao bancaria e de cartoes. Em volume, apoia-se no script `parse_ofx.py`.

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com "analisar extrato", "ler OFX", "conciliacao bancaria", "conciliar cartao", "relatorio de adquirente", "importar CSV". Entrada: arquivo OFX de extrato bancario ou CSV (extrato, relatorio de adquirente, planilha de movimento). Entrega: extrato estruturado com lancamentos, totais e flag de divergencias — insumo da conciliacao.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.
- **Entrega para:** skills de conciliacao bancaria e de cartoes (Tier 5, v0.2), apuracao de receita (Tier 2), auditoria (Tier 7, v0.3) e o `CASO.md`.
- **Nao escritura** — le e confere os lancamentos; o lancamento contabil e da escrituracao (v0.2).

## 2. Arquivo OFX — extrato bancario

O **OFX** (Open Financial Exchange) e o formato de extrato exportado pelos bancos. Duas versoes:
- **OFX 1.x** — SGML, tags sem fechamento (`<TRNAMT>123.45` sem `</TRNAMT>`).
- **OFX 2.x** — XML bem-formado.

O script `parse_ofx.py` cobre as duas. Campos extraidos:
- **Conta:** banco, agencia, numero, tipo de conta, moeda.
- **Periodo:** data inicial e final do extrato.
- **Por lancamento:** tipo (credito/debito), data (`DTPOSTED`), valor (`TRNAMT` — negativo = debito), identificador (`FITID`), descricao (`MEMO`/`NAME`).
- **Saldo:** saldo final informado (`BALAMT`) e data de referencia.

## 3. Arquivos CSV — extratos e adquirentes

CSV nao tem layout unico — cada banco, adquirente e ERP exporta de um jeito. A skill identifica as colunas pela leitura do cabecalho:

| Origem do CSV | Colunas tipicas | Uso |
|---------------|-----------------|-----|
| **Extrato bancario** | data, historico, valor, saldo | Conciliacao bancaria |
| **Adquirente / credenciadora** | data da venda, data do credito, bandeira, bruto, taxa MDR, liquido, parcelas | Conciliacao de cartoes, receita |
| **Relatorio de vendas / ERP** | data, documento, valor, cliente | Cruzamento com notas fiscais |

No CSV de **adquirente**, atentar: o valor **bruto** da venda e a receita; a **taxa MDR** e despesa financeira; o valor **liquido** e o que entra no banco. A data da venda (competencia) difere da data do credito (caixa) — PA-13.

## 4. Uso do script de parsing (volume)

```bash
# Extrato OFX — resumo de integridade e totais
python3 scripts/parse_ofx.py casos/<slug>/arquivos/extrato.ofx
python3 scripts/parse_ofx.py casos/<slug>/arquivos/extrato.ofx --json
python3 scripts/parse_ofx.py casos/<slug>/arquivos/extrato.ofx --lancamentos
```

O script estrutura banco/agencia/conta, periodo, totais de credito e debito e o saldo final. O LLM consome o resultado tabulado. Para CSV, a leitura e direta (formato variavel) — identificar as colunas e tratar como tabela; o LLM le CSV nativamente, mas conferir totais.

## 5. Conferencia de integridade (Protocolo 2)

Antes de usar os dados na conciliacao:
- **Equacao do saldo** — saldo inicial + total de creditos + total de debitos = saldo final informado. Divergencia indica extrato incompleto ou lancamento faltante.
- **Periodo completo** — o extrato cobre toda a competencia, sem lacuna de dias.
- **Sem duplicidade** — nenhum `FITID` (OFX) ou documento (CSV) repetido.
- **Adquirente** — bruto - taxa = liquido em cada linha; a soma dos liquidos bate com os creditos no extrato bancario.

## 6. Conciliacao — banco x razao (Protocolo 4)

A skill **prepara** a conciliacao; a conciliacao contabil propriamente dita e da escrituracao (v0.2). O cruzamento tipico:
- Cada credito do extrato deve ter contrapartida no razao (recebimento de cliente, venda em cartao, aporte).
- Cada debito deve ter contrapartida (pagamento de fornecedor, tributo, despesa, tarifa).
- Lancamento no extrato sem contrapartida no razao, ou vice-versa, e **divergencia** — apontada explicitamente, nunca silenciada.
- Receita de cartao: a venda bruta entra como receita; a taxa MDR, como despesa; so o liquido transita no banco.

## 7. Vedacoes especificas

- **PA-02** — usar apenas os lancamentos reais dos arquivos; nao presumir lancamento ausente.
- **PA-09** — extratos e relatorios ficam em `casos/<slug>/arquivos/`, gitignored; sem mistura de clientes (dado bancario e sigiloso).
- **PA-13** — distinguir a data da venda/fato gerador (competencia) da data do credito/recebimento (caixa); nao confundir receita bruta com valor liquido.
- **P4** — toda divergencia de conciliacao e apontada — valor, as duas pontas e a causa provavel.
- Nao escriturar nesta skill — le e confere; o lancamento e da escrituracao (v0.2).

## 8. Protocolos acionados

- **P2 — Ingestao e Conferencia de Arquivos** — esta skill **executa** o P2 para OFX e CSV.
- **P4 — Cruzamento e Conciliacao** — prepara a conciliacao banco × razao e cartao × extrato.

## 9. Localizacao

O extrato bancario e nacional — nao tem eixo geografico proprio. A localizacao entra de forma indireta: a receita identificada no extrato (vendas, servicos) alimenta apuracoes de ICMS (UF) e ISS (municipio) feitas em outras skills. Quando o relatorio de adquirente traz vendas de varias pracas, sinalizar para que a apuracao trate a localizacao de cada operacao.

## 10. Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.

**Entrega para:** skills de conciliacao (v0.2), apuracao de receita (Tier 2), auditoria (v0.3) e o `CASO.md`. A entrega final passa por `revisao-final` (R1-R4).

**Sem esta skill:** a conciliacao bancaria e de cartoes opera sem leitura conferida dos extratos — risco de receita omitida, divergencia de saldo e despesa financeira nao registrada.
