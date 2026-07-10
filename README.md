# ClockJumper Working-Hours Overlap Dataset

Working-hour overlap for every pair of 223 world cities — 24,753 pairs —
computed from IANA timezone data, sampled on January 15 and July 15, 2026.

This is the dataset behind the [ClockJumper overlap research](https://clockjumper.com/research/overlap),
including the finding that **San Francisco shares working hours with fewer
cities than Honolulu** for any 8-hour workday.

## What's in this repo

| Path | Description |
|---|---|
| `data/overlap-dataset.csv` | 24,753 city pairs with January and July overlap minutes |
| `data/cities.csv` | The 223-city roster: IANA ids, UTC offsets, inclusion gate, GaWC tier |
| `data/data-dictionary.json` | Full column definitions, conventions, and methodology summary |
| `data/excluded-cities.json` | Documented omissions and the reason for each |
| `scripts/build_overlap.py` | **Builds** the dataset from `cities.csv` using IANA timezone rules |
| `verify_overlap.py` | **Verifies** the dataset: independently recomputes every published figure |
| `CITATION.cff` | Citation metadata (GitHub's "Cite this repository" button) |

The build script and the verification script use independently written
overlap logic — the dataset can be regenerated from scratch and checked
against itself.

## Verify the numbers yourself

Requirements: Python 3.9+ with the standard library only. On Windows,
run `pip install tzdata` first if you hit a zoneinfo error.

```
python3 verify_overlap.py data/overlap-dataset.csv
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

To rebuild the dataset from the city roster instead:

```
python3 scripts/build_overlap.py
```

> **Note:** browser Python sandboxes (e.g. online-python.com) won't work —
> they can't take the CSV as a command-line argument and often lack timezone
> data. Use a local Python install, [Google Colab](https://colab.research.google.com)
> (upload the script and `data/` folder, then run the command above with `!`
> in front), or open this repo in a GitHub Codespace.

## Notes on definitions

- **Overlap** = shared minutes between the two cities' 9:00–17:00 local
  windows, computed dateline-aware (circular offset difference). January 15
  and July 15 capture both hemispheres' DST states.
- **Reach** counts every city that shares at least one working minute in
  either January or July.
- Published staircase figures floor partial minutes (the Δ0 mean is
  479.94 min, displayed as 7h59m). The verification script matches this
  convention.
- The 9:00–17:00 window is a fixed analytical baseline. Results are identical
  for any 8-hour window regardless of start time; longer windows change the
  results, including reversing the SF–Honolulu finding at 10 hours. See the
  [window sensitivity study](https://clockjumper.com/research/overlap/window-sensitivity).

Built and verified against IANA tzdata **2026a**. If a jurisdiction changes
its timezone rules after this release, offsets recomputed with newer tzdata
may differ.

## Methodology and sources

City roster gates, the dual city-weighted/regime-weighted framing, and all
sources are documented in `data/data-dictionary.json` and at
[clockjumper.com/research/overlap/methodology](https://clockjumper.com/research/overlap/methodology).

## License

[CC BY 4.0](LICENSE) — free to use with attribution to
[ClockJumper](https://clockjumper.com). Citation format is in `CITATION.cff`.
