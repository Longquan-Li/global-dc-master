from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"processed"/"reported_power_observations.csv"
out=ROOT/"processed"/"reported_power_simple.csv"

df=pd.read_csv(p,low_memory=False)
df=df[df["power_mw"].notna()].copy()

keep=[
 "source_record_id","name","operator","country","admin1","city",
 "latitude","longitude","status","power_mw","power_type",
 "site_area","site_area_unit","floor_area","floor_area_unit",
 "source_dataset","source_url","source_asof","confidence"
]
for c in keep:
    if c not in df.columns:
        df[c]=pd.NA

def model_use(t):
    t=str(t or "").strip()
    return {
      "it_load":"Quantitative model input (reported IT load; apply PUE/load profile separately)",
      "facility_total":"Quantitative input only after confirming facility-total definition",
      "planned_maximum":"Forward-looking SMR candidate screening; not current load",
      "utility_supply":"Screening/upper-bound only; not direct IT demand",
      "campus_total":"Campus-level screening; avoid double counting buildings",
      "unknown":"Screening only until capacity definition is verified",
    }.get(t,"Screening only until capacity definition is verified")

df["model_use"]=df["power_type"].map(model_use)
cols=[
 "name","operator","country","admin1","city","latitude","longitude","status",
 "power_mw","power_type","model_use","site_area","site_area_unit",
 "floor_area","floor_area_unit","source_dataset","source_url","source_asof",
 "confidence","source_record_id"
]
df=df[cols].sort_values(["country","power_mw","name"],ascending=[True,False,True])
df.to_csv(out,index=False)
print({"rows":len(df),"facilities":df["source_record_id"].nunique(),"countries":df["country"].nunique()})
