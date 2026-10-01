from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"processed"/"dc_master.csv"
out=ROOT/"processed"/"operator_reported_capacity_queue.csv"
if p.exists():
    df=pd.read_csv(p,low_memory=False)
    q=df[df["power_mw"].isna()].copy()
    q=q[q["operator"].notna() & (q["operator"].astype(str).str.strip()!="")]
    q["operator_norm"]=q["operator"].astype(str).str.strip()
    counts=q.groupby("operator_norm").size().rename("missing_capacity_facilities").reset_index()
    counts=counts.sort_values("missing_capacity_facilities",ascending=False)
    counts.to_csv(out,index=False)
    print("operator queue",len(counts))
