from pathlib import Path
import csv, json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
OUT = ROOT / "processed"
OUT.mkdir(parents=True, exist_ok=True)

src = RAW / "human_override" / "datacenters.csv"
if not src.exists():
    raise FileNotFoundError(src)

df = pd.read_csv(src, low_memory=False)

# Preserve the source schema in raw/. Build a separate harmonized table.
master = pd.DataFrame({
    "facility_id": df.get("id"),
    "name": df.get("name"),
    "operator": df.get("operator"),
    "owner": df.get("owner"),
    "address": df.get("address"),
    "city": df.get("city"),
    "admin1": df.get("state_province"),
    "country": df.get("country"),
    "country_code": df.get("country_code"),
    "latitude": df.get("latitude"),
    "longitude": df.get("longitude"),
    "status": df.get("status"),
    "facility_type": df.get("facility_type"),
    "year_built": df.get("year_built"),
    "year_decommissioned": df.get("year_decommissioned"),
    "power_mw": df.get("power_capacity_mw"),
    "power_type": "it_load",
    "power_method": df.get("power_capacity_mw").notna().map({True:"reported_or_source_compiled",False:""}),
    "pue": df.get("pue"),
    "total_facility_area_m2": df.get("total_area_sqm"),
    "grid_operator": df.get("grid_operator"),
    "grid_substation": df.get("grid_substation"),
    "cooling_type": df.get("cooling_type"),
    "water_usage_m3_per_day": df.get("water_usage_m3_per_day"),
    "ai_workload": df.get("ai_workload"),
    "known_ai_tenants": df.get("known_ai_tenants"),
    "source_urls": df.get("sources"),
    "last_verified": df.get("last_verified"),
    "seed_source": df.get("seed_source"),
    "source_dataset": "Human Override",
})
master.to_csv(OUT / "dc_master.csv", index=False)

power = master.loc[master["power_mw"].notna(), [
    "facility_id","name","country","latitude","longitude","power_mw",
    "power_type","power_method","status","source_urls","last_verified"
]].copy()
power.to_csv(OUT / "power_observations.csv", index=False)

area = master.loc[master["total_facility_area_m2"].notna(), [
    "facility_id","name","country","latitude","longitude",
    "total_facility_area_m2","source_urls","last_verified"
]].copy()
area["area_type"] = "total_facility_area"
area["area_method"] = "reported_or_source_compiled"
area.to_csv(OUT / "area_observations.csv", index=False)

summary = {
    "facilities": int(len(master)),
    "with_coordinates": int((master["latitude"].notna() & master["longitude"].notna()).sum()),
    "with_power_mw": int(master["power_mw"].notna().sum()),
    "with_area_m2": int(master["total_facility_area_m2"].notna().sum()),
    "countries": int(master["country"].dropna().nunique()),
}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
