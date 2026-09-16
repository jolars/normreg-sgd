"""Frozen configuration, source data, and provenance for practical selection."""

import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
from scipy import sparse

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results/practical-selection"
DATA = ROOT / "data/mushroom/agaricus-lepiota.data"
DATA_HASH = "e65d082030501a3ebcbcd7c9f7c71aa9d28fdfff463bf4cf4716a3fe13ac360e"
PROTOCOL = "notes/practical-selection.md"
BASELINE = "a7741925090965fafc0bbdda8f979f75de7225ba"
SCALES = ("none", "sd", "damped")
ARMS = (
    "known",
    "estimated_scale",
    "centered_fixed",
    "centered_fitted",
    "uncentered_fitted",
)
FACTORS = (0.001, 0.01, 0.05, 0.2, 0.8)
SYNTHETIC_M = (0, 128, 512, 2048)
MUSHROOM_M = (0, 512, 2048, 8192)
SIZES = ((256, 128), (2048, 1024))
REPS = (128, 32)
LAWS = [
    dict(name="C1", q=0.02, ell=0, beta=[1, 1], sigma2=3),
    dict(name="rarer_C1", q=0.002, ell=0, beta=[1, 1], sigma2=3),
    dict(name="C2", q=0.02, ell=1, beta=[2, 1], sigma2=4),
    dict(name="rarer_C2", q=0.002, ell=1, beta=[2, 1], sigma2=4),
    dict(name="opposite_nested", q=0.02, ell=1, beta=[2, -1], sigma2=4),
    dict(name="opposite_disjoint", q=0.02, ell=-1, beta=[2, -1], sigma2=4),
    dict(name="rare_only", q=0.02, ell=0, beta=[0, 1], sigma2=1),
    dict(name="common_only", q=0.02, ell=0, beta=[1, 0], sigma2=1),
]
FIELDS = (
    "cap-shape",
    "cap-surface",
    "cap-color",
    "bruises",
    "odor",
    "gill-attachment",
    "gill-spacing",
    "gill-size",
    "gill-color",
    "stalk-shape",
    "stalk-root",
    "stalk-surface-above-ring",
    "stalk-surface-below-ring",
    "stalk-color-above-ring",
    "stalk-color-below-ring",
    "veil-type",
    "veil-color",
    "ring-number",
    "ring-type",
    "spore-print-color",
    "population",
    "habitat",
)


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def rng(stage, law, rep, stream):
    return np.random.default_rng(
        np.random.SeedSequence([20260916, stage, law, rep, stream])
    )


def binary_law(law):
    q, ell = law["q"], law["ell"]
    x = np.array(list(itertools.product((0.0, 1.0), repeat=2)))
    p = np.array(
        [
            0.5 - q * (1 - ell) / 2,
            q * (1 - ell) / 2,
            0.5 - q * (1 + ell) / 2,
            q * (1 + ell) / 2,
        ]
    )
    mu = np.array([0.5, q])
    return x, p, mu


def synthetic_data(law_id, rep):
    law = LAWS[law_id]
    cells, prob, mu = binary_law(law)
    parts = []
    for stream, n in enumerate((256, 128)):
        generator = rng(0, law_id, rep, stream)
        x = cells[generator.choice(4, n, p=prob)]
        y = (x - mu) @ law["beta"] + generator.normal(0, np.sqrt(law["sigma2"]), n)
        parts.append((x, y, x[:, 1].astype(bool)))
    test = (cells, (cells - mu) @ law["beta"], cells[:, 1].astype(bool))
    return parts, test, prob, mu


def load_mushroom():
    assert sha256(DATA) == DATA_HASH, "Mushroom source checksum changed."
    raw = np.loadtxt(DATA, delimiter=",", dtype="U1")
    assert raw.shape == (8124, 23)
    assert len(np.unique(raw[:, 1:], axis=0)) == len(raw), (
        "Duplicate predictors: revise protocol."
    )
    return raw[:, 1:], (raw[:, 0] == "p").astype(float), raw[:, 20] == "r"


def encode_fit(x):
    return [sorted(set(x[:, j])) for j in range(x.shape[1])]


def encode(x, vocabulary):
    rows, columns, unknown = [], [], []
    offset = 0
    for j, levels in enumerate(vocabulary):
        lookup = {level: i + offset for i, level in enumerate(levels)}
        ids = np.array([lookup.get(value, -1) for value in x[:, j]])
        valid = ids >= 0
        rows.extend(np.flatnonzero(valid))
        columns.extend(ids[valid])
        unknown.append(int((~valid).sum()))
        offset += len(levels)
    result = sparse.csr_matrix(
        (np.ones(len(rows)), (rows, columns)), shape=(len(x), offset)
    )
    return result, unknown


def mushroom_data(raw, size_id, rep):
    x, y, rare = raw
    n, nv = SIZES[size_id]
    order = rng(1, 0, rep, 0).permutation(len(x))
    ids = (order[:n], order[n : n + nv], order[n + nv :])
    vocabulary = encode_fit(x[ids[0]])
    parts, unknown = [], []
    for idx in ids:
        design, missing = encode(x[idx], vocabulary)
        parts.append((design, y[idx], rare[idx]))
        unknown.append(missing)
    names = [
        f"{field}={level}"
        for field, levels in zip(FIELDS, vocabulary, strict=True)
        for level in levels
    ]
    return parts, dict(
        vocabulary=vocabulary,
        names=names,
        unknown=unknown,
        partitions=[a.tolist() for a in ids],
    )


def configurations(stage):
    arms = ARMS if stage == 0 else ARMS[2:]
    return [
        dict(arm=arm, scale=scale, factor=factor)
        for arm, scale, factor in itertools.product(arms, SCALES, FACTORS)
    ]


def jsonable(value):
    if isinstance(value, np.ndarray):
        return jsonable(value.tolist())
    if isinstance(value, np.generic):
        return jsonable(value.item())
    if isinstance(value, dict):
        return {k: jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def write_json(path, value):
    Path(path).write_text(json.dumps(jsonable(value), indent=2, allow_nan=False) + "\n")
