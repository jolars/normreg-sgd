"""Summary statistics shared by sampled-data experiments."""

import numpy as np


def statistics(values):
    values = np.asarray(values)
    good = np.isfinite(values)
    n = int(good.sum())
    # Rescaling avoids overflow when summarizing retained unstable candidates.
    scale = max(float(np.max(np.abs(values[good]))), 1e-300) if n else 1
    normalized = values[good] / scale
    return dict(
        n=n,
        missing=int((~good).sum()),
        mean=float(normalized.mean() * scale) if n else None,
        mcse=float(normalized.std(ddof=1) / np.sqrt(n) * scale) if n > 1 else None,
        median=float(np.median(normalized) * scale) if n else None,
        p95=float(np.quantile(normalized, 0.95) * scale) if n else None,
        maximum=float(normalized.max() * scale) if n else None,
        aggregation="finite_replicates_only" if n < len(values) else "all_replicates",
    )
