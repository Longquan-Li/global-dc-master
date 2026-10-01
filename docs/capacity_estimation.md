# Reported-capacity-only policy

The Global DC Facility Database does **not** estimate capacity for facilities without a public capacity observation.

## Rules

1. A facility MW value is stored only when an upstream source explicitly reports a capacity.
2. Missing capacity remains blank.
3. Area, floor space and footprint are descriptive attributes only and are never converted into MW.
4. Statistical imputation, market priors and operator-based estimates are excluded.
5. Reported and source-compiled values must retain provenance and capacity meaning.

## Power taxonomy

Reported MW observations should be classified whenever possible as:

- `it_load`
- `facility_total`
- `utility_supply`
- `campus_total`
- `planned_maximum`
- `unknown`

The database does not convert one category into another.

## Area

Area fields may be retained from public sources:

- site / land area
- footprint area
- gross floor area
- data-hall / whitespace area

They are not used to infer power capacity.

## Energy

Annual electricity is not derived unless a separate analysis explicitly requests it. The facility database itself stores observed/reported infrastructure attributes only.
