---
name: onboarding-contabil
description: >
  Wizard de configuracao inicial do plugin no ambiente do escritorio contabil. Coleta a identidade do contador responsavel (nome, CRC e UF do CRC), o escritorio, o municipio e a UF de atuacao (eixo critico de localizacao — ISS municipal, ICMS estadual), as frentes de atuacao, os sujeitos atendidos (PJ/PF), o tom de voz e o modo de melhor saida fiscal. Grava a persona local fora do plugin. Aciona: configurar plugin, primeira vez, /start-auditoria-contabil, onboarding, instalar, comecar a usar.
---

# ONBOARDING CONTABIL

> Wizard de configuracao inicial **Tier 0**. Linguagem acolhedora, tom didatico. Conduz o operador a configurar o plugin ao perfil do escritorio contabil — com atencao especial a **localizacao** (municipio + UF), que e o eixo de toda apuracao de ISS e ICMS.

---

## 0. Escopo e acionamento

Acionada por `/start-auditoria-contabil` ou quando o operador disser "configurar plugin", "primeira vez", "onboarding", "instalar". Cria a pasta `auditoria-contabil/` no diretorio de trabalho com identidade, localizacao, frentes, sujeitos, tom e modo de melhor saida fiscal.

## 1. Posicao na orquestra

- **Chamada por:** `/start-auditoria-contabil` ou intencao de configuracao.
- **Entrega para:** os arquivos de runtime em `<cwd>/auditoria-contabil/` — lidos por `auditoria-contabil-master`, `validador-legislacao-vigente`, `triagem-contabil` e todas as demais skills.
- Roda uma vez na instalacao; idempotente nas execucoes seguintes.

## 2. Regras do wizard

1. Portugues (Brasil), tom acolhedor e direto.
2. Uma pergunta por vez para campos criticos; agrupar relacionados quando fizer sentido.
3. Defaults inteligentes — o operador aceita com Enter.
4. Validar em tempo real (CRC numerico, UF com 2 letras maiusculas, email valido).
5. Confirmar antes de gravar (resumo + "confirma? s/n").
6. **Idempotencia** — se ja existe `auditoria-contabil/cowork-state.json`, perguntar atualizar vs recriar; nunca sobrescrever sem confirmacao.
7. **Privacidade (PA-09)** — NUNCA pedir CPF, CNPJ de cliente real, dados de cliente nem conteudo de documento.
8. A **localizacao** (municipio + UF) e campo critico — explicar por que importa.

## 3. Fluxo do wizard

### Bloco 0 — Abertura
> "Ola! Sou o assistente do **Plugin Auditoria Contabil OS**. Vou te guiar na configuracao (~5 min). Ao final, as skills contabeis estarao adaptadas ao seu escritorio. Pronto para comecar?"

### Bloco 1 — Diretorio de trabalho
Detectar o cwd atual. Mostrar:
> "Vou criar a pasta `auditoria-contabil/` aqui em `<cwd>`.
> **Atencao LGPD (PA-09):** se este diretorio estiver dentro de uma pasta sincronizada (iCloud, OneDrive, Dropbox, Google Drive), os dados dos clientes podem subir para a nuvem. Recomendo um caminho **local**, fora de sync. Confirma este diretorio?"

Se nao, perguntar o path. Se for pasta sincronizada, alertar e so prosseguir com confirmacao expressa.

### Bloco 2 — Identidade profissional
> "Preciso da sua identidade profissional:
> 1. Nome completo do contador responsavel?
> 2. Numero do CRC?
> 3. UF do CRC?
> 4. Nome do escritorio?
> 5. Email institucional (opcional)?
> 6. Telefone (opcional)?"

Validar: CRC (digitos), UF do CRC (2 letras maiusculas), email se preenchido. O CRC ativo e o que sustenta a responsabilidade tecnica de toda entrega (PA-07).

### Bloco 3 — Localizacao (eixo critico)
> "Agora o campo mais importante para a precisao das apuracoes — a **localizacao**:
> 1. Municipio-sede do escritorio?
> 2. UF do escritorio?
>
> Por que importa: o **ISS e municipal** — aliquota (2% a 5%), lista de servicos e NFS-e variam por municipio. O **ICMS e estadual** — aliquotas, ICMS-ST, beneficios e RICMS variam por UF. Toda apuracao de ISS usa o municipio; toda de ICMS usa a UF (Protocolo 5). A `triagem-contabil` pode sobrescrever a localizacao por caso quando o cliente atua em outra praca."

Gravar `municipio` e `uf` no state.

### Bloco 4 — Sujeitos e frentes de atuacao
> "Quais **sujeitos** o escritorio atende? PJ, PF ou ambos *(default: ambos)*.
>
> Em quais **frentes** o escritorio atua? (multi-select, ou `todas`)
> - fiscal (apuracao de tributos por regime)
> - obrigacoes-acessorias (SPED, EFD, declaracoes)
> - folha-dp (folha, eSocial, encargos)
> - escrituracao (contabil, balancete, fechamento)
> - pessoa-fisica (IRPF, carne-leao, ganho de capital)
> - auditoria (revisao e diagnostico)
> - recuperacao (creditos tributarios)
> - operacional-societario (abertura, alteracao, baixa de empresa)
>
> Sua resposta nao restringe nenhuma skill — registra o foco do escritorio. A `triagem-contabil` confirma sujeito, frente(s) e localizacao caso a caso e grava no `CASO.md`."

### Bloco 5 — Especialidades
> "Quais especialidades o escritorio mais atende? (multi-select, ou `todas`)
> - Simples Nacional (LC 123/2006) · Lucro Presumido · Lucro Real · MEI
> - ICMS / ICMS-ST · IPI · ISS · PIS/COFINS
> - Folha e DP / eSocial · Escrituracao e fechamento · SPED
> - IRPF e pessoa fisica · Recuperacao de creditos · Auditoria contabil-fiscal
> - Abertura e alteracao de empresa · Reforma tributaria (CBS/IBS/IS — LC 214/2025)"

### Bloco 6 — Tom de voz
> "Perfil de tom:
> 1. **tecnico-objetivo** *(default)* — direto, conciso, focado no resultado
> 2. **tecnico-didatico** — explicativo, voltado ao cliente nao-contabil
> 3. **tecnico-cordial** — respeitoso e formal
>
> Intensidade de 0 a 10? *(default 6)*"

Gravar `tom_voz_perfil` e `tom_voz_intensidade`.

### Bloco 7 — Modo de melhor saida fiscal
> "Quando o plugin comparar regimes ou calcular a melhor saida fiscal, como prefere a entrega?
> 1. **recomendar-e-listar** *(default)* — recomenda a melhor opcao E lista as alternativas, com a memoria de calculo de cada cenario, para voce decidir.
> 2. **apenas-listar** — apresenta as opcoes lado a lado sem recomendar; o contador decide sozinho.
>
> Em ambos os casos a escolha de regime e sempre apresentada como **opcao do contribuinte** (PA-12), nunca como obrigacao, e sempre exige proposito negocial (PA-10)."

Gravar `MODO_MELHOR_SAIDA` (`recomendar-e-listar` | `apenas-listar`).

### Bloco 8 — Revisao Tecnica R1-R4
> "O plugin tem a **Revisao Tecnica R1-R4** — auditoria de 4 rodadas (escopo/dados, tecnica, conformidade, entrega) que revisa toda apuracao, relatorio e parecer antes da entrega. Adiciona alguns segundos mas garante qualidade e conformidade com as 20 Proibicoes Absolutas. Manter ATIVA? (s/n — default: s)
>
> Bypass disponivel caso a caso: `--no-revisao` ou `/revisao off`."

### Bloco 9 — Ferramentas (opcional)
> "Voce usa alguma ferramenta especifica? (pode pular)
> - Sistema contabil / ERP? · Emissor de documentos fiscais?
> - Controle de tarefas e prazos? · CRM ou gestao de clientes?
> - Banco / PSP? · Plataforma de assinatura/certificado digital?"

### Bloco 10 — Geracao dos arquivos
Apresentar o resumo da configuracao e pedir "confirma? (s/n)". Confirmado, gerar:
1. **`auditoria-contabil/cowork-state.json`** — via `python3 scripts/state.py init <cwd> --firm-name "<X>" --firm-slug "<x>" --contador "<X>"`, completar com `python3 scripts/state.py set <cwd> <campo> "<valor>"` (incluindo `municipio`, `uf`, `crc_numero`, `crc_uf`).
2. **`auditoria-contabil/persona.md`** — de `templates/persona.md.tpl`, resolvendo todos os tokens `{{...}}` com os valores coletados.
3. **`auditoria-contabil/config.md`** — de `templates/config.md.tpl` (localizacao, frentes, sujeitos, especialidades, tom, modo de melhor saida, ferramentas).
4. **`auditoria-contabil/casos/`** — pasta vazia onde cada caso/cliente sera compartimentado (PA-09).
5. **`.claude/settings.local.json`** — de `templates/settings-local.json.tpl`, apontando `CONTABIL_PERSONA`, `CONTABIL_COWORK_PATH` e `CONTABIL_STATE_FILE`.

### Bloco 11 — Encerramento
```
Plugin Auditoria Contabil OS configurado.

Contador: <nome> — CRC/<UF> <numero>
Escritorio: <firma>
Localizacao: <municipio> / <UF>   (eixo de ISS e ICMS)
Sujeitos: <PJ | PF | ambos>
Frentes: <lista>
Tom: <perfil> (intensidade <X>/10)
Modo de melhor saida fiscal: <recomendar-e-listar | apenas-listar>
Revisao Tecnica R1-R4: <ATIVA | DESATIVADA>

PROXIMOS PASSOS:
1. Reinicie a sessao (o hook SessionStart injeta a sua persona)
2. Use /contabil-master para ativar a cadeia completa
3. Use /caso-contabil para abrir o primeiro caso
4. Ou faca uma pergunta contabil/fiscal — o plugin desperta
5. /status-contabil para diagnostico do ambiente
```

## 4. Fluxo alternativo — state ja existente (idempotencia)

Se `auditoria-contabil/cowork-state.json` ja existir ao ser acionada:
> "Detectei uma configuracao existente. Contador: <nome>. Localizacao: <municipio/UF>. O que deseja?
> (a) Continuar usando — nada muda
> (b) Atualizar — refaco os blocos que voce escolher
> (c) Recriar do zero — **isto apaga a configuracao atual** (os casos em `casos/` sao preservados)"

Se (c): confirmar duas vezes antes de prosseguir. Casos existentes nunca sao apagados. Rodar N vezes com os mesmos dados = mesmo resultado.

## 5. Vedacoes especificas

- **PA-09** — NUNCA coletar CPF, CNPJ de cliente real, dados de cliente nem conteudo de documento. Avisar sobre pasta sincronizada e so prosseguir com confirmacao expressa.
- Nunca sobrescrever `cowork-state.json` existente sem dupla confirmacao.
- Nunca enviar dados a servicos externos durante o wizard.
- Tokens `{{...}}` permanecem literais no disco — o LLM resolve em runtime via persona.
- O municipio e a UF sao campos obrigatorios — sem eles a apuracao de ISS/ICMS fica sem eixo (PA-05).

## 6. Protocolos acionados

- **P5 — Localizacao** — o Bloco 3 captura o eixo geografico que toda apuracao usara.
- Nao executa P1-P4 nem P6 (skill de configuracao, nao de calculo).

## 7. Localizacao

Esta skill **estabelece** a localizacao padrao do escritorio (municipio + UF), gravada na persona e no state. E o ponto de origem do Protocolo 5: a partir daqui, `validador-legislacao-vigente` sabe qual RICMS e qual lei municipal de ISS validar, e a `triagem-contabil` sabe qual localizacao confirmar ou sobrescrever por caso.

## 8. Integracao

**Chamada por:** `/start-auditoria-contabil` ou intencao de configuracao inicial.

**Entrega para:** os arquivos de runtime em `<cwd>/auditoria-contabil/` (`persona.md`, `config.md`, `cowork-state.json`, `casos/`) e `.claude/settings.local.json`. Esses arquivos sao lidos por todas as skills do plugin via hook SessionStart.

**Checklist final:**
- [ ] `auditoria-contabil/cowork-state.json` valido no schema, com `municipio` e `uf` preenchidos
- [ ] `auditoria-contabil/persona.md` com tokens resolvidos
- [ ] `auditoria-contabil/config.md` com localizacao, frentes, sujeitos e modo de melhor saida
- [ ] `auditoria-contabil/casos/` criada
- [ ] `.claude/settings.local.json` com `CONTABIL_PERSONA` e `CONTABIL_COWORK_PATH`
