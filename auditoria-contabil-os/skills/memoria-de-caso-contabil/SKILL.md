---
name: memoria-de-caso-contabil
description: >
  Mantem o CASO.md persistente e compartimentado — uma pasta por cliente/caso, com sujeito (PJ/PF), frentes, localizacao municipio/UF, regime, prazos, Selo de Validacao Legal, entregas produzidas e historico. Skill transversal invariante. Garante sigilo dos dados do cliente (LGPD, PA-09): pasta de caso gitignored, sem mistura de clientes, alerta se sincronizada. Aciona: memoria do caso, retomar caso, historico, atualizar o caso, abrir caso novo, onde paramos, listar casos, /caso-contabil, registrar entrega.
---

# MEMORIA DE CASO CONTABIL

> Skill **transversal invariante** — gestao do `CASO.md` persistente por cliente/caso. Compartimentada por pasta: cada cliente tem sua propria pasta sob `<cwd>/auditoria-contabil/casos/`. Opera em todas as frentes (fiscal, obrigacoes, folha, escrituracao, PF, auditoria, recuperacao, operacional) e para sujeito PJ e PF.

---

## 0. Escopo e acionamento

Acionada com: "memoria do caso", "retomar caso", "historico do caso", "atualizar o caso", "abrir caso novo", "onde paramos", "listar casos", "registrar entrega". Tambem acionada automaticamente por `triagem-contabil` (criacao do `CASO.md` inicial) e por cada skill produtora ao finalizar uma entrega (atualizacao do historico).

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, qualquer skill produtora ao final de entrega, operador direto.
- **Entrega para:** todas as skills — o `CASO.md` e a fonte de contexto compartilhada do caso ativo.
- **Integra com:** `triagem-contabil` (criacao inicial), `validador-legislacao-vigente` (registro do Selo), `revisao-final` (registro do veredito R1-R4).

## 2. Estrutura de pastas

```
<cwd>/auditoria-contabil/
├── persona.md            (identidade do operador — fora do plugin)
├── config.md             (configuracoes do escritorio)
├── cowork-state.json     (estado do plugin)
└── casos/
    └── <slug-do-caso>/
        ├── CASO.md       (ficha master do caso)
        ├── MEMORY.md     (log de atualizacoes e entregas produzidas)
        └── arquivos/     (XML/OFX/CSV/SPED do caso — gitignored)
```

**Slug do caso:** formato `<cliente-slug>-<assunto-slug>` — ex: `empresa-abc-apuracao-simples`, `padaria-do-joao-efd-contribuicoes`. Letras minusculas, sem espacos, sem acentos, separado por hifens.

## 3. CASO.md — estrutura canonica

Ficha master do caso. Criado pela `triagem-contabil`, atualizado a cada entrega.

```markdown
# CASO.md — [Nome do Cliente / Empresa]
CNPJ/CPF: [numero ou INFORMAR]
Slug: [slug-do-caso]

## Identificacao
- Cliente: [nome / razao social]
- Sujeito: [PJ | PF]
- Responsavel tecnico: {{CONTADOR_NOME}}, CRC/{{CRC_UF}} {{CRC_NUMERO}}
- Escritorio: {{FIRM_NAME}}, {{MUNICIPIO}}/{{UF}}
- Data de abertura: [DD/MM/AAAA]
- Ano do fato gerador principal: [AAAA ou INFORMAR]

## Classificacao
- Frente(s): [fiscal | obrigacoes-acessorias | folha-dp | escrituracao |
  pessoa-fisica | auditoria | recuperacao | operacional-societario]
- Regime tributario (PJ): [Simples | Lucro Presumido | Lucro Real | MEI | N/A]
- CNAE / atividade principal: [codigo + descricao ou INFORMAR]
- Localizacao do cliente: [municipio]/[UF]  (eixo de ISS e ICMS — P5)

## Localizacao
- Municipio: [nome]  (ISS — aliquota e regra municipal)
- UF: [sigla]  (ICMS — aliquota e regra estadual)
- Observacao: [se o cliente esta em praca diferente da sede do escritorio]

## Prazos em curso
- Prazo mais urgente: [descricao — vence em DD/MM/AAAA]
- Obrigacoes do periodo: [lista — DAS, EFD, DCTFWeb, etc.]

## Resumo da demanda
[2-4 linhas descrevendo o que o cliente precisa]

## Documentos e arquivos recebidos
- [lista de arquivos em casos/<slug>/arquivos/ ou "nenhum ate o momento"]

## Selo de Validacao Legal
- [A emitir | Emitido em DD/MM/AAAA — normas: ... — regime do ano: ...]

## Entregas produzidas
| Data | Tipo de entrega | Skill produtora | Veredito R1-R4 |
|------|-----------------|-----------------|----------------|
| [DD/MM/AAAA] | [tipo] | [skill] | [APROVADO/REVISAR/BLOQUEADO/N/A] |

## Historico de updates
- [DD/MM/AAAA]: [descricao do que foi feito]
```

## 4. MEMORY.md — log de atualizacoes

O `MEMORY.md` dentro da pasta do caso e o diario de bordo tecnico — mais detalhado que o historico do `CASO.md`.

```markdown
# MEMORY.md — [slug-do-caso]

## Estado atual
- Frente ativa: [frente]
- Ultima etapa concluida: [descricao]
- Proximo passo: [acao imediata]

## Pendencias / Pontos de omissao
- [INFORMAR]: [dado ausente]
- [VERIFICAR]: [item a confirmar — ex: aliquota de ISS do municipio]

## Log cronologico
| Data | Evento | Skill | Detalhe |
|------|--------|-------|---------|
| [DD/MM/AAAA] | [evento] | [skill] | [detalhe tecnico] |
```

## 5. Operacoes

### 5.1 Criar caso novo

1. Verificar se ja existe pasta com o mesmo slug. Se sim, oferecer retomar.
2. Perguntar o nome do cliente e o assunto central (para compor o slug).
3. Criar a pasta `<cwd>/auditoria-contabil/casos/<slug>/` e a subpasta `arquivos/`.
4. Criar o `CASO.md` com o cabecalho canonico (secao 3), preenchido com os dados da triagem.
5. Criar o `MEMORY.md` inicial (secao 4).
6. Acionar `triagem-contabil` se a classificacao ainda nao foi feita.

### 5.2 Retomar caso existente

1. Localizar a pasta pelo slug (argumento) ou listar as pastas em `casos/`.
2. Ler o `CASO.md` e o `MEMORY.md`.
3. Apresentar o resumo:

```
RESUMO DO CASO — [cliente] | [slug]

Sujeito: [PJ | PF]
Frente(s): [lista]
Regime: [Simples | Presumido | Real | MEI | N/A]
Localizacao: [municipio]/[UF]
Selo de Validacao Legal: [emitido em DD/MM/AAAA | a emitir]
Prazo urgente: [prazo ou "nenhum em curso"]
Ultima etapa: [do MEMORY.md]
Pendencias: [lista de [INFORMAR] e [VERIFICAR]]
Proximo passo: [do MEMORY.md]
```

4. Perguntar se o operador quer continuar de onde parou ou iniciar nova etapa.

### 5.3 Atualizar caso apos entrega

Ao final de toda entrega aprovada pela `revisao-final`:

1. Abrir o `CASO.md` do caso ativo.
2. Adicionar a entrega na tabela "Entregas produzidas".
3. Registrar o veredito da Revisao Tecnica (R1-R4).
4. Atualizar prazos em curso e frente ativa, se mudaram.
5. Registrar o Selo de Validacao Legal, se foi emitido nesta etapa.
6. Adicionar entrada no "Historico de updates".
7. Atualizar o `MEMORY.md` com a nova entrada no log cronologico.

### 5.4 Listar casos

```
CASOS ATIVOS — {{FIRM_NAME}}
[Lista das pastas em casos/ com: slug, cliente, sujeito, frente(s),
 regime, localizacao, prazo urgente]
```

## 6. Compartimentacao por caso

**Regra absoluta:** cada caso ocupa sua propria pasta. Dados de um cliente nunca aparecem no `CASO.md` de outro.

- O operador pode ter multiplos casos abertos simultaneamente.
- O caso ativo e o referenciado no argumento do comando ou o mais recente atualizado.
- Em caso de ambiguidade, perguntar qual caso antes de qualquer acao.
- Um mesmo cliente com dimensoes PJ e PF (ex.: a empresa e o IRPF do socio) ocupa **casos separados** — nao misturar a apuracao da PJ com a declaracao da PF.

## 7. Privacidade e LGPD (PA-09)

Dados do cliente — CPF, CNPJ, faturamento, valores de tributo, arquivos fiscais — sao dados sensiveis.

- Os arquivos `CASO.md`, `MEMORY.md` e a pasta `arquivos/` residem no diretorio local do operador (`<cwd>/auditoria-contabil/casos/`) — **nunca no plugin**.
- A pasta `casos/` e gitignored por default.
- O plugin nao acessa esses dados remotamente.
- **Alerta automatico:** se o diretorio `casos/` for detectado dentro de pasta sincronizada (iCloud, OneDrive, Dropbox, Google Drive), emitir:

```
ALERTA LGPD: o diretorio casos/ parece estar em pasta sincronizada ([caminho]).
Dados de clientes (CNPJ, faturamento, arquivos fiscais) nao devem ser
sincronizados sem controle de acesso adequado. Mova para um diretorio
local seguro.
```

- Ao exibir dados de caso no chat, usar apenas os dados necessarios para a tarefa.

## 8. Vedacoes especificas

- **PA-09** — nunca mesclar dados de clientes distintos no mesmo `CASO.md`; pasta de caso sempre gitignored.
- **PA-07** — o operador e o contador responsavel; o plugin apenas organiza as informacoes.
- Nao criar caso sem ao menos o nome do cliente e o assunto central.
- Nao assumir qual caso esta ativo sem verificar — confirmar com o operador em ambiguidade.

## 9. Protocolos acionados

- **Protocolo 1** (Validacao Legal Previa) — o `CASO.md` registra se o Selo foi emitido e suas normas.
- **Protocolo 5** (Localizacao) — o `CASO.md` registra municipio e UF do cliente, eixo de ISS e ICMS.
- **Protocolo 6** (Auditoria de Qualidade) — o `CASO.md` registra o veredito R1-R4 de cada entrega.

## 10. Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, skills produtoras (atualizacao pos-entrega), operador direto.

**Entrega para:** todas as skills — o `CASO.md` e o contexto compartilhado do caso ativo.

**Sem esta skill:** cada sessao reinicia do zero; sujeito, frentes, localizacao, Selo, prazos e historico sao perdidos entre conversas. E invariante (nao-removivel).
