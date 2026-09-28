"""Compare reconstructed JSON results with their saved records."""

import math


def assert_reproduced(actual, expected, path="result"):
    """Allow numerical roundoff while preserving types, identities, and order."""
    assert type(actual) is type(expected), f"{path}: different types"
    if isinstance(expected, dict):
        assert actual.keys() == expected.keys(), f"{path}: different fields"
        for key in expected:
            assert_reproduced(actual[key], expected[key], f"{path}.{key}")
    elif isinstance(expected, list):
        assert len(actual) == len(expected), f"{path}: different lengths"
        for index, (value, reference) in enumerate(zip(actual, expected, strict=True)):
            assert_reproduced(value, reference, f"{path}[{index}]")
    elif isinstance(expected, float):
        # Recomputed roots and summaries can differ in their final bits. These
        # tolerances remain far below the independent risk-replay tolerances.
        assert math.isfinite(actual) and math.isfinite(expected), f"{path}: nonfinite"
        assert math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-14), (
            f"{path}: {actual!r} != {expected!r} within numerical tolerance"
        )
    else:
        assert actual == expected, f"{path}: {actual!r} != {expected!r}"
