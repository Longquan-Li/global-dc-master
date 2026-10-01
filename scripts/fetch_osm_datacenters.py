from pathlib import Path
import json, math, time
import requests
import pandas as pd
from pyproj import Geod

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"raw"/"osm"
OUT.mkdir(parents=True,exist_ok=True)
UA={"User-Agent":"global-dc-facility-database/0.1 (research)"}
endpoint="https://overpass-api.de/api/interpreter"

# Continental bboxes to avoid one huge global query.
boxes=[
 ("north_america","5,-170,85,-50"),
 ("south_america","-60,-90,15,-30"),
 ("europe_africa","-40,-30,75,60"),
 ("asia","0,55,80,180"),
 ("oceania","-50,90,10,180"),
]
records={}
geod=Geod(ellps="WGS84")
for label,bbox in boxes:
    q=f'''[out:json][timeout:180];
(
  way["telecom"="data_center"]({bbox});
  relation["telecom"="data_center"]({bbox});
  way["building"="data_center"]({bbox});
  relation["building"="data_center"]({bbox});
  way["industrial"="data_centre"]({bbox});
  relation["industrial"="data_centre"]({bbox});
);
out tags center geom;'''
    try:
        r=requests.post(endpoint,data={"data":q},timeout=240,headers=UA)
        r.raise_for_status()
        obj=r.json()
        (OUT/f"{label}.json").write_text(json.dumps(obj,ensure_ascii=False),encoding="utf-8")
        for el in obj.get("elements",[]):
            records[f'{el.get("type")}/{el.get("id")}']=el
        time.sleep(3)
    except Exception as e:
        (OUT/f"{label}_ERROR.txt").write_text(str(e))

# Keep a compact index. No MW inference.
out=[]
for el in records.values():
    tags=el.get("tags") or {}
    center=el.get("center") or {}
    area_m2=None
    geom=el.get("geometry") or []
    if el.get("type")=="way" and len(geom)>=3:
        try:
            lons=[p["lon"] for p in geom]
            lats=[p["lat"] for p in geom]
            a,_=geod.polygon_area_perimeter(lons,lats)
            area_m2=abs(a)
        except Exception:
            area_m2=None
    out.append({
      "osm_type":el.get("type"),"osm_id":el.get("id"),
      "name":tags.get("name"),"operator":tags.get("operator"),"owner":tags.get("owner"),
      "latitude":center.get("lat"),"longitude":center.get("lon"),
      "telecom":tags.get("telecom"),"building":tags.get("building"),"industrial":tags.get("industrial"),
      "footprint_area_m2":area_m2,
      "source":"OpenStreetMap"
    })
(OUT/"osm_dc_index.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"osm_features":len(out)},indent=2))

# Write a processed footprint table. This is descriptive geometry only; it is never converted to MW.
PROC=ROOT/"processed"
PROC.mkdir(parents=True,exist_ok=True)
pdf=pd.DataFrame(out)
if not pdf.empty:
    pdf.to_csv(PROC/"osm_area_observations.csv",index=False)
