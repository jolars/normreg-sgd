"""Fixed settings for the exploratory common-feature dimension study."""

from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "results/common-block"
COMMON_COUNTS = np.array([1, 2, 4, 8, 16, 32, 64])
PREVALENCES = np.array([0.02, 0.005, 0.0001])
TARGET_BUDGETS = np.array([1.0, 2.0, 4.0])
SIGNALS = np.array([[0.01, 1.0], [1.0, 0.01]])
SIGNAL_NAMES = ["Dominant rare signal", "Dominant common signal"]
SCALINGS = ["Unscaled", "Standardized"]
NOISE_VARIANCE = 1.0
RATE_FRACTIONS = np.r_[0.0, np.geomspace(1e-7, 0.999, 1025)]
