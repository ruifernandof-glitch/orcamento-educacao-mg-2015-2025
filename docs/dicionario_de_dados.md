# Dicionário de dados

Todos os valores monetários estão em **reais (R$ 1,00)**. Os campos com sufixo `_real` estão a **preços de dezembro de 2025** (IPCA). Os CSV usam ponto decimal e vírgula como separador; as tabelas em `outputs/tabelas` usam o padrão brasileiro (`;` e vírgula decimal).

## `data/raw/execucao_detalhada.csv`

Execução orçamentária extraída do Portal de Dados Abertos de MG (SIAFI-MG). São 3.847 linhas, e cada linha corresponde a um cruzamento ano × UO × subfunção × programa × ação × fonte.

| Campo | Tipo | Descrição |
|---|---|---|
| `ano` | inteiro | Exercício financeiro (2015–2025) |
| `recorte_funcao12` | booleano | A linha pertence à extração da **Função 12 – Educação** (todas as UOs) |
| `recorte_see1261` | booleano | A linha pertence à extração da **UO 1261 – SEE/MG** |
| `cd_unidade_orc`, `nm_unidade_orc`, `sg_unidade_orc` | inteiro, texto | Unidade orçamentária: código, nome e sigla |
| `cd_funcao`, `nm_funcao` | inteiro, texto | Função de governo (sempre 12 – Educação) |
| `cd_subfuncao`, `nm_subfuncao` | inteiro, texto | Subfunção (p. ex., 361 Ensino Fundamental) |
| `cd_programa`, `nm_programa` | inteiro, texto | Programa do PPAG |
| `cd_acao`, `nm_acao` | inteiro, texto | Ação orçamentária. **O código é a chave; o nome pode mudar dentro do ano** |
| `cd_fonte`, `nm_fonte` | inteiro, texto | Fonte de recursos (p. ex., 23 Fundeb, 10 Recursos Ordinários) |
| `vr_empenhado` | decimal | Despesa empenhada no exercício |
| `vr_liquidado` | decimal | Despesa liquidada no exercício |
| `vr_pago` | decimal | Despesa paga no exercício |

> ⚠️ **Os recortes não se somam.** A tabela empilha duas extrações. Uma linha pode pertencer às duas (913 linhas), só à Função 12 (703) ou só à SEE (2.231, em granularidade maior). Use sempre `filtrar_recorte(ex, "funcao12")` ou `filtrar_recorte(ex, "see1261")`. O teste `test_recortes_nao_se_somam` garante que a parte SEE da Função 12 é idêntica ao recorte SEE.

## `data/raw/creditos_detalhados.csv`

Lançamentos de créditos orçamentários (2020–2025), 12.340 linhas.

| Campo | Descrição |
|---|---|
| `ano` | Exercício |
| `dt_documento`, `nr_documento_global` | Data e número do documento de alteração |
| `tp_operacao` | 1 ou 2: par de lançamentos de uma mesma alteração (origem e destino) |
| `tp_documento` | Tipo do documento de alteração (40–46) |
| `cd_unidade_orc` … `nm_acao` | Classificação, como na execução |
| `vr_credito_inicial` | Dotação inicial da LOA |
| `vr_credito_suplem`, `vr_credito_extraord`, `vr_credito_especial` | Créditos adicionais |
| `vr_anulacao_credito` | Anulações (redução de dotação) |
| `vr_credito_autorizado` | Crédito autorizado = inicial + adicionais − anulações (dotação atualizada) |

## `data/raw/dotacao_inicial_loa.csv`

| Campo | Descrição |
|---|---|
| `ano`, `recorte` | Exercício e recorte (`funcao12` ou `see1261`) |
| `dotacao_inicial` | Dotação inicial autorizada na LOA |
| `arquivo_fonte`, `aba_origem` | Arquivo da LOA e aba da base bruta de onde o valor foi transcrito |

Lacunas: não há valor para **2016** (o Volume V da LOA 2016 está incompleto) nem para a SEE em **2015–2018** (sem desagregação por ação).

## `data/raw/ipca_anual.csv`

`ano`, `ipca_variacao_anual` (variação de dezembro a dezembro) e `fonte`.

## `data/processed/` (gerados pelo pipeline)

| Arquivo | Conteúdo |
|---|---|
| `fatores_ipca.csv` | Fator que leva o valor de cada ano a preços de dez./2025 |
| `serie_anual.csv` | Uma linha por ano e recorte: dotação, créditos, empenhado, liquidado, pago (nominais e reais), variações, `classificacao` e taxas de execução |
| `persistencia_regressoes.csv` | Regressões Yₜ = α + βYₜ₋₁, com `base` real ou nominal, `n_pares`, `beta`, `erro_padrao_beta`, `r2`, `p_beta` e a versão em log |
| `sensibilidade_limiares.csv` | Número e anos de variações acima de cada limiar |
| `painel_subfuncoes.csv` | Ano × subfunção: empenhado, participação, valor real, valor real do ano anterior, `var_real`, `contribuicao_real` e `na_distribuicao` (base anterior ≥ R$ 1 milhão) |
| `distribuicao_subfuncoes.csv` | Estatísticas da distribuição em quatro cenários (principal, sem 2020, log, log sem 2020) |
| `concentracao_hhi.csv` | HHI e número de subfunções com empenho por ano |
| `rastreamento_acoes.csv` | Ano × UO × ação: empenho real no ano e no anterior, contribuição e `situacao` (`comparável`, `código novo`, `código extinto`) |
| `quebra_codificacao_acoes.csv` | Por ano, quantas ações são comparáveis, novas ou extintas e quanto da variação cada grupo explica |
