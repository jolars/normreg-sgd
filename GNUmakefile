.DEFAULT_GOAL := all

FROZEN := python scripts/frozen_experiment.py

.PHONY: all paper figures paper-figures check check-quick verify check-experiments
.PHONY: check-markdown check-config check-python check-frozen-inputs format
.PHONY: prepare-results prepare-lean check-lean
.PHONY: check-moments check-normalization-risk check-normalization-robustness
.PHONY: check-predictive-theorem check-predictive-review check-predictive-intro
.PHONY: check-practical-selection check-mushroom-rate-search
.PHONY: check-mushroom-sensitivity check-variance-scaling
.PHONY: check-review-diagnostics check-signal-allocation
.PHONY: reproduce-normalization-robustness reproduce-practical-selection
.PHONY: reproduce-mushroom-rate-search reproduce-mushroom-sensitivity
.PHONY: reproduce-variance-scaling reproduce-predictive-intro
.PHONY: reproduce-review-diagnostics reproduce-signal-allocation

PAPER_FIGURES := build/figures/predictive-intro/tuned-rare-risk.pdf \
	build/figures/signal-allocation/risk-map.pdf \
	build/figures/mushroom-final/selected-risks.pdf \
	build/figures/practical-selection/practical-selection.pdf \
	build/figures/mushroom-rate-search/paths-n2048-aggregate.pdf

all: paper

paper: paper-figures
	cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error -outdir=../build main.tex

figures paper-figures: $(PAPER_FIGURES)

$(PAPER_FIGURES): scripts/figures/style.py devenv.nix devenv.lock uv.lock

build/figures/predictive-intro/tuned-rare-risk.pdf: scripts/figures/plot_predictive_intro.py results/predictive-intro/summary.json
	python scripts/figures/plot_predictive_intro.py

build/figures/practical-selection/practical-selection.pdf: scripts/figures/plot_practical_selection.py results/practical-selection/summary.json
	python scripts/figures/plot_practical_selection.py

build/figures/signal-allocation/risk-map.pdf: scripts/figures/plot_signal_allocation.py results/signal-allocation/summary.json
	python scripts/figures/plot_signal_allocation.py

build/figures/mushroom-final/selected-risks.pdf: scripts/figures/plot_mushroom_final.py results/variance-scaling-followup/mushroom-summary-c1.json
	python scripts/figures/plot_mushroom_final.py

build/figures/mushroom-rate-search/paths-n2048-aggregate.pdf: scripts/figures/plot_mushroom_rate_search.py results/mushroom-rate-search/summary.json
	python scripts/figures/plot_mushroom_rate_search.py

check: check-markdown check-config check-python verify paper

# The retired elastic-net Monte Carlo check was the only quick/full difference.
check-quick: check

check-markdown:
	panache format --check .
	panache lint .

check-config:
	nixfmt --check devenv.nix
	actionlint
	uv lock --check

check-python:
	ruff format --check experiments scripts
	ruff check experiments scripts

verify: check-experiments

check-experiments: check-frozen-inputs check-moments check-normalization-risk check-normalization-robustness
check-experiments: check-predictive-theorem check-predictive-review check-predictive-intro
check-experiments: check-practical-selection check-mushroom-rate-search check-mushroom-sensitivity
check-experiments: check-variance-scaling check-review-diagnostics check-signal-allocation

check-frozen-inputs:
	python scripts/check_frozen_inputs.py

check-moments:
	python experiments/check_joint_interactions.py

check-normalization-risk:
	python experiments/check_normalization_risk_theorem.py

check-predictive-theorem:
	python experiments/check_predictive_theorem.py

check-predictive-review:
	python experiments/check_predictive_review.py

check-predictive-intro:
	python experiments/plot_predictive_intro.py --check

check-review-diagnostics:
	python scripts/review_diagnostics.py --check

check-signal-allocation:
	python scripts/illustrate_signal_allocation.py --check

prepare-results:
	python scripts/prepare_results.py

check-normalization-robustness check-practical-selection check-mushroom-rate-search check-mushroom-sensitivity check-variance-scaling: prepare-results
reproduce-normalization-robustness reproduce-practical-selection reproduce-mushroom-rate-search reproduce-mushroom-sensitivity reproduce-variance-scaling: prepare-results

check-normalization-robustness:
	$(FROZEN) check_normalization_robustness

check-practical-selection:
	$(FROZEN) check_practical_selection

check-mushroom-rate-search:
	OPENBLAS_NUM_THREADS=1 $(FROZEN) check_mushroom_rate_search

check-mushroom-sensitivity:
	OPENBLAS_NUM_THREADS=1 $(FROZEN) check_mushroom_sensitivity

check-variance-scaling:
	OPENBLAS_NUM_THREADS=1 $(FROZEN) check_variance_scaling

reproduce-normalization-robustness:
	$(FROZEN) check_normalization_robustness --numerics-only
	$(MAKE) check-normalization-risk
	$(FROZEN) run_normalization_robustness
	$(FROZEN) simulate_normalization_robustness
	$(FROZEN) summarize_normalization_robustness
	$(FROZEN) plot_normalization_robustness
	$(MAKE) check-normalization-robustness

reproduce-practical-selection:
	$(FROZEN) check_practical_selection --numerics-only
	$(FROZEN) run_practical_selection
	$(FROZEN) summarize_practical_selection
	$(FROZEN) audit_practical_precision
	$(MAKE) check-practical-selection

reproduce-mushroom-rate-search:
	OPENBLAS_NUM_THREADS=1 $(FROZEN) check_mushroom_rate_search --numerics-only
	$(FROZEN) mushroom_rate_spec --declare
	OPENBLAS_NUM_THREADS=1 $(FROZEN) run_mushroom_rate_search
	OPENBLAS_NUM_THREADS=1 $(FROZEN) summarize_mushroom_rate_search
	$(MAKE) check-mushroom-rate-search

reproduce-mushroom-sensitivity:
	OPENBLAS_NUM_THREADS=1 $(FROZEN) check_mushroom_sensitivity --numerics-only
	$(FROZEN) mushroom_sensitivity_spec --declare
	OPENBLAS_NUM_THREADS=1 $(FROZEN) run_mushroom_sensitivity
	OPENBLAS_NUM_THREADS=1 $(FROZEN) summarize_mushroom_sensitivity
	$(MAKE) check-mushroom-sensitivity

reproduce-variance-scaling:
	OPENBLAS_NUM_THREADS=1 $(FROZEN) check_variance_scaling --numerics-only
	$(FROZEN) variance_scaling_spec --declare
	OPENBLAS_NUM_THREADS=1 $(FROZEN) run_variance_scaling
	OPENBLAS_NUM_THREADS=1 $(FROZEN) summarize_variance_scaling
	OPENBLAS_NUM_THREADS=1 $(FROZEN) check_variance_scaling --write-audit

reproduce-predictive-intro:
	python experiments/plot_predictive_intro.py

reproduce-review-diagnostics:
	python scripts/review_diagnostics.py --update-paper

reproduce-signal-allocation:
	python scripts/illustrate_signal_allocation.py

prepare-lean:
	cd lean && lake exe cache get Mathlib.Data.Real.Basic Mathlib.Tactic.FieldSimp Mathlib.Tactic.Linarith Mathlib.Tactic.Positivity Mathlib.Tactic.Ring

check-lean:
	cd lean && lake build

format:
	panache format .
	nixfmt devenv.nix
	ruff format experiments scripts
