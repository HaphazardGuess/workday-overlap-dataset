"""
Reproducibly builds the ClockJumper Global Workday Overlap Dataset.
Reads cities.csv, computes shared 09:00-17:00 workday minutes for every city pair
in January and July 2026 using the IANA Time Zone Database, and writes overlap-dataset.csv.

Overlap wraps the international dateline (uses the shorter of the two ways around the
24h clock), so trans-Pacific pairs are computed correctly.

Requires: Python 3.9+ (zoneinfo). Built and verified against IANA tzdata 2026a.
Run:  python3 build_overlap.py
"""
import csv, os
from datetime import datetime
from zoneinfo import ZoneInfo
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
JAN, JUL = datetime(2026, 1, 15, 12), datetime(2026, 7, 15, 12)

def offset_minutes(iana, when):
    return int(when.replace(tzinfo=ZoneInfo(iana)).utcoffset().total_seconds() // 60)

def overlap_minutes(off_a, off_b):
    """Shared minutes of two 09:00-17:00 (480-min) local workdays, wrapping the dateline."""
    d = abs(off_a - off_b)
    if d > 720:                 # shorter way around the 24h clock
        d = 1440 - d
    return max(0, 480 - d)

def main():
    with open(os.path.join(DATA, "cities.csv"), encoding="utf-8") as f:
        cities = list(csv.DictReader(f))
    for c in cities:
        c["jan"] = offset_minutes(c["iana"], JAN)
        c["jul"] = offset_minutes(c["iana"], JUL)
    cities.sort(key=lambda c: c["city"])

    out = os.path.join(DATA, "overlap-dataset.csv")
    n = 0
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["city_a","city_b","country_a","country_b","iana_a","iana_b",
                    "overlap_jan_minutes","overlap_jul_minutes"])
        for a, b in combinations(cities, 2):
            w.writerow([a["city"], b["city"], a["country"], b["country"],
                        a["iana"], b["iana"],
                        overlap_minutes(a["jan"], b["jan"]),
                        overlap_minutes(a["jul"], b["jul"])])
            n += 1
    print(f"wrote {n} pairs to overlap-dataset.csv")

if __name__ == "__main__":
    main()
