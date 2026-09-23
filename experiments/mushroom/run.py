"""Run the mushroom comparisons independently of other experiments."""

import argparse

from experiments.common import five_rates, matched
from experiments.mushroom import run_damping, run_rates17
from experiments.mushroom.config import CONFIGS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", choices=("all", *CONFIGS), default="all")
    args = parser.parse_args()
    for config in CONFIGS if args.config == "all" else (args.config,):
        print(f"Run mushroom: {config}", flush=True)
        if config == "rates5":
            five_rates.run(1)
        elif config == "rates17":
            run_rates17.main()
        elif config == "rates25":
            matched.run(1)
        elif config == "damping":
            run_damping.main()


if __name__ == "__main__":
    main()
