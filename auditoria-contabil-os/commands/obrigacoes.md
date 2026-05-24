---
description: Roteia para as skills de obrigacoes acessorias e SPED (Tier 3) — ECD, ECF, EFD ICMS/IPI, EFD-Contribuicoes, EFD-Reinf, DCTFWeb, DIRF, DIMOB e DMED.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint: [demanda de obrigacao acessoria — ex: preparar a EFD-Contribuicoes, DCTFWeb, ECD]
---

Voce foi acionado pelo comando `/obrigacoes` do plugin Auditoria Contabil OS.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** rotear a demanda de obrigacao acessoria / SPED para a skill Tier 3 adequada.

## PROTOCOLO

1. **Verificar** se o `CASO.md` esta criado. Se nao, acionar `triagem-contabil` primeiro — a obrigacao certa depende do regime tributario (PA-13).
2. **Calendario fiscal** — acionar `calendario-fiscal` para confirmar o prazo de entrega da obrigacao no ente correto (federal/estadual/municipal) e sinalizar vencimentos (PA-18).
3. **Ingestao de arquivos** — se a obrigacao consome SPED ou arquivos fiscais, acionar `leitura-arquivos-sped` / `analise-xml-fiscal` antes (Protocolo 2).
4. **Cruzamento (Protocolo 4)** — toda obrigacao confronta o que foi escriturado com o apurado/pago/declarado. Divergencia e apontada explicitamente.
5. **Identificar** a demanda e rotear:

| Demanda | Skill |
|---------|-------|
| Escrituracao Contabil Digital | `ecd` |
| Escrituracao Contabil Fiscal (IRPJ/CSLL) | `ecf` |
| EFD ICMS/IPI — apuracao escriturada | `efd-icms-ipi` |
| EFD-Contribuicoes — PIS/COFINS escriturado | `efd-contribuicoes` |
| EFD-Reinf — retencoes e informacoes a RFB | `efd-reinf` |
| DCTFWeb — confissao de debitos | `dctfweb` |
| DIRF — declaracao de imposto retido na fonte | `dirf` |
| DIMOB — informacoes de atividades imobiliarias | `dimob` |
| DMED — informacoes de servicos medicos | `dmed` |

6. **PA-08** — o plugin **prepara** a obrigacao; a transmissao e a assinatura sao do contador com CRC ativo. Nunca afirmar que transmitiu.
7. Ao concluir, acionar `revisao-final` (R1-R4) antes de entregar.

**Skills do Tier 3:** `ecd`, `ecf`, `efd-icms-ipi`, `efd-contribuicoes`, `efd-reinf`, `dctfweb`, `dirf`, `dimob`, `dmed`.
