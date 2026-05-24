# Auditoria Contábil OS — Marketplace

Marketplace oficial do plugin **Auditoria Contábil OS** para Claude Code — sistema operacional da contabilidade brasileira. Opera a rotina fiscal, contábil e de departamento pessoal de clientes PJ e PF.

---

## O que é

O Auditoria Contábil OS transforma o Claude Code em uma operação contábil-fiscal completa — não apenas auditoria, mas a rotina inteira de um escritório contábil: apurações tributárias, obrigações acessórias, SPED, retenções, ingestão de arquivos fiscais e auditoria de qualidade.

- **33 skills** organizadas em Tier 0-3 (orquestrador → triagem e ingestão → apurações tributárias → obrigações acessórias e SPED) + transversais
- **Validação de legislação vigente** como premissa de qualquer cálculo — nos três níveis: federal, estadual e municipal. A lei é alvo móvel (reforma tributária 2026-2033: CBS/IBS/IS)
- **Localização município + UF** como eixo de toda análise — ISS é municipal, ICMS é estadual, benefícios e prazos variam por ente
- **Ingestão de arquivos** — XML (NF-e, NFC-e, NFS-e, CT-e), OFX (extrato bancário), CSV e SPED, com parsing determinístico para volume
- **20 Proibições Absolutas** (PA-01..PA-20) e **6 Protocolos Técnicos** aplicados automaticamente
- **Revisão Técnica R1-R4** — auditoria de qualidade obrigatória antes de entregar qualquer apuração, relatório ou parecer
- **Onboarding guiado** via `/start-auditoria-contabil` (~5 minutos)
- **100% configurável** ao perfil do escritório contábil em runtime — identidade, CRC, município/UF, frentes de atuação e tom de voz. Nada hardcoded.

### Áreas cobertas (v0.1 — Núcleo Operacional)

| Frente | Escopo |
|--------|--------|
| Triagem e ingestão | Classificação de sujeito (PJ/PF), frentes e localização; análise de XML fiscal, extratos OFX/CSV e arquivos SPED; análise de CNAE e atividades; calendário fiscal |
| Apurações tributárias | Simples Nacional, Lucro Presumido, Lucro Real, MEI, ICMS e ICMS-ST, IPI, ISS, PIS/COFINS (cumulativo e não-cumulativo), IRRF da folha, INSS empresa, retenções do tomador |
| Obrigações acessórias e SPED | ECD, ECF, EFD ICMS/IPI, EFD-Contribuições, EFD-Reinf, DCTFWeb, DIRF, DIMOB, DMED |
| Transversais | Validador de legislação vigente, calendário fiscal, memória de caso, estilo de entrega contábil, revisão final R1-R4 |

> **Roadmap:** v0.2 adiciona folha e DP / eSocial, escrituração e fechamento, IRPF. v0.3 adiciona auditoria, recuperação de créditos, operacional/societário, relatórios consolidados e decks.

### Fronteira

Este é um plugin de **contabilidade** — para contador e escritório contábil. Onde uma demanda extrapola o contábil (litígio judicial tributário, estruturação societária estratégica), o plugin sinaliza "encaminhar a advogado".

---

## Instalação

1. Abra o **Claude Code** (Cowork)
2. Vá em **Settings → Plugins → aba Pessoal → "+" → Uploads locais**
3. Cole a URL deste repositório:
   ```
   https://github.com/sbroggioadv/auditoria-contabil-os-marketplace
   ```
4. Sincronize e instale o plugin **auditoria-contabil-os**
5. Em qualquer sessão, rode `/start-auditoria-contabil` para configurar seu escritório contábil

---

## Conteúdo do marketplace

| Plugin | Descrição |
|--------|-----------|
| [`auditoria-contabil-os`](./auditoria-contabil-os) | Plugin completo — 33 skills, 8 commands, 4 hooks, 4 parsers de arquivos fiscais (XML NF-e/NFS-e, OFX, SPED) |

---

## Requisitos

- Claude Code (Cowork)
- Python 3.11+ (scripts internos de hooks e parsing de arquivos fiscais)

---

## Licença

O marketplace é distribuído sob licença MIT (ver [`LICENSE`](./LICENSE)). O uso comercial do plugin segue os termos da licença de uso fornecida na aquisição.
