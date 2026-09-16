# The original Makefile is a hashed input of the preserved robustness study.
.DEFAULT_GOAL := all
include Makefile

.PHONY: check-practical-selection reproduce-practical-selection paper-notes

paper-notes:
	cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error -outdir=../build research-notes.tex

check-optimization: check-practical-selection

check-practical-selection:
	python experiments/check_practical_selection.py

reproduce-practical-selection:
	python experiments/check_practical_selection.py --numerics-only
	python experiments/run_practical_selection.py
	python experiments/summarize_practical_selection.py
	python experiments/audit_practical_precision.py
	$(MAKE) check-practical-selection
