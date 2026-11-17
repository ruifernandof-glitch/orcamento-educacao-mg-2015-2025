# Divergências em relação à planilha original e impactos no texto da dissertação

O pipeline recalcula tudo a partir dos dados brutos e compara com a planilha original de análise (`outputs/conferencia_planilha_original.csv`). Dos 492 valores comparados, **483 conferem exatamente** e **9 divergem por razões identificadas**. Este documento explica cada divergência e o que ela implica para o texto.

---

## 1. Regressões de persistência estimadas em valores nominais

**O que acontece.** A aba `Testes_Estatisticos` traz β = 1,009 e R² = 0,844 para o empenho da Função 12. Esses valores só são reproduzidos com **valores nominais**. Em valores reais, que são a especificação descrita na metodologia (seção 4.6.3), o resultado é:

| Estágio (Função 12) | β real | R² real | p | β nominal | R² nominal |
|---|---|---|---|---|---|
| Empenhado | 0,818 | 0,582 | 0,010 | 1,009 | 0,844 |
| Liquidado | 0,933 | 0,730 | 0,002 | 1,050 | 0,893 |
| Pago | 0,952 | 0,767 | < 0,001 | 1,054 | 0,904 |

**Por que importa.** Em séries nominais, a inflação cria uma tendência comum que infla o R². Em valores reais, a persistência continua estatisticamente significativa, mas é **menor**: o empenho do ano anterior explica cerca de 58% da variação do nível, e não 84%.

**O que muda na dissertação.** Corrigir os valores de β e R² no Resumo/Abstract/Resumen, na seção 5.2, na Tabela 7 e nas Considerações finais, ou declarar explicitamente que a regressão foi feita em valores nominais. A leitura teórica (persistência compatível com o incrementalismo) se mantém, em tom mais moderado.

## 2. Dotação inicial pareada entre anos não consecutivos

**O que acontece.** Não há dotação inicial da Função 12 para 2016. A planilha original pareou 2015 com 2017 como se fossem anos consecutivos (n = 9). O repositório usa só pares consecutivos (n = 8): β nominal = 1,164, R² = 0,946.

**O que muda.** Pouco. Basta ajustar n e β da dotação na Tabela 7.

## 3. Variações por subfunção entre anos não consecutivos

**O que acontece.** Em 5 casos, uma subfunção não teve execução em um ano. A planilha original comparou o ano seguinte com **dois anos antes**, como se fosse uma variação anual. Por exemplo: Assistência à Criança e ao Adolescente, 2021 contra 2019, +35.346%. O repositório só calcula variação entre anos consecutivos.

**Consequência.** A planilha original informa n = 136; o repositório obtém **n = 138**. A diferença líquida de n não pôde ser reconstituída a partir das abas disponíveis. As estatísticas são próximas (curtose excedente 70,9 na planilha contra 71,7 recalculada) e as conclusões não mudam.

**O que muda.** Atualizar a Tabela 10 e o parágrafo da seção 5.5 para n = 138 e os valores de `distribuicao_subfuncoes.csv`.

## 4. Ação renomeada dentro do exercício (2025)

**O que acontece.** Em 2025, as ações 2058 e 2059 da PMMG (Colégios Tiradentes) aparecem com dois nomes no mesmo ano. A planilha original separou os registros pelo nome, gerando contribuição de −R$ 167,5 milhões. Agregando pelo código, a contribuição real é de +R$ 8,8 milhões.

**O que muda.** Nada no texto da dissertação, pois o caso não é citado.

## 5. Rastreamento de 2020 vazio na planilha original

**O que acontece.** A aba `Rastreamento_Acoes` deixa 2020 sem valores. O motivo é que **nenhum código de ação de 2020 existe em 2019**: houve recodificação integral no início do PPAG 2020–2023. Por exemplo, “Pagamento de Pessoal do Ensino Fundamental – Magistério” (2144, R$ 5,04 bi reais em 2019) foi substituída por “Proventos dos Profissionais do Magistério – Ensino Fundamental” (2065) e “Desenvolvimento do Ensino Fundamental” (4297). O repositório registra essas ações como `código extinto` e `código novo`.

**Por que importa.**
- A queda de 2020 por subfunção e boa parte das caudas pesadas da distribuição refletem **reclassificação**, e não necessariamente mudança de política. Isso confirma a verificação nº 10 da base bruta das LOAs (subfunção 122 → 368).
- O nome “Proventos” no código 2065 sucede a folha de **pessoal do magistério**. A previdência dos servidores da Educação está classificada na função 09, e não na 12 (base bruta LOA, aba `08_Previdencia`). Portanto, “proventos”, aqui, **não deve ser lido como aposentadorias**.

**O que muda.** A seção 5.5 e a Tabela 11 podem citar a recodificação de 2020 com base em `quebra_codificacao_acoes.csv`. O comentário de revisão sobre “proventos de inativos” pode ser resolvido no sentido acima, após conferência na LOA 2020.

## 6. Estimadores de assimetria e curtose

O repositório usa os estimadores corrigidos para amostra (`bias=False`), idênticos a `DISTORÇÃO` e `CURT` do Excel e do LibreOffice, para que a memória em planilha reproduza o Python. A planilha original não documenta qual estimador usou.

## 7. Referências do relatório técnico de análise

A seção 17 do relatório técnico (`Relatorio_Analise_Empirica…docx`) traz referências que divergem da dissertação e contêm erros (periódico de Myaing & Lim e de Wordliczek, DOI de Desmarais, autores de Jones et al., 2009, e uma entrada de Oliveira et al. ainda como modelo). **Use as referências da dissertação**, que foram conferidas.
