"""Audit the repository's transcription of Kripka (2004), Table 4, method 6.

The hosted source prints A5=2.2; the repository stores 2.1. This reports both
under the unchanged reference model, retaining the rejected repository vector.
"""

import argparse
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from truss.independent import check
from truss.model import load
from truss.solver import Solver
from truss.verify import candidate, verify


BASE = "d3a2a3da00c7cb329474470f9e112f0ac0d32cb1"
MODEL_SHA256 = "5291c9023163d70b696d644923fc2ad94bcaf07984a6f037986f13035ef42328"
SEED = "232b9fe2013342d0308b72a1556a8437"
LOWER, UPPER = Decimal("484.325"), Decimal("484.335")
FIELDS = (
    "mass_lbm", "displacements", "forces", "reactions",
    "stress_utilization", "displacement_utilization", "buckling_utilization",
)


def mass_decimal(areas):
    """Group-length formula derived directly from the frozen geometry (50 digits).

    Decimal square roots provide a separate numerical cross-check, not interval
    certification. Group numbering in the report is one based.
    """
    with localcontext() as ctx:
        ctx.prec = 50
        a = [Decimal(str(value)) for value in areas]
        return (
            Decimal("7.5") * a[0]
            + 5 * Decimal(109).sqrt() * a[1]
            + 5 * Decimal(73).sqrt() * a[2]
            + 15 * (a[3] + a[4])
            + 5 * Decimal(210).sqrt() * (a[5] + a[6])
            + 5 * Decimal(114).sqrt() * a[7]
        )


def audit():
    b = load("25bar")
    assert b["sha256"] == MODEL_SHA256, "This audit is specific to the pinned model"
    source_path = Path(__file__).with_name("source-transcription.json")
    source = json.loads(source_path.read_text())
    locked_sources = json.loads((ROOT / "docs/source-lock.json").read_text())["files"]
    for name in ("table2", "table3", "table4", "figure2"):
        assert any(item["url"] == source[name]["url"] and item["sha256"] == source[name]["sha256"]
                   for item in locked_sources), f"Source lock mismatch: {name}"
    x = b["published_disputed"]["areas"]
    assert x == [0.1, 0.4, 3.4, 0.1, 2.1, 1, 0.4, 3.4]
    assert b["published_disputed"]["mass_lbm"] == 484.33
    solver = Solver(b, "reference")

    def evaluate(areas):
        primary = solver.evaluate(areas, full=True)
        other = check(b, areas, "reference")
        differences = {}
        for field in FIELDS:
            p, q = np.asarray(primary[field]), np.asarray(other[field])
            differences[field] = float(np.max(abs(p - q)) / max(1.0, float(np.max(abs(p)))))
        assert max(differences.values()) <= b["tolerance"]["agreement_relative"]
        assert primary["valid"] == other["valid"], "Solver verdict disagreement"
        mass = mass_decimal(areas)
        assert abs(primary["mass_lbm"] - float(mass)) < 1e-9
        assert abs(other["mass_lbm"] - float(mass)) < 1e-9
        summary = {
            "mass_lbm_decimal": str(mass),
            "matches_method6_mass_bin": LOWER <= mass < UPPER,
            "primary_valid": primary["valid"],
            "second_valid": other["valid"],
            "primary_displacement_utilization": primary["displacement_utilization"],
            "second_displacement_utilization": other["displacement_utilization"],
            "primary_stress_utilization": primary["stress_utilization"],
            "second_stress_utilization": other["stress_utilization"],
            "max_solver_relative_difference": max(differences.values()),
        }
        full = {
            "areas": areas,
            "primary": primary,
            "second": other,
            "solver_relative_differences": differences,
            **summary,
        }
        return summary, full

    original, original_full = evaluate(x)
    baseline, baseline_full = evaluate(b["published"]["areas"])
    assert source["table4"]["method4"]["areas"] == b["published"]["areas"]
    assert not original["primary_valid"] and not original["matches_method6_mass_bin"]
    assert baseline["primary_valid"]
    assert abs(float(baseline["mass_lbm_decimal"]) - b["published"]["mass_lbm"]) < 0.005

    rows, witnesses, distances = [], [], []
    for group, old_area in enumerate(x):
        for new_area in b["catalog"]:
            if new_area == old_area:
                continue
            areas = list(x)
            areas[group] = new_area
            summary, full = evaluate(areas)
            change = {"group": group + 1, "old_area_in2": old_area, "new_area_in2": new_area}
            rows.append({**change, **summary})
            if summary["matches_method6_mass_bin"]:
                witnesses.append({**change, **full})
            else:
                mass = Decimal(summary["mass_lbm_decimal"])
                distances.append(max(LOWER - mass, mass - UPPER))

    # Positive and rejection controls make an altered interpretation fail loudly.
    assert len(rows) == 8 * (30 - 1) == 232
    assert [(w["group"], w["new_area_in2"]) for w in witnesses] == [(1, 0.3), (4, 0.2), (5, 2.2)]
    assert [w["group"] for w in witnesses if w["primary_valid"]] == [5]
    assert [w["group"] for w in witnesses if w["second_valid"]] == [5]
    source_witness = witnesses[2]
    assert source_witness["areas"] == source["table4"]["method6"]["areas"]
    winner_path = ROOT / "results/25bar-reference-winner.json"
    winner = json.loads(winner_path.read_text())
    assert winner["areas"] == source_witness["areas"]
    assert winner["model_sha256"] == b["sha256"] and winner["profile"] == "reference"
    table_rows = []
    for method in range(1, 7):
        printed = source["table4"][f"method{method}"]
        _, full = evaluate(printed["areas"])
        reported = Decimal(printed["reported_weight_lb"])
        mass = Decimal(full["mass_lbm_decimal"])
        full.update(source_method=method, reported_weight_lb=str(reported),
                    mass_minus_reported_lbm=str(mass - reported),
                    matches_own_reported_weight=reported-Decimal("0.005") <= mass < reported+Decimal("0.005"))
        assert full["matches_own_reported_weight"] == (method != 3)
        assert full["primary_valid"] == (method != 3)
        table_rows.append(full)
    for witness in [original_full, baseline_full, *witnesses, *table_rows]:
        try:
            verify(candidate(b, "reference", witness["areas"]))
        except ValueError as error:
            assert not witness["primary_valid"]
            assert str(error) == "primary rejection: constraint violation"
            witness["official_verifier"] = str(error)
        else:
            assert witness["primary_valid"]
            witness["official_verifier"] = "accepted"
    return {
        "base_commit": BASE,
        "seed": SEED,
        "task": "source-audit",
        "evidence_level": "author-checked",
        "case": "25bar",
        "profile": "reference",
        "model_sha256": b["sha256"],
        "source_transcription_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        "replay_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "environment": {"python": platform.python_version(), "platform": platform.platform(),
                        "numpy": np.__version__, "scipy": scipy.__version__},
        "reported_mass_lbm": "484.33",
        "mass_match_interval_lbm": {"lower_inclusive": str(LOWER), "upper_exclusive": str(UPPER)},
        "domain": "Exactly one of eight group areas replaced by another of 30 frozen catalogue values",
        "replacements_checked": len(rows),
        "feasible_replacements": sum(row["primary_valid"] for row in rows),
        "mass_matches": len(witnesses),
        "feasible_mass_matches": sum(w["primary_valid"] for w in witnesses),
        "closest_nonmatching_mass_distance_from_interval_lbm": str(min(distances)),
        "repository_disputed_control": original_full,
        "source_transcribed_method6": source_witness,
        "existing_winner_comparison": {
            "path": str(winner_path.relative_to(ROOT)),
            "sha256": hashlib.sha256(winner_path.read_bytes()).hexdigest(),
            "areas_equal_source_transcription": winner["areas"] == source_witness["areas"],
        },
        "selected_method4_control": baseline_full,
        "source_table4_all_methods": table_rows,
        "mass_matching_witnesses": witnesses,
        "all_single_group_replacements": rows,
        "limitations": [
            "The hosted Table 4 directly prints A5=2.2; no correction to the paper is proposed.",
            "Any change to the frozen repository transcription requires maintainer adjudication.",
            "No claim about changes to two or more groups, other models, or other error mechanisms.",
            "Float64 structural checks and 50-digit mass arithmetic are not interval certificates.",
            "Both structural implementations originated with the project; no external solver review.",
            "Reference profile excludes buckling and physical-transfer obligations.",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write the audit JSON to this path; default stdout")
    args = parser.parse_args()
    report = audit()
    text = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(text)
        print(f"PASS: {report['replacements_checked']} replacements; {report['mass_matches']} mass matches; "
              f"{report['feasible_mass_matches']} feasible mass match. Wrote {args.output}")
    else:
        print(text, end="")
