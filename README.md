# Global DC Facility Database

Open, auditable facility-level database for data-center **location, area, power capacity and energy-system modelling**.

## Architecture

```
raw/                  # untouched upstream snapshots
processed/
  dc_master.csv       # harmonized facility table
  power_observations.csv
  area_observations.csv
scripts/
  build_master.py
docs/
  methodology.md
sources/
  source_manifest.csv
.github/workflows/
  refresh-data.yml
```

## Current backbone

The first global backbone is **Human Override**, an ODbL-1.0 open dataset seeded from ATLAS, Compute Atlas, PeeringDB and PNNL. Its canonical schema includes facility identity, coordinates, lifecycle status, total IT power capacity, PUE, facility area, grid information and claim-level source URLs.

The refresh workflow also preserves independent raw snapshots of:
- Human Override
- ATLAS / Global Data Center Map
- Compute Atlas
- PeeringDB
- Japan Data Center Watch

## Critical modelling rule

These are **not interchangeable**:

- IT load
- facility-total electrical capacity
- utility/grid connection capacity
- campus capacity
- planned maximum capacity

Likewise, do not mix:

- site/land area
- building footprint
- gross floor area
- data-hall / whitespace area

Every normalized value must retain source, method and meaning.

## Refresh

The GitHub Action `refresh-data.yml` runs automatically when first added and can later be run on schedule. It downloads upstream sources into `raw/`, runs `scripts/build_master.py`, and commits refreshed outputs.

## Citation / license

Each upstream dataset retains its own license and provenance. This repository does not relicense upstream data. See `sources/source_manifest.csv` and source repositories before redistribution.
