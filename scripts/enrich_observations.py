from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
OUT = ROOT / "processed"
OUT.mkdir(parents=True, exist_ok=True)

# ---------- Japan Data Center Watch ----------
jp_detail = RAW / "japan_dc_watch" / "facility_details.json"
jp_list = RAW / "japan_dc_watch" / "facilities.json"
jp_rows = []

if jp_detail.exists():
    detail_obj = json.loads(jp_detail.read_text(encoding="utf-8"))
    for rec in detail_obj:
        fac = rec.get("facility", {}) or {}
        ops = rec.get("operators", []) or []
        sources = rec.get("sources", []) or []
        source_url = sources[0].get("canonical_url","") if sources and isinstance(sources[0],dict) else ""
        jp_rows.append({
            "source_dataset":"Japan Data Center Watch",
            "source_record_id":fac.get("slug") or fac.get("id"),
            "name":fac.get("canonical_name_en") or fac.get("canonical_name"),
            "operator":"; ".join([o.get("name","") for o in ops if isinstance(o,dict) and o.get("name")]),
            "country":"Japan",
            "admin1":fac.get("prefecture"),
            "city":fac.get("municipality"),
            "latitude":fac.get("latitude"),
            "longitude":fac.get("longitude"),
            "site_area":fac.get("site_area_m2"),
            "site_area_unit":"m2" if fac.get("site_area_m2") is not None else "",
            "floor_area":fac.get("floor_area_m2"),
            "floor_area_unit":"m2" if fac.get("floor_area_m2") is not None else "",
            "power_mw":fac.get("power_capacity_mw"),
            "power_type":fac.get("power_capacity_type") or "unknown",
            "power_method":"reported",
            "status":fac.get("status"),
            "confidence":fac.get("evidence_level"),
            "source_url":source_url or ("https://japandatacenter.org/facilities/" + str(fac.get("slug",""))),
            "source_asof":fac.get("status_as_of") or fac.get("updated_at"),
        })
elif jp_list.exists():
    jp_obj = json.loads(jp_list.read_text(encoding="utf-8"))
    for r in jp_obj.get("items", []):
        jp_rows.append({
            "source_dataset":"Japan Data Center Watch",
            "source_record_id":r.get("slug"),
            "name":r.get("canonical_name_en") or r.get("canonical_name"),
            "country":"Japan",
            "admin1":r.get("prefecture"),
            "city":r.get("municipality"),
            "latitude":None,
            "longitude":None,
            "site_area":None,
            "site_area_unit":"",
            "floor_area":None,
            "floor_area_unit":"",
            "power_mw":r.get("power_capacity_mw"),
            "power_type":r.get("power_capacity_type") or "unknown",
            "power_method":"reported",
            "status":r.get("status"),
            "confidence":r.get("evidence_level"),
            "source_url":"https://japandatacenter.org/facilities/" + str(r.get("slug")),
            "source_asof":r.get("status_as_of"),
        })

if jp_rows:
    jp_df = pd.DataFrame(jp_rows)
    jp_df.to_csv(OUT / "japan_observations.csv", index=False)
    jp_area = jp_df.loc[(jp_df["site_area"].notna()) | (jp_df["floor_area"].notna())].copy()
    jp_area.to_csv(OUT / "japan_area_observations.csv", index=False)

# ---------- Compute Atlas ----------
ca_path = RAW / "compute_atlas" / "facilities.json"
if ca_path.exists():
    ca_obj = json.loads(ca_path.read_text(encoding="utf-8"))
    facilities = ca_obj if isinstance(ca_obj, list) else ca_obj.get("facilities", [])
    rows = []
    for r in facilities:
        if r.get("facilityType") != "data_center":
            continue
        loc = r.get("location") or {}
        cap = r.get("capacityMw") or {}
        land = r.get("landAcres")
        srcs = r.get("sources") or []
        source_url = ""
        if srcs and isinstance(srcs[0], dict):
            source_url = srcs[0].get("url","")
        if cap.get("operational") is not None:
            rows.append({
                "source_dataset":"Compute Atlas",
                "source_record_id":r.get("id"),
                "name":r.get("name"),
                "operator":r.get("operator"),
                "country":"United States",
                "admin1":loc.get("state"),
                "city":loc.get("city"),
                "latitude":loc.get("lat"),
                "longitude":loc.get("lon"),
                "site_area":land,
                "site_area_unit":"acre" if land is not None else "",
                "power_mw":cap.get("operational"),
                "power_type":"unknown",
                "power_method":"reported",
                "status":r.get("status"),
                "confidence":r.get("confidence"),
                "source_url":source_url,
                "source_asof":r.get("lastUpdated"),
                "notes":r.get("notes"),
            })
        if cap.get("planned") is not None:
            rows.append({
                "source_dataset":"Compute Atlas",
                "source_record_id":r.get("id"),
                "name":r.get("name"),
                "operator":r.get("operator"),
                "country":"United States",
                "admin1":loc.get("state"),
                "city":loc.get("city"),
                "latitude":loc.get("lat"),
                "longitude":loc.get("lon"),
                "site_area":land,
                "site_area_unit":"acre" if land is not None else "",
                "power_mw":cap.get("planned"),
                "power_type":"planned_maximum",
                "power_method":"reported",
                "status":"planned",
                "confidence":r.get("confidence"),
                "source_url":source_url,
                "source_asof":r.get("lastUpdated"),
                "notes":r.get("notes"),
            })
    ca_df = pd.DataFrame(rows)
    ca_df.to_csv(OUT / "compute_atlas_observations.csv", index=False)

# ---------- Combine source observations ----------
parts = []
for fn in ["japan_observations.csv","compute_atlas_observations.csv"]:
    p = OUT / fn
    if p.exists():
        try:
            parts.append(pd.read_csv(p, low_memory=False))
        except Exception:
            pass
if parts:
    cols = sorted(set().union(*[set(df.columns) for df in parts]))
    norm = []
    for df in parts:
        norm.append(df.reindex(columns=cols))
    reported = pd.concat(norm, ignore_index=True)
    reported.to_csv(OUT / "reported_power_observations.csv", index=False)
    # Compatibility alias
    reported.to_csv(OUT / "all_power_observations.csv", index=False)

# ---------- Summary enrichment ----------
summary_path = OUT / "summary.json"
summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
if (OUT/"japan_observations.csv").exists():
    j = pd.read_csv(OUT/"japan_observations.csv")
    summary["japan_records"] = int(len(j))
    summary["japan_with_power"] = int(j["power_mw"].notna().sum()) if "power_mw" in j else 0
if (OUT/"compute_atlas_observations.csv").exists():
    c = pd.read_csv(OUT/"compute_atlas_observations.csv", low_memory=False)
    summary["compute_atlas_power_observations"] = int(len(c))
    summary["compute_atlas_with_land_area"] = int(c["site_area"].notna().sum()) if "site_area" in c else 0
summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
