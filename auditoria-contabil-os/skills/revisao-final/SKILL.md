---
name: revisao-final
description: >
  Auditoria de qualidade obrigatoria de 4 rodadas (Revisao Tecnica R1-R4) sobre toda entrega contabil-fiscal antes de devolver ao usuario. R1 escopo e dados; R2 tecnica (calculo, norma vigente e citada, memoria rastreavel, Selo); R3 conformidade (obrigacao certa, prazo, localizacao ISS/ICMS, cruzamento); R4 entrega (clareza, estrutura, ressalva CRC, numeros batendo com a memoria de calculo). Reprovacao em qualquer rodada bloqueia e devolve ao produtor. Veredito APROVADO / REVISAR / BLOQUEADO. Skill invariante (Protocolo 6). Aciona: revisar entrega, auditoria final, conferir antes de entregar, revisao final, /revisao-final, R1 R2 R3 R4, validar apuracao, checar relatorio.
---

# REVISAO FINAL

> Skill **transversal invariante** — Protocolo 6 (Auditoria de Qualidade). Nenhuma apuracao, obrigacao preparada, relatorio, parecer ou deck sai do plugin sem passar pelas 4 rodadas R1-R4. Opera independente de sujeito (PJ/PF), frente e Tier.

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master` antes de qualquer entrega relevante, ou diretamente pelo operador com: "revisar entrega", "auditoria final", "conferir antes de entregar", "revisao final", `/revisao-final`. **Sem esta auditoria, nenhuma entrega e considerada concluida** — mesmo que o conteudo tecnico esteja correto. Entregas curtas e puramente conceituais (sem valor, sem apuracao) podem dispensar via bypass transparente.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master` (obrigatoriamente antes de toda entrega) e operador direto.
- **Recebe de:** qualquer skill produtora (Tier 1-9) — apuracao, obrigacao preparada, relatorio, parecer, deck, conciliacao.
- **Entrega para:** o operador — entrega aprovada, ou devolvida ao produtor para retrabalho.
- **Integra com:** `estilo-entrega-contabil` (R4 confere se o padrao de entrega foi aplicado), `memoria-de-caso-contabil` (registra o veredito no `CASO.md`).
- **Bypass:** `--no-revisao`, `--quick` (R1+R2 apenas, para rascunhos internos) ou `/revisao off` (session toggle) — usado com transparencia, sob responsabilidade do operador.

## 2. Sequencia obrigatoria R1 -> R2 -> R3 -> R4

As rodadas sao **sequenciais**. Reprovacao em qualquer rodada **bloqueia** as seguintes e devolve ao produtor.

```
R1 — Escopo e dados
    | (APROVADO)
    v
R2 — Tecnica
    | (APROVADO)
    v
R3 — Conformidade
    | (APROVADO)
    v
R4 — Entrega
    | (APROVADO)
    v
ENTREGA AUTORIZADA
```

## 3. R1 — Escopo e dados

**Pergunta central:** o pedido foi entendido e os dados de entrada sao reais, completos e da competencia certa?

```
[ ] O pedido foi compreendido — a entrega responde ao que o cliente solicitou?
[ ] A entrega e do tipo certo (apuracao, obrigacao, relatorio, parecer, deck)?
[ ] Sujeito identificado corretamente (PJ ou PF)?
[ ] Localizacao identificada (municipio + UF) no CASO.md?
[ ] Os dados de entrada sao dados REAIS do cliente, nao presumidos (PA-02)?
[ ] Os dados estao completos — receita, competencia, CNAE/atividade, valores?
[ ] A competencia / ano do fato gerador esta correta e explicita (PA-03)?
[ ] Dado faltante foi marcado [INFORMAR], nao inventado?
[ ] Nao ha conteudo fora do escopo solicitado (excesso que confunde)?
```

**Resultado R1:** `APROVADO` / `APROVADO COM RESSALVAS` (itens menores listados) / `REPROVADO` (escopo errado ou dado presumido — devolver ao produtor).

## 4. R2 — Tecnica

**Pergunta central:** o calculo esta correto, a norma vigente e citada, e a memoria rastreavel?

```
Selo e legislacao
[ ] O Selo de Validacao Legal Previa foi emitido antes do calculo (PA-04)?
[ ] Toda norma citada esta datada pelo ano do fato gerador (PA-03)?
[ ] A vigencia foi confirmada — norma nao revogada para a competencia?
[ ] O regime tributario do ano esta correto (Simples/Presumido/Real/MEI;
    transicao CBS/IBS 2026-2033 conforme o ano)?
[ ] Cada norma citada tem artigo/numero — nada de "a lei diz" (PA-11)?
[ ] Norma de alvo movel ou regra local nao confirmada marcada [VERIFICAR] (PA-06)?

Calculo
[ ] O calculo esta correto e foi feito de forma deterministica (Python) (P3)?
[ ] A memoria de calculo e rastreavel — cada numero pode ser conferido?
[ ] Valores atualizados pelo indice correto (Selic acumulada), nao nominal (PA-15)?
[ ] Quando ha mais de uma opcao, os cenarios foram apresentados lado a lado?
[ ] Competencia x caixa nao foram confundidos (PA-13)?
```

**Resultado R2:** `APROVADO` / `APROVADO COM RESSALVAS` / `REPROVADO` (norma errada, Selo ausente, calculo errado, PA violada — devolver com o erro indicado).

## 5. R3 — Conformidade

**Pergunta central:** a obrigacao e a certa, o prazo correto, a localizacao aplicada e o cruzamento feito?

```
Obrigacao e prazo
[ ] A obrigacao acessoria e a certa para o regime do cliente (PA-13)?
[ ] O que e obrigatorio foi distinguido do que e opcao do contribuinte (PA-12)?
[ ] Os prazos estao corretos e sinalizados — vencimento da obrigacao,
    decadencia/prescricao de 5 anos, opcao de regime (PA-18)?
[ ] O plugin nao afirma ter transmitido nem assinado a obrigacao (PA-08)?

Localizacao
[ ] O ISS usa a aliquota e a regra do MUNICIPIO do caso (PA-05)?
[ ] O ICMS usa a aliquota e a regra da UF do caso (PA-05)?
[ ] Regra municipal/estadual nao confirmada marcada [VERIFICAR] (PA-06)?

Cruzamento e legalidade
[ ] Os cruzamentos necessarios foram feitos — SPED x apurado x pago x
    declarado; banco x razao (P4)?
[ ] Toda divergencia encontrada foi apontada explicitamente?
[ ] Em recuperacao: o SPED foi retificado antes de compensar (PA-14)?
[ ] Nenhuma orientacao de sonegacao, fraude, simulacao ou omissao (PA-01)?
[ ] Demanda de litigio judicial encaminhada a advogado, nao tratada aqui (PA-16)?
[ ] Achado de auditoria com rastreabilidade — aponta documento e norma (PA-19)?
```

**Resultado R3:** `APROVADO` / `APROVADO COM RESSALVAS` / `REPROVADO` (violacao de PA, obrigacao/prazo errado, localizacao ausente, cruzamento omisso — devolver ao produtor).

## 6. R4 — Entrega

**Pergunta central:** a entrega esta clara, bem estruturada, com a ressalva CRC, e os numeros batem com a memoria de calculo?

```
Estrutura (Camada 3 / estilo-entrega-contabil)
[ ] A entrega segue a estrutura canonica — Escopo, Dados de entrada,
    Base legal, Memoria de calculo, Resultado, Ressalva?
[ ] A abertura traz a data do Selo de Validacao Legal?
[ ] O fechamento traz a ressalva de responsabilidade tecnica do contador (PA-07)?

Coerencia dos numeros
[ ] Todos os numeros do relatorio/resultado/deck batem com a memoria de
    calculo (PA-20)? Nenhum numero "solto" sem origem rastreavel.

Clareza e completude
[ ] Linguagem clara, tecnica e objetiva, adequada ao tipo de entrega?
[ ] Todos os pontos relevantes da demanda foram abordados?
[ ] Nao ha lacunas injustificadas ("a completar", "INSERIR", "[...]")?
[ ] O tom respeita {{TOM_VOZ_PERFIL}} e {{TOM_VOZ_INTENSIDADE}} configurados?

Pendencias
[ ] Cada ponto [INFORMAR] e [VERIFICAR] remanescente foi listado ao operador?
```

**Resultado R4:** `APROVADO` (pronta para entrega) / `APROVADO COM RESSALVAS` (ajustes menores, operador decide) / `REPROVADO` (estrutura ausente, numeros divergentes, lacunas criticas — devolver).

## 7. Relatorio final da Revisao Tecnica

Ao concluir as 4 rodadas, emitir o relatorio consolidado:

```
RELATORIO DE REVISAO TECNICA — R1-R4
Data da auditoria: [DD/MM/AAAA]
Entrega auditada: [tipo — ex: Apuracao Simples Nacional — competencia MM/AAAA]
Skill produtora: [nome da skill que gerou a entrega]
Caso: [slug do CASO.md]

R1 — Escopo e dados:  [APROVADO | APROVADO COM RESSALVAS | REPROVADO]
R2 — Tecnica:         [APROVADO | APROVADO COM RESSALVAS | REPROVADO]
R3 — Conformidade:    [APROVADO | APROVADO COM RESSALVAS | REPROVADO]
R4 — Entrega:         [APROVADO | APROVADO COM RESSALVAS | REPROVADO]

Veredito final:       [APROVADO | REVISAR | BLOQUEADO]

Ressalvas: [lista numerada — ou "nenhuma"]
Retrabalho exigido: [descricao precisa do que corrigir — ou "N/A"]
```

**Veredito final:**
- `APROVADO` — todas as rodadas APROVADO (ou COM RESSALVAS menores). A entrega vai ao usuario.
- `REVISAR` — ha ajustes pontuais; voltar a skill responsavel, corrigir e resubmeter.
- `BLOQUEADO` — violacao de Camada 1 (PA) ou erro tecnico grave; a entrega NAO sai ate ser refeita.

## 8. Retrabalho e ciclo de correcao

1. **Identificar** a rodada (R1/R2/R3/R4) e o item exato que falhou.
2. **Devolver** ao produtor original com o relatorio da rodada reprovada.
3. **O produtor** corrige e resubmete a entrega inteira — a Revisao reinicia do R1.
4. **Limite:** 3 ciclos de retrabalho. No 4o ciclo, alertar o operador de que o caso precisa de revisao manual urgente.

## 9. Vedacoes especificas

- **Nunca** emitir `APROVADO` sem completar as 4 rodadas em sequencia.
- **Nunca** ignorar uma reprovacao por pressao de prazo — registrar o waiver com `--no-revisao` para auditoria.
- **Nunca** criar conteudo contabil nesta skill — funcao exclusiva de auditoria.
- **Nunca** aprovar entrega com PA violada — qualquer PA ativa veredito `BLOQUEADO` em R3.

## 10. Protocolos acionados

Esta skill **e** o Protocolo 6 (Auditoria de Qualidade). Verifica em cada rodada a aplicacao dos demais: P1 (Selo em R2), P3 (memoria de calculo em R2 e R4), P4 (cruzamento em R3), P5 (localizacao em R3).

## 11. Localizacao

R3 confere explicitamente o eixo de localizacao: ISS pela aliquota e regra do municipio do caso, ICMS pela aliquota e regra da UF (PA-05). Regra local nao confirmada na entrega deve estar marcada `[VERIFICAR — norma municipal/estadual]` (PA-06) — sua ausencia reprova R3.

## 12. Integracao

**Chamada por:** `auditoria-contabil-master` antes de toda entrega; operador direto com `/revisao-final`.

**Recebe de:** qualquer skill produtora (Tier 1-9).

**Entrega para:** o operador (entrega aprovada) ou o produtor (retrabalho). Registra o veredito no `CASO.md` via `memoria-de-caso-contabil`.

**Sem esta skill:** entregas saem sem auditoria das 4 Camadas — risco de violacao de PA, calculo errado, norma desatualizada e responsabilidade tecnica do contador nao ressalvada. E invariante (nao-removivel).
