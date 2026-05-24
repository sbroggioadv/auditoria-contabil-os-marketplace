---
name: calculo-iss
description: >
  Apuracao mensal de ISS — identificacao do municipio competente (regra geral
  do prestador x excecoes do art. 3o da LC 116/2003 x dominio do tomador da
  LC 175/2020), retencao pelo tomador, aliquota minima 2% e maxima 5%, deducao
  de materiais e subempreitadas na construcao civil, NFS-e nacional e ISS do
  Simples pela aliquota efetiva do anexo. Calcula via Python, NFS-e a NFS-e,
  com memoria rastreavel. Base: LC 116/2003, LC 157/2016, LC 175/2020, lei
  municipal. Aciona: calcular ISS, item da LC 116, retencao de ISS, NFS-e,
  aliquota municipal, conflito entre municipios, construcao civil, ISS no
  Simples.
---

# CALCULO ISS

> Skill **Tier 2** — apuracao mensal do ISS. O ISS e tributo **municipal**: cada municipio define aliquota, lista de servicos, regra de retencao e prazo na sua lei propria. Esta e a skill mais sensivel ao eixo de localizacao. Toda apuracao exige o Selo de Validacao Legal Previa (P1) e e datada pelo ano do fato gerador (PA-03).

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com "calcular ISS", "item da LC 116", "retencao de ISS", "NFS-e", "aliquota municipal", "conflito entre municipios", "construcao civil", "ISS no Simples". Entrada: CNPJ do prestador, competencia, valor da NFS-e, item da LC 116/2003 (ou descricao do servico), municipio do prestador e do tomador, local de execucao, regime do prestador, materiais e subempreitadas (itens 7.02/7.05), se o tomador e obrigado a reter. Entrega: definicao do municipio competente, calculo passo a passo, memoria de calculo, instrucao de DAM e de emissao da NFS-e, checklist de conformidade.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.
- **Aciona antes de calcular:** `validador-legislacao-vigente` (P1) — aliquota, lista de servicos e regra de retencao sao definidas por lei municipal (alvo movel local); sem o Selo a apuracao nao comeca (PA-04).
- **Apoia-se em:** `analise-xml-fiscal` (dados da NFS-e), `analise-cnae-atividades` (incidencia ISS x ICMS).
- **Entrega para:** `revisao-final` (R1-R4), o `CASO.md`, a `apuracao-simples-nacional` (se prestador do Simples) e a `retencoes-tomador` (lado do tomador).

## 2. Lista de servicos da LC 116/2003 — pontos quentes

```
ITEM   SERVICO                          LOCAL DE INCIDENCIA
1.04   licenciamento de software        prestador (salvo SaaS — ver LC 175)
7.02   execucao de obra civil           LOCAL DA OBRA (excecao art. 3o)
7.05   reparos, reformas, conservacao   LOCAL DA OBRA (excecao art. 3o)
9.01   hospedagem                       LOCAL DO ESTABELECIMENTO
14.05  restaurantes / industrializacao  LOCAL DA EXECUCAO
15.01-15.18  servicos financeiros e cartao   DOMICILIO DO TOMADOR (LC 175)
16.01-16.02  transporte municipal        regime proprio
17.05  agenciamento / cessao de MO      LOCAL DA EXECUCAO / tomador
```

O **item** correto e a primeira decisao da apuracao — o item define o local de incidencia e, em parte, a aliquota. Item errado contamina todo o calculo.

## 3. Municipio competente — prestador, tomador ou execucao

```
REGRA GERAL (LC 116 art. 3o, caput)
  ISS devido ao municipio do ESTABELECIMENTO PRESTADOR.

EXCECOES — local da execucao (art. 3o, incisos)
  construcao civil 7.02/7.05, limpeza, vigilancia, seguranca,
  cessao de mao de obra, recreacao e lazer, hospedagem.

DOMICILIO DO TOMADOR (LC 175/2020)
  planos de saude, administracao de cartoes, leasing, agenciamento e
  itens correlatos — recolhimento para o municipio do tomador.
```

Decidir o municipio competente **antes** de aplicar aliquota. Errar o municipio gera ISS recolhido ao ente errado e exposicao a cobranca pelo ente correto — bitributacao de fato.

## 4. Aliquotas, base e deducoes

```
Aliquota minima 2% (LC 157/2016) — vedado beneficio que reduza abaixo de 2%,
  salvo itens 7.02, 7.05 e 16.01.
Aliquota maxima 5% (LC 116) — cada municipio fixa a sua na lei municipal.
Base = valor do servico - deducoes admitidas.
```

**Construcao civil (itens 7.02/7.05)** — deducao da base, conforme permitir a lei municipal: materiais incorporados a obra fornecidos pelo prestador (com NF de aquisicao) e subempreitadas ja tributadas pelo ISS. A amplitude da deducao varia por municipio — `[VERIFICAR]` a lei municipal.

A aliquota concreta e sempre a da **lei municipal vigente** (nao decreto). Cravar aliquota de memoria e fonte de erro — `[VERIFICAR — norma municipal]` (PA-05/PA-06).

## 5. ISS no Simples Nacional e retencao pelo tomador

- **Prestador do Simples:** o ISS esta embutido no DAS, pela **aliquota efetiva do anexo** (Resolucao CGSN 140/2018, art. 21). Quando ha retencao, o tomador retem pela aliquota efetiva informada na NFS-e — **nunca a aliquota cheia municipal**. Erro classico: reter 5% cheia de prestador do Simples gera ISS pago em duplicidade.
- **Retencao pelo tomador (regime normal):** quando a lei municipal obriga, o tomador retem o ISS, recolhe via DAM e fornece comprovante; o prestador abate o valor retido na apuracao mensal. A obrigacao de reter e definida pela lei do municipio competente — `[VERIFICAR]`.

## 6. Calculo via Python (P3)

```python
python3 -c "
def iss(valor_servico, materiais=0, subempreitada_com_iss=0, descontos=0, aliquota=0.05):
    base = valor_servico - materiais - subempreitada_com_iss - descontos
    return base, base * aliquota

def iss_simples(valor_servico, aliq_efetiva_iss_anexo):
    return valor_servico * aliq_efetiva_iss_anexo  # aliq efetiva [VERIFICAR]

base, devido = iss(100_000, 30_000, 0, 0, 0.05)   # construcao 7.02, aliquota [VERIFICAR]
print(f'Base ISS: R\$ {base:,.2f} | ISS devido: R\$ {devido:,.2f}')
"
```

## 7. Formato de entrega

```
APURACAO ISS — NFS-e [n] — competencia [MM/AAAA] — CNPJ [...]
Selo de Validacao Legal Previa: [data]   Item LC 116: [...]

Municipio do prestador: [...]   Municipio do tomador: [...]
Local de execucao: [...]   ISS DEVIDO A: [municipio] (LC 116 art. 3o [...])

Valor do servico ............... [...]
(-) Materiais (com NF) ......... [...]
(-) Subempreitadas com ISS ..... [...]
(=) Base de calculo ............ [...]
Aliquota municipal [VERIFICAR] . [...]%
ISS .............................. [...]
(-) ISS retido pelo tomador .... [...]
ISS a recolher (DAM) ........... [...]   Vencimento: [lei municipal]

RESSALVA: rascunho operacional sujeito a revisao e responsabilidade tecnica
do contador com CRC ativo (PA-07).
```

## 8. Anti-padroes

- Recolher o ISS ao municipio errado (prestador x execucao x tomador).
- Reter ISS de prestador do Simples pela aliquota cheia — o correto e a efetiva do anexo.
- Aceitar bitributacao por dois municipios sem apontar a divergencia.
- Nao emitir NFS-e em municipio com o Sistema Nacional NFS-e ativo.
- Esquecer a deducao de materiais na construcao quando a lei municipal a permite.
- Confundir item 14.05 (restaurante) com 9.01 (hospedagem).
- Cravar aliquota municipal de memoria — `[VERIFICAR]` na lei do municipio.

## 9. Casos de borda

- **Software como servico (SaaS):** o STF (ADI 5.659) firmou que software e ISS, nao ICMS — item 1.05. Alguns municipios resistem; guardar a fundamentacao.
- **Servico prestado a distancia entre UFs:** regra geral e o municipio do estabelecimento prestador; sendo item 7.02 ou cessao de MO, e o local da execucao.
- **Prestador autonomo (PF) com ISS fixo:** regime proprio do municipio, em regra trimestral.
- **Importacao de servico:** ISS na importacao (LC 116, art. 1o, §1o) — recolhido pelo tomador.
- **ISS pago indevidamente a maior:** restituicao/compensacao municipal — trabalho de auditoria (Tier 7, v0.3).

## Vedacoes especificas

- **PA-01** — nao orientar simulacao de local de prestacao para reduzir ISS.
- **PA-02** — calcular so com dado real (valor da NFS-e, item, municipios, regime).
- **PA-03** — datar a apuracao pelo ano do fato gerador (reforma 2026-2033 — ISS sera absorvido pelo IBS na transicao).
- **PA-04** — sem o Selo de Validacao Legal Previa, a apuracao nao comeca.
- **PA-05** — aliquota, item e regra de retencao sempre do **municipio** do caso — nunca aliquota generica.
- **PA-06** — `[VERIFICAR]` em aliquota municipal, regra de deducao e obrigacao de retencao nao confirmadas.
- **PA-08** — a skill calcula e prepara a DAM; nao transmite a NFS-e nem recolhe o tributo.
- **PA-11** — citar a norma (LC 116/2003 com item; LC 157/2016; LC 175/2020; lei municipal com numero) — exigir o numero da lei municipal.

## Protocolos acionados

- **P1 — Validacao Legal Previa** — Selo emitido por `validador-legislacao-vigente`, confirmando a lei municipal vigente.
- **P3 — Calculo** — memoria rastreavel NFS-e a NFS-e, calculo em Python.
- **P5 — Localizacao** — eixo central desta skill: o municipio competente define item, aliquota, retencao e prazo.
- **P6 — Auditoria de Qualidade** — `revisao-final` R1-R4 antes da entrega.

## Localizacao

O ISS e tributo **municipal** — esta e a skill mais dependente do eixo geografico de todo o plugin. O **municipio competente** (definido pela regra do art. 3o da LC 116 — prestador, local da execucao ou domicilio do tomador) determina: a aliquota concreta (entre 2% e 5%, fixada na lei municipal), a lista de servicos e o enquadramento do item, a obrigacao e a aliquota de retencao pelo tomador, a amplitude da deducao de materiais na construcao civil, o prazo de recolhimento da DAM e o sistema de emissao da NFS-e. Como a legislacao municipal e fragmentada — cada um dos milhares de municipios tem lei propria —, toda regra municipal nao confirmada e marcada `[VERIFICAR — norma municipal]` (PA-06). Nunca inventar aliquota, codigo de receita da DAM ou prazo municipal. O Sistema Nacional NFS-e padroniza a emissao, mas nao a aliquota nem a lei material, que seguem municipais.

## Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.

**Entrega para:** `revisao-final` (R1-R4), o `CASO.md`, a `apuracao-simples-nacional` (prestador do Simples — ISS no DAS) e a `retencoes-tomador` (lado do tomador). Restituicao de ISS pago a maior e trabalho de auditoria (Tier 7, v0.3). Disputa entre municipios contestada em juizo extrapola o contabil — encaminhar a advogado (slot generico, PA-16).

**Sem esta skill:** o ISS e recolhido sem confirmar o municipio competente — risco de bitributacao e de retencao incorreta do prestador do Simples.
