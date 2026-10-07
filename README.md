# Three-valued evidence contracts for IFC compliance pre-checking

Reproducibility package for the manuscript *Three-valued evidence contracts for IFC egress-door and building-information compliance pre-checks*.

A compliance failure should mean that the required evidence was read and did not satisfy the
requirement. In an IFC model the same value may sit on an occurrence, on a type reached
through `IfcRelDefinesByType`, on a host, or once on a shared building object, and a checker
that does not traverse the right path reports the fact as absent. This package contains the
derived ledgers, the executable evidence contract, the analysis code and the figure sources
behind the reported results.

## What is here

| Path | Contents |
|---|---|
| `contract/` | Machine-readable evidence contract: the four executable rules (entity, admissible path, value predicate, engineering action when pending) |
| `inputs/` | Frozen mask totals used by Figure 2 |
| `analysis/` | Frozen policy-comparison ledgers used by Figure 4 |
| `results/` | Masked-width validation on the published HS benchmark variants |
| `cold_start_2026-09-21/` | Derived quality-assurance artefacts from a clean-directory raw-IFC replay |
| `scripts/` | Figure rebuild, contract tightness check, benchmark validation |
| `figures/` | The four vector figures, as PDF, SVG and PNG preview |

## Not here

No raw third-party IFC or IDS file is redistributed. `DATASETS_AND_LINKS.csv` lists every
source with its provider and access terms. A `.gitignore` excludes `*.ifc` and `*.ids` so a
local run cannot commit them by accident.

## Quick start

```bash
python -m pip install -r requirements.txt
python scripts/verify_tightness.py          # mathematical smoke check, prints PASS
python scripts/build_figures.py             # rebuilds figures/ from the frozen ledgers
```

Re-running the benchmark validation additionally needs IfcOpenShell 0.8.5, IfcTester 0.8.5,
and local copies of the benchmark files obtained through `DATASETS_AND_LINKS.csv`.

## Scope

Everything here concerns checker behaviour under declared contracts on fixed public models.
Nothing here establishes legal compliance, engineering ground truth, field omission rates,
industry prevalence, or cost and time savings.
