.PHONY: all paper check check-quick check-markdown check-config check-python check-optimization check-joint-interactions check-normalization-risk reproduce-joint-interactions verify reproduce format

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

check-joint-interactions:
	python experiments/check_joint_interactions.py

check-normalization-risk:
	python experiments/check_normalization_risk_candidate.py

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
