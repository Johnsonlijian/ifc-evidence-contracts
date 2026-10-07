# Reproducible runbook

Target: *Three-valued evidence contracts for IFC egress-door and building-information compliance pre-checks*.

## Environment

Python 3.11 or later. Install the pinned plotting dependencies with
`python -m pip install -r requirements.txt` in an isolated environment.

The recorded runs used IfcOpenShell 0.8.5, IfcTester 0.8.5, pandas 3.0.3 and NumPy 2.4.4.

## Step 1 - contract tightness check

```
python scripts/verify_tightness.py
```

Expected verdict: `PASS (T1 exact for monotone, T2 sound, T3 loose counterexample exists)`.
The script uses only the standard library.

## Step 2 - rebuild the figures

```
python scripts/build_figures.py
```

Writes `figures/fig1_mechanism.{pdf,svg}`, `fig2_scorecard.{pdf,svg}`,
`fig3_shared_source.{pdf,svg}` and `fig4_recovery.{pdf,svg}`, with PNG previews under
`figures/preview/`. Every plotted value is read from `inputs/counts.json` and `analysis/`;
the mechanism panel is a schematic of the same numbers. No random seed or stochastic model
is involved.

## Step 3 - validate the pending state on the published benchmark

```
python scripts/hs_pending_validation.py \
    --benchmark-dir <directory with the four HS IFC variants> \
    --ids <adapted two-attribute IDS file> \
    --vendor <directory containing IfcTester 0.8.5> \
    --out results
```

For each of the four published variants the script evaluates the declared contract on the
frozen bytes, removes the `OverallWidth` argument from every `IfcDoor`, evaluates again, and
reopens the original bytes. It records the contract decision per door, the missing source it
names, and what IfcTester 0.8.5 reports on the same masked bytes.

Expected shape of the result, as recorded in `results/`: nine doors per variant; nine pending
obligations naming `IfcDoor.OverallWidth` whenever the source is withheld; both pass variants
failed by the binary toolchain under masking; the intact decision restored in all four
variants. The four variants share one project, so this is a task-transfer check, not a
population sample.

## Inputs

Provider-controlled raw IFC and IDS files are deliberately excluded. Obtain them through
`DATASETS_AND_LINKS.csv`, confirm their current licence and version, then replay. The SHA-256
digests of the exact files used are recorded in `PROVENANCE.md`.

## Boundary

The package supports the bounded computational claims of the manuscript only. It does not
establish legal compliance, engineering truth, field omission prevalence, or operational
savings.
