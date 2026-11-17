# Log metodológico

Decisões M01–M10 da análise original (aba `Log_Metodologico`), seguidas das decisões tomadas na construção deste repositório (M11–M17).

| ID | Decisão | Operacionalização | Justificativa |
|---|---|---|---|
| M01 | Separação dos recortes | Função 12 e UO 1261 analisadas separadamente | Evita equivalência indevida entre política funcional e órgão executor |
| M02 | Deflação | Valores multiplicados pelo fator IPCA encadeado até dez./2025 | Distingue recomposição nominal de mudança substantiva |
| M03 | Incrementalismo | Variação real do empenhado: \|Δ\| ≤ 5% | Regra operacional exploratória, não universal |
| M04 | Mudança moderada | 5% < \|Δ\| < 10% | Faixa intermediária para evitar dicotomia rígida |
| M05 | Pontuação candidata | \|Δ real\| ≥ 10% | Exige confirmação por permanência e rastreamento classificatório |
| M06 | Persistência | Regressão de Yₜ sobre Yₜ₋₁, em nível e em log | Evidência descritiva, limitada pelo n pequeno e pela tendência temporal |
| M07 | Equilíbrio pontuado | Assimetria, curtose e Shapiro–Wilk das variações por subfunção | Caudas pesadas são compatíveis com a teoria; não provam causalidade |
| M08 | Concentração | HHI pela participação das subfunções no empenhado | Indica a concentração da composição orçamentária |
| M09 | Robustez | Limiares de 5%, 10% e 15%; Função 12 versus SEE | Avalia a sensibilidade dos achados |
| M10 | Reclassificações | Movimentos extremos rastreados por UO, programa e ação | Evita tratar mudança contábil como mudança de política |
| **M11** | Regressão em valores reais | Persistência estimada em valores reais (principal) e nominais (para conferência) | Coerência com M02 e com a metodologia declarada; ver divergências, item 1 |
| **M12** | Somente anos consecutivos | Regressões e variações por subfunção usam apenas pares t e t − 1 | Uma variação bienal não é uma variação anual; ver divergências, itens 2 e 3 |
| **M13** | Ação identificada pelo código | Rastreamento por (UO, código da ação) | O nome pode mudar dentro do exercício; ver divergências, item 4 |
| **M14** | Códigos novos e extintos explícitos | Contribuição integral, com rótulo de situação | Torna visível a quebra de codificação em vez de descartá-la; ver divergências, item 5 |
| **M15** | Cenários de robustez da distribuição | Sem 2020 e em variação logarítmica | Mede quanto das caudas pesadas depende da recodificação de 2020 |
| **M16** | Estimadores corrigidos para amostra | Assimetria e curtose com `bias=False` | Equivalência exata com a memória em planilha |
| **M17** | Dados originais imutáveis | Planilhas em `data/original` com SHA-256; cálculo só a partir de `data/raw` | Cadeia de custódia auditável |
