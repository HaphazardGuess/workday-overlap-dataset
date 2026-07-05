# ClockJumper Global Workday Overlap Dataset

The workday-overlap dataset from ClockJumper Research: shared 9-to-5 working hours between every pair of **223 major world cities**, computed for January and July 2026 from IANA time-zone rules. The cities span **42 distinct time-zone regimes** and are selected through four documented inclusion gates — not a convenience sample. (This is one of ClockJumper's research datasets; the event-viewing "watch-time" studies are published separately.)

**Full analysis and interactive tools:** https://clockjumper.com/research/overlap
**License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to use, share, and adapt with attribution.

## What's here

| File | Contents |
|---|---|
| `data/overlap-dataset.csv` | 24,753 city-pair rows: January and July shared-workday minutes (0–480) |
| `data/cities.csv` | The 223 cities: IANA zone, January/July UTC offset, inclusion gate |
| `data/data-dictionary.json` | Column definitions, methodology, conventions |
| `data/excluded-cities.json` | Notable cities not in the dataset, and why |
| `scripts/build_overlap.py` | Reproducibly regenerates `overlap-dataset.csv` from `cities.csv` |

The canonical CSV is also served live at <https://clockjumper.com/research/clockjumper-overlap-dataset.csv>.

## The dataset at a glance

- **223 cities · 42 time-zone regimes · 24,753 unique pairs**
- Workday defined as 09:00–17:00 local (480 minutes)
- In January, the average pair shares **3h04m** of the workday; **7,294 pairs (29.5%)** share no working hours at all, while 2,334 (9.4%) share the entire day
- Overlap is measured in absolute time and **wraps the international dateline** — so, correctly, Los Angeles and Auckland share five hours (LA afternoon = Auckland morning), not zero

## How cities were chosen

A city enters through any one of four gates, recorded per city in `cities.csv`:

1. **GaWC 2024** — Alpha/Beta/Gamma world city (190 cities)
2. **Services-delivery hub** — a principal delivery city in a Kearney GSLI top-tier country, per national industry-association data (12)
3. **Time-zone-regime completeness** — the most populous city (≥100k) of any inhabited UTC-offset regime not otherwise covered (15)
4. **Euromonitor 2025** — named in the publicly-released Top 100 City Destinations rankings (6)

Headline statistics are reported both **city-weighted** (each pair counts once) and **regime-weighted** (each of the 861 distinct different-regime pairs counts once), so roster composition cannot drive the findings. Cities that meet no gate — and the reasons — are listed in `excluded-cities.json`.

## Reproducing the data

```bash
python3 scripts/build_overlap.py   # Python 3.9+; regenerates data/overlap-dataset.csv
```

All offsets are computed from the IANA Time Zone Database at build time — nothing is hardcoded. This release was built against **IANA tzdata 2026a**; a different tz-database release may shift a handful of pairs for jurisdictions with recent daylight-saving rule changes.

## Citation

> ClockJumper Research (2026). *ClockJumper Global Workday Overlap Dataset*, 2026 edition. https://clockjumper.com/research/overlap/dataset. Licensed CC BY 4.0.

(A machine-readable citation is in `CITATION.cff`.)
