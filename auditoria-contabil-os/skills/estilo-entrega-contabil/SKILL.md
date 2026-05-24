---
name: estilo-entrega-contabil
description: >
  Padrao de entrega de toda saida contabil-fiscal — estrutura do relatorio, formato da memoria de calculo, abertura com o Selo de Validacao Legal, fechamento com a ressalva de revisao e responsabilidade tecnica do contador (CRC), e tom tecnico-objetivo. Skill transversal invariante (Camada 3), acionada por toda skill produtora antes de redigir qualquer apuracao, obrigacao, relatorio, parecer ou deck. Aciona: formatar entrega, estrutura do relatorio, memoria de calculo, padrao de saida, como estruturar, ressalva CRC, estilo da entrega contabil.
---

# ESTILO ENTREGA CONTABIL

> Skill **transversal invariante** — Camada 3 (Identidade Tecnica e Estilo). Define a estrutura, o formato da memoria de calculo, a abertura, o fechamento e o tom de toda entrega do plugin. Acionada automaticamente por toda skill produtora (Tier 1-9) antes de redigir um documento. Invariante de sujeito e frente.

---

## 0. Escopo e acionamento

Acionada implicitamente por toda skill que produz entrega — apuracao, obrigacao preparada, relatorio, parecer, conciliacao, deck. Ativacao direta pelo operador: "formatar entrega", "estrutura do relatorio", "memoria de calculo", "padrao de saida", "como estruturar". Entrega: template de estrutura aplicado a saida solicitada, com tom ajustado pela persona do operador.

## 1. Posicao na orquestra

- **Chamada por:** toda skill produtora (Tier 1-9) ao iniciar a redacao de uma entrega.
- **Integra com:** `revisao-final` — a rodada R4 verifica se esta skill foi aplicada (estrutura presente, abertura e fechamento corretos, numeros batendo).
- **Pre-requisito para:** qualquer entrega — saida sem a estrutura canonica falha em R4.

## 2. Estrutura canonica da entrega contabil

Toda apuracao, relatorio, parecer e analise segue **6 secoes**:

### 1 — Escopo

```
ESCOPO
O que foi pedido: [descricao objetiva da demanda]
Sujeito: [PJ | PF]
Cliente: [nome / razao social — ou INFORMAR]
Competencia / ano do fato gerador: [MM/AAAA ou AAAA]
Localizacao: [municipio]/[UF]
Regime tributario (PJ): [Simples | Presumido | Real | MEI]
```

### 2 — Dados de entrada

```
DADOS DE ENTRADA
[Tabela ou lista dos dados REAIS do cliente usados na entrega, com a origem
 de cada um — arquivo XML, OFX, SPED, informe do cliente.]
Dado | Valor | Origem
[Dado faltante: marcar [INFORMAR] — nunca presumir (PA-02).]
```

### 3 — Base legal

```
BASE LEGAL
Data-base desta analise: [DD/MM/AAAA]
Normas aplicaveis (vigentes no ano do fato gerador):
- [Lei/LC/Decreto/IN — com o artigo exato e o ano de vigencia]
- [Norma estadual de ICMS / municipal de ISS, quando aplicavel]
- [MP/PL pendente relevante — marcar [VERIFICAR]]
```

Regra: toda norma citada recebe artigo/numero e ano de vigencia (PA-03, PA-11). Norma incerta ou de alvo movel → `[VERIFICAR]` (PA-06).

### 4 — Memoria de calculo

A secao mais critica. Formato canonico (P3) — ver secao 5.

### 5 — Resultado

```
RESULTADO
[Valores apurados, de forma consolidada.]
[Divergencias de cruzamento apontadas explicitamente — SPED x apurado x
 pago x declarado; banco x razao (P4).]
[Prazos e obrigacoes decorrentes, com vencimento (PA-18).]
```

### 6 — Ressalva

Fechamento obrigatorio — ver secao 7.

## 3. Abertura obrigatoria — Selo de Validacao Legal

Toda entrega que envolva calculo ou apuracao abre com o **Selo de Validacao Legal Previa** (Protocolo 1):

```
---------------------------------------------------------------------
SELO DE VALIDACAO LEGAL PREVIA
Data da validacao: [DD/MM/AAAA]
Normas validadas: [lista das normas auditadas]
Regime do ano: [Simples | Presumido | Real | MEI | transicao CBS/IBS]
Localizacao: [municipio]/[UF]
Vigencia confirmada: [sim | parcial — ver ressalvas]
Alertas: [PL/MP pendente, regra local nao confirmada — ou "nenhum"]
Emitido por: validador-legislacao-vigente
---------------------------------------------------------------------
```

Se o Selo ainda nao foi emitido, bloquear a redacao e acionar `validador-legislacao-vigente` (PA-04).

## 4. Fechamento obrigatorio — ressalva CRC

Toda entrega fecha com a ressalva de responsabilidade tecnica do contador:

```
---------------------------------------------------------------------
RESSALVA DE REVISAO E RESPONSABILIDADE TECNICA
Esta [apuracao / relatorio / parecer / minuta] e um rascunho operacional,
elaborado como suporte tecnico a partir das informacoes fornecidas e das
normas vigentes na data-base indicada. Nao substitui o juizo profissional
do contador responsavel. A conferencia, a decisao tecnica, a transmissao
e a assinatura da obrigacao/declaracao sao do contador com CRC ativo
(PA-07, PA-08). Revisao obrigatoria antes de qualquer ato formal.
Data de geracao: [DD/MM/AAAA]
Responsavel tecnico: {{CONTADOR_NOME}}, CRC/{{CRC_UF}} {{CRC_NUMERO}}
                     {{FIRM_NAME}}, {{MUNICIPIO}}/{{UF}}
---------------------------------------------------------------------
```

## 5. Formato da memoria de calculo (P3)

A memoria de calculo e **rastreavel** — cada numero pode ser conferido. Apresentada em tabela passo a passo. O resultado nunca aparece "solto".

```
MEMORIA DE CALCULO — [tributo/contribuicao] — competencia [MM/AAAA]

Etapa | Descricao              | Base de Calculo | Aliquota | Valor
1     | Receita bruta do mes   | R$ ...          |   —      | —
2     | (-) deducoes/exclusoes | R$ ...          |   —      | R$ ...
3     | Base de calculo        | R$ ...          |   —      | —
4     | Tributo apurado        | R$ ...          |  X,XX%   | R$ ...
5     | (+) multa, se em atraso| R$ ...          |  X,XX%   | R$ ...
6     | (+) juros Selic acum.  | R$ ...          |  X,XX%   | R$ ...
7     | TOTAL a recolher       |                 |          | R$ ...

Premissas: [cada premissa explicitada — competencia x caixa, anexo do
Simples, fator R, MVA, etc.]
Data-base da atualizacao: [DD/MM/AAAA]
```

Regras: cálculos com volume ou multiplas etapas sao feitos em Python (deterministico, auditavel). Atualizacao pela Selic acumulada com data de referencia (PA-15) — nunca valor nominal. Quando ha mais de uma opcao (comparativo de regime, competencia x caixa), apresentar os cenarios lado a lado, cada premissa explicitada.

## 6. Tom e voz

O tom respeita a persona configurada em runtime:

| Token | O que configura |
|-------|----------------|
| `{{TOM_VOZ_PERFIL}}` | Perfil — `tecnico-objetivo` (padrao), `tecnico-didatico`, `tecnico-cordial`, `personalizado` |
| `{{TOM_VOZ_INTENSIDADE}}` | Intensidade 0-10 — 0 = puramente didatico-cordial, 10 = maximo direto |

| Intensidade | Caracteristicas |
|-------------|----------------|
| 0-3 | Didatico: explica conceito, contextualiza a norma, tom acolhedor |
| 4-6 | Tecnico-objetivo (padrao): direto ao ponto, fundamentado, sem rodeios |
| 7-10 | Incisivo: foco no resultado e no risco, alertas destacados |

> Independente do tom, o rigor tecnico e a memoria de calculo sao sempre os mesmos — o tom afeta a densidade explicativa, nunca a precisao.

## 7. Pontos de omissao

Quando um dado necessario nao foi fornecido, nao supor — sinalizar:

```
[INFORMAR]: [dado ausente]   — ex: [INFORMAR]: faturamento do mes de competencia
[VERIFICAR]: [item a confirmar] — ex: [VERIFICAR]: aliquota de ISS do municipio
```

Acumular todos os pontos de omissao ao fim da entrega, em lista separada, para o operador.

## 8. Formato por tipo de entrega

- **Apuracao** — as 6 secoes; memoria de calculo e o nucleo; resultado com guia/prazo.
- **Obrigacao acessoria preparada** — escopo + dados + base legal + checklist de preenchimento + prazo + ressalva (o plugin prepara, nao transmite — PA-08).
- **Relatorio / diagnostico** — escopo + dados + achados com rastreabilidade (documento + norma — PA-19) + recomendacoes + ressalva.
- **Parecer** — as 6 secoes em prosa tecnica; conclusao objetiva respondendo a questao.
- **Deck de apresentacao** — todo numero vem de memoria de calculo verificavel (PA-20); a memoria acompanha o deck.

## 9. Vedacoes especificas

- **PA-04** — nunca redigir entrega de calculo sem o Selo de Validacao Legal na abertura.
- **PA-07** — a ressalva de responsabilidade tecnica do contador no fechamento e obrigatoria.
- **PA-11** — toda norma citada com artigo/numero; nada de "a lei diz".
- **PA-20** — nenhum numero "solto"; todo valor exibido tem origem na memoria de calculo.
- Nao usar o caractere en-dash (U+2013) como travessao — usar em-dash (`—`) ou virgula.

## 10. Protocolos acionados

- **Protocolo 1** (Validacao Legal Previa) — Selo na abertura.
- **Protocolo 3** (Calculo) — formato da memoria de calculo (secao 5).
- **Protocolo 5** (Localizacao) — municipio/UF explicitos no escopo e no Selo.

## 11. Localizacao

A localizacao (municipio + UF) e explicitada no Escopo (secao 1) e no Selo (secao 3) de toda entrega. ISS sempre referido ao municipio do caso, ICMS a UF (PA-05). Regra local nao confirmada aparece na entrega como `[VERIFICAR — norma municipal/estadual]` (PA-06).

## 12. Integracao

**Chamada por:** toda skill produtora (Tier 1-9) ao iniciar a redacao de uma entrega.

**Entrega para:** `revisao-final` — a rodada R4 verifica a aplicacao desta skill (estrutura, abertura, fechamento, coerencia dos numeros).

**Sem esta skill:** entregas saem sem estrutura canonica, sem Selo na abertura, sem ressalva CRC no fechamento — reprovadas em R4 da Revisao Tecnica. E invariante (nao-removivel).
