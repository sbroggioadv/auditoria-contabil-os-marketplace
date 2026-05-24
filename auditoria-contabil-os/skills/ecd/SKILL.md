---
name: ecd
description: >
  Preparacao e conferencia da ECD anual (SPED Contabil) — Livro Diario, Razao e
  balancetes em arquivo digital. Conhece os blocos (0, I, J, K, 9), os registros
  I050/I150/I200/I250 e J005/J100/J150, o plano referencial (Anexo III), a amarracao
  de saldos iniciais e a validacao no PVA. Base: IN RFB 2.003/2021, Lei 11.638/2007,
  Decreto 8.683/2016 (autenticacao automatica na Junta), CPC 26. Aciona: preparar ECD,
  SPED Contabil, plano referencial, J005/J100/J150, I050/I200/I250, erro de bloqueio
  no validador, saldo inicial divergente, transmissao da ECD.
---

# ECD — ESCRITURACAO CONTABIL DIGITAL

> Skill **Tier 3** — obrigacao acessoria. Prepara e confere a ECD: consolida a
> escrituracao contabil do exercicio num arquivo digital. Exige o Selo de Validacao
> Legal Previa (P1) e e datada pelo ano do fato gerador. O plugin **prepara**; a
> transmissao e a responsabilidade tecnica sao do contador com CRC ativo (PA-07, PA-08).

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com
"preparar ECD", "SPED Contabil", "plano referencial", "erro de bloqueio no validador",
"saldo inicial divergente". Entrada: ano-calendario, CNPJ, regime tributario, balancete
e DRE fechados, plano de contas com codigo referencial, ECD do ano anterior (amarracao),
TXT da ECD se ja gerado. Entrega: checklist de pre-validacao, diagnostico do TXT,
lancamentos modelo I200/I250, plano de mitigacao de erros do PVA.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.
- **Aciona antes:** `validador-legislacao-vigente` (P1) — o leiaute da ECD e o Manual
  mudam por ano; sem o Selo a preparacao nao comeca (PA-04).
- **Apoia-se em:** `leitura-arquivos-sped` (le e confere o TXT da ECD — bloco I/J,
  registro 9999) e nas apuracoes do Tier 2 (a ECD consolida o que foi contabilizado).
- **Entrega para:** `ecf` (a ECF recupera a ECD — sequencia obrigatoria), `revisao-final`
  (R1-R4) e o `CASO.md`.

## 2. Estrutura da ECD — blocos e registros

```
Bloco 0  Abertura, identificacao, parametros (0000 com indicador LECD)
Bloco I  Escrituracao contabil:
         I050 plano de contas (campo do codigo referencial)
         I100 centros de custo  I150 saldos periodicos  I155 detalhe de saldos
         I200 cabecalho do lancamento  I250 partidas (conta, D/C, valor, historico)
         I300/I310/I350 balancetes e demonstracoes periodicas
Bloco J  Demonstracoes: J005 DRE, J100 BP ativo, J150 BP passivo, J210 DLPA,
         J215 DMPL, J800 outras informacoes/notas, J930 auditor independente
Bloco K  SCP — sociedade em conta de participacao
Bloco 9  Encerramento; registro 9999 declara o total de linhas
```

**Prazo de entrega:** ate o ultimo dia util de maio do ano seguinte ao do fato gerador
— `[VERIFICAR]` o prazo do ano (IN RFB 2.003/2021 e atualizacoes). Autenticacao na
Junta Comercial automatica via SPED (Decreto 8.683/2016). Multa por atraso conforme
IN RFB vigente — `[VERIFICAR]` o percentual e o piso.

## 3. Obrigatoriedade

Estao obrigadas, em regra (IN RFB 2.003/2021, art. 3o): empresas do Lucro Real;
Lucro Presumido que distribuiram lucro acima do presumido liquido (Lei 9.249/1995,
art. 10); imunes/isentas acima do limite de receita bruta; e a SCP. A obrigatoriedade
e alvo de revisao por IN — `[VERIFICAR]` o enquadramento do ano (PA-06).

## 4. Amarracao de saldos iniciais

O saldo inicial de cada conta analitica deve ser **identico** ao saldo final da ECD
do ano anterior. Divergencia gera bloqueio total no validador.

- **Empresa com ECD anterior:** saldo inicial = saldo final da ECD entregue.
- **Cliente novo / primeira ECD:** os saldos iniciais vem do balancete de abertura do
  exercicio, com ajuste retroativo se aplicavel; declarar a circunstancia no J800.
- **Migracao de Simples para Real no meio do ano:** a ECD cobre o periodo no Real;
  o saldo inicial e o saldo de transicao.

## 5. Plano referencial (Anexo III da IN RFB 2.003/2021)

Cada conta analitica precisa de um **codigo referencial fiscal** mapeado no I050. O
referencial e a traducao da conta da empresa para a estrutura fiscal padrao — base da
ECF posterior. Conta analitica sem referencial → bloqueio. A estrutura do Anexo III
e atualizada por IN; `[VERIFICAR]` a versao vigente (PA-06).

## 6. Lancamentos I200/I250 — partida dobrada

```
|I200|<num>|<data>|<valor total>|<indicador>|
|I250|<conta contabil>|D|<valor>||<historico explicativo>|
|I250|<conta contabil>|C|<valor>||<historico explicativo>|
```

Regra de partida dobrada: em cada lancamento, soma de debitos = soma de creditos
(D - C = 0). O historico deve ser explicativo e rastreavel — nada de "conforme
documentos"; a auditoria precisa identificar a operacao (PA-19).

## 7. Conferencia antes do PVA (P4)

- Toda conta analitica do I050 tem codigo referencial?
- Saldo inicial I150 = saldo final da ECD anterior?
- Soma das partidas I250 = valor do cabecalho I200?
- D = C em cada lancamento?
- J005 (DRE), J100/J150 (BP) e J210 (DLPA) batem com o balancete?
- J800 anexo quando obrigatorio; J930 quando ha auditoria independente?
- Termos de abertura e encerramento com data e assinatura?

Erros frequentes do PVA EFD-Contabil: conta sem referencial, saldo inicial divergente,
partidas D ≠ C, conta com natureza errada, J800 obrigatorio sem anexo.

## 8. Anti-padroes

- Saldo inicial divergente da ECD anterior — bloqueio total.
- Conta analitica sem codigo referencial.
- Lancamento com partidas que nao fecham (D ≠ C).
- Plano de contas com natureza errada (receita marcada como ativo).
- Esquecer o J800 quando obrigatorio.
- Historico generico ("conforme documentos") — impede a rastreabilidade.
- Termo de abertura sem CRC ativo.
- Transmitir a ECD e nao sequenciar a ECF (a ECF recupera a ECD).
- Cravar prazo, multa ou versao do Anexo III de memoria — `[VERIFICAR]`.

## 9. Casos de borda

- **Primeira ECD (sem anterior):** saldos iniciais do balancete + ajuste retroativo,
  declarados no J800.
- **SCP:** bloco K obrigatorio e separado.
- **Empresa em recuperacao judicial:** a ECD continua obrigatoria; o passivo
  parcelado na RJ aparece normalmente.
- **Auditoria independente:** J930 obrigatorio nas hipoteses legais (capital aberto
  e outras) — confirmar antes de transmitir.
- **Alteracao de plano de contas no exercicio:** garantir continuidade do referencial.

## 10. Vedacoes especificas

- **PA-02** — preparar so com dado real (balancete fechado, DRE, plano de contas).
- **PA-03** — datar a ECD pelo ano do fato gerador; leiaute e Manual mudam por ano.
- **PA-04** — sem o Selo de Validacao Legal Previa, a preparacao nao comeca.
- **PA-06** — `[VERIFICAR]` no prazo de entrega, na multa, na versao do Anexo III e
  na regra de obrigatoriedade do ano.
- **PA-07** — a saida e rascunho operacional; a decisao e a responsabilidade tecnica
  sao do contador com CRC ativo.
- **PA-08** — a skill prepara e confere a ECD; nao transmite nem assina (atos do
  contador via PVA/Receitanet).
- **PA-11** — citar a norma com artigo (IN RFB 2.003/2021; Decreto 8.683/2016;
  Lei 11.638/2007; CPC 26).
- **PA-13** — nao confundir o regime tributario com a obrigacao acessoria; a ECD e
  obrigacao, nao apuracao.
- **PA-19** — todo lancamento aponta documento e historico rastreavel.

## 11. Protocolos acionados

- **P1 — Validacao Legal Previa** — Selo emitido por `validador-legislacao-vigente`,
  com a IN e o Manual da ECD do ano.
- **P2 — Ingestao** — leitura e conferencia do TXT da ECD via `leitura-arquivos-sped`.
- **P4 — Cruzamento e Conciliacao** — J005/J100/J150 batem com o balancete; saldo
  inicial bate com a ECD anterior; a ECD alimenta a recuperacao na ECF.
- **P6 — Auditoria de Qualidade** — `revisao-final` R1-R4 antes da entrega.

## 12. Localizacao

A ECD e obrigacao **federal** — leiaute e prazo valem em todo o pais. O eixo
geografico aparece na **autenticacao**: a Junta Comercial e do estado da sede; embora
a autenticacao seja automatica via SPED (Decreto 8.683/2016), algumas Juntas cobram
taxa. Quando uma regra da Junta estadual nao puder ser confirmada, marcar
`[VERIFICAR — norma da Junta estadual]` (PA-06).

## 13. Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.

**Entrega para:** `ecf` (recupera a ECD — sequencia obrigatoria), `revisao-final`
(R1-R4) e o `CASO.md`. O TXT da ECD e lido e conferido por `leitura-arquivos-sped`;
as apuracoes do Tier 2 fornecem os valores que a contabilidade consolidou.

**Sem esta skill:** a ECD e montada sem checklist de pre-validacao nem amarracao de
saldos — risco de bloqueio no PVA, multa por atraso e ECF que nao recupera dados.
