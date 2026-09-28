"""Check tolerance to rounding without accepting changed experiment records."""

from copy import deepcopy
from math import inf, nextafter

from experiments.common.reproduction import assert_reproduced


def main():
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
