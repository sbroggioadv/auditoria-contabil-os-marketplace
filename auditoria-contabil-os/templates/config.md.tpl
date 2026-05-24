# Configuracao — auditoria-contabil-os

> Configuracao operacional do plugin no ambiente do escritorio contabil. Vive em
> `<COWORK>/auditoria-contabil/config.md`. Gerada pelo `/start-auditoria-contabil`. Editavel
> manualmente — mudancas valem na proxima sessao.

---

## Localizacao

- **Municipio-sede:** {{MUNICIPIO}}
- **UF-sede:** {{UF}}

> Eixo do Protocolo 5 (Localizacao). O municipio define ISS e obrigacoes municipais; a UF
> define ICMS e obrigacoes estaduais. A `triagem-contabil` pode sobrescrever por caso quando
> o cliente atua em outra praca.

---

## Frentes e Sujeitos de Atuacao

- **Frentes:** {{FRENTES}}
  <!-- fiscal | obrigacoes-acessorias | folha-dp | escrituracao | pessoa-fisica | auditoria | recuperacao | operacional-societario -->
- **Sujeitos:** {{SUJEITOS}}
  <!-- PJ | PF | ambos -->

> Define as frentes contabeis e os sujeitos (PJ/PF) que o escritorio atende. A
> `triagem-contabil` confirma sujeito, frente(s) e localizacao caso a caso e grava no `CASO.md`.

---

## Especialidades

- **Especialidades:** {{ESPECIALIDADES}}
  <!-- ex: Simples Nacional, Lucro Real, folha e DP, SPED, recuperacao de creditos,
       auditoria contabil, IRPF, abertura de empresa, escrituracao e fechamento -->

---

## Tom de voz

- **Perfil:** {{TOM_VOZ_PERFIL}}
  <!-- tecnico-objetivo | tecnico-didatico | tecnico-cordial | personalizado -->
- **Intensidade:** {{TOM_VOZ_INTENSIDADE}}/10
- **Postura default:** {{POSTURA_DEFAULT}}

---

## Modo de melhor saida fiscal

- **Modo:** {{MODO_MELHOR_SAIDA}}
  <!-- recomendar-e-listar (default) | apenas-listar -->

> `recomendar-e-listar` — a skill `planejamento-melhor-saida-fiscal` recomenda a melhor opcao
> e lista as alternativas. `apenas-listar` — apresenta as opcoes sem recomendar.

---

## Revisao Tecnica

- **Auditoria R1-R4:** {{REVISAO_TECNICA_STATUS}}
  <!-- ATIVA (default) | DESATIVADA -->
- Bypass por demanda: `--no-revisao`, `--quick`, `/revisao off`.

---

## Ferramentas declaradas

- **Ferramentas:** {{FERRAMENTAS}}
  <!-- sistema contabil/ERP, emissor fiscal, CRM, banco/PSP, etc. — campos livres -->

---

**Plugin:** `auditoria-contabil-os` v{{PLUGIN_VERSION}}
**Gerado em:** {{GENERATED_AT}}
**State source:** `{{COWORK_PATH}}/auditoria-contabil/cowork-state.json`
