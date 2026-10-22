#!/usr/bin/env python3
"""Exact mass audit; standard library only, no structural solver imports."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from math import isqrt
from pathlib import Path
import json
import sys


MODEL_SHA256 = "5291c9023163d70b696d644923fc2ad94bcaf07984a6f037986f13035ef42328"
AREAS = tuple(map(F, ("0.1", "1.8", "2.6", "0.1", "0.1", "0.8", "2.1", "2.6")))
WINDOW = (F("562.925"), F("562.935"))  # Explicit half-open convention.
SCALE = 10**30


def sqrt_bounds(q):
    """Enclose sqrt(q) with rationals; exact roots get zero-width intervals."""
    assert q >= 0
    n, d = q.numerator, q.denominator
    k = isqrt((n * SCALE * SCALE) // d)
    lo = F(k, SCALE)
    hi = lo if k * k * d == n * SCALE * SCALE else F(k + 1, SCALE)
    assert lo * lo <= q <= hi * hi
    assert 0 <= hi - lo <= F(1, SCALE)
    return lo, hi


def decimal_bound(q, up=False, places=30):
    """Format outwards using integer division, never binary floating point."""
    scale = 10**places
    n, d = q.numerator * scale, q.denominator
    k = -((-n) // d) if up else n // d
    sign = "-" if k < 0 else ""
    k = abs(k)
    return f"{sign}{k // scale}.{k % scale:0{places}d}"


def interval_record(bounds):
    lo, hi = bounds
    return {
        "lower_fraction": str(lo),
        "upper_fraction": str(hi),
        "decimal_outward_bounds": [decimal_bound(lo), decimal_bound(hi, up=True)],
    }


def classify(bounds):
    lo, hi = bounds
    if hi < WINDOW[0] or lo >= WINDOW[1]:
        return "excluded"
    if lo >= WINDOW[0] and hi < WINDOW[1]:
        return "inside"
    raise AssertionError("Interval meets a rounding boundary: increase SCALE")


def main():
    if not __debug__:
        raise SystemExit("Run without -O: the arithmetic audit uses assertion self-checks")
    path = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parents[2] / "benchmarks/25bar.json"
    if len(sys.argv) > 2:
        raise SystemExit("usage: python3 check_mass_exact.py [25bar.json]")
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    if digest != MODEL_SHA256:
        raise SystemExit(f"Frozen model SHA-256 mismatch: {digest}")
    model = json.loads(raw, parse_float=F)
    nodes = [tuple(map(F, row)) for row in model["nodes"]]
    density = F(model["density_lbm_in3"])
    catalog = tuple(map(F, model["catalog"]))
    assert density == F(1, 10)
    assert len(catalog) == len(set(catalog)) == 30
    assert all(a in catalog and a > 0 for a in AREAS)
    assert all(a > 0 for a in catalog)
    assert len(model["members"]) == len(model["groups"]) == 25
    assert set(model["groups"]) == set(range(8))

    lengths = [[F(0), F(0)] for _ in AREAS]
    squared = [Counter() for _ in AREAS]
    member_ids = [[] for _ in AREAS]
    for member_id, ((i, j), g) in enumerate(zip(model["members"], model["groups"]), 1):
        q = sum((x - y) ** 2 for x, y in zip(nodes[i - 1], nodes[j - 1]))
        assert q > 0
        lo, hi = sqrt_bounds(q)
        lengths[g][0] += lo
        lengths[g][1] += hi
        squared[g][q] += 1
        member_ids[g].append(member_id)

    def mass(areas):
        return tuple(density * sum(a * length[end] for a, length in zip(areas, lengths)) for end in (0, 1))

    # Check the printed closed-form group lengths against coordinate-derived q.
    # G = [75, 50*sqrt(109), 50*sqrt(73), 150, 150,
    #      50*sqrt(210), 50*sqrt(210), 50*sqrt(114)].
    forms = [(75, 1), (50, 109), (50, 73), (150, 1), (150, 1), (50, 210), (50, 210), (50, 114)]
    for counts, (coefficient, radicand) in zip(squared, forms):
        assert len(counts) == 1
        q, count = next(iter(counts.items()))
        assert count * count * q == coefficient * coefficient * radicand

    original = mass(AREAS)
    assert classify(original) == "excluded"
    checked = [0] * 8
    matches = []
    excluded = []
    for g in range(8):
        for area in catalog:
            if area == AREAS[g]:
                continue
            trial = list(AREAS)
            trial[g] = area
            assert sum(a != b for a, b in zip(trial, AREAS)) == 1
            bounds = mass(trial)
            checked[g] += 1
            row = {
                "group_one_based": g + 1,
                "old_area_in2": str(AREAS[g]),
                "new_area_in2": str(area),
                "areas_in2": list(map(str, trial)),
                "mass_lbm": interval_record(bounds),
            }
            if classify(bounds) == "inside":
                matches.append(row)
            else:
                gap = WINDOW[0] - bounds[1] if bounds[1] < WINDOW[0] else bounds[0] - WINDOW[1]
                assert gap > 0
                excluded.append((gap, row))
    assert checked == [29] * 8
    assert len(matches) + len(excluded) == 232
    assert [(r["group_one_based"], r["new_area_in2"]) for r in matches] == [(2, "19/10")]

    # Construct a family, without claiming to exhaust two-or-more-entry changes.
    assert squared[3] == squared[4] and squared[5] == squared[6]
    family = [(a, AREAS[5] + AREAS[6] - a) for a in catalog if AREAS[5] + AREAS[6] - a in catalog]
    assert len(family) == 26
    example = tuple(map(F, ("0.1", "1.9", "2.6", "0.1", "0.1", "0.9", "2.0", "2.6")))
    match_areas = tuple(map(F, matches[0]["areas_in2"]))
    assert all(a in catalog for a in example)
    assert sum(a != b for a, b in zip(example, AREAS)) == 3
    assert example[5] + example[6] == match_areas[5] + match_areas[6]
    assert mass(example) == mass(match_areas)
    for a, b in family:
        trial = list(match_areas)
        trial[5:7] = [a, b]
        assert mass(trial) == mass(match_areas)

    # Small arithmetic self-checks include exact roots and an irrational root.
    assert sqrt_bounds(F(9, 4)) == (F(3, 2), F(3, 2))
    assert sqrt_bounds(F(0)) == (F(0), F(0))
    assert sqrt_bounds(F(2))[0] ** 2 < 2 < sqrt_bounds(F(2))[1] ** 2
    assert decimal_bound(F(1, 3), places=2) == "0.33"
    assert decimal_bound(F(1, 3), up=True, places=2) == "0.34"
    assert classify((WINDOW[0], WINDOW[0])) == "inside"
    assert classify((WINDOW[1], WINDOW[1])) == "excluded"
    closest_gap, closest = min(excluded, key=lambda item: item[0])
    result = {
        "audit_kind": "author-internal AI arithmetic check; not external scientific review",
        "model_file": path.name,
        "model_sha256": digest,
        "script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "sqrt_enclosure_scale": str(SCALE),
        "density_lbm_in3": str(density),
        "rounding_window_lbm": "[562.925, 562.935)",
        "groups": [
            {"group_one_based": g + 1, "member_ids": member_ids[g],
             "squared_member_lengths_in2": {str(q): count for q, count in squared[g].items()},
             "exact_total_length_in": f"{forms[g][0]}*sqrt({forms[g][1]})"}
            for g in range(8)
        ],
        "printed_areas_in2": list(map(str, AREAS)),
        "zero_change_mass_lbm": interval_record(original),
        "reported_minus_zero_change_lbm": interval_record((F("562.93") - original[1], F("562.93") - original[0])),
        "zero_change_status": classify(original),
        "one_change_checked_by_group": checked,
        "one_change_count": sum(checked),
        "one_change_matches": matches,
        "one_change_excluded_count": len(excluded),
        "unresolved_count": 0,
        "closest_excluded_candidate": closest,
        "closest_excluded_distance_to_window_lower_bound_lbm": str(closest_gap),
        "equal_total_length_group_pairs_one_based": [[4, 5], [6, 7]],
        "explicit_equal_mass_family_g6_g7": [[str(a), str(b)] for a, b in family],
        "family_count": len(family),
        "three_change_example_areas_in2": list(map(str, example)),
        "limits": "Mass only; no stiffness, stress, displacement, historical-source adjudication, or exhaustive multi-entry search.",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
