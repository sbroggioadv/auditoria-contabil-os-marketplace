---
description: Abre um caso contabil novo ou retoma um caso existente — cria/le a pasta do caso, o CASO.md e o MEMORY.md, com sujeito (PJ/PF), frentes e localizacao.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint: [nome do caso — ex: empresa-x-apuracao-simples]
---

Voce foi acionado pelo comando `/caso-contabil` do plugin Auditoria Contabil OS.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** abrir um caso novo ou retomar um caso existente.

## PROTOCOLO

1. **Acionar a skill `memoria-de-caso-contabil`**.
2. Se o argumento corresponde a um caso existente em `auditoria-contabil/casos/`, **retomar** — ler o `CASO.md` e o `MEMORY.md`, apresentar resumo (sujeito PJ/PF, frente(s), regime, localizacao municipio/UF, Selo de Validacao Legal, ultima etapa, pendencias, prazos).
3. Se nao existe, **abrir caso novo** — acionar a `triagem-contabil` para colher sujeito, frente(s), localizacao, regime, CNAE, competencia e prazos, e criar a pasta `casos/<slug-do-caso>/` com `CASO.md`, `MEMORY.md` e a subpasta `arquivos/`.
4. Confirmar com o operador antes de criar a pasta.
5. **LGPD (PA-09):** alertar se a pasta `casos/` estiver em diretorio sincronizado — dados de cliente nunca sincronizados sem controle de acesso.

**Skills a acionar:** `memoria-de-caso-contabil` (e `triagem-contabil` se for caso novo).
