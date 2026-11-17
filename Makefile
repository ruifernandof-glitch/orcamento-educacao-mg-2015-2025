.PHONY: tudo extrair analise testes limpar

tudo: extrair analise testes

extrair:
	python scripts/00_extrair_brutos.py

analise:
	python scripts/run_all.py

testes:
	pytest -q

limpar:
	rm -rf data/processed/* outputs/tabelas/* outputs/figuras/* outputs/*.xlsx outputs/*.csv
