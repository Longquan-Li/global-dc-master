# Methodology

## 1. Raw-first principle

All upstream data are saved unchanged under `raw/<source>/` with retrieval metadata. Harmonization never overwrites raw values.

## 2. Backbone

Human Override is used as the initial global backbone because it already merges several open sources while retaining source URLs and includes:

- facility identity
- operator / owner
- address and coordinates
- lifecycle status
- facility type
- total IT power capacity (MW)
- PUE
- total facility area (m²)
- grid operator / substation
- source URLs and last verification date

ATLAS, Compute Atlas, PeeringDB and Japan Data Center Watch are retained independently for validation and later entity-level enrichment.

## 3. Power taxonomy

The master database uses explicit `power_type`:

- `it_load`
- `facility_total`
- `utility_supply`
- `campus_total`
- `planned_maximum`
- `unknown`

Human Override defines `power_capacity_mw` as total IT power capacity, so these observations enter as `it_load`.

No annual energy is calculated from `utility_supply`, `planned_maximum` or `unknown` without additional assumptions.

## 4. Area taxonomy

Area observations are stored separately by meaning:

- `site_area`
- `footprint_area`
- `floor_area`
- `data_hall_area`
- `total_facility_area`
- `unknown`

Human Override `total_area_sqm` is retained as `total_facility_area`.

## 5. Annual electricity

Annual electricity is not treated as observed unless directly reported.

For scenario calculations using IT capacity:

```
E_MWh = P_IT_MW × utilization × PUE × 8760
```

Utilization and PUE assumptions must be stored with the derived value and never replace measured energy.

## 6. Next enrichment layers

Priority:
1. Japan Data Center Watch — explicit power type + site/floor area.
2. China Scientific Data 2026 — verified facility locations.
3. Singapore/Malaysia DSET — regional power/status.
4. OSM polygons — footprint geometry.
5. national/EU energy reporting — calibration.
