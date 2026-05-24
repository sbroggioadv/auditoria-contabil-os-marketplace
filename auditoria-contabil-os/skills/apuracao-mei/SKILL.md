---
name: apuracao-mei
description: >
  Apuracao do MEI — DAS-MEI mensal de valor fixo, DASN-SIMEI anual, controle do
  limite anual de faturamento, diagnostico de estouro e migracao para ME no
  Simples. Trata empregado do MEI (DAE) e retencao de INSS pelo tomador. Base: LC
  123/2006, art. 18-A, Resolucao CGSN 140/2018. Nao trata ME/EPP no Simples (ver
  apuracao-simples-nacional). Aciona: apurar MEI, DAS-MEI, PGMEI, DASN-SIMEI,
  limite do MEI, desenquadramento, migracao do MEI para ME, NFS-e do MEI,
  empregado do MEI, MEI estourou o limite.
---

# APURACAO MEI

> Skill **Tier 2** — apuracao do Microempreendedor Individual: DAS-MEI mensal fixo, DASN-SIMEI anual, controle do limite de faturamento e diagnostico de migracao para ME. Toda apuracao exige o Selo de Validacao Legal Previa (P1) e e datada pelo ano do fato gerador.

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com "apurar MEI", "DAS-MEI", "PGMEI", "DASN-SIMEI", "limite do MEI", "desenquadramento", "MEI estourou". Entrada: CNPJ, competencia, faturamento do mes e acumulado do ano, atividade, mes de abertura, existencia de empregado. Entrega: tabela de controle anual, DAS-MEI ou instrucao de emissao, diagnostico de risco de estouro e, quando perto do limite, carta-aviso ao cliente.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.
- **Aciona antes de calcular:** `validador-legislacao-vigente` (P1) — o limite, o valor do DAS-MEI e a lista de atividades permitidas sao alvo movel; sem o Selo a apuracao nao comeca (PA-04).
- **Apoia-se em:** `analise-cnae-atividades` (atividade permitida ao MEI), `calendario-fiscal` (vencimentos).
- **Entrega para:** `revisao-final` (R1-R4), o `CASO.md`. Em estouro, encaminha para `apuracao-simples-nacional`.

## 2. DAS-MEI mensal — valor fixo

O MEI recolhe um DAS de **valor fixo** mensal (LC 123/2006, art. 18-A), nao um percentual sobre a receita. O DAS-MEI compoe-se de:

- **INSS** — percentual do salario minimo vigente (contribuicao do segurado).
- **ICMS** — valor fixo, para atividade de comercio/industria.
- **ISS** — valor fixo, para atividade de servico.

Comercio recolhe INSS + ICMS; servico, INSS + ISS; atividade mista, INSS + ICMS + ISS. Os valores absolutos acompanham o salario minimo do ano — `[VERIFICAR]` o valor vigente, nunca cravar de memoria (PA-06). O DAS-MEI vence mensalmente; o calendario exato fica em `calendario-fiscal`.

## 3. Limite anual e desenquadramento

O MEI tem um **limite anual de faturamento** (LC 123/2006, art. 18-A; o valor e alvo movel — `[VERIFICAR]` o teto do ano). Inicio de atividade no meio do ano: limite proporcional aos meses de existencia do CNPJ no ano.

Regra de estouro:

| Situacao | Efeito |
|----------|--------|
| Faturamento dentro do limite | Mantem MEI |
| Excesso de ate 20% do limite | Mantem MEI no ano-calendario; migra para ME em 1o/jan do ano seguinte; comunicacao no portal |
| Excesso acima de 20% | Desenquadramento **retroativo** a 1o/jan do ano corrente; apura Simples como ME desde janeiro, com encargo por atraso |

> O MEI-Caminhoneiro tem teto e regra propria — fora do escopo desta skill.

## 4. Diagnostico de risco — sempre rodado

A cada apuracao, estimar em quantos meses o cliente estoura:

```
Meses ate o estouro = (limite anual - acumulado) / faturamento medio mensal
```

Estimativa abaixo de 3 meses: alerta imediato. Abaixo de 6 meses: alerta com plano de migracao. O MEI opera em volume — o cliente que estoura sem aviso vira passivo.

## 5. Calculo e controle via Python (P3)

```python
python3 -c "
def das_mei(tipo, inss_valor, icms_valor, iss_valor):
    base = {'comercio': inss_valor + icms_valor,
            'servico': inss_valor + iss_valor,
            'misto': inss_valor + icms_valor + iss_valor}
    return base[tipo]   # valores absolutos do ano — [VERIFICAR]

def status_anual(meses_ativos, acumulado, limite_anual, limite_mensal):
    limite = min(limite_anual, limite_mensal * meses_ativos)
    excesso = acumulado - limite
    if excesso <= 0:
        return f'OK — uso {acumulado/limite:.1%} do limite'
    if excesso <= limite_anual * 0.20:
        return f'EXCESSO ATE 20% — migra para ME em 1o/jan; Simples sobre R\$ {excesso:,.2f}'
    return 'EXCESSO > 20% — DESENQUADRAMENTO RETROATIVO a 1o/jan do ano corrente'

print(status_anual(12, 85_000, 81_000, 6_750))
"
```

Os limites usados sao confirmados com `validador-legislacao-vigente` no ano do fato gerador.

## 6. Empregado do MEI e retencao do tomador

- **Empregado:** o MEI pode ter **1 empregado**, com salario igual ao minimo ou ao piso da categoria. O encargo (INSS patronal + FGTS) e recolhido em guia propria (DAE) mensal; folha simplificada no portal.
- **Retencao de INSS pelo tomador:** PJ tomadora retem INSS sobre o servico do MEI quando a atividade for de cessao de mao de obra (construcao, conservacao, vigilancia — Lei 8.212/91, art. 31). Demais atividades nao tem retencao — confirmar a atividade.

## 7. DASN-SIMEI e formato de entrega

A **DASN-SIMEI** e a declaracao anual de informacoes (receita bruta do ano anterior), com prazo anual proprio e multa por atraso.

```
CONTROLE MEI — [CNPJ] — atividade [...] — ano [AAAA]
Selo de Validacao Legal Previa: [data]   Local: [municipio]/[UF]

| Mes | Faturamento | Acumulado | DAS-MEI | NFS-e a PJ |
Limite anual: R$ [...] [VERIFICAR]   Uso: [...]%   Estimativa de estouro: [mes]
Status: [OK | ATENCAO — preparar migracao | DESENQUADRADO]
DASN-SIMEI: [situacao]

RESSALVA: rascunho operacional sujeito a revisao e responsabilidade tecnica
do contador com CRC ativo (PA-07).
```

## 8. Anti-padroes

- Esquecer o DAS-MEI de algum mes — gera debito e suspende beneficios previdenciarios.
- Nao monitorar o acumulado — o estouro chega de surpresa em dezembro.
- Receber pagamento de PJ sem emitir NFS-e.
- Manter o cliente como MEI ja desenquadrado — acumula divida de Simples retroativo.
- Confundir o limite proporcional de inicio de atividade com o teto anual cheio.
- Dar um unico alerta no fim do ano — alertar mensalmente acima de 70% do limite.
- Cravar valor do DAS-MEI ou teto de memoria — `[VERIFICAR]` no ano.

## 9. Casos de borda

- **Cliente novo com poucos meses de CNPJ e faturamento alto:** aplicar o limite proporcional — pode ja ter estourado.
- **CNPJ aberto cedo mas faturamento so depois:** o limite e anual cheio; meses iniciais sem atividade nao reduzem o teto.
- **Atividade que passou a ser vedada ao MEI:** desenquadrar imediatamente.
- **Debitos de DAS-MEI acumulados:** parcelamento especifico do MEI; sinalizar.
- **Repasse de programa social:** em regra nao compoe o faturamento — confirmar.

## 10. Vedacoes especificas

- **PA-01 / PA-10** — nao orientar a manter o MEI apos o estouro nem fracionar receita; a migracao e obrigatoria.
- **PA-02** — apurar so com dado real (faturamento, acumulado, mes de abertura, atividade).
- **PA-03** — datar a apuracao pelo ano do fato gerador; limite e valor do DAS-MEI mudam por ano.
- **PA-04** — sem o Selo de Validacao Legal Previa, a apuracao nao comeca.
- **PA-06** — `[VERIFICAR]` no teto, no valor do DAS-MEI e na lista de atividades permitidas.
- **PA-08** — a skill apura e prepara; nao transmite a DASN-SIMEI nem recolhe o DAS.
- **PA-11** — citar a norma (LC 123/2006, art. 18-A; CGSN 140/2018) com artigo.
- **PA-12** — distinguir obrigacao (DAS, DASN) de opcao (desenquadramento voluntario).
- **PA-18** — sinalizar o prazo da DASN-SIMEI e o risco de estouro do limite.

## 11. Protocolos acionados

- **P1 — Validacao Legal Previa** — Selo emitido por `validador-legislacao-vigente` antes do calculo.
- **P3 — Calculo** — controle anual e diagnostico de estouro em Python.
- **P5 — Localizacao** — ICMS (UF) e ISS (municipio) compoem o DAS-MEI; NFS-e e municipal.
- **P6 — Auditoria de Qualidade** — `revisao-final` R1-R4 antes da entrega.

## 12. Localizacao

O DAS-MEI embute uma parcela fixa de **ICMS** (definida pela **UF**) e/ou de **ISS** (definida pelo **municipio**). A obrigacao de NFS-e para servico prestado a PJ segue o sistema do **municipio**. Quando a regra municipal de NFS-e nao puder ser confirmada, marcar `[VERIFICAR — norma municipal]` (PA-05/PA-06).

## 13. Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.

**Entrega para:** `revisao-final` (R1-R4) e o `CASO.md`. No estouro, a apuracao retroativa como ME e feita por `apuracao-simples-nacional`; a contratacao de empregado aciona as skills de folha (Tier 4, v0.2).

**Sem esta skill:** o MEI opera sem controle do limite — risco de estouro silencioso e divida de Simples retroativo.
