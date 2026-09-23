# UCI Mushroom source data

Unmodified `agaricus-lepiota.data` and `agaricus-lepiota.names`, extracted from
[the UCI archive](https://archive.ics.uci.edu/static/public/73/mushroom.zip) on
September 16, 2026. Dataset attribution: *Mushroom* (1981), UCI Machine Learning
Repository, [DOI 10.24432/C5959T](https://doi.org/10.24432/C5959T). The
[repository record](https://archive.ics.uci.edu/dataset/73/mushroom) licenses
the dataset under [Creative Commons Attribution
4.0](https://creativecommons.org/licenses/by/4.0/). The data describe
hypothetical samples derived from a field guide. The recorded poisonous class
includes unknown edibility. The data-loading code in
`experiments/common/data.py` defines the one-hot representation, split rules,
target, and subgroup.

Experiments read these local files without downloading or replacing them.
