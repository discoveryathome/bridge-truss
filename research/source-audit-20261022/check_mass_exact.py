"""Exact finite mass classification using only Python's standard library.

Integer square-root enclosures decide mass-bin membership, not structural
feasibility, source intent, or optimality. No repository solver is imported.
"""

from decimal import Decimal, localcontext
from fractions import Fraction as F
from hashlib import sha256
from math import isqrt
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[2]


def classify():
    raw = (ROOT / "benchmarks/25bar.json").read_bytes()
    assert sha256(raw).hexdigest() == "5291c9023163d70b696d644923fc2ad94bcaf07984a6f037986f13035ef42328"
    b = json.loads(raw, parse_float=F)
    assert b["density_lbm_in3"] == F(1, 10)
    groups = b["groups"]
    original = list(map(F, b["published_disputed"]["areas"]))
    catalog = list(map(F, b["catalog"]))
    assert len(catalog) == len(set(catalog)) == 30
    assert all(a in catalog for a in original)
    assert len(groups) == len(b["members"]) == 25
    assert set(groups) == set(range(8))

    # Doubling the half-inch coordinates makes every squared length integral.
    squares = []
    for i, j in b["members"]:
        squared = sum((2 * (v - u)) ** 2 for u, v in zip(b["nodes"][i-1], b["nodes"][j-1]))
        assert F(squared).denominator == 1
        squares.append(int(squared))
    precision = 10**50
    roots = [isqrt(s * precision**2) for s in squares]
    eps = [int(r*r != s * precision**2) for r, s in zip(roots, squares)]
    assert all(r*r <= s * precision**2 < (r+1)**2 for r, s in zip(roots, squares))

    def enclosure(areas):
        ticks = [10 * a for a in areas]
        assert all(t.denominator == 1 and t > 0 for t in ticks)
        lower = sum(ticks[g] * r for g, r in zip(groups, roots))
        upper = sum(ticks[g] * (r + e) for g, r, e in zip(groups, roots, eps))
        return lower / (200 * precision), upper / (200 * precision)

    low, high = F("484.325"), F("484.335")
    inside, outside, widths = [], [], []
    for group in range(8):
        for area in catalog:
            if area == original[group]:
                continue
            candidate = original.copy()
            candidate[group] = area
            ml, mu = enclosure(candidate)
            widths.append(mu - ml)
            if low <= ml and mu < high:
                inside.append((group + 1, area))
            else:
                assert mu < low or ml >= high, "Enclosure crosses a mass-bin boundary"
                gl, gu = (low - mu, low - ml) if mu < low else (ml - high, mu - high)
                outside.append((gl, gu, group + 1, area))

    assert len(inside) + len(outside) == 232
    assert inside == [(1, F("0.3")), (4, F("0.2")), (5, F("2.2"))]
    assert len(outside) == 229
    assert max(widths) == F("2.32e-50")
    nearest = min(outside)
    assert nearest[2:] == (1, F("0.4"))
    assert nearest[1] < min(v[0] for v in outside if v[2:] != nearest[2:])
    assert all(v[0] > F("0.74364419607749081316") for v in outside)
    with localcontext() as ctx:
        ctx.prec = 60
        decimal = lambda value: str(Decimal(value.numerator) / Decimal(value.denominator))
        return {
            "scope": "Exact mass-bin classification of 232 single-group replacements only",
            "model_sha256": sha256(raw).hexdigest(),
            "script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
            "matching_group_and_area_fraction": [[g, str(a)] for g, a in inside],
            "excluded_count": len(outside),
            "closest_excluded_group": nearest[2],
            "closest_excluded_area_fraction": str(nearest[3]),
            "minimum_distance_lower_bound_fraction": str(nearest[0]),
            "minimum_distance_upper_bound_fraction": str(nearest[1]),
            "minimum_distance_decimal_approximations": [decimal(nearest[0]), decimal(nearest[1])],
            "maximum_enclosure_width_lbm": decimal(max(widths)),
            "structural_feasibility_checked": False,
        }


if __name__ == "__main__":
    print(json.dumps(classify(), indent=2))
