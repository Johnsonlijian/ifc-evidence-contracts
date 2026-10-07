# Provenance

## Software

| Component | Version |
|---|---|
| Python | 3.11 |
| IfcOpenShell | 0.8.5 |
| IfcTester | 0.8.5 |
| pandas | 3.0.3 |
| NumPy | 2.4.4 |
| matplotlib | 3.10.9 |

## Input identity

Provider-controlled IFC and IDS files are not redistributed. Each source is listed in
`DATASETS_AND_LINKS.csv` with its provider and access terms. The SHA-256 digests of the exact
bytes used in the recorded runs are:

| Input | SHA-256 |
|---|---|
| Custom test model (escape-route analysis) | `29945f654c636d758a95b66eb0e107ec35afc7e1c7857a7ff652586e7728ba29` |
| Real-world test model (escape-route analysis) | `759c5e5f516eb23eb4a9a5f113e626e35e995029ca153ee759ac94a59043652e` |
| Extended IDS archive | `921429dd16b3ad098a90f243deab88d5df91a8379b20f8d12e81171e2926be1b` |
| DigitalHub architectural model | `19d7d02d53c2b88e86890ee236297b12bbb0f7748030cd32ff6a22762e9966bb` |

The four published HS benchmark variants used for the masked-width validation are identified
by digest in `results/hs_pending_validation.json`.

## Derivation

`analysis/` and `inputs/` are frozen ledgers produced by the contract evaluator and the
masking protocol described in the manuscript. `cold_start_2026-09-21/` records a clean
directory replay from raw IFC bytes to results, including quality-assurance artefacts.
`results/` was produced by `scripts/hs_pending_validation.py` from the frozen benchmark bytes.

No derived file here reproduces a raw third-party asset. Property-level evidence extracts are
derived observations about public models, kept so that the reported route effects can be
recomputed without redistributing the models themselves.
