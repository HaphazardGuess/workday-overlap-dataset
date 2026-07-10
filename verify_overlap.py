#!/usr/bin/env python3
"""ClockJumper overlap dataset verification script.

Recomputes every headline figure in the ClockJumper overlap research
directly from the published CSV, independent of the site's own pipeline.

Usage:
    python3 verify_overlap.py clockjumper-overlap-dataset.csv

Requires Python 3.9+ (zoneinfo). No third-party packages.
On Windows, `pip install tzdata` if zoneinfo lacks timezone data.
"""

import csv
import sys
from collections import Counter, defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

WORK_START = 9 * 60   # 09:00 local
WORK_END = 17 * 60    # 17:00 local
JAN = (1, 15)
JUL = (7, 15)
YEAR = 2026


def fmt(minutes):
    return f"{int(minutes // 60)}h{int(minutes % 60):02d}m"


def utc_offset_minutes(tz_name, month, day):
    dt = datetime(YEAR, month, day, 12, tzinfo=ZoneInfo(tz_name))
    return dt.utcoffset().total_seconds() / 60


def circular_delta(a, b):
    """Circular minimum distance between two UTC offsets, in minutes.

    This is the dateline fix: naive abs(a-b) computes LA-Auckland as a
    21-hour gap; the true separation around the clock face is 3 hours.
    """
    d = abs(a - b)
    return min(d, 1440 - d)


def independent_overlap(off_a, off_b):
    """Recompute working-hour overlap from offsets alone (9:00-17:00 local).

    Overlap between two fixed daily windows on a 24h circle, checking the
    three candidate day-alignments (-1, 0, +1 days) and taking the max.
    """
    best = 0
    for shift in (-1440, 0, 1440):
        # window of city B expressed in city A's local clock
        delta = (off_a - off_b) + shift
        b_start = WORK_START + delta
        b_end = WORK_END + delta
        overlap = min(WORK_END, b_end) - max(WORK_START, b_start)
        best = max(best, overlap)
    return max(best, 0)


def check(name, actual, expected):
    ok = actual == expected
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}: {actual}" + ("" if ok else f"  (expected {expected})"))
    return ok


def main(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))

    tz_names = {r["iana_a"] for r in rows} | {r["iana_b"] for r in rows}
    offsets = {tz: (utc_offset_minutes(tz, *JAN), utc_offset_minutes(tz, *JUL))
               for tz in tz_names}

    cities = {r["city_a"] for r in rows} | {r["city_b"] for r in rows}

    all_ok = True
    print("== Structure ==")
    all_ok &= check("pair rows", len(rows), 24753)
    all_ok &= check("cities", len(cities), 223)

    regimes = {offsets[tz] for tz in tz_names}
    all_ok &= check("timezone regimes (Jan,Jul offset pairs)", len(regimes), 42)

    print("\n== Headline statistics (January, city-weighted) ==")
    jan = [int(r["overlap_jan_minutes"]) for r in rows]
    mean_jan = sum(jan) / len(jan)
    all_ok &= check("mean overlap", fmt(round(mean_jan)), "3h04m")
    zero_jan = sum(1 for v in jan if v == 0)
    all_ok &= check("zero-overlap pairs", zero_jan, 7294)
    all_ok &= check("zero-overlap share", f"{100 * zero_jan / len(rows):.1f}%", "29.5%")

    print("\n== Connectivity (reach) ==")
    reach_any = Counter()
    reach_jan = Counter()
    for r in rows:
        oj, ol = int(r["overlap_jan_minutes"]), int(r["overlap_jul_minutes"])
        if oj > 0:
            reach_jan[r["city_a"]] += 1
            reach_jan[r["city_b"]] += 1
        if oj > 0 or ol > 0:
            reach_any[r["city_a"]] += 1
            reach_any[r["city_b"]] += 1
    all_ok &= check("San Francisco reach (either season)", reach_any["San Francisco"], 73)
    all_ok &= check("San Francisco reach (January only)", reach_jan["San Francisco"], 72)
    all_ok &= check("Honolulu reach (either season)", reach_any["Honolulu"], 117)

    print("\n== Anchor pairs (January) ==")
    idx = {}
    for r in rows:
        idx[frozenset((r["city_a"], r["city_b"]))] = r
    anchors = [
        ("New York", "London", 180),
        ("Los Angeles", "Auckland", 300),
        ("London", "Sydney", 0),
        ("San Francisco", "Sydney", 180),
    ]
    for a, b, expected in anchors:
        r = idx[frozenset((a, b))]
        all_ok &= check(f"{a} - {b}", int(r["overlap_jan_minutes"]), expected)

    print("\n== Meridian staircase (January) ==")
    buckets = defaultdict(list)
    for r in rows:
        d = circular_delta(offsets[r["iana_a"]][0], offsets[r["iana_b"]][0]) / 60
        # explicit thresholds: half-hour offsets (e.g. India +5:30) round UP,
        # avoiding Python round()'s banker's rounding at exact .5 values
        if d < 0.5:
            key = "0"
        elif d < 1.5:
            key = "1"
        elif d < 2.5:
            key = "2"
        elif d < 3.5:
            key = "3"
        elif d < 4.5:
            key = "4"
        else:
            key = "5+"
        buckets[key].append(int(r["overlap_jan_minutes"]))
    expected_stairs = {"0": (2344, "7h59m"), "1": (2369, "7h01m"),
                       "2": (1749, "6h04m"), "3": (1766, "5h10m"),
                       "4": (1433, "4h06m"), "5+": (15092, "0h58m")}
    for k in ["0", "1", "2", "3", "4", "5+"]:
        vals = buckets[k]
        mean = sum(vals) / len(vals)
        exp_n, exp_m = expected_stairs[k]
        all_ok &= check(f"delta {k}h pairs", len(vals), exp_n)
        # floor, not round: the published figures truncate partial minutes
        # (delta-0 mean is 479.94 min -> displayed as 7h59m)
        all_ok &= check(f"delta {k}h mean", fmt(int(mean)), exp_m)

    print("\n== Independent recomputation (dateline check) ==")
    mismatches = 0
    for r in rows:
        oa, ob = offsets[r["iana_a"]][0], offsets[r["iana_b"]][0]
        if independent_overlap(oa, ob) != int(r["overlap_jan_minutes"]):
            mismatches += 1
            if mismatches <= 5:
                print(f"  mismatch: {r['city_a']} - {r['city_b']}")
    all_ok &= check("pairs where independent recomputation differs", mismatches, 0)

    print("\n" + ("ALL CHECKS PASSED" if all_ok else "SOME CHECKS FAILED"))
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1])
