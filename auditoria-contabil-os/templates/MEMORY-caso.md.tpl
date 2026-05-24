# MEMORY.md — Caso {{CLIENTE}}

> Log evolutivo deste caso contabil. Persistente entre sessoes do Claude Code.
> Vive em `<COWORK>/auditoria-contabil/casos/{{CASO_SLUG}}/MEMORY.md`. Atualizado a cada etapa.

---

## Identificacao do Caso

- **Cliente:** {{CLIENTE}}
- **CNPJ / CPF:** {{DOCUMENTO}}
- **Sujeito:** {{SUJEITO}}  <!-- PJ | PF -->
- **Frente(s):** {{FRENTES}}
- **Regime tributario:** {{REGIME_TRIBUTARIO}}
- **Localizacao:** {{MUNICIPIO}}/{{UF}}

---

## Como Funciona

**Leitura automatica:** o Claude le este arquivo ao iniciar trabalho no caso. Usa o que encontra para retomar de onde parou.

**Escrita:** a skill `memoria-de-caso-contabil` registra aqui cada etapa concluida (triagem, ingestao de arquivos, apuracao, obrigacao preparada, achado de auditoria, Revisao Tecnica R1-R4). Anotacoes manuais do operador ("lembre disso", "anote") tambem entram aqui.

**Compartimentacao (PA-09):** este MEMORY.md cobre **apenas** este cliente/caso. Nunca misturar informacao de outro cliente aqui. Pasta de caso gitignored — sigilo LGPD.

---

## Linha do Tempo do Caso

| Data | Etapa | Resultado / Observacao |
|------|-------|------------------------|
| {{GENERATED_AT}} | Caso aberto | Sujeito: {{SUJEITO}} · Frente(s): {{FRENTES}} · Local: {{MUNICIPIO}}/{{UF}} |

---

## Selo de Validacao Legal

*(Registrado pelo `validador-legislacao-vigente` apos o Protocolo 1: normas validadas, data-base, regime do ano, alertas.)*

---

## Apuracoes e Entregas

*(Cada apuracao, obrigacao preparada e relatorio e listado aqui com data e veredito da Revisao Tecnica R1-R4.)*

---

## Pendencias e Pontos de Omissao

*(Documentos faltantes, dados a colher, prazos a confirmar, divergencias de cruzamento sinalizadas. Apontados pela triagem e pela Revisao Tecnica R1.)*

---

**Workspace:** `{{COWORK_PATH}}`
**Caso:** {{CLIENTE}}
**Plugin:** `auditoria-contabil-os` v{{PLUGIN_VERSION}}
**Inicializado em:** {{GENERATED_AT}}
