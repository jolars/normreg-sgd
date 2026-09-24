"""Settings specified before evaluating the controlled bridge study."""

from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "results/theory-bridge"
SEED = 20260924
PREVALENCES = (0.02, 0.005)
SIGNALS = np.array([[0.1, 1.0], [1.0, 0.1]])
SIGNAL_NAMES = ("rare", "common")
SCALINGS = ("none", "sd")
TRAIN_SIZE = 256
VALIDATION_SIZES = (128, 512, 2048)
CALIBRATION_REPS = 2048
EVALUATION_REPS = 4096
CHUNK_SIZE = 64
RATE_INTERVALS = 128
STOP_POINTS = 65
ARMS = (
    "fresh",
    "fresh_intercept",
    "reuse",
    "reuse_scales",
    "reuse_intercept",
    "reuse_scales_intercept",
    "reuse_centered_intercept",
    "reuse_mean_initialized",
)
ARM_LABELS = (
    "Fresh observations",
    "Fresh + fitted intercept",
    "Reuse observations",
    "Reuse + estimated scales",
    "Reuse + fitted intercept",
    "Reuse + scales + intercept",
    "Also estimate centering",
    "Also initialize at sample mean",
)
REUSE = np.array([False, False, True, True, True, True, True, True])
ESTIMATE_SCALE = np.array([False, False, False, True, False, True, True, True])
FIT_INTERCEPT = np.array([False, True, False, False, True, True, True, True])
ESTIMATE_CENTER = np.array([False, False, False, False, False, False, True, True])
INITIALIZE_MEAN = np.array([False, False, False, False, False, False, False, True])
POLICIES = ("calibrated", "coarse_calibrated", "path_oracle") + tuple(
    f"validation_{n}" for n in VALIDATION_SIZES
)


def rates(intervals=RATE_INTERVALS):
    return np.r_[0.0, np.geomspace(1e-4, 1.9, intervals + 1)]


def budgets(q):
    b = q * (1 - q)
    return np.array([int(np.ceil(1 / b)), int(np.rint(2 / b)), int(np.floor(4 / b))])


def stops(q):
    caps = budgets(q)
    return np.unique(
        np.r_[0, np.rint(np.geomspace(1, caps[-1], STOP_POINTS)), caps]
    ).astype(int)


def coarse_mask(q):
    checkpoints = stops(q)
    mask = np.arange(len(checkpoints)) % 2 == 0
    mask |= np.isin(checkpoints, np.r_[0, budgets(q)])
    return mask
