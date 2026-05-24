---
name: inss-empresa
description: >
  Apuracao do INSS patronal mensal — cota patronal de 20%, RAT ajustado pelo
  FAP, contribuicao a Terceiros, CPP de 20% sobre o pro-labore de contribuinte
  individual, desoneracao da folha (CPRB) na transicao da Lei 14.973/2024,
  atividades concomitantes proporcionalizadas por receita e regra do Simples
  Anexo IV (INSS por fora do DAS). Calcula via Python, com memoria rastreavel,
  comparativo CPRB x folha e guia de recolhimento. Base: Lei 8.212/91, Decreto
  3.048/99, Lei 12.546/11, Lei 14.973/2024. Aciona: calcular INSS patronal,
  CPP, RAT, FAP, Terceiros, CPRB, desoneracao da folha, Anexo IV, DCTFWeb INSS.
---

# INSS EMPRESA

> Skill **Tier 2** — apuracao da contribuicao previdenciaria patronal mensal. O RAT, o FAP, a composicao de Terceiros e o cronograma da desoneracao sao **alvo movel** — variam por CNAE e por ano. Exige o Selo de Validacao Legal Previa (P1) e e datada pelo ano do fato gerador (PA-03).

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com "calcular INSS patronal", "CPP", "RAT", "FAP", "Terceiros", "CPRB", "desoneracao da folha", "Anexo IV", "DCTFWeb INSS". Entrada: CNPJ, competencia, folha total bruta do mes (salario, adicionais, horas extras, comissoes habituais), CNAE preponderante, RAT e FAP, pro-labore, regime (normal, Simples Anexo IV, setor desonerado), receita do mes (para o comparativo CPRB). Entrega: apuracao mensal por rubrica, comparativo CPRB x folha quando aplicavel, guia de recolhimento, memoria de calculo e checklist.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto, e a frente de folha (Tier 4, v0.2).
- **Aciona antes de calcular:** `validador-legislacao-vigente` (P1) — RAT por CNAE, FAP do ano, composicao de Terceiros e o estagio da desoneracao mudam por norma; sem o Selo a apuracao nao comeca (PA-04).
- **Apoia-se em:** a folha bruta consolidada e premissa; o INSS patronal incide sobre as rubricas habituais da folha.
- **Entrega para:** `revisao-final` (R1-R4), o `CASO.md` e a `dctfweb` (Tier 3 — debitos por rubrica).

## 2. Componentes do INSS patronal — estrutura

```
REGIME REGULAR
  CPP (cota patronal) ... 20% sobre a folha
  RAT (Risco Ambiental do Trabalho) ... 1%, 2% ou 3% conforme o CNAE
       (Anexo V do Decreto 3.048/99)                              [VERIFICAR]
  FAP (Fator Acidentario de Prevencao) ... 0,5 a 2,0, publicado
       anualmente pela RFB, por CNPJ                              [VERIFICAR]
  RAT efetivo = RAT x FAP
  Terceiros ... composicao por CNAE (SESI/SESC/SENAI/INCRA/
       Salario-Educacao/SEBRAE), em torno de 5,8% no caso tipico  [VERIFICAR]

CPP de 20% sobre o pro-labore -> contribuinte individual
  (Lei 8.212 art. 22, III). NAO incide RAT x FAP nem Terceiros sobre pro-labore.
```

O RAT, o FAP e a composicao de Terceiros sao especificos do CNAE e do ano — nunca cravar de memoria. `[VERIFICAR]` no Selo (P1).

## 3. Bases — o que entra e o que nao entra

```
ENTRA na base do INSS patronal
  salario, horas extras, adicionais (periculosidade, insalubridade, noturno),
  comissoes habituais, 13o salario (na 2a parcela), ferias e o terco
  constitucional, aviso previo indenizado.

NAO ENTRA
  vale-transporte, vale-refeicao/alimentacao pelo PAT, indenizacoes nao
  habituais, PLR (Lei 10.101/2000), diarias dentro do limite legal.
```

## 4. Desoneracao da folha — CPRB na transicao da Lei 14.973/2024

A Lei 14.973/2024 estabeleceu a **reoneracao gradual** da folha dos setores antes desonerados — a CPRB (contribuicao sobre a receita bruta) e substituida progressivamente pela CPP sobre a folha, ano a ano, ate a extincao do regime.

```
A divisao por ano entre CPRB e CPP-folha durante a transicao e definida
pela Lei 14.973/2024 -> confirmar o percentual do ano no Selo (P1).  [VERIFICAR]
A opcao pela CPRB e feita no inicio do ano e e irretratavel para o exercicio.
CPRB: DARF 2985, vencimento dia 20 do mes seguinte.
```

Para o setor desonerado, apresentar o **comparativo CPRB x folha** no ano do fato gerador.

## 5. Regras criticas

- **Atividades concomitantes:** empresa com parte da atividade desonerada e parte nao — proporcionaliza a contribuicao pela receita de cada atividade (Lei 12.546, art. 9o, §1o).
- **Simples Anexo IV** (construcao, vigilancia, limpeza): o INSS patronal e recolhido **por fora do DAS**, em guia propria — CPP 20% + RAT x FAP + Terceiros. Nos demais anexos (I, II, III, V), a CPP esta embutida no DAS.
- **Pro-labore:** CPP de 20% como contribuinte individual; sem RAT x FAP e sem Terceiros.
- **Aprendiz:** aliquota de CPP reduzida sobre o salario do aprendiz (Lei 10.097/2000) — `[VERIFICAR]`.

## 6. Calculo via Python (P3)

```python
python3 -c "
def inss_patronal(folha, rat, fap, terceiros, prolabore=0):
    cpp = folha * 0.20
    rat_efetivo = folha * rat * fap
    terc = folha * terceiros
    cpp_prolabore = prolabore * 0.20
    total = cpp + rat_efetivo + terc + cpp_prolabore
    return dict(cpp=cpp, rat_efetivo=rat_efetivo, terceiros=terc,
                cpp_prolabore=cpp_prolabore, total=total)

# rat / fap / terceiros = [VERIFICAR] no Selo (P1) — valores ilustrativos
for k, v in inss_patronal(100_000, 0.02, 1.0, 0.058, 5_000).items():
    print(f'{k}: R\$ {v:,.2f}')
"
```

## 7. Formato de entrega

```
INSS PATRONAL — competencia [MM/AAAA] — CNPJ [...] — CNAE [...]
Selo de Validacao Legal Previa: [data]   RAT/FAP/Terceiros: [VERIFICAR]

Folha total ........................ [...]
Pro-labore ......................... [...]
CPP 20% x folha .................... [...]
RAT [%] x FAP [valor] x folha ...... [...]
Terceiros [%] x folha .............. [...]
CPP 20% x pro-labore ............... [...]
(=) TOTAL INSS PATRONAL ............ [...]
Vencimento: dia 20/MM+1   —   DCTFWeb (debitos por rubrica)

Comparativo CPRB x folha (se setor desonerado): [...]
RESSALVA: rascunho operacional sujeito a revisao e responsabilidade tecnica
do contador com CRC ativo (PA-07).
```

## 8. Anti-padroes

- Aplicar RAT incorreto para o CNAE da empresa.
- Usar FAP desatualizado — a RFB o publica a cada ano, por CNPJ.
- Nao separar a atividade desonerada da nao-desonerada na proporcionalizacao.
- Esquecer a CPP de 20% sobre o pro-labore (contribuinte individual).
- Omitir a contribuicao a Terceiros.
- Empresa do Simples Anexo IV recolhendo o INSS patronal apenas pelo DAS.
- Cravar RAT, FAP ou Terceiros de memoria — `[VERIFICAR]` no Selo.

## 9. Casos de borda

- **Transicao CPRB -> folha:** simular os cenarios ano a ano durante a vigencia da Lei 14.973/2024 — pode ser vantajoso migrar antes da extincao.
- **Empresa multi-CNAE:** o RAT e o da atividade preponderante (em regra, a de maior numero de empregados).
- **Folha com PLR:** a PLR nao entra na base do INSS (Lei 10.101/2000).
- **Filial em outra UF:** lotacao tributaria distinta — o RAT pode diferir.
- **Aprendiz:** aliquota de CPP reduzida — `[VERIFICAR]` na lei vigente.

## Vedacoes especificas

- **PA-01** — nao orientar a classificar rubrica habitual como indenizatoria para reduzir a base.
- **PA-02** — calcular so com dado real (folha bruta, CNAE, RAT/FAP, pro-labore, competencia).
- **PA-03** — datar pelo ano do fato gerador — o cronograma da desoneracao e ano a ano.
- **PA-04** — sem o Selo de Validacao Legal Previa, a apuracao nao comeca.
- **PA-06** — `[VERIFICAR]` em RAT, FAP, composicao de Terceiros e percentual da transicao da CPRB nao confirmados.
- **PA-08** — a skill calcula e prepara a guia; nao transmite a DCTFWeb nem recolhe.
- **PA-11** — citar a norma (Lei 8.212/91 art. 22; Decreto 3.048/99; Lei 12.546/11; Lei 14.973/2024) com artigo.
- **PA-13** — nao confundir o regime tributario com a obrigacao acessoria; nao confundir contribuinte individual com empregado.
- **PA-15** — INSS em atraso atualizado pelo encargo legal, nunca valor nominal.

## Protocolos acionados

- **P1 — Validacao Legal Previa** — Selo emitido por `validador-legislacao-vigente`, com RAT/FAP/Terceiros e o estagio da desoneracao do ano.
- **P3 — Calculo** — memoria rastreavel por rubrica, calculo em Python; comparativo CPRB x folha como cenario (P3).
- **P4 — Cruzamento** — INSS apurado x eSocial x DCTFWeb.
- **P6 — Auditoria de Qualidade** — `revisao-final` R1-R4 antes da entrega.

## Localizacao

O INSS patronal e contribuicao **federal** — aliquotas e regras sao uniformes em todo o territorio nacional, sem variacao por municipio ou UF. O eixo de localizacao incide de forma pontual: uma **filial em outra UF** pode ter lotacao tributaria propria e, portanto, RAT distinto, conforme a atividade preponderante daquele estabelecimento. A apuracao em si nao depende da localizacao; o RAT/FAP e funcao do CNAE e do estabelecimento, nao do municipio.

## Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto, e a frente de folha (Tier 4, v0.2).

**Entrega para:** `revisao-final` (R1-R4), o `CASO.md` e a `dctfweb` (debitos de INSS por rubrica). O INSS patronal e uma das saidas da folha mensal completa, consolidada pela frente de folha (Tier 4, v0.2). A decisao estrategica entre CPRB e folha conecta-se ao comparativo de regime. Discussao judicial sobre a base do INSS extrapola o contabil — encaminhar a advogado (slot generico, PA-16).

**Sem esta skill:** o INSS patronal e estimado sem RAT/FAP confirmados e sem o comparativo da desoneracao — risco de recolhimento incorreto e de divergencia na DCTFWeb.
