"""Run the synthetic comparisons independently of other experiments."""

import argparse

from experiments.common import five_rates, matched
from experiments.synthetic.config import CONFIGS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", choices=("all", *CONFIGS), default="all")
    args = parser.parse_args()
    for config in CONFIGS if args.config == "all" else (args.config,):
        print(f"Run synthetic: {config}", flush=True)
        if config == "rates5":
            five_rates.run(0)
        elif config == "rates25":
            matched.run(0)


if __name__ == "__main__":
    main()
