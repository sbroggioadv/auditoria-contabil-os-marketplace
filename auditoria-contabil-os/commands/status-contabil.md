---
description: Mostra o estado do caso contabil ativo — sujeito, frente(s), regime, localizacao, Selo de Validacao Legal, prazos, pendencias, entregas produzidas e configuracao do plugin.
allowed-tools: Read, Bash, Glob, Grep
argument-hint: [nome do caso — opcional]
---

Voce foi acionado pelo comando `/status-contabil` do plugin Auditoria Contabil OS.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** apresentar um diagnostico do caso contabil ativo (ou do indicado no argumento) e da configuracao do plugin.

## PROTOCOLO

1. Localizar o caso: se o argumento indica um caso, usar; senao, usar o caso ativo / o mais recente em `auditoria-contabil/casos/`.
2. **Ler o `CASO.md`** e o `MEMORY.md` do caso (mantidos pela `memoria-de-caso-contabil`).
3. Apresentar o resumo:

```
STATUS — [cliente] | [slug-do-caso]

Sujeito: [PJ | PF]
Frente(s): [fiscal | obrigacoes-acessorias | folha-dp | escrituracao |
           pessoa-fisica | auditoria | recuperacao | operacional-societario]
Regime tributario: [Simples | Lucro Presumido | Lucro Real | MEI | N/A]
CNAE / atividade: [codigo + descricao]
Localizacao: [municipio]/[UF]
Selo de Validacao Legal: [emitido em DD/MM/AAAA — normas: ... | a emitir]
Prazo urgente: [prazo ou "nenhum em curso"]
Ultima etapa concluida: [do MEMORY.md]
Pendencias / Pontos de omissao: [lista de [INFORMAR] e [VERIFICAR]]
Entregas produzidas: [lista com veredito R1-R4]
Proximo passo sugerido: [do MEMORY.md]
```

4. Exibir tambem o estado da configuracao do plugin:

```
CONFIGURACAO DO PLUGIN
Contador: {{CONTADOR_NOME}} — CRC/{{CRC_UF}} {{CRC_NUMERO}}
Escritorio: {{FIRM_NAME}}, {{MUNICIPIO}}/{{UF}}
Tom: {{TOM_VOZ_PERFIL}}, intensidade {{TOM_VOZ_INTENSIDADE}}/10
Modo melhor saida fiscal: {{MODO_MELHOR_SAIDA}}
Revisao Tecnica R1-R4: [ativa | desativada]
```

5. Se nao houver caso configurado, sugerir `/caso-contabil` ou `/start-auditoria-contabil`.

**Sem skill obrigatoria** — leitura direta do `CASO.md` e do `MEMORY.md`.
