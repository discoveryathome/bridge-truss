"""Recheck the printed method-3 row and a bounded, diagnostic catalogue census.

Run with the repository's pinned environment. JSON is written to stdout only.
No benchmark, verifier, stored result or accepted frontier is modified.
"""
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
from truss.independent import check
from truss.model import load
from truss.solver import Solver
from truss.verify import candidate, verify

FIELDS = (
    "mass_lbm", "forces", "displacements", "reactions",
    "stress_utilization", "displacement_utilization", "buckling_utilization",
)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    source = json.loads((HERE / "source.json").read_text())
    model = load(source["case"])
    require(model["sha256"] == source["model_sha256"], "Unexpected frozen model")
    profile = source["profile"]
    solver = Solver(model, profile)
    printed = source["areas_in2"]
    lower, upper = source["reporting_window_lbm"]
    tolerance = model["tolerance"]["agreement_relative"]

    def evaluate(areas):
        primary = solver.evaluate(areas, full=True)
        independent = check(model, areas, profile)
        require(primary["valid"] == independent["valid"], "Validity disagreement")
        errors = {}
        for field in FIELDS:
            a = np.asarray(primary[field])
            b = np.asarray(independent[field])
            require(a.shape == b.shape, f"Shape disagreement: {field}")
            require(np.isfinite(a).all() and np.isfinite(b).all(),
                    f"Nonfinite result: {field}")
            errors[field] = float(np.max(abs(a - b))) / max(1., float(np.max(abs(a))))
            require(errors[field] <= tolerance, f"Solver disagreement: {field}")
        return dict(areas_in2=list(areas), primary=primary, independent=independent,
                    solver_relative_differences=errors)

    original = evaluate(printed)
    require(not original["primary"]["valid"], "Printed rejection control changed")
    require(original["primary"]["displacement_utilization"] >
            1 + model["tolerance"]["constraint"], "Displacement rejection changed")
    require(not lower <= original["primary"]["mass_lbm"] < upper,
            "Printed mass discrepancy disappeared")

    census = []
    matching = []
    for group, before in enumerate(printed):
        for area in model["catalog"]:
            if area == before:
                continue
            areas = printed.copy()
            areas[group] = area
            result = evaluate(areas)
            p = result["primary"]
            row = dict(group=group + 1, before=before, after=area,
                       mass_lbm=p["mass_lbm"], valid=p["valid"],
                       displacement_utilization=p["displacement_utilization"],
                       max_solver_relative_difference=max(
                           result["solver_relative_differences"].values()))
            census.append(row)
            if lower <= p["mass_lbm"] < upper:
                matching.append(dict(change=row, result=result))
    require(len(census) == 8 * 29, "Incomplete one-group census")
    require([(m["change"]["group"], m["change"]["after"]) for m in matching]
            == [(2, 1.9)], "One-group mass-match finding changed")
    match = matching[0]["result"]
    require(match["primary"]["valid"], "Mass-matching diagnostic is infeasible")
    # The unchanged project verifier independently enforces acceptance for this
    # feasible diagnostic; the printed infeasible row remains in the output.
    verify(candidate(model, profile, match["areas_in2"]))

    # Equal total lengths in groups 6 and 7 make their area redistribution
    # mass-neutral. These controls disprove uniqueness beyond the stated census.
    alternatives = []
    for a6, a7, expected_valid in [(0.9, 2.0, True), (2.1, 0.8, False)]:
        areas = match["areas_in2"].copy()
        areas[5:7] = [a6, a7]
        result = evaluate(areas)
        p = result["primary"]
        require(lower <= p["mass_lbm"] < upper, "Mass-neutral control changed")
        require(p["valid"] == expected_valid, "Feasibility ambiguity control changed")
        alternatives.append(result)

    # Positive control is the frozen reference comparator, not a new record.
    baseline = verify(candidate(model, profile, model["published"]["areas"]))
    output = dict(
        case=model["id"], profile=profile, model_sha256=model["sha256"],
        evidence_level="author-checked; two separately coded existing solvers",
        source_table_sha256=source["table_sha256"],
        reporting_window_lbm=[lower, upper],
        printed=original, one_group_matches=matching,
        mass_neutral_controls=alternatives,
        census_summary=dict(evaluated=len(census),
                            feasible=sum(r["valid"] for r in census),
                            mass_matches=len(matching),
                            max_solver_relative_difference=max(
                                r["max_solver_relative_difference"] for r in census)),
        census=census,
        frozen_reference_positive_control=dict(
            areas_in2=model["published"]["areas"],
            mass_lbm=baseline["primary"]["mass_lbm"],
            valid=baseline["primary"]["valid"]),
        limitations=["A mass match does not establish a historical correction",
                     "Structural results use the frozen float64 model, not interval arithmetic",
                     "No new optimum, frontier result or physical suitability is claimed"],
    )
    print(json.dumps(output, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
