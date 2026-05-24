---
description: Ativa a cadeia completa de operacao contabil-fiscal — 4 Camadas, 20 Proibicoes Absolutas, 6 Protocolos Tecnicos e Revisao Tecnica R1-R4. Comando-coracao do plugin.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint: [contexto opcional da demanda]
---

Voce foi acionado pelo comando `/contabil-master` do plugin Auditoria Contabil OS.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** ativar a cadeia completa de operacao contabil-fiscal. A partir deste comando, toda demanda passa pela governanca integral do plugin.

## PROTOCOLO

1. **Verificar configuracao** — procurar `auditoria-contabil/cowork-state.json` subindo a arvore. Se nao encontrar, sugerir `/start-auditoria-contabil`; se o operador declinar, operar em modo fallback generico.
2. **Acionar a skill `auditoria-contabil-master`** (Tier 0) — ela carrega a Hierarquia das 4 Camadas, as 20 PAs, os 6 Protocolos, o mapa de roteamento por Tier e a regra de que nenhuma skill de calculo roda sem o Selo de Validacao Legal Previa.
3. **Saudar o operador** apresentando: contador responsavel, escritorio, diretorio, municipio/UF, frentes ativas, Revisao Tecnica (ativa/desativada).
4. **Conduzir** toda demanda subsequente pelo pipeline: `triagem-contabil` → ingestao de arquivos (se houver) → `validador-legislacao-vigente` (Selo) → Tier correto (apuracao/obrigacao) → `revisao-final` R1-R4 → entrega + atualiza `CASO.md`.
5. Faltando dado essencial: sinalizar Ponto de Omissao `[INFORMAR]`, nunca inventar (PA-02).
6. Demanda de Tier ainda nao liberado na v0.1 (folha, escrituracao, IRPF, auditoria, recuperacao, operacional): sinalizar ao operador e cobrir o possivel com os Tiers 0-3.

**Skill a acionar:** `auditoria-contabil-master`.
