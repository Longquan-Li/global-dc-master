from pathlib import Path
import re, json, urllib.parse
import requests

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"raw"/"dset_sg_my"
OUT.mkdir(parents=True,exist_ok=True)
UA={"User-Agent":"global-dc-facility-database/0.1"}

url="https://sedc.dset.tw/"
r=requests.get(url,timeout=90,headers=UA)
r.raise_for_status()
(OUT/"index.html").write_text(r.text,encoding="utf-8",errors="ignore")

assets=[]
for src in re.findall(r'(?:src|href)=["\']([^"\']+)["\']',r.text,re.I):
    u=urllib.parse.urljoin(r.url,src)
    if any(x in u.lower() for x in [".js",".json",".zst",".csv"]):
        assets.append(u)

manifest=[]
for i,u in enumerate(dict.fromkeys(assets),1):
    try:
        rr=requests.get(u,timeout=120,headers=UA)
        name=Path(urllib.parse.urlparse(rr.url).path).name or f"asset_{i}"
        p=OUT/name
        if p.exists(): p=OUT/f"{i}_{name}"
        p.write_bytes(rr.content)
        manifest.append({"url":u,"resolved":rr.url,"file":p.name,"bytes":len(rr.content),"content_type":rr.headers.get("content-type","")})
    except Exception as e:
        manifest.append({"url":u,"error":str(e)})

# Also preserve the public client.zst endpoint surfaced by DSET.
try:
    rr=requests.get("https://sedc.dset.tw/client.zst",timeout=120,headers=UA)
    (OUT/"client.zst").write_bytes(rr.content)
    manifest.append({"url":"https://sedc.dset.tw/client.zst","resolved":rr.url,"file":"client.zst","bytes":len(rr.content),"content_type":rr.headers.get("content-type","")})
except Exception as e:
    manifest.append({"url":"https://sedc.dset.tw/client.zst","error":str(e)})

(OUT/"asset_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"assets":len(manifest)},indent=2))
