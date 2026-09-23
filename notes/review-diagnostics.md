# Diagnostics added after independent review

September 23, 2026. These post hoc analyses support the manuscript revision.
They preserve every frozen candidate, selection, summary, and numerical gate
violation. They do not constitute a prospective study or higher-precision
replay.

## Numerical discrepancies and affected claims

The script maps all 63 records in the four-rule study's `audit.json` to the
synthetic manifest. It identifies each selected candidate, its original rate,
batch, stop, validation objective, search, and archived test risks. The 60
selected-prediction records occur in four laws, all in the centered/fitted arm
and with empty rare validation groups. Repeated queries can select the same
endpoint. The other three records concern failure times and a batch-one
trajectory replay in rarer C2, replication zero.

For the primary expanded search with original stops, aggregate selection, and
cap 2048, flagged selections account for essentially all of four mean rare
risks: damping in rarer C1, and SD, damping, and variance scaling in rarer C2.
Appendix H reports their contributions without deleting or correcting any
observation. The manuscript no longer relies on those extreme magnitudes or
rankings for normalization conclusions. A query without a flagged prediction
check is not a blanket certificate for its law or trajectories.

The original practical study's 160-digit investigation retains its original
scope. It does not certify these expanded candidate searches. Their precise
risks and selections remain unresolved in transformed or higher-precision
arithmetic. Mushroom replay and the theorem certificates have separate evidence.

## Prediction clipping

The diagnostic reconstructs the saved final Mushroom selections at both sample
sizes, cap 8192, original stopping checkpoints, centered predictors, and a
fitted intercept. It retains all 32 partitions, all four rules, and both
validation objectives. Vocabulary construction and data partitions come from the
frozen data loader. Raw reconstructed losses must match the saved test losses.

Predictions are clipped to the known label interval `[0,1]`. The script checks
the pointwise squared-loss inequality and the resulting half-loss bound of one
half. No model is retrained, and the original unclipped validation scores still
determine selection. Thus this is a diagnostic of postprocessing the selected
predictors, not a comparison after selecting with clipped predictions.

Clipping greatly reduces several raw aggregate losses. In the larger-sample
rare-validation comparison, it reverses the descriptive aggregate mean ordering
of SD and unscaled training. Damping retains the smallest mean of both losses
under both validation objectives in that larger-sample comparison. These mean
orderings alone do not establish uniform superiority or statistical
significance. The artifact retains per-partition pairs, MCSEs, medians, 95th
percentiles, maxima, and the smaller-sample results.

## Reproduction

Inside `devenv shell`, run:

```sh
make reproduce-review-diagnostics
make check-review-diagnostics
```

The [script](../scripts/review_diagnostics.py) writes
[`summary.json`](../results/review-diagnostics/summary.json) and
[`tables.tex`](../results/review-diagnostics/tables.tex). Reproduction also
updates the two marked, generated tables inline in `paper/main.tex`. The check
verifies both saved artifacts and their manuscript copies. The JSON includes
hashes of the script, runtime lock, data loader, source data, manifests, audit,
summaries, and every archive read. No frozen file is written.
