"""Compare reconstructed numerical results with their saved records."""

import math

import numpy as np

RTOL = 1e-12
ATOL = 1e-14


def assert_arrays_reproduced(actual, expected):
    """Preserve archive fields, shapes, dtypes, and discrete selections exactly."""
    assert set(actual) == set(expected), "archive: different fields"
    for key, value in actual.items():
        reference = expected[key]
        assert value.shape == reference.shape, f"{key}: different shapes"
        assert value.dtype == reference.dtype, f"{key}: different dtypes"
        if np.issubdtype(value.dtype, np.inexact):
            assert np.isfinite(value).all() and np.isfinite(reference).all(), (
                f"{key}: nonfinite"
            )
            np.testing.assert_allclose(value, reference, rtol=RTOL, atol=ATOL)
        else:
            np.testing.assert_array_equal(value, reference)


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
        assert math.isclose(actual, expected, rel_tol=RTOL, abs_tol=ATOL), (
            f"{path}: {actual!r} != {expected!r} within numerical tolerance"
        )
    else:
        assert actual == expected, f"{path}: {actual!r} != {expected!r}"
