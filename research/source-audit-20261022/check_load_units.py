"""Separate Table 3 load-unit diagnostic; never a frozen-model result.

Only the loads change. Geometry, areas, material and tolerances remain those of
the frozen imperial reference model. This is not a complete SI reconstruction.
"""

import argparse
from copy import deepcopy
from decimal import Decimal
import hashlib
import itertools
import json
from pathlib import Path
import sys

import numpy as np

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(ROOT / "src"))

from truss.independent import check
from truss.model import load
from truss.solver import Solver


def audit_loads():
    original = load("25bar")
    assert original["sha256"] == "5291c9023163d70b696d644923fc2ad94bcaf07984a6f037986f13035ef42328"
    source_path = PACKAGE / "source-transcription.json"
    source = json.loads(source_path.read_text(), parse_float=Decimal)
    newtons_per_lbf = Decimal(source["force_conversion"]["newtons_per_lbf"])
    assert newtons_per_lbf == Decimal("0.45359237") * Decimal("9.80665")
    printed = source["table3"]["nodal"]
    nonzero = [(i, j) for i, row in enumerate(printed) for j in range(1, 4) if row[j] != 0]
    assert len(nonzero) == 7

    def model(signs=None):
        nodal = deepcopy(printed)
        if signs is not None:
            for (i, j), sign in zip(nonzero, signs):
                nodal[i][j] += sign * Decimal("0.005")
        diagnostic = deepcopy(original)
        del diagnostic["sha256"]
        diagnostic["id"] = "25bar-table3-newtons-diagnostic-v1"
        diagnostic["version"] = "source-unit-diagnostic-v1"
        diagnostic["loads"] = [{"name": "Table 3 newtons converted using standard lbf",
                                 "nodal": [[row[0], *[float(Decimal(v) / newtons_per_lbf) for v in row[1:]]]
                                           for row in nodal]}]
        return diagnostic

    def evaluate(b, areas):
        p = Solver(b, "reference").evaluate(areas, full=True)
        q = check(b, areas, "reference")
        differences = []
        for field in ("mass_lbm", "displacements", "forces", "reactions",
                      "stress_utilization", "displacement_utilization", "buckling_utilization"):
            a, c = np.asarray(p[field]), np.asarray(q[field])
            differences.append(float(np.max(abs(a - c)) / max(1.0, float(np.max(abs(a))))))
        assert max(differences) <= original["tolerance"]["agreement_relative"]
        assert p["valid"] == q["valid"]
        assert p["equilibrium_relative"] <= original["tolerance"]["equilibrium_relative"]
        for field in ("equilibrium_relative", "global_force_balance_relative",
                      "global_moment_balance_relative", "energy_relative"):
            assert q[field] <= original["tolerance"]["equilibrium_relative"]
        return {"primary": p, "second": q, "max_solver_relative_difference": max(differences)}

    center_model = model()
    cases = []
    for name in ("method4", "method6"):
        areas = [float(a) for a in source["table4"][name]["areas"]]
        frozen = evaluate(original, areas)
        center = evaluate(center_model, areas)
        corners = []
        for signs in itertools.product((-1, 1), repeat=len(nonzero)):
            result = evaluate(model(signs), areas)
            corners.append({
                "signs": signs,
                "primary_valid": result["primary"]["valid"],
                "second_valid": result["second"]["valid"],
                "primary_displacement_utilization": result["primary"]["displacement_utilization"],
                "second_displacement_utilization": result["second"]["displacement_utilization"],
                "primary_node2_y_in": result["primary"]["displacements"][0][4],
                "second_node2_y_in": result["second"]["displacements"][0][4],
                "max_solver_relative_difference": result["max_solver_relative_difference"],
            })
        assert frozen["primary"]["valid"]
        assert center["primary"]["valid"] == (name == "method4")
        assert len(corners) == 128
        assert all(row["primary_valid"] == (name == "method4") for row in corners)
        # Linear node-2 Y response is negative and beyond the limit at every
        # method-6 corner, so convex combinations cannot rescue it in this box.
        if name == "method6":
            for row in corners:
                for engine in ("primary", "second"):
                    assert row[f"{engine}_node2_y_in"] < -0.35 * (1 + original["tolerance"]["constraint"])
        cases.append({"source_column": name, "areas": areas, "frozen_reference": frozen,
                      "literal_table3_center": center, "rounding_corners": corners,
                      "corner_displacement_utilization_range": [
                          min(row["primary_displacement_utilization"] for row in corners),
                          max(row["primary_displacement_utilization"] for row in corners)]})

    return {
        "evidence_level": "author-checked",
        "scope": "Changed-load diagnostic only; not a frozen-model result or a complete SI reconstruction",
        "parent_frozen_model_sha256": original["sha256"],
        "source_transcription_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "newtons_per_lbf": str(newtons_per_lbf),
        "center_model": center_model,
        "center_model_sha256": hashlib.sha256(json.dumps(center_model, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "rounding_assumption": "Seven nonzero Table 3 forces independently within +/-0.005 N; listed zeros treated as exactly absent loads",
        "nonzero_coordinate_order": [{"node": printed[i][0], "axis": "xyz"[j-1]} for i, j in nonzero],
        "cases": cases,
        "limitations": ["The source does not specify a rounding algorithm or a force-conversion convention.",
                        "All non-load inputs retain their frozen imperial interpretation.",
                        "Float64 evaluations are not interval-certified structural bounds.",
                        "No inference about the author's intended loads, physical safety or optimum."]
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit_loads()
    text = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(text)
        print(f"PASS: two source vectors, 128 rounding corners each. Wrote {args.output}")
    else:
        print(text, end="")
