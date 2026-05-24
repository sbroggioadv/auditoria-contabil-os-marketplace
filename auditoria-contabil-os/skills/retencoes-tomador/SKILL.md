---
name: retencoes-tomador
description: >
  Calculo das retencoes tributarias devidas pelo TOMADOR de servico ao pagar
  notas fiscais de PJ — IRRF de 1,5% ou 1% (limpeza/vigilancia), CSRF de 4,65%
  condicionada ao limite mensal acumulado, INSS de 11% na cessao de mao de obra
  (Lei 8.212 art. 31), ISS retido conforme a lei municipal, e as dispensas
  com declaracao de optante do Simples Nacional. Calcula via Python, NF a NF,
  com memoria rastreavel, valor liquido a pagar, comprovantes e eventos da
  EFD-Reinf. Base: RIR/2018, Lei 10.833 art. 30, IN RFB 1.234/2012, Lei
  13.137/2015. Aciona: retencao na fonte, IRRF de PJ, CSRF, INSS 11%, cessao
  de mao de obra, declaracao de Simples, valor liquido a pagar ao prestador.
---

# RETENCOES DO TOMADOR

> Skill **Tier 2** — calculo das retencoes que o tomador deve fazer ao pagar notas fiscais de servico de PJ. Apura quatro tributos com regras distintas (IRRF, CSRF, INSS, ISS) e suas dispensas. Exige o Selo de Validacao Legal Previa (P1) e e datada pelo ano do fato gerador (PA-03).

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com "retencao na fonte", "IRRF de PJ", "CSRF", "INSS 11%", "cessao de mao de obra", "declaracao de Simples", "valor liquido a pagar ao prestador". Entrada: dados da NF de servico (prestador, regime, atividade, valor bruto), competencia, acumulado mensal pago ao mesmo prestador, municipio do prestador e do tomador, declaracao de optante do Simples. Entrega: cada retencao identificada com sua norma, calculo, valor liquido a pagar, DARFs e guias, comprovantes para o prestador e indicacao dos eventos da EFD-Reinf.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.
- **Aciona antes de calcular:** `validador-legislacao-vigente` (P1) — o limite de dispensa da CSRF, as aliquotas e a regra municipal de ISS sao alvo movel; sem o Selo o calculo nao comeca (PA-04).
- **Apoia-se em:** `analise-xml-fiscal` (dados da NF de servico), `calculo-iss` (aliquota e regra de retencao do ISS no municipio).
- **Entrega para:** `revisao-final` (R1-R4), o `CASO.md`, a `efd-reinf` e a `dctfweb` (Tier 3).

## 2. Quadro de retencoes do tomador

```
RETENCAO       ALIQUOTA   NORMA                APLICACAO TIPICA          DARF/GUIA
IRRF servico   1,5%       RIR/2018             servicos profissionais    1708
IRRF limpeza   1,0%       RIR/2018             limpeza, conservacao,
                                               vigilancia, seguranca     1708
CSRF           4,65%      Lei 10.833 art. 30   consultoria, contabilidade,
                          IN RFB 1.234/2012    limpeza — acima do limite 5952
INSS retencao  11%        Lei 8.212 art. 31    cessao de MO / empreitada DCTFWeb
ISS retido     2% a 5%    LC 116 + lei mun.    itens do art. 3o da LC    DAM municipal

CSRF = CSLL + PIS + COFINS. Dispensada quando o acumulado mensal pago ao
mesmo prestador fica abaixo do limite legal (Lei 13.137/2015).  [VERIFICAR]
```

O limite de dispensa da CSRF e atualizado por norma — `[VERIFICAR]` no Selo (P1).

## 3. Prazos de recolhimento

```
IRRF (1708 e demais codigos) ... dia 20 do mes seguinte    [VERIFICAR]
CSRF (5952) .................... ultimo dia util da quinzena seguinte ao pagamento
INSS 11% ....................... dia 20 do mes seguinte (DCTFWeb apos a Reinf)
ISS retido ..................... conforme a lei do municipio competente  [VERIFICAR]
```

## 4. Dispensas — quem nao sofre retencao

- **Prestador optante do Simples Nacional** (sem cessao de mao de obra): dispensa de IRRF e de CSRF, mediante **declaracao assinada** anexa a NF (IN RFB 1.234/2012). Atencao: prestador do Simples **em cessao de mao de obra** (limpeza, vigilancia, construcao) **sofre a retencao de INSS de 11%** (Lei 8.212, art. 31) — a dispensa do Simples nao alcanca o INSS.
- **Entidade imune ou isenta:** dispensa de IRRF e CSRF mediante prova da imunidade/isencao.
- **ME/EPP do Anexo IV:** sofre IRRF e CSRF normalmente.
- **Acumulado mensal abaixo do limite legal:** dispensa de CSRF (Lei 13.137/2015) — `[VERIFICAR]` o valor do limite.

## 5. Calculo via Python (P3)

```python
python3 -c "
LIMITE_CSRF = 0.0  # limite mensal de dispensa da CSRF — [VERIFICAR] no Selo (P1)
CESSAO_MO = ('cessao_mo', 'construcao', 'limpeza', 'vigilancia', 'conservacao', 'seguranca')

def retencoes(valor, atividade, regime, acumulado_mes=0, retem_iss=False, aliq_iss=0.05):
    irrf = valor * (0.01 if atividade in CESSAO_MO else 0.015)
    csrf = 0.0
    if regime != 'simples' or atividade in CESSAO_MO:
        if acumulado_mes + valor > LIMITE_CSRF:
            csrf = valor * 0.0465
    inss = valor * 0.11 if atividade in CESSAO_MO else 0.0
    iss = valor * aliq_iss if retem_iss else 0.0
    total = irrf + csrf + inss + iss
    return dict(irrf=irrf, csrf=csrf, inss=inss, iss=iss,
                total_retido=total, liquido=valor - total)

for k, v in retencoes(10_000, 'consultoria', 'real', 5_000, True, 0.05).items():
    print(f'{k}: R\$ {v:,.2f}')
"
```

## 6. Formato de entrega

```
RETENCOES DO TOMADOR — NF [n] — competencia [MM/AAAA] — tomador CNPJ [...]
Selo de Validacao Legal Previa: [data]
Prestador: [...]   Regime: [...]   Atividade: [...]   Municipio: [...]

Valor bruto da NF .................. [...]
[ ] IRRF [1,5%/1,0%] (cod 1708) .... [...]
[ ] CSRF 4,65% (cod 5952) .......... [...]   acumulado no mes: [...]
[ ] INSS 11% (cessao de MO) ........ [...]
[ ] ISS retido [%] (DAM) ........... [...]
(=) Total retido ................... [...]
(=) LIQUIDO A PAGAR ao prestador ... [...]

Guias a recolher pelo tomador: DARF 1708, DARF 5952, DCTFWeb (INSS),
DAM municipal (ISS) — com codigo e vencimento.
Comprovantes a entregar ao prestador (escrituracao do prestador).
EFD-Reinf: R-2010 (INSS de cessao de MO) e R-4020 (IRRF/CSRF de PJ).
RESSALVA: rascunho operacional sujeito a revisao e responsabilidade tecnica
do contador com CRC ativo (PA-07).
```

## 7. Anti-padroes

- Nao reter INSS de prestador do Simples em cessao de mao de obra — a retencao de 11% e devida.
- Reter CSRF abaixo do limite mensal de dispensa (Lei 13.137/2015).
- Aplicar IRRF de 1,5% em limpeza/vigilancia — nesses servicos a aliquota e 1%.
- Esquecer os eventos da EFD-Reinf (R-2010, R-4020).
- Reter INSS de cooperativa de trabalho — o STF (RE 595.838) afastou a antiga retencao.
- Aceitar declaracao de Simples para dispensar tambem o INSS de cessao de MO — nao alcanca.

## 8. Casos de borda

- **13o pago a autonomo:** tributacao pela tabela progressiva sobre o 13o, sem dispensa.
- **Adiantamento ao prestador:** ha retencao se o servico ja foi prestado; sinal sem execucao nao gera retencao ate a NF.
- **Multiplos pagamentos no mes ao mesmo prestador:** somar para verificar o limite da CSRF.
- **Locacao de bens (nao e servico):** sem retencao das de servico.
- **Royalties pagos a PF ou PJ:** regra propria de IRRF — fora do quadro de retencao de servico.

## Vedacoes especificas

- **PA-01** — nao orientar fracionamento de NF para escapar do limite da CSRF.
- **PA-02** — calcular so com dado real (NF, regime do prestador, atividade, acumulado, competencia).
- **PA-03** — datar pelo ano do fato gerador — limites e aliquotas mudam por norma.
- **PA-04** — sem o Selo de Validacao Legal Previa, o calculo nao comeca.
- **PA-05** — o ISS retido sempre pela aliquota e regra do **municipio** competente — nunca generica.
- **PA-06** — `[VERIFICAR]` no limite de dispensa da CSRF e na regra municipal de ISS nao confirmados.
- **PA-08** — a skill calcula e prepara as guias; nao transmite a EFD-Reinf nem recolhe.
- **PA-11** — citar a norma (RIR/2018; Lei 10.833 art. 30; Lei 8.212 art. 31; IN RFB 1.234/2012; Lei 13.137/2015) com artigo.
- **PA-15** — retencao em atraso atualizada pela Selic acumulada, nunca valor nominal.

## Protocolos acionados

- **P1 — Validacao Legal Previa** — Selo emitido por `validador-legislacao-vigente`, com limites e aliquotas do ano.
- **P2 — Ingestao** — dados da NF de servico vindos de `analise-xml-fiscal`.
- **P3 — Calculo** — memoria rastreavel NF a NF, calculo em Python.
- **P5 — Localizacao** — o ISS retido depende da lei do municipio competente.
- **P6 — Auditoria de Qualidade** — `revisao-final` R1-R4 antes da entrega.

## Localizacao

As retencoes federais — IRRF, CSRF e INSS de 11% — sao uniformes em todo o territorio nacional, sem variacao por municipio ou UF. O **ISS retido**, ao contrario, depende inteiramente do eixo de localizacao: a obrigacao de o tomador reter, a aliquota e o prazo da DAM sao definidos pela **lei do municipio competente** (regra do art. 3o da LC 116/2003). Essa parte da retencao e calculada em conjunto com a `calculo-iss`, que decide qual municipio e competente. Toda regra municipal nao confirmada e marcada `[VERIFICAR — norma municipal]` (PA-06).

## Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.

**Entrega para:** `revisao-final` (R1-R4), o `CASO.md`, a `efd-reinf` (eventos R-2010 e R-4020) e a `dctfweb` (debitos de INSS retido). A parte do ISS retido e articulada com a `calculo-iss`; a parte de IRRF cruza com a `irrf-folha` quando o pagamento e a PF. Discussao judicial sobre a exigibilidade de uma retencao extrapola o contabil — encaminhar a advogado (slot generico, PA-16).

**Sem esta skill:** o tomador paga a NF sem reter os tributos devidos — responsabilidade solidaria e autuacao pela falta de retencao e de recolhimento.
