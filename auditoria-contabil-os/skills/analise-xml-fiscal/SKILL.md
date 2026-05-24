---
name: analise-xml-fiscal
description: >
  Leitura e interpretacao de XML fiscal: NF-e (modelo 55), NFC-e (modelo 65), CT-e e NFS-e (padrao nacional e variacoes municipais). Extrai os campos-chave de cada documento e de cada item — CST/CSOSN, CFOP, NCM, CEST, valores, aliquotas, destaque de ICMS, ICMS-ST, IPI, ISS, PIS e COFINS, emitente, destinatario e chave de acesso. Confere integridade antes de usar (totais batem, sem nota duplicada). Para volume, orienta os scripts parse_nfe.py e parse_nfse.py — parsing deterministico, sem o LLM ler nota a nota. Aciona: analisar XML, ler nota fiscal, NF-e, NFC-e, CT-e, NFS-e, extrair CFOP/NCM/CST, conferir notas, importar XML, ingestao de notas.
---

# ANALISE DE XML FISCAL

> Skill **Tier 1** — Protocolo 2 (Ingestao e Conferencia de Arquivos) aplicado a documentos fiscais eletronicos. Le e interpreta NF-e, NFC-e, CT-e e NFS-e; extrai campos-chave; confere integridade. Em volume, apoia-se nos scripts `parse_nfe.py` e `parse_nfse.py`.

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com "analisar XML", "ler nota fiscal", "extrair CFOP/NCM", "conferir as notas do mes". Entrada: um ou mais XML fiscais (ou a pasta de arquivos do caso). Entrega: ficha estruturada dos documentos com campos-chave, totalizadores e flag de divergencias — insumo para apuracao (Tier 2) e escrituracao.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.
- **Entrega para:** apuracoes do Tier 2 (`calculo-icms-st`, `calculo-ipi`, `calculo-iss`, apuracoes de regime), skills de escrituracao (Tier 5, v0.2) e o `CASO.md` (secao "Arquivos do caso").
- **Nao calcula tributo** — extrai e confere os dados; o calculo e das skills de Tier 2, sempre apos o Selo (P1).

## 2. Tipos de XML cobertos

| Documento | Modelo | Uso contabil-fiscal | Script |
|-----------|--------|---------------------|--------|
| **NF-e** | mod. 55 | ICMS, IPI, ICMS-ST, escrituracao, cruzamento | `parse_nfe.py` |
| **NFC-e** | mod. 65 | Receita de varejo, ICMS varejo | `parse_nfe.py` |
| **CT-e** | conhec. de transporte | Credito de frete, ICMS transporte | `parse_nfe.py` |
| **NFS-e** | padrao nacional + municipais | ISS, retencao, receita de servico | `parse_nfse.py` |

## 3. Campos-chave por documento

### NF-e / NFC-e / CT-e (XML de produto/transporte)
- **Identificacao:** chave de acesso (44 digitos), numero, serie, data de emissao, natureza da operacao, modelo.
- **Partes:** emitente e destinatario — CNPJ/CPF, nome, **municipio e UF** (eixo de localizacao).
- **Por item:** codigo, descricao, **NCM**, **CFOP**, **CEST** (se ST), quantidade, valor.
- **Tributos por item:** **CST/CSOSN** de ICMS, base de calculo, aliquota, valor; CST e valor de IPI; valores de PIS e COFINS.
- **Totais:** valor dos produtos, valor da nota, BC e valor de ICMS, valor de ICMS-ST, IPI, PIS, COFINS, frete.

### NFS-e (XML de servico)
- Numero, data de emissao, layout (nacional ou municipal legado).
- Prestador e tomador — CNPJ/CPF, nome, municipio.
- **Item da lista de servicos** (LC 116/2003), discriminacao.
- **Municipio de incidencia do ISS**, base de calculo, **aliquota**, valor do ISS, indicador de ISS retido.

## 4. Leitura dos codigos fiscais

| Codigo | O que significa | Atencao |
|--------|-----------------|---------|
| **CFOP** | Natureza da operacao (entrada/saida, dentro/fora do estado) | 1o digito: 1/2/3 entrada, 5/6/7 saida; define direito a credito |
| **CST ICMS** | Situacao tributaria — regime normal (3 digitos) | 00 tributada integral, 60 ST ja recolhida, 40 isenta, 41 nao tributada |
| **CSOSN** | Situacao tributaria do Simples Nacional | 101/102 com/sem credito, 500 ST/antecipacao |
| **CST IPI** | Situacao do IPI | 50 saida tributada, 99 outras saidas |
| **NCM** | Classificacao da mercadoria (8 digitos) | Define aliquota de IPI e enquadramento de ST/monofasico |
| **CEST** | Codigo Especificador da ST | Presente quando a mercadoria esta sujeita a ICMS-ST |

A leitura correta de CFOP × CST/CSOSN × NCM e o que determina se a operacao gera credito, esta sob ST ou e monofasica. Divergencia entre CFOP e CST e sinalizada como inconsistencia.

## 5. Uso dos scripts de parsing (volume)

Para **volume** (dezenas a milhares de notas), nao ler XML a XML — usar os scripts deterministicos:

```bash
# NF-e / NFC-e / CT-e — arquivo unico ou pasta inteira
python3 scripts/parse_nfe.py casos/<slug>/arquivos/ --json
python3 scripts/parse_nfe.py casos/<slug>/arquivos/ --itens   # resumo + itens

# NFS-e — padrao nacional e layouts municipais
python3 scripts/parse_nfse.py casos/<slug>/arquivos/ --json
```

O script extrai campos-chave, totaliza e sinaliza notas em layout municipal legado. O LLM consome o **resultado tabulado**, nao o XML bruto. Para 1-3 notas, a leitura direta do XML e aceitavel.

## 6. Conferencia de integridade (Protocolo 2)

Antes de qualquer apuracao usar os dados:
- **Totais batem** — soma dos itens = total da nota; soma das notas = receita esperada da competencia.
- **Sem duplicidade** — nenhuma chave de acesso repetida.
- **Sem corrupcao** — XML valido, todos os campos obrigatorios presentes.
- **Periodo correto** — as datas de emissao cobrem a competencia do caso (PA-13 — competencia x caixa).
- **Sem nota cancelada computada** — notas canceladas/inutilizadas nao entram na receita.

Divergencia de integridade e apontada **antes** de qualquer calculo — nunca silenciada.

## 7. Vedacoes especificas

- **PA-02** — usar apenas os dados reais dos XML; campo ausente e sinalizado, nunca presumido.
- **PA-05** — a aliquota de ICMS depende da UF; a de ISS, do municipio de incidencia da NFS-e — nunca generica.
- **PA-06** — NFS-e em layout municipal nao reconhecido → `[VERIFICAR — layout municipal]`; nao inventar campo ausente.
- **PA-09** — os XML do caso ficam em `casos/<slug>/arquivos/`, gitignored; sem mistura de clientes.
- **PA-13** — distinguir a data de emissao (competencia) do efetivo recebimento (caixa).
- Nao calcular tributo nesta skill — extrair e conferir; o calculo e do Tier 2, apos o Selo.

## 8. Protocolos acionados

- **P2 — Ingestao e Conferencia de Arquivos** — esta skill **executa** o P2 para XML fiscal.
- **P4 — Cruzamento e Conciliacao** — os dados extraidos alimentam o cruzamento nota × SPED × apurado.
- **P5 — Localizacao** — emitente/destinatario e municipio de incidencia definem o ente competente.

## 9. Localizacao

A UF do emitente/destinatario define a aliquota de ICMS e o regime de ICMS-ST a aplicar; o **municipio de incidencia** da NFS-e define a aliquota de ISS e a lista de servicos. O script `parse_nfse.py` ja sinaliza notas em layout municipal legado — campos nao reconhecidos sao marcados `[VERIFICAR — layout municipal]` (PA-06). A cobertura de NFS-e municipal e reconhecidamente fragmentada.

## 10. Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.

**Entrega para:** as apuracoes do Tier 2 (insumo de receita e tributos destacados), as skills de escrituracao (v0.2) e o `CASO.md`. A entrega final passa por `revisao-final` (R1-R4).

**Sem esta skill:** a apuracao opera sem leitura conferida dos documentos fiscais — risco de receita errada, credito indevido e divergencia com o SPED.
