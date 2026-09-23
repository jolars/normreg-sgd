"""Certify normalization-risk comparisons with outward-rounded integer intervals.

The certificates cover continuous parameter intervals. Floating-point checks
against the existing moment operator are separate from the certificates.
"""

import itertools
from dataclasses import dataclass
from fractions import Fraction

import numpy as np

from checks.joint_interactions import enumerate_paths
from experiments.common.moments import make_model, moment_path

SCALE = 10**60


@dataclass(frozen=True)
class Interval:
    """Enclose a real value between integer multiples of 10**-60."""

    lo: int
    hi: int

    def __post_init__(self):
        assert self.lo <= self.hi

    @classmethod
    def rational(cls, lower, upper=None):
        lower = Fraction(lower) * SCALE
        upper = lower if upper is None else Fraction(upper) * SCALE
        return cls(
            lower.numerator // lower.denominator,
            -((-upper.numerator) // upper.denominator),
        )

    def __add__(self, other):
        other = as_interval(other)
        return Interval(self.lo + other.lo, self.hi + other.hi)

    __radd__ = __add__

    def __neg__(self):
        return Interval(-self.hi, -self.lo)

    def __sub__(self, other):
        return self + (-as_interval(other))

    def __rsub__(self, other):
        return as_interval(other) - self

    def __mul__(self, other):
        other = as_interval(other)
        products = [a * b for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        return Interval(min(products) // SCALE, -((-max(products)) // SCALE))

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = as_interval(other)
        assert other.lo > 0 or other.hi < 0
        if other.hi < 0:
            return (-self) / (-other)
        return self * Interval(SCALE**2 // other.hi, -((-(SCALE**2)) // other.lo))

    def __rtruediv__(self, other):
        return as_interval(other) / self

    def __pow__(self, count):
        assert isinstance(count, int) and count >= 0
        result, base = as_interval(1), self
        while count:
            if count % 2:
                result = result * base
            count //= 2
            if count:
                base = base * base
        return result

    def upper(self):
        return Interval(self.hi, self.hi)

    def display(self):
        # These decimals are for inspection; assertions use integer endpoints.
        return f"[{self.lo / SCALE:.12g}, {self.hi / SCALE:.12g}]"


def as_interval(value):
    assert not isinstance(value, (float, np.floating))
    return value if isinstance(value, Interval) else Interval.rational(value)


def hull(values):
    return Interval(min(v.lo for v in values), max(v.hi for v in values))


def largest_upper(values):
    upper = max(v.hi for v in values)
    return Interval(upper, upper)


def partition(lower, upper, pieces):
    lower, upper = Fraction(lower), Fraction(upper)
    return [
        Interval.rational(
            lower + (upper - lower) * i / pieces,
            lower + (upper - lower) * (i + 1) / pieces,
        )
        for i in range(pieces)
    ]


def geometric_sum(value, count):
    """Avoid cancellation and dependent endpoints in (1-value**k)/(1-value)."""
    power, total = as_interval(1), as_interval(0)
    block_power, block_sum = value, as_interval(1)
    while count:
        if count % 2:
            total = total + power * block_sum
            power = power * block_power
        count //= 2
        if count:
            block_sum = block_sum * (1 + block_power)
            block_power = block_power * block_power
    return total


def matrix_product(left, right):
    return [
        [sum(a * b for a, b in zip(row, column, strict=True)) for column in zip(*right)]
        for row in left
    ]


def matrix_power(matrix, count):
    size = len(matrix)
    result = [[as_interval(int(i == j)) for j in range(size)] for i in range(size)]
    while count:
        if count % 2:
            result = matrix_product(result, matrix)
        count //= 2
        if count:
            matrix = matrix_product(matrix, matrix)
    return result


def transition(q, dependence, common_step, batch, scaled):
    """Propagate (V_CC, V_CR, V_RR, noise variance) on the original scale."""
    a, b = as_interval("0.25"), q * (1 - q)
    c = q * dependence / 2
    dc = 4 * common_step
    dr = common_step / b if scaled else dc
    cross_square = c**2 + (a * b - c**2) / batch
    mixed = c * (b + (1 - 4 * b) / batch)
    return [
        [
            (1 - dc * a) ** 2,
            -2 * dc * (1 - dc * a) * c,
            dc**2 * cross_square,
            dc**2 * a / batch,
        ],
        [
            -dr * (1 - dc * a) * c,
            (1 - dc * a) * (1 - dr * b) + dc * dr * cross_square,
            -dc * c + dc * dr * mixed,
            dc * dr * c / batch,
        ],
        [
            dr**2 * cross_square,
            -2 * dr * c + 2 * dr**2 * mixed,
            (1 - dr * b) ** 2 + dr**2 * b * (1 - 4 * b) / batch,
            dr**2 * b / batch,
        ],
        [as_interval(0), as_interval(0), as_interval(0), as_interval(1)],
    ]


def scalar_envelope(q, common_step, batch, count):
    """Bound the scalar approximation and its omitted coordinate coupling."""
    weights = [(as_interval("0.25") + (1 - q) ** 2) / 2, (1 - q) ** 2 / 2]
    signal_square = Interval.rational("0.9025", "1.1025")
    parts = []
    radii = []
    for scaled in (False, True):
        matrix = transition(q, as_interval(0), common_step, batch, scaled)
        a, d = matrix[0][0], matrix[2][2]
        e, f = matrix[0][2], matrix[2][0]
        gc, gr = matrix[0][3], matrix[2][3]
        coupling = largest_upper([e, f])
        radius = largest_upper([a + e, d + f])
        assert 0 <= radius.lo < SCALE
        assert 0 <= matrix[1][1].lo <= matrix[1][1].hi < SCALE
        homogeneous_error = (
            weights[0].upper()
            * signal_square.upper()
            * coupling
            * count
            * radius ** (count - 1)
        )
        noise_error = (
            weights[0].upper() * largest_upper([gc, gr]) * coupling / (1 - radius) ** 2
        )
        parts.append(
            (d**count, gr * geometric_sum(d, count), homogeneous_error, noise_error)
        )
        radii.append(radius)
    plain, scaled = parts
    f_proxy = weights[1] * signal_square * (scaled[0] - plain[0])
    n_proxy = weights[1] * (scaled[1] - plain[1])
    homogeneous = Interval(f_proxy.lo - plain[2].hi, f_proxy.hi + scaled[2].hi)
    noise = Interval(n_proxy.lo - plain[3].hi, n_proxy.hi + scaled[3].hi)
    assert homogeneous.hi < 0 < noise.lo
    return homogeneous, noise, largest_upper(radii)


def certify_c1(pieces=8):
    reported = {
        (1, 1000): (("-0.353", "-0.160"), ("10.46", "17.76")),
        (1, 10000): (("0.0021", "0.125"), ("0.53", "1.405")),
        (10, 1000): (("-0.386", "-0.286"), ("112.61", "184.22")),
        (10, 10000): (("-0.0281", "-0.0016"), ("5.69", "14.49")),
    }
    contrasts = {
        (batch, count): [] for batch, count in itertools.product([1, 10], [1000, 10000])
    }
    for q, step in itertools.product(
        partition("0.019", "0.021", pieces), partition("0.0019", "0.0021", pieces)
    ):
        for (batch, count), entries in contrasts.items():
            homogeneous, noise, radius = scalar_envelope(q, step, batch, count)
            difference = homogeneous + Interval.rational("1.5", "5") * noise
            if (batch, count) == (1, 10000):
                assert difference.lo > 0, difference.display()
            else:
                assert difference.hi < 0, difference.display()
            entries.append((difference, -homogeneous / noise, radius))
    print(f"C1: {pieces**2} closed rectangles cover the entire q/h box.")
    for key, entries in contrasts.items():
        gap, threshold, radius = [hull([row[i] for row in entries]) for i in range(3)]
        for value, endpoints in zip([gap, threshold], reported[key], strict=True):
            bound = Interval.rational(*endpoints)
            assert bound.lo <= value.lo <= value.hi <= bound.hi
        assert radius.hi < as_interval("0.999719").lo
        print(
            key,
            "contrast",
            gap.display(),
            "threshold",
            threshold.display(),
            "radius <=",
            radius.hi / SCALE,
        )
    return contrasts


def moment_coefficients(q, dependence, step, batch, count, signal):
    powers = [
        matrix_power(transition(q, dependence, step, batch, scaled), count)
        for scaled in (False, True)
    ]
    initial = [
        as_interval(signal[0]) ** 2,
        as_interval(signal[0]) * as_interval(signal[1]),
        as_interval(signal[1]) ** 2,
    ]
    difference = [
        [powers[1][i][j] - powers[0][i][j] for j in range(4)] for i in range(3)
    ]
    return [
        (sum(difference[i][j] * initial[j] for j in range(3)), difference[i][3])
        for i in range(3)
    ]


def weight_moments(q, dependence, moments):
    weights = [
        [as_interval("0.125"), q * dependence / 2, q * (1 - q) / 2],
        [as_interval("0.125"), dependence * (1 - q) / 2, (1 - q) ** 2 / 2],
    ]
    return [
        (
            sum(w[i] * moments[i][0] for i in range(3)),
            sum(w[i] * moments[i][1] for i in range(3)),
        )
        for w in weights
    ]


def certify_c2(pieces=128):
    records = []
    second_records = []
    for dependence in partition("0.9", "1", pieces):
        moments = moment_coefficients(
            as_interval("0.02"), dependence, as_interval("0.01"), 1, 100, [2, 1]
        )
        parts = weight_moments(as_interval("0.02"), dependence, moments)
        second = [f + Interval.rational("3.8", "4.1") * n for f, n in moments]
        assert second[0].lo > 0 and second[2].lo > 0
        assert second[1].hi < 0
        second_records.append(second)
        differences = [f + Interval.rational("3.8", "4.1") * n for f, n in parts]
        assert differences[0].lo > 0, differences[0].display()
        assert differences[1].hi < 0, differences[1].display()
        records.append(differences)
    print(
        f"C2: {pieces} closed intervals cover dependence in [0.9, 1]; "
        "noise variance in [3.8, 4.1]."
    )
    for i, (name, endpoints) in enumerate(
        [("aggregate", ("0.00077", "0.00194")), ("rare", ("-0.0983", "-0.0233"))]
    ):
        value, bound = hull([row[i] for row in records]), Interval.rational(*endpoints)
        assert bound.lo <= value.lo <= value.hi <= bound.hi
        print(name, "contrast", value.display())
    for i, name in enumerate(["common MSE", "cross moment", "rare MSE"]):
        print(name, "contrast", hull([row[i] for row in second_records]).display())
    for dependence, rare_signal in [(0, 1), (1, 1), (1, -1), (-1, -1)]:
        moments = moment_coefficients(
            as_interval("0.02"),
            as_interval(dependence),
            as_interval("0.01"),
            1,
            100,
            [2, rare_signal],
        )
        parts = weight_moments(as_interval("0.02"), as_interval(dependence), moments)
        print("dependence", dependence, "signal", (2, rare_signal))
        for name, (f, n) in zip(["aggregate", "rare"], parts, strict=True):
            assert f.hi < 0 < n.lo
            gap = f + 4 * n
            if name == "rare" and dependence * rare_signal == 1:
                assert gap.hi < 0
            else:
                assert gap.lo > 0
            print(
                name,
                "threshold",
                (-f / n).display(),
                "contrast at noise variance 4",
                (f + 4 * n).display(),
            )
    return records


def dependent_model(q, dependence):
    model = make_model(q, "independent")
    joint = q * (1 + dependence) / 2
    probabilities = np.array([0.5 - q + joint, q - joint, 0.5 - joint, joint])
    assert np.all(probabilities >= 0)
    x = model["x"]
    model.update(
        probabilities=probabilities,
        gram=x.T @ (probabilities[:, None] * x),
        rare_second=x.T @ ((probabilities * model["cells"][:, 1] / q)[:, None] * x),
    )
    return model


def check_against_updates():
    signal, noise_variance = np.array([2.0, -1.0]), 1.69
    cases = 0
    for dependence, batch, scaled in itertools.product(
        [-1, 0, 0.9, 1], [1, 2], [False, True]
    ):
        model = dependent_model(0.02, dependence)
        scales = np.diag(model["gram"]) ** (0.5 if scaled else 0)
        step = 0.01 if scaled else 0.04
        full = moment_path(
            model, scales, step, batch, [0, 1, 2, 100], signal, noise_variance
        )
        _, enumerated = enumerate_paths(model, scales, step, batch, signal, 1.3, 2)
        for i, count in enumerate([0, 1, 2, 100]):
            power = matrix_power(
                transition(
                    as_interval("0.02"),
                    as_interval(str(dependence)),
                    as_interval("0.01"),
                    batch,
                    scaled,
                ),
                count,
            )
            initial = [
                as_interval(4),
                as_interval(-2),
                as_interval(1),
                as_interval("1.69"),
            ]
            actual = matrix_product(power, [[v] for v in initial])
            vector = np.array([(v[0].lo + v[0].hi) / (2 * SCALE) for v in actual[:3]])
            second = np.array([[vector[0], vector[1]], [vector[1], vector[2]]])
            np.testing.assert_allclose(
                second, full["second"][i], rtol=2e-11, atol=2e-12
            )
            if count <= 2:
                np.testing.assert_allclose(
                    second, enumerated[i], rtol=2e-11, atol=2e-12
                )
            cases += 1
    print(
        f"Three-moment reduction agrees with full moments at {cases} endpoints "
        "and with short enumerated updates."
    )


def check_interval_arithmetic():
    for left, right in itertools.product(
        [("-3", "-0.1"), ("-1", "2"), ("0.01", "3")], repeat=2
    ):
        x, y = Interval.rational(*left), Interval.rational(*right)
        for a, b in itertools.product(map(Fraction, left), map(Fraction, right)):
            for result, exact in [(x + y, a + b), (x - y, a - b), (x * y, a * b)]:
                assert Fraction(result.lo, SCALE) <= exact <= Fraction(result.hi, SCALE)
            if y.lo > 0 or y.hi < 0:
                result = x / y
                assert Fraction(result.lo, SCALE) <= a / b <= Fraction(result.hi, SCALE)
    for count in [0, 1, 2, 3, 17]:
        value = Interval.rational("0.91", "0.97")
        power, total = value**count, geometric_sum(value, count)
        for endpoint in [Fraction("0.91"), Fraction("0.97")]:
            assert (
                Fraction(power.lo, SCALE)
                <= endpoint**count
                <= Fraction(power.hi, SCALE)
            )
            assert (
                Fraction(total.lo, SCALE)
                <= sum(endpoint**j for j in range(count))
                <= Fraction(total.hi, SCALE)
            )


def print_decompositions():
    cases = [
        ("C1 early", make_model(0.02, "independent"), 0.002, 1000, np.ones(2), 3),
        ("C1 late", make_model(0.02, "independent"), 0.002, 10000, np.ones(2), 3),
        ("C2", dependent_model(0.02, 1), 0.01, 100, np.array([2, 1]), 4),
    ]
    print(
        "Illustrative floating-point risk decompositions: squared bias, "
        "update variance, observation-noise variance, total."
    )
    for name, model, step, count, signal, variance in cases:
        for scaled in (False, True):
            moments = moment_path(
                model,
                np.diag(model["gram"]) ** (0.5 if scaled else 0),
                step if scaled else 4 * step,
                1,
                [count],
                signal,
                variance,
            )
            for objective in ("gram", "rare_second"):
                weight = model[objective]
                bias = moments["bias"][0]
                values = [
                    0.5 * bias @ weight @ bias,
                    0.5 * np.sum(weight * moments["design_covariance"][0]),
                    0.5 * np.sum(weight * moments["noise_covariance"][0]),
                ]
                np.testing.assert_allclose(
                    sum(values), 0.5 * np.sum(weight * moments["second"][0]), atol=1e-12
                )
                print(
                    name,
                    "S" if scaled else "U",
                    objective,
                    *(f"{value:.12g}" for value in [*values, sum(values)]),
                )


def main():
    assert __debug__, "Run ordinary Python without -O."
    check_interval_arithmetic()
    check_against_updates()
    certify_c1()
    certify_c2()
    print_decompositions()


if __name__ == "__main__":
    main()
