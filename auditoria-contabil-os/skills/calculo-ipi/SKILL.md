---
name: calculo-ipi
description: >
  Apuracao mensal de IPI para industria e equiparados — debitos x creditos do mes,
  TIPI vigente por NCM, suspensao (drawback, RECOF, encomenda), credito presumido
  de exportacao e Bloco K. Calcula via Python, com memoria rastreavel e DARF. Base:
  Decreto 7.212/2010 (RIPI), Decreto 11.158/2022 (TIPI), Lei 4.502/64, Lei
  9.363/96. Aciona: calcular IPI, apurar IPI, TIPI, NCM, suspensao de IPI,
  drawback, RECOF, industrializacao por encomenda, credito presumido de
  exportacao, credito de IPI, DARF 5123.
---

# CALCULO IPI

> Skill **Tier 2** — apuracao mensal de IPI para industria e equiparados: confronta debitos das saidas com creditos das entradas. Toda apuracao exige o Selo de Validacao Legal Previa (P1) e e datada pelo ano do fato gerador.

---

## 0. Escopo e acionamento

Acionada por `auditoria-contabil-master`, `triagem-contabil` ou diretamente com "calcular IPI", "apurar IPI", "TIPI", "suspensao de IPI", "drawback", "RECOF", "industrializacao por encomenda", "credito presumido de exportacao". Entrada: CNPJ, competencia, tipo de empresa (industria, atacadista equiparado, importador), NFs de entrada com IPI destacado, saidas tributadas, saldo credor anterior, operacoes especiais. Entrega: apuracao mensal creditos x debitos, calculo passo a passo, DARF com vencimento, memoria de calculo.

## 1. Posicao na orquestra

- **Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.
- **Aciona antes de calcular:** `validador-legislacao-vigente` (P1) — a TIPI muda por decreto; sem o Selo a apuracao nao comeca (PA-04).
- **Apoia-se em:** `analise-xml-fiscal` (IPI por CST e CFOP), `leitura-arquivos-sped` (registros E520/E530 da EFD ICMS/IPI).
- **Entrega para:** `revisao-final` (R1-R4), o `CASO.md`, a `efd-icms-ipi` e a `dctfweb` (Tier 3).

## 2. Premissa — nao-cumulatividade e IPI por fora

O IPI e nao-cumulativo (CF, art. 153, §3o, II): a industria credita o IPI de **todas** as entradas tributadas (insumos, materia-prima, embalagem) e debita o IPI das saidas tributadas. A apuracao do mes confronta os dois.

- **IPI por fora:** o IPI nao compoe a propria base de calculo. Mas integra a base do **ICMS** quando o destinatario for nao-contribuinte ou a mercadoria for para uso/consumo.
- **Credito mantido em saida suspensa:** a saida suspensa **nao** estorna o credito das entradas — a industria mantem o credito.
- **TIPI:** cada NCM tem aliquota propria na TIPI (Decreto 11.158/2022 e atualizacoes); a TIPI muda — `[VERIFICAR]` a versao vigente no ano (PA-03/PA-06).

## 3. Apuracao mensal — creditos x debitos

```
Saldo apurado = saldo credor anterior + creditos do mes - debitos do mes
Saldo >= 0  -> saldo credor, carrega para o mes seguinte
Saldo < 0   -> IPI a recolher (DARF 5123)
```

CSTs principais: **00** entrada com credito; **50** saida tributada; **51** saida tributada com aliquota zero; **52** saida isenta; **53** saida suspensa; **54** saida imune (exportacao). O CST errado distorce a apuracao.

## 4. Regimes especiais

- **Suspensao x isencao:** a suspensao e **condicional** — exige cumprir uma condicao posterior (no drawback, exportar dentro do prazo). Se a condicao nao se cumpre, o IPI vira devido com encargo. A isencao e definitiva. Tratar suspensao como isencao e erro grave.
- **Industrializacao por encomenda:** o encomendante envia o insumo com suspensao; o industrializador devolve o produto com suspensao, sendo o IPI **tributado sobre o valor agregado** (mao de obra + insumos proprios).
- **Exportacao direta:** imune (CF, art. 153, §3o, III); a industria mantem os creditos das entradas e gera **credito presumido** de PIS/COFINS via IPI (Lei 9.363/96, ou a sistematica alternativa da Lei 10.276/2001).
- **Drawback / RECOF:** regimes aduaneiros especiais com suspensao — verificar o NCM autorizado e o prazo da condicao.
- **ZFM / ALC:** produtos da Zona Franca de Manaus e Areas de Livre Comercio tem regime especifico (Decreto-Lei 288/67) — conferir NCM e NF.

## 5. Calculo via Python (P3)

```python
python3 -c "
def ipi_apuracao(creditos, debitos, saldo_anterior=0):
    saldo = saldo_anterior + creditos - debitos
    if saldo >= 0:
        return saldo, 0          # saldo credor a carregar
    return 0, abs(saldo)         # IPI a recolher

saldo_credor, a_recolher = ipi_apuracao(creditos=12_500, debitos=18_000, saldo_anterior=1_500)
print(f'IPI a recolher (DARF 5123): R\$ {a_recolher:,.2f}')
print(f'Saldo credor a carregar: R\$ {saldo_credor:,.2f}')

def credito_presumido(insumos, rec_exp, rec_total, fator=0.0537):
    return (rec_exp / rec_total) * insumos * fator   # fator [VERIFICAR]

cp = credito_presumido(insumos=500_000, rec_exp=2_000_000, rec_total=10_000_000)
print(f'Credito presumido de PIS/COFINS via IPI: R\$ {cp:,.2f}')
"
```

## 6. Formato de entrega

```
APURACAO IPI — [CNPJ] — competencia [MM/AAAA]
Selo de Validacao Legal Previa: [data]   Local: [municipio]/[UF]

ENTRADAS COM CREDITO: NF | fornecedor | NCM | base | IPI % | IPI
SAIDAS TRIBUTADAS:     NF | cliente    | NCM | base | IPI % | IPI
(+) Saldo credor anterior
(=) IPI a recolher (DARF 5123)  ou  saldo credor a carregar
Vencimento: [DD/MM/AAAA] [VERIFICAR]

RESSALVA: rascunho operacional sujeito a revisao e responsabilidade tecnica
do contador com CRC ativo (PA-07).
```

## 7. Anti-padroes

- Calcular o IPI por dentro — o IPI e sempre por fora.
- Nao tomar o credito das entradas tributadas (perde a nao-cumulatividade).
- Usar TIPI desatualizada — confirmar o decreto vigente.
- Tratar como suspensao o que e isencao — a suspensao exige condicao posterior.
- Estornar credito de entrada por causa de saida suspensa — nao se estorna.
- Esquecer a industrializacao por encomenda no registro E520.
- Aproveitar o credito presumido em duplicidade (so em um demonstrativo).
- Cravar aliquota da TIPI de memoria — `[VERIFICAR]` o NCM.

## 8. Casos de borda

- **Revenda de produto importado:** o importador equiparado a industrial recolhe IPI na revenda; o atacadista comum nao.
- **Devolucao de mercadoria com IPI:** NF de devolucao com debito espelho.
- **Imobilizado:** nao gera credito de IPI — o credito e so de insumo de producao.
- **PJ optante do Simples:** nao recolhe IPI proprio (incluso no DAS); atencao se equiparada a industrial em alguma operacao.
- **Drawback nao cumprido no prazo:** o IPI suspenso vira devido com encargo legal.

## 9. Vedacoes especificas

- **PA-01** — nao orientar a usar suspensao sem o regime aduaneiro correspondente nem credito indevido.
- **PA-02** — apurar so com dado real (NFs de entrada/saida, NCM, saldo anterior).
- **PA-03** — datar a apuracao pelo ano do fato gerador; a TIPI muda por decreto.
- **PA-04** — sem o Selo de Validacao Legal Previa, a apuracao nao comeca.
- **PA-06** — `[VERIFICAR]` na aliquota da TIPI, no fator do credito presumido e no NCM autorizado em regime especial.
- **PA-08** — a skill apura e prepara o DARF; nao transmite a EFD/DCTFWeb nem recolhe.
- **PA-11** — citar a norma (RIR/IPI — Decreto 7.212/2010; TIPI — Decreto 11.158/2022; Lei 9.363/96) com artigo.
- **PA-13** — nao confundir regime de IPI com a obrigacao acessoria (EFD ICMS/IPI, DCTFWeb).
- **PA-15** — IPI em atraso atualizado pela Selic acumulada, nunca valor nominal.

## 10. Protocolos acionados

- **P1 — Validacao Legal Previa** — Selo emitido por `validador-legislacao-vigente`, com a TIPI do ano.
- **P2 — Ingestao** — IPI por CST/CFOP vindo de `analise-xml-fiscal`.
- **P3 — Calculo** — apuracao creditos x debitos em Python, memoria rastreavel.
- **P4 — Cruzamento** — o IPI apurado bate com a EFD ICMS/IPI (E520/E530) e a DCTFWeb.
- **P6 — Auditoria de Qualidade** — `revisao-final` R1-R4 antes da entrega.

## 11. Localizacao

O IPI e tributo **federal** — a aliquota da TIPI vale em todo o pais e nao varia por municipio ou UF. O eixo geografico aparece de forma indireta: o IPI integra a base do **ICMS** (estadual) quando o destinatario for nao-contribuinte, e os regimes da ZFM/ALC tem base territorial. Quando uma regra territorial nao puder ser confirmada, marcar `[VERIFICAR]` (PA-06).

## 12. Integracao

**Chamada por:** `auditoria-contabil-master`, `triagem-contabil`, operador direto.

**Entrega para:** `revisao-final` (R1-R4), o `CASO.md`, a `efd-icms-ipi` e a `dctfweb`. O ICMS interestadual da mesma operacao e tratado por `calculo-icms-st`; a recuperacao retroativa de IPI pago a maior e trabalho de auditoria (Tier 7, v0.3).

**Sem esta skill:** a apuracao de IPI e estimada sem confronto creditos x debitos nem controle de suspensao — risco de recolher a maior ou ser autuado por credito indevido.
