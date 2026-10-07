"""Masked-width validation of the pending state on published benchmark variants.

For each supplied IFC variant the script:
  1. evaluates the declared evidence contract on the frozen bytes;
  2. removes the OverallWidth argument from every IfcDoor and evaluates again;
  3. reopens the original bytes and evaluates once more.

The contract decision, the source it names when a decision is pending, and what the IDS
toolchain reports on the same masked bytes are all recorded. Nothing is assumed about the
outcome; every count in the output is measured in the run.

Requires IfcOpenShell and IfcTester (see the runbook). Point --vendor at a directory that
contains the IfcTester package when it is not installed in the active environment.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

MIN_MM = 900.0


def split_args(s: str) -> list[str]:
    parts, depth, cur, in_str = [], 0, [], False
    for ch in s:
        if ch == "'":
            in_str = not in_str
        if not in_str:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            elif ch == "," and depth == 0:
                parts.append("".join(cur)); cur = []; continue
        cur.append(ch)
    parts.append("".join(cur))
    return parts


def mask_overall_width(text: str) -> tuple[str, list[int]]:
    """Replace the OverallWidth argument of every IFCDOOR record with $ (absent)."""
    out_lines, masked = [], []
    for line in text.splitlines():
        m = re.match(r"^#(\d+)\s*=\s*IFCDOOR\s*\((.*)\)\s*;\s*$", line.strip(), re.I)
        if not m:
            out_lines.append(line); continue
        step_id = int(m.group(1))
        args = split_args(m.group(2))
        if len(args) >= 10 and args[9].strip() != "$":
            args[9] = "$"
            masked.append(step_id)
            out_lines.append(f"#{step_id}= IFCDOOR({','.join(args)});")
        else:
            out_lines.append(line)
    return "\n".join(out_lines) + "\n", masked


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--benchmark-dir", required=True,
                    help="directory containing the IFC variants to test")
    ap.add_argument("--ids", required=True, help="adapted IDS file for the binary comparison")
    ap.add_argument("--vendor", default=None,
                    help="directory containing the IfcTester package, if not installed")
    ap.add_argument("--min-mm", type=float, default=MIN_MM)
    ap.add_argument("--out", default="results")
    args = ap.parse_args()

    if args.vendor:
        sys.path.insert(0, str(Path(args.vendor).resolve()))

    import ifcopenshell
    import ifcopenshell.util.unit as units
    from ifctester import ids

    bench = Path(args.benchmark_dir).resolve()
    ids_path = Path(args.ids).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    variants = sorted(p for p in bench.glob("*.ifc"))

    def contract_eval(path: Path) -> list[dict]:
        model = ifcopenshell.open(str(path))
        scale = units.calculate_unit_scale(model)
        rows = []
        for door in model.by_type("IfcDoor"):
            raw = door.OverallWidth
            if raw is None:
                decision = "pending"
            else:
                decision = "pass" if raw * scale * 1000.0 >= args.min_mm else "fail"
            rows.append({"step_id": door.id(), "global_id": door.GlobalId,
                         "decision": decision, "named_source": "IfcDoor.OverallWidth"})
        return rows

    def binary_eval(path: Path) -> dict:
        model = ifcopenshell.open(str(path))
        doc = ids.open(str(ids_path), validate=True)
        doc.validate(model)
        return {"document_passes": all(bool(s.status) for s in doc.specifications),
                "specs": [{"name": s.name, "status": bool(s.status)} for s in doc.specifications]}

    report, detail = {"min_mm": args.min_mm, "benchmark_dir": str(bench), "variants": {}}, []
    for src in variants:
        raw = src.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        masked_text, masked_ids = mask_overall_width(raw.decode("utf-8", "replace"))
        masked_path = out / f"{src.stem}__width_masked.ifc"
        masked_path.write_text(masked_text, encoding="utf-8")

        ic, mc, rc = contract_eval(src), contract_eval(masked_path), contract_eval(src)
        ib, mb = binary_eval(src), binary_eval(masked_path)

        def tally(rows):
            t = {"pass": 0, "fail": 0, "pending": 0}
            for r in rows:
                t[r["decision"]] += 1
            return t

        first = {r["step_id"]: r["decision"] for r in ic}
        report["variants"][src.name] = {
            "sha256": sha, "doors": len(ic), "masked_step_ids": masked_ids,
            "intact_contract": tally(ic), "masked_contract": tally(mc),
            "restored_contract": tally(rc),
            "restored_equals_intact": all(r["decision"] == first[r["step_id"]] for r in rc),
            "every_pending_names_source": all(r["named_source"] == "IfcDoor.OverallWidth"
                                              for r in mc if r["decision"] == "pending"),
            "intact_binary": ib, "masked_binary": mb,
            "binary_fails_after_masking": ib["document_passes"] and not mb["document_passes"],
        }
        for r in ic:
            detail.append({"variant": src.name, "sha256": sha, "step_id": r["step_id"],
                           "global_id": r["global_id"], "intact": r["decision"],
                           "masked": next(x["decision"] for x in mc if x["step_id"] == r["step_id"]),
                           "restored": next(x["decision"] for x in rc if x["step_id"] == r["step_id"])})

    (out / "hs_pending_validation.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8")
    if detail:
        with (out / "hs_pending_validation.csv").open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(detail[0])); w.writeheader(); w.writerows(detail)

    for name, v in report["variants"].items():
        print(f"{name}: doors={v['doors']} intact={v['intact_contract']} "
              f"masked={v['masked_contract']} restored_ok={v['restored_equals_intact']} "
              f"binary_fails_after_masking={v['binary_fails_after_masking']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
