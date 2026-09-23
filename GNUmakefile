# The original Makefile is a hashed input of the preserved robustness study.
.DEFAULT_GOAL := all
include Makefile

.PHONY: check-practical-selection reproduce-practical-selection check-predictive-claim check-predictive-feasibility
.PHONY: check-mushroom-rate-search reproduce-mushroom-rate-search
.PHONY: check-mushroom-sensitivity reproduce-mushroom-sensitivity
.PHONY: prepare-results check-scripts format-scripts
.PHONY: check-variance-scaling reproduce-variance-scaling
.PHONY: check-predictive-regime check-predictive-theorem
.PHONY: check-predictive-review
.PHONY: reproduce-predictive-intro check-predictive-intro
.PHONY: prepare-lean check-lean
.PHONY: figures paper-figures
.PHONY: reproduce-review-diagnostics check-review-diagnostics
.PHONY: reproduce-signal-allocation check-signal-allocation

PAPER_FIGURES := build/figures/predictive-intro/tuned-rare-risk.pdf \
	build/figures/signal-allocation/risk-map.pdf \
	build/figures/mushroom-final/selected-risks.pdf \
	build/figures/practical-selection/practical-selection.pdf \
	build/figures/mushroom-rate-search/paths-n2048-aggregate.pdf

paper: paper-figures

paper-figures: $(PAPER_FIGURES)

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

figures: prepare-results
	python scripts/figures/plot_predictive_intro.py
	python scripts/figures/plot_practical_selection.py
	python scripts/figures/plot_mushroom_rate_search.py
	python scripts/figures/plot_joint_interactions.py
	python scripts/figures/plot_normalization_robustness.py
	python scripts/figures/plot_mushroom_sensitivity.py
	python scripts/figures/plot_variance_scaling.py
	python scripts/figures/plot_signal_allocation.py
	python scripts/figures/plot_mushroom_final.py

reproduce-review-diagnostics:
	python scripts/review_diagnostics.py --update-paper

check-review-diagnostics:
	python scripts/review_diagnostics.py --check

reproduce-signal-allocation:
	python scripts/illustrate_signal_allocation.py

check-signal-allocation:
	python scripts/illustrate_signal_allocation.py --check

check-optimization: check-review-diagnostics check-signal-allocation

prepare-lean:
	cd lean && lake exe cache get Mathlib.Data.Real.Basic Mathlib.Tactic.FieldSimp Mathlib.Tactic.Linarith Mathlib.Tactic.Positivity Mathlib.Tactic.Ring

check-lean:
	cd lean && lake build

prepare-results:
	python scripts/prepare_results.py

check-normalization-robustness check-practical-selection check-mushroom-rate-search check-mushroom-sensitivity: prepare-results
reproduce-practical-selection reproduce-mushroom-rate-search reproduce-mushroom-sensitivity: prepare-results

check-python: check-scripts

check-scripts:
	ruff format --check scripts
	ruff check scripts

format: format-scripts

format-scripts:
	ruff format scripts

check-optimization: check-practical-selection check-predictive-claim check-mushroom-rate-search check-mushroom-sensitivity
check-optimization: check-variance-scaling

check-variance-scaling: prepare-results
	OPENBLAS_NUM_THREADS=1 python experiments/check_variance_scaling.py

reproduce-variance-scaling: prepare-results
	OPENBLAS_NUM_THREADS=1 python experiments/check_variance_scaling.py --numerics-only
	python experiments/variance_scaling_spec.py --declare
	OPENBLAS_NUM_THREADS=1 python experiments/run_variance_scaling.py
	OPENBLAS_NUM_THREADS=1 python experiments/summarize_variance_scaling.py
	OPENBLAS_NUM_THREADS=1 python experiments/check_variance_scaling.py --write-audit

check-predictive-claim: check-predictive-feasibility check-predictive-regime check-predictive-theorem check-predictive-review
	python experiments/check_predictive_claim.py

check-predictive-feasibility:
	python experiments/check_predictive_feasibility.py

check-predictive-regime:
	python experiments/check_predictive_regime.py

check-predictive-theorem:
	python experiments/check_predictive_theorem.py

check-predictive-review:
	python experiments/check_predictive_review.py

reproduce-predictive-intro:
	python experiments/plot_predictive_intro.py

check-predictive-intro:
	python experiments/plot_predictive_intro.py --check

check-optimization: check-predictive-intro

check-practical-selection:
	python experiments/check_practical_selection.py

reproduce-practical-selection:
	python experiments/check_practical_selection.py --numerics-only
	python scripts/frozen_experiment.py run_practical_selection
	python experiments/summarize_practical_selection.py
	python experiments/audit_practical_precision.py
	$(MAKE) check-practical-selection

check-mushroom-rate-search:
	OPENBLAS_NUM_THREADS=1 python scripts/frozen_experiment.py check_mushroom_rate_search

reproduce-mushroom-rate-search:
	OPENBLAS_NUM_THREADS=1 python scripts/frozen_experiment.py check_mushroom_rate_search --numerics-only
	python scripts/frozen_experiment.py mushroom_rate_spec --declare
	OPENBLAS_NUM_THREADS=1 python scripts/frozen_experiment.py run_mushroom_rate_search
	OPENBLAS_NUM_THREADS=1 python experiments/summarize_mushroom_rate_search.py
	$(MAKE) check-mushroom-rate-search

check-mushroom-sensitivity:
	OPENBLAS_NUM_THREADS=1 python scripts/frozen_experiment.py check_mushroom_sensitivity

reproduce-mushroom-sensitivity:
	OPENBLAS_NUM_THREADS=1 python scripts/frozen_experiment.py check_mushroom_sensitivity --numerics-only
	python scripts/frozen_experiment.py mushroom_sensitivity_spec --declare
	OPENBLAS_NUM_THREADS=1 python scripts/frozen_experiment.py run_mushroom_sensitivity
	OPENBLAS_NUM_THREADS=1 python experiments/summarize_mushroom_sensitivity.py
	$(MAKE) check-mushroom-sensitivity
