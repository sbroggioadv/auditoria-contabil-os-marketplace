# Plugin Auditoria Contábil OS

Plugin Claude Code para a contabilidade brasileira completa — opera a rotina fiscal, contábil e de departamento pessoal de clientes PJ e PF.

---

## O Que Este Plugin Faz

O **Auditoria Contábil OS** especializa o Claude Code para atuar como uma operação contábil-fiscal completa — não apenas auditoria, mas a rotina inteira de um escritório contábil: apurações tributárias, obrigações acessórias, SPED, folha e departamento pessoal, escrituração, auditoria e recuperação de créditos.

### Funcionalidades (Release v0.1 — Núcleo Operacional)

- **33 skills** organizadas em Tier 0-3 (orquestrador → triagem e ingestão → apurações tributárias → obrigações acessórias e SPED) + transversais
- **Validação de legislação vigente** como premissa de qualquer cálculo — nos três níveis: federal, estadual e municipal. A lei é alvo móvel (reforma tributária 2026-2033)
- **Localização município + UF** como eixo de toda análise — ISS é municipal, ICMS é estadual, benefícios e prazos variam por ente
- **Ingestão de arquivos** — XML (NF-e, NFC-e, NFS-e, CT-e), OFX (extrato bancário), CSV e SPED, com parsing determinístico para volume
- **20 Proibições Absolutas** (PA-01..PA-20) aplicadas automaticamente em toda apuração e relatório
- **6 Protocolos Técnicos** (Validação Legal Prévia, Ingestão e Conferência de Arquivos, Cálculo, Cruzamento e Conciliação, Localização, Auditoria de Qualidade)
- **Revisão Técnica R1-R4** — auditoria de qualidade obrigatória antes de entregar qualquer apuração, relatório ou parecer
- **Onboarding guiado** via `/start-auditoria-contabil` — configura identidade do contador, CRC, município/UF, frentes de atuação e tom de voz em ~5 minutos
- **Persona em runtime** — identidade do operador vive fora do plugin, nunca hardcoded

### Áreas Cobertas (v0.1)

**Triagem e ingestão:** classificação de sujeito (PJ/PF), frentes e localização; análise de XML fiscal, extratos OFX/CSV e arquivos SPED; análise de CNAE e atividades; calendário fiscal.

**Apurações tributárias:** Simples Nacional, Lucro Presumido, Lucro Real, MEI, ICMS e ICMS-ST, IPI, ISS, PIS/COFINS (cumulativo e não-cumulativo), IRRF da folha, INSS empresa, retenções do tomador.

**Obrigações acessórias e SPED:** ECD, ECF, EFD ICMS/IPI, EFD-Contribuições, EFD-Reinf, DCTFWeb, DIRF, DIMOB, DMED.

> **Roadmap:** v0.2 adiciona folha e DP / eSocial, escrituração e fechamento, IRPF. v0.3 adiciona auditoria, recuperação de créditos, operacional/societário, relatórios consolidados e decks.

---

## Fronteira

Este é um plugin de **contabilidade** — para contador e escritório contábil. Onde uma demanda extrapola o contábil (litígio judicial tributário, estruturação societária estratégica), o plugin sinaliza "encaminhar a advogado".

---

## Instalação

1. Abra o **Claude Code** (Cowork)
2. Acesse **Settings → Plugins → Pessoal → "+" Uploads locais**
3. Cole a URL do repositório marketplace do plugin (fornecida na sua compra)
4. Clique em **Instalar**

Após instalação, rode `/start-auditoria-contabil` em qualquer sessão para configurar seu escritório.

---

## Uso

```
/start-auditoria-contabil    # onboarding — configure identidade, CRC, município/UF e frentes
/contabil-master             # orquestrador geral
/caso-contabil               # abre/gerencia um caso de cliente
/apuracao                    # apuração tributária
/obrigacoes                  # obrigações acessórias e SPED
/regime                      # cálculo da melhor saída fiscal (comparativo de regimes)
/revisao-final               # Revisão Técnica R1-R4 (auditoria de qualidade)
/status-contabil             # estado do caso e da configuração
```

---

## Requisitos

- Claude Code (Cowork) instalado
- Python 3.11+ (para os scripts internos de hooks e parsing de arquivos)

---

## Licença

MIT — ver `LICENSE`.
