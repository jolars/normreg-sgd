"""Serialize numerical experiment settings and results as JSON."""

import json
from pathlib import Path

import numpy as np


def jsonable(value):
    if isinstance(value, np.ndarray):
        return jsonable(value.tolist())
    if isinstance(value, np.generic):
        return jsonable(value.item())
    if isinstance(value, dict):
        return {k: jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    return value


def write_json(path, value):
    """Reject nonfinite numbers; analyses must mark missing values explicitly."""
    Path(path).write_text(json.dumps(jsonable(value), indent=2, allow_nan=False) + "\n")
