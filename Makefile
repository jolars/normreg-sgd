.PHONY: all paper check check-quick check-markdown check-config check-python check-optimization check-joint-interactions check-normalization-risk reproduce-joint-interactions check-normalization-robustness reproduce-normalization-robustness verify reproduce format

all: paper

paper:
	cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error -outdir=../build main.tex

check: check-markdown check-config check-python verify paper

check-quick: check-markdown check-config check-python check-optimization paper
	python experiments/check_two_features.py --draws 20000 --check-only

check-markdown:
	panache format --check .
	panache lint .

check-config:
	nixfmt --check devenv.nix
	actionlint
	uv lock --check

check-python:
	ruff format --check experiments
	ruff check experiments

check-optimization:
	python experiments/check_optimization.py
	python experiments/check_block_flow.py
	python experiments/check_discrete_dynamics.py
	python experiments/check_multivariate_stability.py
	python experiments/check_sampling_schemes.py
	python experiments/check_joint_budget.py
	python experiments/check_rare_subgroup_pilot.py
	$(MAKE) check-joint-interactions
	$(MAKE) check-normalization-risk
	$(MAKE) check-normalization-robustness

check-joint-interactions:
	python experiments/check_joint_interactions.py

check-normalization-risk:
	python experiments/check_normalization_risk_candidate.py
	python experiments/check_normalization_risk_theorem.py

check-normalization-robustness:
	python experiments/check_normalization_robustness.py

reproduce-normalization-robustness:
	python experiments/check_normalization_robustness.py --numerics-only
	$(MAKE) check-normalization-risk
	python experiments/run_normalization_robustness.py
	python experiments/simulate_normalization_robustness.py
	python experiments/summarize_normalization_robustness.py
	python experiments/plot_normalization_robustness.py
	$(MAKE) check-normalization-robustness

reproduce-joint-interactions:
	python experiments/run_joint_interactions.py
	python experiments/plot_joint_interactions.py

verify: check-optimization
	python experiments/check_two_features.py --check-only

reproduce:
	python experiments/check_two_features.py

format:
	panache format .
	nixfmt devenv.nix
	ruff format experiments
