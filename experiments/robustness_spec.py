"""Executable sets and provenance for the September 16 robustness protocol."""

import hashlib
import itertools
import json
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results/normalization-robustness"
PROTOCOL = "notes/normalization-robustness.md"
BATCHES = (1, 10, 100)
QC = (0.002, 0.005, 0.01, 0.02, 0.05, 0.1)
LC = (-1, -0.5, 0, 0.5, 0.9, 1)
PAIRS = (((1, 1), 3), ((2, 1), 4))
HC = np.unique([0] + [h * 2**j for h in (0.002, 0.01) for j in range(-10, 7)])
HF = np.unique(np.r_[HC, np.sqrt(HC[1:-1] * HC[2:])])
KC = np.array([0, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000])
MC = np.array([0, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000])
KF = np.unique(
    np.r_[0, np.arange(1, 201), np.arange(250, 2001, 50), np.arange(2250, 10001, 250)]
)
MF = np.unique(
    np.r_[
        0,
        np.arange(100, 2001, 100),
        np.arange(2500, 20001, 500),
        np.arange(22500, 100001, 2500),
    ]
)
ATOL, RTOL, SIGN_TOL, STABILITY_TOL = 2e-11, 2e-10, 1e-8, 1e-10
PANELS = [
    (0.02, 0, (1, 1), 3, 0.002, (100, 1000, 10000)),
    (0.02, 1, (2, 1), 4, 0.01, (10, 100, 1000)),
    (0.002, 0, (1, 1), 3, 0.002, (100, 1000, 10000)),
    (0.02, -1, (2, -1), 4, 0.01, (10, 100, 1000)),
    (0.02, 0, (1, 0), 1, 0.002, (100, 1000, 10000)),
    (0.02, 1, (0, 0), 4, 0.01, (10, 100, 1000)),
]
FAILURES = {
    0: "valid",
    1: "floating_point_nonfinite",
    2: "negative_psd_residual",
    3: "asymmetry",
    4: "nonfinite_risk",
}


def laws():
    result = {}

    def add(q, ell, beta, sigma2, label):
        key = (q, ell, *beta, sigma2)
        if key not in result:
            result[key] = dict(
                q=q, ell=ell, signal=list(beta), sigma2=sigma2, slices=[]
            )
        result[key]["slices"].append(label)

    for q, ell, (beta, sigma2) in itertools.product(QC, LC, PAIRS):
        add(q, ell, beta, sigma2, "prevalence_dependence")
    signals = (
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (1, -1),
        (2, 1),
        (2, -1),
        (0.5, 1),
        (1, 0.5),
    )
    for ell, beta, sigma2 in itertools.product((-1, 0, 1), signals, (0, 1, 3, 4, 5, 9)):
        add(0.02, ell, beta, sigma2, "signal_noise")
    for i, law in enumerate(result.values()):
        law["id"] = i
        law["refined"] = (
            (
                law["q"] in (0.002, 0.02, 0.1)
                and law["ell"] in (0, 1)
                and (tuple(law["signal"]), law["sigma2"]) in PAIRS
            )
            or (
                law["q"] == 0.02
                and law["ell"] in (-1, 0, 1)
                and law["signal"] == [2, -1]
                and law["sigma2"] == 4
            )
            or (
                law["q"] == 0.02
                and law["ell"] == 1
                and law["signal"] == [0, 0]
                and law["sigma2"] == 4
            )
        )
        law["fixed_h"] = (
            [0.002, 0.01]
            if "signal_noise" in law["slices"]
            else [0.002 if law["signal"] == [1, 1] else 0.01]
        )
    return list(result.values())


def model(q, ell):
    cells = np.array(list(itertools.product((0.0, 1.0), repeat=2)))
    p = np.array(
        [
            0.5 - q * (1 - ell) / 2,
            q * (1 - ell) / 2,
            0.5 - q * (1 + ell) / 2,
            q * (1 + ell) / 2,
        ]
    )
    x = cells - [0.5, q]
    return dict(
        q=q,
        ell=ell,
        cells=cells,
        probabilities=p,
        x=x,
        gram=x.T @ (p[:, None] * x),
        rare_second=x.T @ ((p * cells[:, 1] / q)[:, None] * x),
    )


def grid(law, batch):
    rates = HF if law["refined"] else HC
    updates, observations = (KF, MF) if law["refined"] else (KC, MC)
    counts = np.union1d(updates, observations // batch)
    # Bit labels retain every originating grid when endpoints coincide.
    labels = np.isin(counts, KC).astype(np.uint8) + 2 * np.isin(
        counts * batch, MC
    ).astype(np.uint8)
    if law["refined"]:
        labels += 4 * np.isin(counts, KF).astype(np.uint8) + 8 * np.isin(
            counts * batch, MF
        ).astype(np.uint8)
    return rates, counts, labels


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def preserved():
    paths = [
        "notes/rare-subgroup-pilot.md",
        "notes/joint-interactions.md",
        "notes/joint-interactions-results.md",
        "experiments/run_rare_subgroup_pilot.py",
        "experiments/check_rare_subgroup_pilot.py",
        "experiments/run_joint_interactions.py",
        "experiments/check_joint_interactions.py",
        "experiments/plot_joint_interactions.py",
        "results/rare-subgroup-pilot.json",
        "results/joint-interactions.json",
        "results/joint-interactions.npz",
    ]
    paths += [
        str(p.relative_to(ROOT))
        for p in sorted((ROOT / "results/figures").glob("joint-*"))
    ]
    result = {}
    for path in paths:
        baseline = subprocess.check_output(["git", "show", f"a47cbfb:{path}"], cwd=ROOT)
        digest = hashlib.sha256(baseline).hexdigest()
        assert sha256(ROOT / path) == digest, f"Preserved study changed: {path}"
        result[path] = digest
    return result


def jsonable(value):
    if isinstance(value, np.ndarray):
        return jsonable(value.tolist())
    if isinstance(value, np.generic):
        return jsonable(value.item())
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def write_json(path, value):
    path.write_text(
        json.dumps(jsonable(value), allow_nan=False, separators=(",", ":")) + "\n"
    )
