"""Check tolerance to rounding without accepting changed experiment records."""

import json
import tempfile
from copy import deepcopy
from math import inf, nextafter
from pathlib import Path

import numpy as np

from experiments.common import reproduction
from experiments.common.data import write_json
from experiments.common.reproduction import assert_reproduced
from experiments.common.statistics import statistics


def check_serialization():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "summary.json"
        report = {
            "array": np.array([0.25, 0.5]),
            "integer": np.int64(3),
            "boolean": np.bool_(True),
            "missing": None,
            "statistics": statistics([1.0, np.nan]),
        }
        write_json(path, report)
        saved = path.read_text()
        loaded = json.loads(saved)
        assert loaded["array"] == [0.25, 0.5]
        assert type(loaded["integer"]) is int
        assert type(loaded["boolean"]) is bool
        assert loaded["missing"] is None
        assert loaded["statistics"]["missing"] == 1
        assert loaded["statistics"]["mcse"] is None
        for value in (float("nan"), inf, -inf, np.float64(inf), np.array([np.nan])):
            with np.testing.assert_raises(ValueError):
                write_json(path, {"nested": [{"value": value}]})
            assert path.read_text() == saved
    print(
        "JSON preserves numerical types and explicit missing values; nonfinite fails."
    )


def main():
    check_serialization()
    saved_arrays = {"risk": np.array([0.25, 0.5]), "choice": np.array([0, 2])}
    rounded_arrays = {
        "risk": np.nextafter(saved_arrays["risk"], np.inf),
        "choice": saved_arrays["choice"].copy(),
    }
    reproduction.assert_arrays_reproduced(rounded_arrays, saved_arrays)
    for key, value in (
        ("risk", np.array([0.25, 0.51])),
        ("risk", np.array([[0.25, 0.5]])),
        ("risk", np.array([0.25, np.nan])),
        ("choice", np.array([0, 1])),
        ("choice", np.array([0.0, 2.0])),
    ):
        with np.testing.assert_raises(AssertionError):
            reproduction.assert_arrays_reproduced(
                {**saved_arrays, key: value}, saved_arrays
            )
    with np.testing.assert_raises(AssertionError):
        reproduction.assert_arrays_reproduced(
            {"risk": saved_arrays["risk"]}, saved_arrays
        )
    saved = {
        "cases": [{"name": "crossing", "s": 0.4818850789905079, "cap": 102}],
        "risk": [0.0, 0.50230649],
        "certified": False,
        "ratio": None,
    }
    rounded = deepcopy(saved)
    rounded["cases"][0]["s"] = nextafter(saved["cases"][0]["s"], 0.0)
    rounded["risk"][1] = nextafter(saved["risk"][1], inf)
    assert_reproduced(rounded, saved)

    mutations = [
        ("case name", lambda x: x["cases"][0].update(name="other")),
        ("case parameter", lambda x: x["cases"][0].update(s=0.49)),
        ("integer cap", lambda x: x["cases"][0].update(cap=103)),
        ("integer type", lambda x: x["cases"][0].update(cap=102.0)),
        ("risk", lambda x: x["risk"].__setitem__(1, 0.50230749)),
        ("nonfinite risk", lambda x: x["risk"].__setitem__(1, inf)),
        ("order", lambda x: x["risk"].reverse()),
        ("length", lambda x: x["risk"].append(0.0)),
        ("missing field", lambda x: x.pop("ratio")),
        ("extra field", lambda x: x.update(extra=None)),
        ("boolean", lambda x: x.update(certified=0)),
    ]
    for label, mutate in mutations:
        changed = deepcopy(saved)
        mutate(changed)
        try:
            assert_reproduced(changed, saved)
        except AssertionError:
            continue
        raise AssertionError(f"Accepted a changed {label}.")
    print("Rounding is tolerated; changed values, identities, and structure fail.")


if __name__ == "__main__":
    main()
