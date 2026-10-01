# Capacity estimation framework

Goal: produce a usable MW value for every facility while preserving a strict distinction between observed and modeled capacity.

## Hierarchy

### Tier 1 — Reported power
Directly reported IT load or a source with a clearly defined capacity type.

Fields:
- power_mw
- power_type
- power_method=reported
- confidence_high=true

### Tier 2 — Area-based estimate
Use a calibrated empirical relationship only when a facility has a defensible building footprint or floor area.

Preferred model:

log(P_IT) = alpha + beta*log(A) + controls

Controls can include:
- facility type
- region/country
- operator
- vintage/year built
- hyperscale/colocation/enterprise
- status

Do not use one universal W/m² coefficient without calibration.

If only footprint is known:

floor_area_est = footprint_area * estimated_floor_count

Then:

P_IT_est = f(floor_area_est, facility_type, region, vintage)

All assumptions must be retained.

### Tier 3 — Feature-based statistical estimate
For facilities with no usable area but with metadata, estimate MW from:
- operator
- country/market
- facility type
- year built
- status
- coordinates / metro market
- known AI workload
- network/interconnection indicators

### Tier 4 — Fallback imputation
For records with minimal metadata, allocate capacity using market/type priors and country-level calibration totals.

This gives full coverage but must have the widest uncertainty interval.

## Calibration

Country totals should be benchmarked against government or published industry totals.
Never force every individual site to a false precision simply to match a national total.

## Output fields

- power_mw_best
- power_mw_low
- power_mw_high
- power_estimation_tier
- power_estimation_method
- power_training_sample
- power_model_version
- power_source_url
- power_type

## Important limitation

A building footprint is not equivalent to data-hall floor area. Data-center power density varies substantially across enterprise, colocation, hyperscale and AI facilities. Area can support estimation, but area alone cannot produce equally reliable MW values for every facility.
