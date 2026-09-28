"""Check independent selection, disjoint evaluation, and weighted shard means."""

import numpy as np

from experiments.theory_bridge import config as cfg
from experiments.theory_bridge.calibration_sensitivity import recalibrate


def main():
    q = 0.02
    shape = (len(cfg.stops(q)), len(cfg.ARMS), 2, 2, len(cfg.rates()), 2)
    rng = np.random.default_rng(19)
    counts = np.array([2, 3, 5, 7])
    profiles = rng.integers(0, 20, size=(4, *shape)).astype(float)
    sums = profiles * counts.reshape(-1, 1, 1, 1, 1, 1, 1)
    exact = rng.integers(0, 20, size=(shape[0], *shape[2:])).astype(float)
    partitions = np.array([[0, 2], [1, 2]])
    choices, risks, training_counts = recalibrate(sums, counts, exact, q, partitions)
    checked = 0
    for partition_id, left in enumerate(partitions):
        right = np.array([i for i in range(4) if i not in left])
        for orientation, (train, test) in enumerate(((left, right), (right, left))):
            split = 2 * partition_id + orientation
            assert training_counts[split] == sum(counts[i] for i in train)
            for cap, arm, scaling, signal in np.ndindex(3, len(cfg.ARMS), 2, 2):

                def mean(indices):
                    if arm == 0:
                        return exact[:, scaling, signal, :, 1]
                    return sum(
                        counts[i] * profiles[i, :, arm, scaling, signal, :, 1]
                        for i in indices
                    ) / sum(counts[i] for i in indices)

                training, heldout = mean(train), mean(test)
                candidates = (
                    (training[stop, rate], stop, rate)
                    for stop, updates in enumerate(cfg.stops(q))
                    if updates <= cfg.budgets(q)[cap]
                    for rate in range(len(cfg.rates()))
                )
                _, stop, rate = min(candidates)
                np.testing.assert_array_equal(
                    choices[split, cap, arm, scaling, signal], [stop, rate]
                )
                np.testing.assert_allclose(
                    risks[split, cap, arm, scaling, signal], heldout[stop, rate]
                )
                checked += 1

    # Changing held-out losses must not influence the selected candidate.
    changed = sums.copy()
    changed[1, :, 1:] += 100 * counts[1]
    new_choices, new_risks, _ = recalibrate(changed, counts, exact, q, partitions[:1])
    np.testing.assert_array_equal(new_choices[0], choices[0])
    np.testing.assert_allclose(new_risks[0, :, 0], risks[0, :, 0])
    np.testing.assert_allclose(
        new_risks[0, :, 1:] - risks[0, :, 1:], 100 * counts[1] / counts[[1, 3]].sum()
    )
    print(f"{checked} independent selections and held-out risks; no selection leakage.")


if __name__ == "__main__":
    main()
