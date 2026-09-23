"""Summarize the mushroom comparisons independently of other experiments."""

import argparse

from experiments.common import summarize_five_rates, summarize_matched
from experiments.mushroom import summarize_damping, summarize_rates17
from experiments.mushroom.config import CONFIGS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", choices=("all", *CONFIGS), default="all")
    args = parser.parse_args()
    for config in CONFIGS if args.config == "all" else (args.config,):
        print(f"Summarize mushroom: {config}", flush=True)
        if config == "rates5":
            summarize_five_rates.summarize("mushroom")
        elif config == "rates17":
            summarize_rates17.main()
        elif config == "rates25":
            summarize_matched.summarize("mushroom")
        elif config == "damping":
            summarize_damping.main()


if __name__ == "__main__":
    main()
