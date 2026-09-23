"""Summarize the synthetic comparisons independently of other experiments."""

import argparse

from experiments.common import summarize_five_rates, summarize_matched
from experiments.synthetic.config import CONFIGS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", choices=("all", *CONFIGS), default="all")
    args = parser.parse_args()
    for config in CONFIGS if args.config == "all" else (args.config,):
        print(f"Summarize synthetic: {config}", flush=True)
        if config == "rates5":
            summarize_five_rates.summarize("synthetic")
        elif config == "rates25":
            summarize_matched.summarize("synthetic")


if __name__ == "__main__":
    main()
