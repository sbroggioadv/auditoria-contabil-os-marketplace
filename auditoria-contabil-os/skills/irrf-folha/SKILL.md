---
name: irrf-folha
description: >
  Calculo do IRRF na folha de pagamento (salario CLT, pro-labore, RPA de
  autonomo) e em pagamentos de PJ a PF (aluguel, juros, royalties) — tabela
  progressiva mensal, deducao por dependente e pensao alimenticia, INSS
  deduzido da base, opcao pelo desconto simplificado, regime de tributacao do
  13o em DARF separado e hipoteses de nao-incidencia (aviso indenizado, ferias
  indenizadas, multa de 40% do FGTS). Calcula via Python, com memoria
  rastreavel e DARF por natureza. Base: Lei 7.713/88, RIR/2018, sumulas STJ.
  Aciona: calcular IRRF, folha CLT, pro-labore, RPA, DARF 0561, dependente de
  IR, tabela progressiva, IRRF do 13o, aluguel pago a pessoa fisica.
---

# IRRF FOLHA

> Skill **Tier 2** — calculo do Imposto de Renda Retido na Fonte sobre rendimentos do trabalho e pagamentos de PJ a PF. As faixas, deducoes e o valor do desconto simplificado sao **alvo movel anual** — nunca cravar de memoria. Exige o Selo de Validacao Legal Previa (P1) e e datada pelo ano do fato gerador (PA-03).

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com "calcular IRRF", "folha CLT", "pro-labore", "RPA", "DARF 0561", "dependente de IR", "tabela progressiva", "IRRF do 13o", "aluguel pago a PF". Entrada: natureza do rendimento (salario CLT, pro-labore, RPA, aluguel, 13o), valor bruto, INSS ja calculado, numero de dependentes, pensao alimenticia judicial, competencia. Entrega: calculo passo a passo, comparativo entre deducoes legais e desconto simplificado, DARF correto por natureza, avisos de nao-incidencia, memoria de calculo.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto, e a frente de folha (Tier 4, v0.2).
- **Aciona antes de calcular:** `validador-legislacao-vigente` (P1) — a tabela progressiva, a deducao por dependente e o desconto simplificado mudam por lei/IN a cada ano; sem o Selo o calculo nao comeca (PA-04).
- **Apoia-se em:** o INSS retido do empregado e premissa do calculo (base do IRRF = bruto - INSS - deducoes).
- **Entrega para:** `revisao-final` (R1-R4), o `CASO.md`, a `dctfweb` e a `efd-reinf` (Tier 3 — IRRF declarado).

## 2. Tabela progressiva e parametros — alvo movel

```
A tabela progressiva mensal do IRRF (faixas, aliquotas de 0% a 27,5% e
parcela a deduzir), o valor da deducao por dependente e o valor do desconto
simplificado sao definidos por lei e atualizados anualmente.
-> NAO cravar valores. Confirmar na IN RFB do ano do fato gerador,
   via Selo de Validacao Legal Previa (P1).  [VERIFICAR]

ESTRUTURA (valores [VERIFICAR] no ano)
  Base mensal por faixa -> aliquota -> parcela a deduzir
  IRRF = base x aliquota da faixa - parcela a deduzir
  Deducao por dependente: valor fixo mensal por dependente   [VERIFICAR]
  Desconto simplificado: valor fixo, alternativo as deducoes legais  [VERIFICAR]
```

## 3. Codigos DARF por natureza

```
0561  trabalho assalariado, pro-labore, 13o salario (DARF separado)
0588  servicos profissionais prestados por autonomo (PF) a PF
1708  servicos profissionais prestados por PJ
3208  aluguel e juros pagos a pessoa fisica
0473  juros sobre capital proprio
Vencimento do IRRF da folha: em regra dia 20 do mes seguinte  [VERIFICAR]
```

O codigo errado gera divergencia no cruzamento com a DCTFWeb e a EFD-Reinf.

## 4. Base de calculo e deducoes

```
Base IRRF = rendimento bruto
          - INSS retido do beneficiario
          - (dependentes x deducao por dependente)
          - pensao alimenticia judicial
                            OU
Base IRRF = rendimento bruto - desconto simplificado (opcao mais vantajosa)
```

Calcular **as duas formas** e aplicar a que resultar em menor imposto. O desconto simplificado dispensa a comprovacao das deducoes legais.

## 5. Regras criticas

- **13o salario:** tributado em **DARF 0561 separado**, sobre o total do 13o (nao parcela a parcela). A 1a parcela e antecipacao — sem INSS e sem IRRF; a 2a parcela concentra o INSS e o IRRF sobre o total do 13o.
- **Nao incide IRRF** sobre: aviso previo indenizado (Sumula 463 STJ), ferias indenizadas (Tema 481 STJ) e multa de 40% do FGTS (RE 595.838 STF).
- **Pro-labore:** INSS de 11% ate o teto + IRRF pela tabela progressiva.
- **RPA de autonomo (PF) pago por PJ:** o tomador retem INSS, IRRF pela tabela e ISS conforme a lei municipal — nao e carne-leao.
- **Aluguel de PJ a PF:** IRRF pela tabela; deduz-se da base o IPTU pago pelo locador, o condominio e a comissao imobiliaria.

## 6. Calculo via Python (P3)

```python
python3 -c "
# Faixas e parcelas a deduzir = [VERIFICAR] na IN RFB do ano do fato gerador.
# Estrutura ilustrativa — substituir pelos parametros validados no Selo (P1).
FAIXAS = [
    (0.0,  0.0,   0.0),   # (limite, aliquota, parcela_deduzir) [VERIFICAR]
]
DEP = 0.0  # deducao por dependente [VERIFICAR]

def irrf_mensal(bruto, inss=0, dependentes=0, pensao=0):
    base = bruto - inss - dependentes * DEP - pensao
    for limite, aliq, pd in FAIXAS:
        if base <= limite:
            return max(0.0, base * aliq - pd), base
    limite, aliq, pd = FAIXAS[-1]
    return max(0.0, base * aliq - pd), base

print('Carregar FAIXAS e DEP do ano via Selo de Validacao Legal Previa (P1).')
"
```

## 7. Formato de entrega

```
IRRF — beneficiario [...] — competencia [MM/AAAA] — CPF [...]
Selo de Validacao Legal Previa: [data]   Tabela do ano: [VERIFICAR]

Rendimento bruto ................... [...]
(-) INSS retido .................... [...]
(-) Dependentes ([n] x deducao) .... [...]
(-) Pensao alimenticia ............. [...]
(=) Base IRRF (deducoes legais) .... [...]
(=) Base IRRF (simplificado) ....... [...]   -> aplicar a menor
IRRF = base x aliquota da faixa - parcela a deduzir = [...]
DARF [codigo conforme natureza] .... [...]   Vencimento: [VERIFICAR]

Nao-incidencia (se aplicavel): aviso indenizado / ferias indenizadas /
multa 40% do FGTS — sem IRRF (Sum 463 STJ / Tema 481 STJ / RE 595.838).
RESSALVA: rascunho operacional sujeito a revisao e responsabilidade tecnica
do contador com CRC ativo (PA-07).
```

## 8. Anti-padroes

- Tributar o 13o junto com a folha do mes — o 13o tem DARF 0561 proprio.
- Esquecer dependentes que o beneficiario declarou.
- Calcular a aliquota sem aplicar a parcela a deduzir da faixa.
- Reter sobre o teto do INSS quando a soma pro-labore + autonomo ainda nao o atingiu.
- Nao reter IRRF de autonomo sob o argumento de que ele ajusta no IRPF anual.
- Esquecer a retencao no aluguel pago por PJ a PF.
- Reter IRRF sobre aviso indenizado, ferias indenizadas ou multa de 40%.
- Cravar a tabela progressiva de memoria — `[VERIFICAR]` na IN RFB do ano.

## 9. Casos de borda

- **Beneficiario com duas fontes de renda:** cada fonte retem seu IRRF; o ajuste e no IRPF anual.
- **Pro-labore acima do teto do INSS:** o INSS para no teto; o IRRF segue a tabela progressiva.
- **PLR (Lei 10.101/2000):** tributacao separada, em tabela especifica, com DARF proprio.
- **Stock options / vesting:** tributacao no momento do exercicio, pela tabela progressiva.
- **Pensao alimenticia recebida por PF de PF:** vai para o carne-leao do beneficiario — nao e IRRF na fonte.

## Vedacoes especificas

- **PA-01** — nao orientar a omitir rendimento nem a fracionar pagamento para escapar de faixa.
- **PA-02** — calcular so com dado real (natureza, valor bruto, dependentes, competencia).
- **PA-03** — datar pelo ano do fato gerador — a tabela do IRRF muda a cada ano.
- **PA-04** — sem o Selo de Validacao Legal Previa, o calculo nao comeca.
- **PA-06** — `[VERIFICAR]` na tabela progressiva, deducao por dependente e desconto simplificado nao confirmados.
- **PA-08** — a skill calcula e prepara o DARF; nao transmite declaracao nem recolhe.
- **PA-11** — citar a norma (Lei 7.713/88; RIR/2018; IN RFB do ano; Sumula 463 STJ; Tema 481 STJ; RE 595.838) com artigo.
- **PA-15** — IRRF em atraso atualizado pela Selic acumulada, nunca valor nominal.

## Protocolos acionados

- **P1 — Validacao Legal Previa** — Selo emitido por `validador-legislacao-vigente`, com a tabela do ano travada.
- **P3 — Calculo** — memoria rastreavel passo a passo, calculo em Python.
- **P4 — Cruzamento** — IRRF apurado x DCTFWeb x EFD-Reinf (R-4010/R-4020).
- **P6 — Auditoria de Qualidade** — `revisao-final` R1-R4 antes da entrega.

## Localizacao

O IRRF e tributo **federal** — tabela progressiva, deducoes e codigos de DARF sao uniformes em todo o territorio nacional, sem variacao por municipio ou UF. O eixo de localizacao incide quando o calculo da folha se cruza com o do autonomo: o RPA de autonomo (PF) pago por PJ envolve, alem do IRRF federal, a retencao de **ISS conforme a lei municipal** — essa parte e tratada pela `calculo-iss` e pela `retencoes-tomador`, sensiveis ao municipio do caso. O IRRF em si nao depende de localizacao.

## Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto, e a frente de folha (Tier 4, v0.2).

**Entrega para:** `revisao-final` (R1-R4), o `CASO.md`, a `dctfweb` e a `efd-reinf` (IRRF declarado). O IRRF e uma rubrica da folha mensal completa, consolidada pela frente de folha (Tier 4, v0.2). A retencao no pagamento de servicos a PJ e tratada pela `retencoes-tomador`. Litigio sobre a incidencia de IRRF extrapola o contabil — encaminhar a advogado (slot generico, PA-16).

**Sem esta skill:** o IRRF e estimado sem tabela vigente confirmada e sem o comparativo com o desconto simplificado — risco de retencao incorreta e de divergencia na DCTFWeb.
