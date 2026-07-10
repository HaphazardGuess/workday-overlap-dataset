# ClockJumper Working-Hours Overlap Dataset

Working-hour overlap for every pair of 223 world cities — 24,753 pairs —
computed from IANA timezone data, sampled on January 15 and July 15.

This is the dataset behind the [ClockJumper overlap research](https://clockjumper.com/research/overlap),
including the finding that **San Francisco shares working hours with fewer
cities than Honolulu** for any 8-hour workday.

## Files

| File | Description |
|---|---|
| `clockjumper-overlap-dataset.csv` | 24,753 city pairs with January and July overlap minutes |
| `verify_overlap.py` | Verification script — recomputes every published figure from the CSV |

## CSV columns

`city_a, city_b, country_a, country_b, iana_a, iana_b, overlap_jan_minutes, overlap_jul_minutes`

Overlap = shared minutes between the two cities' 9:00–17:00 local windows,
computed dateline-aware (circular offset difference). January 15 and July 15
capture both hemispheres' DST states.

## Verify the numbers yourself

Requirements: Python 3.9+ with the standard library only. On Windows,
run `pip install tzdata` first if you hit a zoneinfo error.

```
python3 verify_overlap.py clockjumper-overlap-dataset.csv
```

Expected output ends with `ALL CHECKS PASSED` (exit code 0). The script runs
27 checks:

- **Structure** — 24,753 pairs, 223 cities, 42 timezone regimes
- **Headline statistics** — January mean 3h04m, 7,294 zero-overlap pairs (29.5%)
- **Connectivity** — San Francisco reaches 73 of 222 cities (either season;
  72 in January alone), Honolulu reaches 117
- **Anchor pairs** — NY–London 3h00m, LA–Auckland 5h00m, London–Sydney 0h,
  SF–Sydney 3h00m
- **Meridian staircase** — mean overlap and pair count at each hour of
  circular offset separation
- **Independent recomputation** — rebuilds all 24,753 January overlaps from
  raw IANA offsets with its own dateline-aware logic and confirms every value
  matches the CSV

> **Note:** browser Python sandboxes (e.g. online-python.com) won't work —
> they can't take the CSV as a command-line argument and often lack timezone
> data. Use a local Python install, [Google Colab](https://colab.research.google.com)
> (upload both files, then `!python3 verify_overlap.py clockjumper-overlap-dataset.csv`),
> or open this repo in a GitHub Codespace.

## Notes on definitions

- **Reach** counts every city that shares at least one working minute
  (9:00–17:00 local) in either January or July.
- Published staircase figures floor partial minutes (the Δ0 mean is
  479.94 min, displayed as 7h59m). The script matches this convention.
- The 9:00–17:00 window is a fixed analytical baseline. All results are
  identical for any 8-hour window regardless of start time; longer windows
  change the results, including reversing the SF–Honolulu finding at 10 hours.
  See the [window sensitivity study](https://clockjumper.com/research/overlap/window-sensitivity).

Verified against IANA tzdata **2026a**. If a jurisdiction changes its timezone
rules after this release, offsets recomputed with newer tzdata may differ.

## Methodology and sources

Full methodology — city roster gates, dual city-weighted/regime-weighted
framing, and sources — is documented at
[clockjumper.com/research/overlap/methodology](https://clockjumper.com/research/overlap/methodology).

## License

Dataset and script released under CC BY 4.0 — free to use with attribution
to [ClockJumper](https://clockjumper.com).
