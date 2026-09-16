# The original Makefile is a hashed input of the preserved robustness study.
.DEFAULT_GOAL := all
include Makefile

.PHONY: check-practical-selection reproduce-practical-selection paper-notes paper-claim check-predictive-claim
.PHONY: check-mushroom-rate-search reproduce-mushroom-rate-search

paper-notes:
	cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error -outdir=../build research-notes.tex

paper-claim:
	cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error -outdir=../build proposed-claim.tex

check-optimization: check-practical-selection check-predictive-claim check-mushroom-rate-search

check-predictive-claim:
	python experiments/check_predictive_claim.py

check-practical-selection:
	python experiments/check_practical_selection.py

reproduce-practical-selection:
	python experiments/check_practical_selection.py --numerics-only
	python experiments/run_practical_selection.py
	python experiments/summarize_practical_selection.py
	python experiments/audit_practical_precision.py
	$(MAKE) check-practical-selection

check-mushroom-rate-search:
	OPENBLAS_NUM_THREADS=1 python experiments/check_mushroom_rate_search.py

reproduce-mushroom-rate-search:
	OPENBLAS_NUM_THREADS=1 python experiments/check_mushroom_rate_search.py --numerics-only
	python experiments/mushroom_rate_spec.py --declare
	OPENBLAS_NUM_THREADS=1 python experiments/run_mushroom_rate_search.py
	OPENBLAS_NUM_THREADS=1 python experiments/summarize_mushroom_rate_search.py
	$(MAKE) check-mushroom-rate-search
