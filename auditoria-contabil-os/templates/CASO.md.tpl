# CASO — {{CLIENTE}}

> Ficha do caso contabil. Fonte unica das variaveis de **sujeito**, **frente** e
> **localizacao** — todas as skills leem os campos `Sujeito`, `Frentes` e
> `Localizacao` daqui. Vive em
> `<COWORK>/auditoria-contabil/casos/{{CASO_SLUG}}/CASO.md`.

---

## Triagem do caso

- **Sujeito:** {{SUJEITO}}
  <!-- PJ | PF -->
- **Frente(s):** {{FRENTES}}
  <!-- fiscal | obrigacoes-acessorias | folha-dp | escrituracao | pessoa-fisica
       | auditoria | recuperacao | operacional-societario — pode ser mais de uma -->
- **Tipo de tarefa:** {{TAREFA}}

---

## Localizacao (Protocolo 5)

- **Municipio do cliente:** {{MUNICIPIO}}
  <!-- Define a legislacao de ISS e as obrigacoes municipais (NFS-e). -->
- **UF do cliente:** {{UF}}
  <!-- Define a legislacao de ICMS e as obrigacoes estaduais. -->

> Sem regra local confirmada -> marcar `[VERIFICAR — norma municipal/estadual]` (PA-06).
> A localizacao do cliente pode diferir da localizacao-sede do escritorio.

---

## Dados do cliente

- **Nome / Razao social:** {{CLIENTE}}
- **CNPJ / CPF:** {{DOCUMENTO}}
- **Regime tributario:** {{REGIME_TRIBUTARIO}}
  <!-- Simples Nacional | Lucro Presumido | Lucro Real | MEI | PF (carne-leao) -->
- **CNAE / Atividade:** {{CNAE}}
- **Competencia / periodo de apuracao:** {{COMPETENCIA}}

---

## Marco intertemporal

- **Ano / data do fato gerador:** {{FATO_GERADOR_DATA}}
  <!-- Data ou competencia do fato gerador. Determina qual legislacao se aplica (PA-03). -->
- **Regime tributario aplicavel (EC 132/2023 + LC 214/2025):** {{REGIME_MARCO}}
  <!-- Regimes possiveis:
       ANTES DA REFORMA — fato gerador ate 31/12/2025 (PIS/COFINS/ICMS/ISS vigentes)
       ANO-TESTE 2026  — fase experimental CBS/IBS (tributos atuais ainda em vigor)
       2027+           — CBS em vigor, PIS/COFINS extintos; IBS em implantacao progressiva
       TRANSICAO 2027-2033 — aliquotas reduzidas de CBS/IBS + extincao gradual ICMS/ISS
  -->

> Protocolo 1 — toda apuracao e parecer datados pelo ano do fato gerador. A legislacao
> vigente no **ano do fato gerador** e a aplicavel (PA-03). Travar o cronograma da Reforma
> Tributaria antes de qualquer calculo ou planejamento.

---

## Selo de Validacao Legal Previa (PA-04 / Protocolo 1)

- **Status:** {{SELO_STATUS}}
  <!-- PENDENTE | EMITIDO -->
- **Data da validacao:** {{SELO_DATA}}
- **Normas validadas:** {{SELO_NORMAS}}

> Nenhuma skill de calculo roda sem o Selo emitido pelo `validador-legislacao-vigente`.

---

## Prazos e obrigacoes

| Obrigacao / prazo | Competencia | Vencimento | Ente | Observacao |
|-------------------|-------------|------------|------|------------|
| {{PRAZO_TIPO}} | {{PRAZO_COMP}} | {{PRAZO_FIM}} | {{PRAZO_ENTE}} | {{PRAZO_OBS}} |

<!-- Decadencia/prescricao: 5 anos (CTN art. 173 / 174). Sempre verificar suspensoes
     e interrupcoes (PA-18). Opcao de regime tem prazo anual proprio. -->

---

## Arquivos do caso

{{ARQUIVOS}}

<!-- Lista dos arquivos em casos/{{CASO_SLUG}}/arquivos/ —
     XML de NF-e/NFC-e/NFS-e/CT-e, OFX, CSV, arquivos SPED (ECD/ECF/EFD),
     balancetes, planilhas, contratos sociais, comprovantes. -->

---

## Linha de trabalho

{{LINHA_TRABALHO}}

<!-- Preenchida ao longo do caso: apuracoes feitas, obrigacoes preparadas,
     achados de auditoria, divergencias de cruzamento. -->

---

**Plugin:** `auditoria-contabil-os` v{{PLUGIN_VERSION}}
**Caso aberto em:** {{GENERATED_AT}}
