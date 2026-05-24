---
description: Inicia o wizard de configuracao do plugin Auditoria Contabil OS — cria a pasta auditoria-contabil/ com identidade do contador, CRC, municipio/UF, frentes de atuacao, tom e modo de melhor saida fiscal.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint: [--update para reconfigurar]
---

Voce foi acionado pelo comando `/start-auditoria-contabil` do plugin Auditoria Contabil OS.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** configurar o plugin auditoria-contabil no ambiente do operador (contador / escritorio contabil).

## PROTOCOLO

1. **Acionar a skill `onboarding-contabil`** imediatamente — ela conduz o wizard completo.
2. O wizard cria `<cwd>/auditoria-contabil/` com `persona.md`, `config.md`, `casos/` e o `cowork-state.json`, alem de `.claude/settings.local.json`. Captura: identidade do contador, CRC e UF do CRC, escritorio, **municipio + UF** (eixo de ISS e ICMS — Protocolo 5), frentes de atuacao, tom de voz e `MODO_MELHOR_SAIDA` (recomendar-e-listar | apenas-listar).
3. Se ja existir `auditoria-contabil/cowork-state.json`, a skill oferece continuar / atualizar / recriar (idempotencia).
4. Se o argumento for `--update`, ir direto para o fluxo de atualizacao.

**Atencao LGPD (PA-09):** a skill avisa se o diretorio estiver em pasta sincronizada (iCloud/OneDrive/Dropbox/Drive) — dados de cliente nao devem ser sincronizados sem controle de acesso.

**Skill a acionar:** `onboarding-contabil`.
